import Camera
import Movement
import time
import cv2

frequency = 0.0166667
comTime = time.time()

tasks = {"look":True}

def action(omni):
    global comTime
    
    if time.time() >= (comTime + frequency):
        Movement.omniDrive(omni[0], omni[1], omni[2])
        
        comTime = time.time()
    Movement.readSerial()

try:
    while True:
        frame = Camera.get_frame()
        processed_frame = Camera.processed_frame_green(frame)
        
        cv2.imshow('RealSense', frame)
        cv2.imshow('RealSense', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        balls = Camera.green_finder(processed_frame)
        
        if tasks.get("look"):
            if len(balls) == 0:
                    action([0, 0, 1])
                    print("looking")
            else:
                turn = Camera.ball_to_middle(balls)
                if turn == [0, 0, 0]:
                    tasks["look"] = False
                action(turn)
        else:
            print(balls)
            if balls[0][1] < 400:
                action([0,0.3,0])
                print("go")
            else:
                action([0, 0, 0])
                print("Done")
                break
            

except:
    print("Shitty end")
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")