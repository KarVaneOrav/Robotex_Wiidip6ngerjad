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
        
        comTime = time.time()

while True:
    frame = Camera.processed_frame_green()
    if jobs.get("look"): 
        balls = Camera.green_finder(frame)
        if len(balls) == 0:
            action(comTime, "right")
        else:
            status = Camera.ball_to_middle(balls)
            if status != "ok":
                action(comTime, status)
    
    cv2.imshow('RealSense', frame)
    
Camera.stop()
Movement.close()
