from serial.tools import list_ports
import serial


def ss(son):
    global mes
    global tekst
    print(son)
    mes = ''
    tekst = ''


port = (str(list_ports.comports()[0]).split(' '))[0]
ser = serial.Serial(port, 9600, timeout=0.00001)
i = 0
s = "START"
p = "PING"
st = "STOP"
mes = ''

while True:
    i += 1
    print(i)
    while ser.inWaiting():
        mes += ser.read()

    tekst = str(mes)
    print(tekst)

    if st in tekst:
        ss(st)
    elif s in tekst:
        ss(s)
    elif p in tekst:
        ss(p)
