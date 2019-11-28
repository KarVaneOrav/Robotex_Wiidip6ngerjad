import camera
import mainboard
import time
import cv2
import numpy as np

green = [16, 163, 93, 124, 255, 255]  # threshold values, morph values
pink = [95, 203, 61, 255, 255, 255, 3]
blue = [35, 0, 29, 255, 91, 255, 3]
opponent = 'blue'  # 'blue' or 'pink'
robotID = 'A'
courtID = 'A'


def timer(pause):
    # used to set communication intervals
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

tasks = {"nothing": False, "controller": False, "look": True, "rotate":  False, 'throw': False}
current_task = 'look'
frequency = 0.0166667  # send movement signals at 60Hz
thrower_frequency = 0.002

rotating_counter = 0
rotating_limit = 20  # how much robot rotates at a time
pause_counter = 0
pause_limit = 10  # how long robot waits after rotating
throwing_counter = 0
throwing_limit = 60  # how long robot tries to throw the ball
distances = []  # to find middle value

end_control = False
throwing = False
start_throw = False

try:
    set_target_basket(opponent)
    mainboard.thrower(100)  # init thrower motor
    comTime = time.time()

    while True:
        new_task = mainboard.read_ref(robotID, courtID, current_task)
        print('ref: ' + new_task)
        if new_task != current_task:
            tasks[current_task] = False
            tasks[new_task] = True
            current_task = new_task
            throwing = False

        depth_frame, frame = camera.get_frame()
        hsv_frame = camera.to_hsv(frame)
        processed_frame_green = camera.process_balls(hsv_frame, greenValues)

        ball = camera.green_finder(processed_frame_green)  # returns closest ball
        basket = []

        key = cv2.waitKey(1)
        if key == 113:
            break
        elif key == 99 and not tasks['controller']:  # if 'c' is pressed and already not controlling
            tasks[current_task] = False
            tasks["controller"] = True
            current_task = 'controller'

        if tasks['nothing']:
            mainboard.omni_drive([0, 0, 0])
            mainboard.thrower(100)

        elif tasks['controller']:
            print("Controlling by remote")
            print("throwing " + str(throwing))
            if key == 116:  # 't' to start thrower
                throwing = not throwing
                mainboard.thrower(100)
            if timer(frequency):
                end_control = mainboard.controller(key)
            if timer(thrower_frequency) and throwing:
                mainboard.thrower(190)
            if end_control:
                tasks[current_task] = False
                tasks['look'] = True
                current_task = 'look'
                end_control = False
                throwing = False
                mainboard.thrower(100)

        elif tasks['look']:
            print("looking")
            mainboard.thrower(100)  # just in case thrower stays on
            if ball:
                rotating_counter = 0
                pause_counter = 0
                if ball[1] < 500:  # if ball is too far
                    if timer(frequency):
                        mainboard.move_to_ball(ball)
                else:
                    mainboard.omni_drive([0, 0, 0])  # stop
                    tasks[current_task] = False
                    tasks["rotate"] = True
                    current_task = "rotate"
            else:
                if rotating_counter >= rotating_limit:  # take pauses to process
                    if pause_counter >= pause_limit:
                        rotating_counter = 0
                        pause_counter = 0
                    elif timer(frequency):
                        mainboard.omni_drive([0, 0, 0])
                        pause_counter += 1
                elif timer(frequency):
                    mainboard.omni_drive([0, 0, 1])  # turns on the spot
                    rotating_counter += 1

        elif tasks['rotate']:
            print("rotating")
            if not ball or ball[1] < 500:  # if loses the ball or gets too far
                tasks[current_task] = False
                tasks["look"] = True
                current_task = 'look'
                continue
            else:  # starts rotating
                basket = camera.basket_finder(hsv_frame, targetValues)
                if timer(frequency):
                    start_throw = mainboard.rotate_ball(ball, basket)
                if start_throw:
                    tasks[current_task] = False
                    tasks['throw'] = True
                    current_task = 'throw'
                    start_throw = False

        elif tasks['throw']:
            print("throwing")
            basket = camera.basket_finder(hsv_frame, targetValues)
            if not basket:
                continue
            distance = round(depth_frame.get_distance(basket[0], basket[1]), 1)
            distances += [distance]
            if len(distances) > 5:
                del distances[0]
            aprox_distance = round(sum(distances)/len(distances), 1)
            thrower_speed = mainboard.thrower_speed(aprox_distance)
            print("Distance:", distance, "; Speed:", thrower_speed)
            if throwing_counter < 10:  # thrower speedup phase
                if timer(thrower_frequency):
                    mainboard.thrower(thrower_speed)
                    throwing_counter += 1
            elif throwing_counter < throwing_limit:
                if timer(frequency):
                    mainboard.omni_drive([0, 0.2, 0])
                    throwing_counter += 1
                if timer(thrower_frequency):
                    mainboard.thrower(thrower_speed)
            else:
                mainboard.thrower(100)
                throwing_counter = 0
                tasks[current_task] = False
                tasks['look'] = True
                current_task = 'look'

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
    camera.stop()
    mainboard.close()
    cv2.destroyAllWindows()
    print("end")
