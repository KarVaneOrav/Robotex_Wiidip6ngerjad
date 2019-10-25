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


def set_target_basket(op):
    global targetValues
    if op == 'blue':
        target = blue
    else:
        target = pink

    targetValues['lowerLimits'] = np.array([target[0], target[1], target[2]])
    targetValues['upperLimits'] = np.array([target[3], target[4], target[5]])
    targetValues['targetKerne'] = np.ones((target[6], target[6]), np.uint8)


greenValues = {'lowerLimits': np.array([green[0], green[1], green[2]]),
               'upperLimits': np.array([green[3], green[4], green[5]])}
targetValues = {'lowerLimits': None, 'upperLimits': None, 'kernelDilate': None}

tasks = {"controller": False, "look": True, "rotate":  False, 'throw': False}
current_task = 'look'
frequency = 0.0166667  # send movement signals at 60Hz
thrower_frequency = 0.002
ball = []
basket = []

rotating_counter = 0
rotating_limit = 20
pause_counter = 0
pause_limit = 10

end_control = False
throwing = False
start_throw = False

try:
    set_target_basket(opponent)
    print("throwing1")
    Movement.thrower(1000)  # init thrower motor
    comTime = time.time()

    while True:
        frame = Camera.get_frame()
        hsv_frame = Camera.to_hsv(frame)
        processed_frame_green = Camera.process_balls(hsv_frame, greenValues)

        ball = Camera.green_finder(processed_frame_green)  # returns closest ball
        basket = []

        key = cv2.waitKey(1)
        if key == 113:
            break
        elif key == 99 and not tasks['controller']:  # if 'c' is pressed and already not controlling
            tasks[current_task] = False
            tasks["controller"] = True
            current_task = 'controller'

        if tasks['controller']:
            print("Controlling by remote")
            print("throwing " + str(throwing))
            if key == 116:  # 't' to start thrower
                throwing = not throwing
                Movement.thrower(1000)
            if timer(frequency):
                end_control = Movement.controller(key)
            if timer(thrower_frequency) and throwing:
                Movement.thrower(1900)
                print("throw2")
            if end_control:
                tasks[current_task] = False
                tasks['look'] = True
                current_task = 'look'
                end_control = False
                throwing = False
                Movement.thrower(1000)

        elif tasks['look']:
            print("looking")
            if ball:
                rotating_counter = 0
                pause_counter = 0
                if ball[1] < 500:  # if ball is too far
                    if timer(frequency):
                        Movement.move_to_ball(ball)
                else:
                    Movement.omni_drive([0, 0, 0])  # stop
                    tasks[current_task] = False
                    tasks["rotate"] = True
                    current_task = "rotate"
            else:
                if rotating_counter >= rotating_limit:  # take pauses to process
                    if pause_counter >= pause_limit:
                        rotating_counter = 0
                        pause_counter = 0
                    elif timer(frequency):
                        Movement.omni_drive([0, 0, 0])
                        pause_counter += 1
                elif timer(frequency):
                    Movement.omni_drive([0, 0, 1])  # turns on the spot
                    rotating_counter += 1

        elif tasks['rotate']:
            print("rotating")
            if not ball or ball[1] < 500:  # if loses the ball or gets too far
                tasks[current_task] = False
                tasks["look"] = True
                current_task = 'look'
                continue
            else:  # starts rotating
                basket = Camera.basket_finder(hsv_frame, targetValues)
                if timer(frequency):
                    start_throw = Movement.rotate_ball(ball, basket)
                '''if start_throw:
                    tasks[current_task] = False
                    tasks['throw'] = True
                    current_task = 'throw'
                    start_throw = False'''

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
