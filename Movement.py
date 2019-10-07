from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos, radians

# Takes list of existing ports. Chooses the mainboard if there are no others.
port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 115200, timeout=0.00001)


def close():
    ser.close()


def readSerial():
    while ser.inWaiting():
        ser.read()


def move_to_ball(ball):
    print(ball)
    speed = 1
    x = ball[0] - 590
    angle = atan2(x, ball[1])
    motors(speed, angle)


def omniDrive(robotSpeedX, robotSpeedY, robotAngularVelocity):
    # for more manual insertion
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

    readSerial()
    
def thrower():
    ser.write(b'd:1000\n')
