import Camera
import Movement
import time
import cv2

frequency = 0.0166667
comTime = time.time()

tasks = {"look": True, "move": False}


def timer():
    # sets communication to 60Hz
    global comTime
    
    if time.time() >= (comTime + frequency):
        comTime = time.time()
        return True

    else:
        return False


try:
    while True:
        frame = Camera.get_frame()
        processed_frame = Camera.processed_frame_green(frame)

        cv2.imshow('RealSense', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        ball = Camera.green_finder(processed_frame)
        
        if tasks.get("look"):
            if len(ball) == 0:
                    if timer():
                        Movement.omniDrive(1, 1, 1)  # turns on the spot
            else:
                tasks["look"] = False
                tasks["move"] = True

        elif tasks.get("move"):
            if ball[1] > 400:
                Movement.omniDrive(0, 0, 0)  # stops
                print("Done")
                break
            else:
                if timer():
                    Movement.move_to_ball(ball)

        else:
            print("Error in tasks logic")
            break


            '''else:
                turn = Camera.ball_to_middle(ball)
                if turn == [0, 0, 0]:
                    tasks["look"] = False
                action(turn)
        else:
            if len(ball) == 0:
                print("lost ball")
                tasks['look'] = True
            elif ball[1] < 400:
                action([0, 0.3, 0])
                print("go")
            else:
                action([0, 0, 0])
                print("Done")
                break'''
            

except Exception as e:
    print(e)
    print("Shitty end")
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")
