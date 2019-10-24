import Camera
import Movement
import time
import cv2
import numpy as np

# values for image processing green
green = [16, 163, 93, 124, 255, 255]
# greenKernelErode = np.ones((1, 1), np.uint8)
# greenKernelDilate = np.ones((3, 3), np.uint8)
greenValues = {'lowerLimits': np.array([green[0], green[1], green[2]]),
               'upperLimits': np.array([green[3], green[4], green[5]])}

opponent = 'pink'  # 'blue' or 'pink'
pink = [95, 203, 61, 255, 255, 255, 3]  # values to process pink
blue = [35, 0, 29, 255, 91, 255, 3]  # values to process blue
targetValues = {'lowerLimits': None, 'upperLimits': None, 'kernelDilate': None}


def set_target_basket(op):
    if op == 'blue':
        target = blue
    else:
        target = pink

    targetValues['lowerLimits'] = np.array([target[0], target[1], target[2]])
    targetValues['upperLimits'] = np.array([target[3], target[4], target[5]])
    targetValues['targetKerne'] = np.ones((target[6], target[6]), np.uint8)


def timer(pause):
    # sets communication to 60Hz
    global comTime
    if time.time() >= (comTime + pause):
        comTime = time.time()
        return True
    else:
        return False


def timer_thrower():
    global comTime


tasks = {"controller": False, "look": True, "rotate":  False, 'throw': False}
current_task = "look"
frequency = 0.0166667
thrower_frequency = 0.002
end_control = False
start_throw = False
throwing_cycle = 0
throwing = False

try:
    print("throwing1")
    Movement.thrower(1100)  # init thrower motor
    set_target_basket(opponent)
    comTime = time.time()

    while True:
        # to show vanilla frame
        frame = Camera.get_frame()

        hsv_frame = Camera.to_hsv(frame)
        processed_frame_green = Camera.process_balls(hsv_frame, greenValues)
        
        ball = Camera.green_finder(processed_frame_green)

        if ball:
            cv2.putText(frame, str(ball), tuple(ball), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('RealSense', processed_frame_green)

        if timer(thrower_frequency) and throwing:
            Movement.thrower(1900)
            print("throw2")

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
                print("throwing inverted")
            if timer(frequency):
                end_control = Movement.controller(key)
            if end_control:
                tasks[current_task] = False
                tasks['look'] = True
                current_task = 'look'
                end_control = False
                throwing = False

        elif tasks["look"]:
            print("looking")
            if ball:  # if sees a ball
                if ball[1] < 400:  # if ball is too far
                    if timer(frequency):
                        Movement.move_to_ball(ball)
                else:
                    Movement.omni_drive([0, 0, 0])  # stop
                    tasks[current_task] = False
                    tasks["rotate"] = True
                    current_task = "rotate"

            else:  # if sees no balls
                if timer(frequency):
                    Movement.omni_drive([0, 0, 1])  # turns on the spot

        elif tasks["rotate"]:
            print("rotating")
            if not ball or ball[1] < 400:  # if loses the ball or gets too far
                tasks[current_task] = False
                tasks["look"] = True
                current_task = 'look'
                continue
            else:  # starts rotating
                basket = Camera.basket_finder(hsv_frame, targetValues)
                if timer(frequency):
                    start_throw = Movement.rotate_ball(ball, basket)
                if start_throw:
                    tasks[current_task] = False
                    tasks['throw'] = True
                    current_task = 'throw'
                    start_throw = False
                    throwing = True

        elif tasks['throw']:
            print("throwing")
            if throwing_cycle < 10:
                if timer(frequency):
                    Movement.omni_drive([0, 0.2, 0])
                    throwing_cycle += 1
            else:
                Movement.omni_drive([0, 0, 0])
                throwing_cycle = 0
                tasks[current_task] = False
                tasks['look'] = True
                current_task = 'look'
                throwing = False

        else:
            print("Error in tasks logic")
            break

finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")
