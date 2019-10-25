import Camera
import Movement
import time
import cv2
import numpy as np

green = [16, 163, 93, 124, 255, 255]  # threshold values, morph values
pink = [95, 203, 61, 255, 255, 255, 3]
blue = [35, 0, 29, 255, 91, 255, 3]
opponent = 'blue'  # 'blue' or 'pink'


def timer(pause):
    # sets communication to 60Hz
    global comTime
    if time.time() >= (comTime + pause):
        comTime = time.time()
        return True
    else:
        return False


greenValues = {'lowerLimits': np.array([green[0], green[1], green[2]]),
               'upperLimits': np.array([green[3], green[4], green[5]])}
targetValues = {'lowerLimits': None, 'upperLimits': None, 'kernelDilate': None}

tasks = {"controller": False, "look": True, "rotate":  False, 'throw': False}
frequency = 0.0166667  # send movement signals at 60Hz
thrower_frequency = 0.002
ball = []
basket = []

try:
    print("throwing1")
    Movement.thrower(1100)  # init thrower motor
    comTime = time.time()

    while True:
        frame = Camera.get_frame()  # to show vanilla frame
        hsv_frame = Camera.to_hsv(frame)
        processed_frame_green = Camera.process_balls(hsv_frame, greenValues)

        ball = Camera.green_finder(processed_frame_green)
        basket = []

        key = cv2.waitKey(1)
        if key == 113:
            break

        if tasks['look']:
            print("looking")
            if ball:
                if ball[1] < 400:  # if ball is too far
                    if timer(frequency):
                        Movement.move_to_ball(ball)
                else:
                    Movement.omni_drive([0, 0, 0])  # stop
            else:
                if timer(frequency):
                    Movement.omni_drive([0, 0, 1])  # turns on the spot
        else:
            print("Error in tasks logic")
            break

        if ball:
            cv2.putText(frame, str(ball), tuple(ball),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if basket:
            cv2.putText(frame, str(basket), tuple(basket),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow('RealSense', frame)
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")
