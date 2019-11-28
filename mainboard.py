from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos, radians

# Takes list of existing ports. Chooses the mainboard if there are no others.
port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 115200, timeout=0.00001)
ser_ref = serial.Serial(port, 9600, timeout=0.01)

speeds = {3.5: 265, 3.3: 260, 3.2: 255, 3.1: 250, 3.0: 249, 2.9: 245,
          2.8: 240, 2.6: 227, 2.5: 225, 2.4: 224, 2.3: 220, 2.2: 219,
          2.1: 215, 2.0: 214, 1.9: 210, 1.8: 207, 1.7: 206, 1.6: 202,
          1.5: 200, 1.4: 198, 1.3: 196, 1.2: 194, 1.1: 191, 1.0: 190,
          0.9: 188, 0.8: 186, 0.7: 182, 0.6: 181}
ref_mes = ''


def close():
    omni_drive([0, 0, 0])
    ser.close()
    ser_ref.close()


def read_ref(robotID, courtID, current_task):
    global ref_mes
    while ser_ref.inWaiting() > 0:
        ref_mes += ser_ref.read().decode('ascii')

    print("pure:" + ref_mes)
    while True:
        end = ref_mes.find('\n')
        if end == -1:
            return current_task
        else:
            mes = ref_mes[:end]
            print(mes)
            ref_mes = ref_mes[(end+1):]
            if mes[6] == courtID and mes[7] == robotID or mes[7] == 'X':
                ser_ref.write(str.encode('rf:a' + courtID + robotID + 'ACK----- \r \n'))
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
    speed = 0.5
    x = ball[0] - 590
    y = 680 - ball[1]
    angle = atan2(y, x)
    motors(speed, angle)


def omni_drive(values):
    # for more manual insertion
    robotSpeedX = values[0]
    robotSpeedY = values[1]
    robotAngularVelocity = values[2]

    robotSpeed = sqrt(robotSpeedX * robotSpeedX + robotSpeedY * robotSpeedY)
    robotDirectionAngle = atan2(robotSpeedY, robotSpeedX)
    motors(robotSpeed, robotDirectionAngle, robotAngularVelocity)


def motors(robotSpeed, robotDirectionAngle, robotAngularVelocity = 0):
    # the core of omnidrive, also reads serial
    '''
    wheelLinearVelocity = robotSpeed * cos(robotDirectionAngle - wheelAngle) + \
                           wheelDistanceFromCenter * robotAngularVelocity
    Cause our robots wheels turn the other way, speeds are inverted.
    wheelSpeedToMainboardUnits = gearboxReductionRatio * encoderEdgesPerMotorRevolution /\
                                 (2 * PI * wheelRadius * pidControlFrequency)
    wheelAngularSpeedMainboardUnits = floor(wheelLinearVelocity * wheelSpeedToMainboardUnits)
    wheelSpeedToMainboardUnits = 90.991
    '''

    wheelAngularSpeedMainboardUnits0 = round(-1 * (robotSpeed * cos(robotDirectionAngle - radians(0))
                                                   + 0.14 * -robotAngularVelocity) * 90.991)
    wheelAngularSpeedMainboardUnits1 = round(-1 * (robotSpeed * cos(robotDirectionAngle - radians(120))
                                                   + 0.14 * -robotAngularVelocity) * 90.991)
    wheelAngularSpeedMainboardUnits2 = round(-1 * (robotSpeed * cos(robotDirectionAngle - radians(240))
                                                   + 0.14 * -robotAngularVelocity) * 90.991)

    move = 'sd:'+str(wheelAngularSpeedMainboardUnits0)+':'+str(wheelAngularSpeedMainboardUnits1)+':'+\
           str(wheelAngularSpeedMainboardUnits2)+'\n'
    ser.write(move.encode('utf-8'))
    print(move)


def rotate_ball(ball, basket):
    # sets the ball and the basket in a line  590
    if not basket or basket[0] > 600:
        back = '30'
    elif basket[0] < 580:
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
        motors(0.3, 1.57, 0)
    elif key == 97:  # a
        motors(0.3, 3.14, 0)
    elif key == 115:  # s
        motors(0.3, 4.71, 0)
    elif key == 100:  # d
        motors(0.3, 0, 0)
    elif key == 111:  # o
        motors(0, 0, 2)
    elif key == 112:  # p
        motors(0, 0, -2)
    else:
        motors(0, 0, 0)

    return False  # if still controlling


def thrower_speed(distance):
    if distance >= 3.5 or distance == 0:
        return 265
    elif distance <= 0.6:
        return 181
    else:
        speed = speeds.get(distance)
        if speed is None:
            distance_max = distance_min = distance
            speed_min = None
            speed_max = None
            while speed_min is None:
                distance_min = round(distance_min - 0.1, 1)
                speed_min = speeds.get(distance_min, 1)
                print("Speed_min", speed_min, "distance_min", distance_min)
            while speed_max is None:
                distance_max = round(distance_max + 0.1, 1)
                speed_max = speeds.get(distance_max, 1)
                print("Speed_max", speed_max, "distance_min", distance_max)
            # int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
            return int((distance-distance_min) * (speed_max-speed_min) /
                       (distance_max-distance_min) + speed_min)
        else:
            return speed


def thrower(speed):
    # speeds from 130 to 268
    ser.write(('d:' + str(speed) + '\n').encode('utf-8'))
