from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos, radians

# Takes list of existing ports. Chooses the mainboard if there are no others.
port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 115200, timeout=0.00001)


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

    wheelAngularSpeedMainboardUnits0 = round(-1 * (robotSpeed * cos(robotDirectionAngle - radians(0)) +
                           0.14 * -robotAngularVelocity) * 90.991)
    wheelAngularSpeedMainboardUnits1 = round(-1 * (robotSpeed * cos(robotDirectionAngle - radians(120)) +
                           0.14 * -robotAngularVelocity) * 90.991)
    wheelAngularSpeedMainboardUnits2 = round(-1 * (robotSpeed * cos(robotDirectionAngle - radians(240)) +
                           0.14 * -robotAngularVelocity) * 90.991)

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

    
def thrower():
    ser.write(b'd:1000\n')
