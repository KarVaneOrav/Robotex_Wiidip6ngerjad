from serial.tools import list_ports
import serial

port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 9600, timeout=0.00001)

mes = None
while True:
    mes = ser.read(19)

    if len(mes) > 17:
        tekst = str(mes)
        print(tekst)
        mes = None
