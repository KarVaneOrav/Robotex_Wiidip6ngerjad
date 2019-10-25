import Camera
import Movement
import time
import cv2
import numpy as np

green = [16, 163, 93, 124, 255, 255]  # threshold values


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

try:
    while True:
        frame = Camera.get_frame()  # to show vanilla frame
        hsv_frame = Camera.to_hsv(frame)
        processed_frame_green = Camera.process_balls(hsv_frame, greenValues)

        ball = Camera.green_finder(processed_frame_green)
        if ball:
            cv2.putText(frame, str(ball), tuple(ball),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('RealSense', frame)
        key = cv2.waitKey(1)
        if key == 113:
            break
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")