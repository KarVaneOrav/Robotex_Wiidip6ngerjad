import Camera
import Movement
import time
import cv2

frequency = 0.0166667
comTime = time.time()
jobs = {"look":True, "move":False, "throw":False}

def action(omni):
    global comTime
    
    if time.time() >= (comTime + frequency):
        Movement.omniDrive(omni[0], omni[1], omni[2])
        
        comTime = time.time()
    Movement.readSerial()

try:
    Camera.start()
    while True:
        frame = Camera.processed_frame_green()
        cv2.imshow('RealSense', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        balls = Camera.green_finder(frame)
        if len(balls) == 0:
                action([0, 0, 1])
                continue
        if jobs.get("look"): 
            speeds = Camera.ball_to_middle(balls)
            if speeds == [0, 0, 0]:
                jobs["look"] = False
                jobs["move"] = True
            action(speeds)
        elif jobs.get("move"):
            if balls[0][1] < 300:
                action([0,0.5,0])
            else:
                action([0, 0, 0])
            

except:
    print("Shitty end")
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")