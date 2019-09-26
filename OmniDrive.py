from serial.tools import list_ports
import serial
from math import sqrt, atan2, cos

robotSpeedX = 20
robotSpeedY = 0
robotAngularVelocity = 20

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

move = 'sd:'+str(wheelLinearVelocity0)+':'+str(wheelLinearVelocity1)+':'+\
       str(wheelLinearVelocity2)+'\n'
ser.write(bytes(move, 'utf-8'))

while (ser.inWaiting()):
        print(ser.read())

ser.close()