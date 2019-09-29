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
    Camera.start()
    while True:
        frame = Camera.processed_frame_green()
        #cv2.imshow('RealSense', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        if tasks.get("look"):
            balls = Camera.green_finder(frame)
            if len(balls) == 0:
                    action([0, 0, 1])
                    print("looking")
            else:
                turn = Camera.ball_to_middle(balls)
                if turn == [0, 0, 0]:
                    tasks["look"] = False
                action(turn)
        else:
            if balls[0][1] < 300:
                action([0,0.3,0])
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