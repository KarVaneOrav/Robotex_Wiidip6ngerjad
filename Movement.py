from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos, radians

# Takes list of existing ports. Chooses the mainboard if there are no others.
port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 115200, timeout=0.00001)

speeds = {3.2: 2153, 2.9: 2050, 2.8: 2000, 2.6: 1950, 2.4: 1850, 2.3: 1790,
          2.2: 1750, 2.0: 1705, 1.8: 1670, 1.6: 1650, 1.4: 1600, 1.2: 1570,
          1.0: 1535, 0.8: 1500, 0.6: 1470}


def close():
    ser.close()


def read_serial():
    while ser.inWaiting():
        ser.read()


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

    read_serial()


def rotate_ball(ball, basket):
    # sets the ball and the basket in a line
    if not basket or basket[0] > 740:
        back = '30'
    elif basket[0] < 690:
        back = '-30'
    else:
        back = '0'
    if ball[0] < 690:
        other = '-10'
    elif ball[0] > 740:
        other = '10'
    else:
        other = '0'

    ser.write(('sd:'+back+':'+other+':'+other+'\n').encode('utf-8'))
    read_serial()

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
    if distance > 3.4 or distance == 0:
        return 2153
    elif distance < 0.6:
        return 1500
    else:
        speed = speeds.get(distance)
        if speed is None:
            distance_max = distance_min = distance
            speed_min = None
            speed_max = None
            while speed_min is None:
                distance_min -= 0.1
                speed_min = speeds.get(round(distance_min, 1))
                print("Speed_min", speed_min)
            while speed_max is None:
                distance_max += 0.1
                speed_max = speeds.get(round(distance_max, 1))
                print("Speed_max", speed_max)
            # int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
            return int((distance-distance_min) * (speed_max-speed_min) /
                       (distance_max-distance_min) + speed_min)
        else:
            return speed


def thrower(speed):
    # speeds from 1035 to 2153
    ser.write(('d:' + str(speed) + '\n').encode('utf-8'))
