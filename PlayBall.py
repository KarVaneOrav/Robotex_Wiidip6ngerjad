import Camera
import Movement
import time
import cv2
import numpy as np

# values for image processing green
green = [16, 163, 93, 124, 255, 255]
# greenKernelErode = np.ones((1, 1), np.uint8)
# greenKernelDilate = np.ones((3, 3), np.uint8)
# colour detection limits
greenValues = {'lowerLimits': np.array([green[0], green[1], green[2]])
    , 'upperLimits': np.array([green[3], green[4], green[5]])}

opponent = 'blue'  # 'blue' or 'pink'
# values to process pink
pink = [95, 203, 61, 255, 255, 255, 3]
# values to process blue
blue = [35, 0, 29, 255, 91, 255, 3]
# values for processing
targetValues = {'lowerLimits': None
    , 'upperLimits': None
    , 'kernelDilate': None}


tasks = {"look": True, "rotate":  False}
frequency = 0.0166667
comTime = time.time()


def set_target_basket(opponent):
    if opponent == 'blue':
        target = blue
    else:
        target = pink

    targetValues['lowerLimitsTarget'] = np.array([target[0], target[1], target[2]])
    targetValues['upperLimitsTarget'] = np.array([target[3], target[4], target[5]])
    targetValues['targetKernelDilate'] = np.ones((target[6], target[6]), np.uint8)


def timer():
    # sets communication to 60Hz
    global comTime
    
    if time.time() >= (comTime + frequency):
        comTime = time.time()
        return True

    else:
        return False


try:
    set_target_basket(opponent)

    while True:
        # to show vanilla frame
        frame = Camera.get_frame()

        hsv_frame = Camera.to_hsv(frame)
        processed_frame_green = Camera.process_balls(hsv_frame, greenValues)
        
        ball = Camera.green_finder(processed_frame_green)

        if ball:
            cv2.putText(frame, str(ball), tuple(ball), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('RealSense', processed_frame_green)
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
                basket = Camera.basket_finder(hsv_frame, targetValues)
                if timer():
                    print("rotating")
                    Movement.rotate_ball(ball, basket)

        else:
            print("Error in tasks logic")
            break

finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")
