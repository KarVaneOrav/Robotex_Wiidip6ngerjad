from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos, radians

# Chooses the mainboard if there are no others.
port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 115200, timeout=0.00001)
ser_ref = serial.Serial(port, 9600, timeout=0.01)

speeds = {119: 265, 122: 242, 124: 240, 126: 236, 128: 234, 131: 229, 134: 227,
          138: 225, 144: 221, 145: 220, 146: 217, 151: 215, 159: 213, 162: 210,
          166: 208, 172: 205, 184: 200, 190: 193, 196: 191, 206: 189, 220: 188,
          233: 184, 246: 183, 261: 183, 264: 182, 292: 180, 319: 178, 348: 177}
ref_mes = ''


def close():
    omni_drive([0, 0, 0])
    ser.close()
    ser_ref.close()


def read_ref(robot, court, current_task):
    global ref_mes
    while ser_ref.inWaiting() > 0:
        ref_mes += ser_ref.read().decode('ascii')

    while True:
        end = ref_mes.find('\n')
        if end == -1:
            return current_task
        else:
            mes = ref_mes[:end]
            print("From ref: ", mes)
            ref_mes = ref_mes[(end+1):]
            if mes[6] == court and mes[7] == robot or mes[7] == 'X':
                ser_ref.write(str.encode('rf:a' + court + robot + 'ACK----- \r \n'))
                if 'START' in mes:
                    return 'look'
                elif 'STOP' in mes:
                    return 'nothing'
                elif 'PING' in mes:
                    return current_task
                else:
                    print("bad ref message")
                    return current_task
            else:
                return current_task


def move_to_ball(ball):
    speed = 0.9
    x = ball[0] - 590
    y = 680 - ball[1]
    angle = atan2(y, x)
    motors(speed, angle)


def omni_drive(values):
    # for more manual insertion in form of [x, y, rotation]
    side_speed = values[0]
    forward_speed = values[1]
    angular_velocity = values[2]

    speed = sqrt(side_speed * side_speed + forward_speed * forward_speed)
    direction_angle = atan2(forward_speed, side_speed)
    motors(speed, direction_angle, angular_velocity)


def motors(speed, direction_angle, angular_velocity=0):
    # the core of omnidrive
    '''
    wheelLinearVelocity = robotSpeed * cos(robotDirectionAngle - wheelAngle) + \
                           wheelDistanceFromCenter * robotAngularVelocity
    Cause our robots wheels turn the other way, speeds are inverted.
    wheelSpeedToMainboardUnits = gearboxReductionRatio * encoderEdgesPerMotorRevolution /\
                                 (2 * PI * wheelRadius * pidControlFrequency)
    wheelAngularSpeedMainboardUnits = floor(wheelLinearVelocity * wheelSpeedToMainboardUnits)
    wheelSpeedToMainboardUnits = 90.991
    '''

    wheel0 = round(-1 * (speed * cos(direction_angle - radians(0)) + 0.13 * -angular_velocity) * 90.991)
    wheel1 = round(-1 * (speed * cos(direction_angle - radians(120)) + 0.13 * -angular_velocity) * 90.991)
    wheel2 = round(-1 * (speed * cos(direction_angle - radians(240)) + 0.13 * -angular_velocity) * 90.991)

    move = 'sd:'+str(wheel0)+':'+str(wheel1)+':'+str(wheel2)+'\n'
    ser.write(move.encode('utf-8'))
    print(move)


def rotate_ball(ball, basket):
    # sets the ball and the basket in a line (580 used as middle, real 590)
    if not basket:
        back = '40'
    elif basket[0] > 600:
        if basket[0] > 585:
            back = '15'
        else:
            back = '30'
    elif basket[0] < 560:
        if basket[0] < 575:
            back = '-15'
        else:
            back = '-30'
    else:
        back = '0'

    if ball[0] < 570:
        other = '-10'
    elif ball[0] > 610:
        other = '10'
    else:
        other = '0'

    ser.write(('sd:'+back+':'+other+':'+other+'\n').encode('utf-8'))

    if back == other:  # if both '0' start throwing
        return True
    else:
        return False


def controller(key):
    if key == 27:  # esc
        return True
    elif key == 119:  # w
        motors(0.6, 1.57, 0)
    elif key == 97:  # a
        motors(0.6, 3.14, 0)
    elif key == 115:  # s
        motors(0.6, 4.71, 0)
    elif key == 100:  # d
        motors(0.6, 0, 0)
    elif key == 111:  # o
        motors(0, 0, 2)
    elif key == 112:  # p
        motors(0, 0, -2)
    else:
        motors(0, 0, 0)

    return False  # if still controlling


def thrower_speed(distance):
    print(distance)
    if distance <= 119 or distance == 0:
        return 265
    elif distance >= 348:
        return 181
    else:
        speed = speeds.get(distance)
        if speed is None:
            distance_max = distance_min = distance
            speed_min = None
            speed_max = None
            while speed_min is None:
                distance_min += 1
                speed_min = speeds.get(distance_min)
            while speed_max is None:
                distance_max -= 1
                speed_max = speeds.get(distance_max)
            # int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
            return int((distance-distance_min) * (speed_max-speed_min) /
                       (distance_max-distance_min) + speed_min)
        else:
            return speed


def thrower(speed):
    # speeds from 130 to 268
    ser.write(('d:' + str(speed) + '\n').encode('utf-8'))
