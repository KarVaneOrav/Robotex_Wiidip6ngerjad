import Movement
import time

try:
    while True:
        Movement.thrower()
        Movement.readSerial()
        time.sleep(0.2)
        
finally:
    print("done")
    Movement.close()