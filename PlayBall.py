import Camera
import Movement
import time
import cv2

frequency = 0.0166667
comTime = time.time()

# True for blue, False for pink
Camera.get_target_basket(True)

tasks = {"look": True, "rotate":  False}


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
        # to show vanilla frame
        frame = Camera.get_frame()

        hsv_frame = Camera.to_hsv(frame)
        processed_frame = Camera.process_balls(hsv_frame)
        
        ball = Camera.green_finder(processed_frame)

        if ball:
            cv2.putText(frame, str(ball), tuple(ball), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('RealSense', processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if tasks["look"]:
            print("looking")
            if ball:  # if sees a ball
                if ball[1] < 400:  # if ball is too far
                    if timer():
                        Movement.move_to_ball(ball)
                else:
                    Movement.omni_drive([0, 0, 0])
                    tasks["look"] = False
                    tasks["rotate"] = True

            else:  # if sees no balls
                if timer():
                    Movement.omni_drive([0, 0, 1])  # turns on the spot

        elif tasks["rotate"]:
            if not ball or ball[1] < 400:  # if loses the ball or gets too far
                tasks["rotate"] = False
                tasks["look"] = True
                continue
            else:  # starts rotating
                basket = Camera.basket_finder(hsv_frame)
                if timer():
                    print("rotating")
                    Movement.rotate_ball(ball, basket)

        else:
            print("Error in tasks logic")
            break
            

#except Exception as e:
#    print(e)
#    print("Shitty end")
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")
