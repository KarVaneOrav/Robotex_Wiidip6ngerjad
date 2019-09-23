from serial.tools import list_ports
import serial
import time

# List of existing ports. Chooses the right device if there are no others
port = (str(list_ports.comports()[0]).split(' '))[0]
ser=serial.Serial(port, 115200, timeout=0.00001)

def forward(ser=ser):
    ser.write(b'sd:0:-10:10\n')

def right(ser=ser):
    ser.write(b'sd:10:10:10\n')

def left(ser=ser):
    ser.write(b'sd:-10:-10:-10\n')

def close(ser=ser):
    ser.close()