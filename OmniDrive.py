from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos
import time

robotSpeedX = 1
robotSpeedY = 3
robotAngularVelocity = 0

port = (str(list_ports.comports()[0]).split(' '))[0]
ser=serial.Serial(port, 115200, timeout=0.00001)


robotSpeed = sqrt(robotSpeedX * robotSpeedX + robotSpeedY * robotSpeedY)
robotDirectionAngle = atan2(robotSpeedY, robotSpeedX)

#wheelLinearVelocity = robotSpeed * cos(robotDirectionAngle - wheelAngle) + \
#                       wheelDistanceFromCenter * robotAngularVelocity
wheelLinearVelocity0 = robotSpeed * cos(robotDirectionAngle - 0) + \
                       0.14 * robotAngularVelocity
wheelLinearVelocity1 = robotSpeed * cos(robotDirectionAngle - 240) + \
                       0.14 * robotAngularVelocity
wheelLinearVelocity2 = robotSpeed * cos(robotDirectionAngle - 120) + \
                       0.14 * robotAngularVelocity

#wheelSpeedToMainboardUnits = gearboxReductionRatio * encoderEdgesPerMotorRevolution /\
#                             (2 * PI * wheelRadius * pidControlFrequency)
wheelSpeedToMainboardUnits = 90.991

wheelAngularSpeedMainboardUnits0 = wheelLinearVelocity0 * wheelSpeedToMainboardUnits
wheelAngularSpeedMainboardUnits1 = wheelLinearVelocity1 * wheelSpeedToMainboardUnits
wheelAngularSpeedMainboardUnits2 = wheelLinearVelocity2 * wheelSpeedToMainboardUnits

move = 'sd:'+str(wheelAngularSpeedMainboardUnits0)+':'+str(wheelAngularSpeedMainboardUnits1)+':'+\
       str(wheelAngularSpeedMainboardUnits2)+'\n'
print(move)
ser.write(move.encode('ascii'))
print("sent")

while (ser.inWaiting()):
    print(ser.read())

ser.close()