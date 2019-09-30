import Movement
import time

try:
    while True:
        Movement.thrower()
        time.sleep(0.2)
        
finally:
    print("done")
    Movement.close()