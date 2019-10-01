from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos, floor, pi

# Takes list of existing ports. Chooses the mainboard if there are no others.
port = (str(list_ports.comports()[0]).split(' '))[0]
ser=serial.Serial(port, 115200, timeout=0.00001)

def close():
    ser.close()

def readSerial():
    while (ser.inWaiting()):
        ser.read()

def omniDrive(robotSpeedX, robotSpeedY, robotAngularVelocity):
    robotSpeed = sqrt(robotSpeedX * robotSpeedX + robotSpeedY * robotSpeedY)
    robotDirectionAngle = atan2(robotSpeedY, robotSpeedX)
    
    '''
    wheelLinearVelocity = robotSpeed * cos(robotDirectionAngle - wheelAngle) + \
                           wheelDistanceFromCenter * robotAngularVelocity
    Cause our robots wheels turn the other way, speeds are inverted.
    wheelSpeedToMainboardUnits = gearboxReductionRatio * encoderEdgesPerMotorRevolution /\
                                 (2 * PI * wheelRadius * pidControlFrequency)
    wheelAngularSpeedMainboardUnits = floor(wheelLinearVelocity * wheelSpeedToMainboardUnits)
    '''
    wheelSpeedToMainboardUnits = 90.991
    
    wheelAngularSpeedMainboardUnits0 = floor(-1 * (robotSpeed * cos(robotDirectionAngle - 0) + \
                           0.14 * -robotAngularVelocity) * 90.991)
    wheelAngularSpeedMainboardUnits1 = floor(-1 * (robotSpeed * cos(robotDirectionAngle - (120*pi/180)) + \
                           0.14 * -robotAngularVelocity) * 90.991)
    wheelAngularSpeedMainboardUnits2 = floor(-1 * (robotSpeed * cos(robotDirectionAngle - (240*pi/180)) + \
                           0.14 * -robotAngularVelocity) * 90.991)

    move = 'sd:'+str(wheelAngularSpeedMainboardUnits0)+':'+str(wheelAngularSpeedMainboardUnits1)+':'+\
           str(wheelAngularSpeedMainboardUnits2)+'\n'
    ser.write(move.encode('ascii'))
    print(move)
    
def thrower():
    ser.write(b'd:1000\n')
