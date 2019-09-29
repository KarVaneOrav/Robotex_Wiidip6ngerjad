import Camera
import Movement
import time
import cv2

frequency = 0.0166667
comTime = time.time()
jobs = {"look":True, "move":False, "throw":False}

def action(omni):
    global comTime
    
    if time.time() >= (timeCount + frequency):
        Movement.omniDrive(omni[0], omni[1], omni[2])
        
        comTime = time.time()
    Movement.readSerial()

Camera.start()

try:
    while True:
        frame = Camera.processed_frame_green()
        cv2.imshow('RealSense', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        if jobs.get("look"): 
            balls = Camera.green_finder(frame)
            if len(balls) == 0:
                action([0, 0, 1])
            else:
                speeds = Camera.ball_to_middle(balls)
                action(speeds)

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