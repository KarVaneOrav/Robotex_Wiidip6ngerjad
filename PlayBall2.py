import Camera, Movement, time, cv2
import numpy as np


def timer(pause):
    # sets communication to 60Hz
    global comTime
    if time.time() >= (comTime + pause):
        comTime = time.time()
        return True
    else:
        return False


try:
    while True:
        frame = Camera.get_frame()  # to show vanilla frame

        cv2.imshow('RealSense', frame)
        key = cv2.waitKey(1)
        if key == 113:
            break
finally:
    Camera.stop()
    Movement.close()
    cv2.destroyAllWindows()
    print("end")