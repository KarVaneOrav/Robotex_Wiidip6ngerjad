from serial.tools import list_ports
import serial


def ss(son):
    global a
    global tekst
    print(son)
    a = ''
    tekst = ''


port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 9600, timeout=0.00001)

a = ''
s = "START"
p = "PING"
st = "STOP"
tekst = 'ssdsd'

while True:
    while ser.inWaiting():
        tekst += ser.read()

    print(tekst)

    #tekst = a.decode()
    if st in tekst:
        ss(st)
    elif a in tekst:
        ss(a)
    elif p in tekst:
        ss(p)
