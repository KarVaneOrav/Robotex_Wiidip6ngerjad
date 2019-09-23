import Camera
import Movement
import time
import cv2

frequency = 0.0166667
comTime = time.time()
jobs = {"look"=True, "move"=False, "throw"=False}

def action(time, job):
    global comTime
    
    if time.time() >= (time + frequency):
        if job == "forward":
            Movement.forward()
        elif job == "right":
            Movement.right()
        elif job == "left":
            Movement.left()
        
        comTime = time.time()

while True:    
    if jobs.get("look"): 
        balls = Camera.green_finder()
        if balls.lenght() == 0:
            action(comTime, "right")
        else:
            status = Camera.ball_to_middel(balls)
            if status != "ok":
                action(comTime, status)
    
    cv2.imshow('RealSense', processed_frame_green())
    
Camera.stop()
Movement.close()