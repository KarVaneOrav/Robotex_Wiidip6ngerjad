from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos, floor, pi
import time

robotSpeedX = 0
robotSpeedY = -1
robotAngularVelocity = -4

port = (str(list_ports.comports()[0]).split(' '))[0]
ser=serial.Serial(port, 115200, timeout=0.00001)


robotSpeed = sqrt(robotSpeedX * robotSpeedX + robotSpeedY * robotSpeedY)
robotDirectionAngle = atan2(robotSpeedY, robotSpeedX)

#wheelLinearVelocity = robotSpeed * cos(robotDirectionAngle - wheelAngle) + \
#                       wheelDistanceFromCenter * robotAngularVelocity
wheelLinearVelocity0 = -1 * (robotSpeed * cos(robotDirectionAngle - 0) + \
                       0.14 * -robotAngularVelocity)
wheelLinearVelocity1 = -1 * (robotSpeed * cos(robotDirectionAngle - (120*pi/180)) + \
                       0.14 * -robotAngularVelocity)
wheelLinearVelocity2 = -1 * (robotSpeed * cos(robotDirectionAngle - (240*pi/180)) + \
                       0.14 * -robotAngularVelocity)

#wheelSpeedToMainboardUnits = gearboxReductionRatio * encoderEdgesPerMotorRevolution /\
#                             (2 * PI * wheelRadius * pidControlFrequency)
wheelSpeedToMainboardUnits = 90.991

wheelAngularSpeedMainboardUnits0 = floor(wheelLinearVelocity0 * wheelSpeedToMainboardUnits)
wheelAngularSpeedMainboardUnits1 = floor(wheelLinearVelocity1 * wheelSpeedToMainboardUnits)
wheelAngularSpeedMainboardUnits2 = floor(wheelLinearVelocity2 * wheelSpeedToMainboardUnits)

move = 'sd:'+str(wheelAngularSpeedMainboardUnits0)+':'+str(wheelAngularSpeedMainboardUnits1)+':'+\
       str(wheelAngularSpeedMainboardUnits2)+'\n'
print(move)
ser.write(move.encode('ascii'))
print("sent")
while (ser.inWaiting()):
    print(ser.read())

ser.close()
