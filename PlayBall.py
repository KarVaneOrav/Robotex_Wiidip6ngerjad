import Camera
import Movement
import time
import cv2

frequency = 0.0166667
comTime = time.time()
jobs = {"look":True, "move":False, "throw":False}

def action(timeCount, job):
    global comTime
    
    if time.time() >= (timeCount + frequency):
        if job == "forward":
            Movement.forward()
        elif job == "right":
            Movement.right()
        elif job == "left":
            Movement.left()
        elif job == "stop":
            Movement.stop()
        
        comTime = time.time()
    Movement.readSerial()

try:
    while True:
        frame = Camera.processed_frame_green()
        cv2.imshow('RealSense', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        print("show frame")
        
        if jobs.get("look"): 
            balls = Camera.green_finder(frame)
            print("get balls")
            if len(balls) == 0:
                action(comTime, "right")
                print("no balls")
            else:
                status = Camera.ball_to_middle(balls)
                action(comTime, status)
                print("balls"+status)

except:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("Shitty end")
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("Good end")