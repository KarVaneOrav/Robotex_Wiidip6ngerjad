import Movement
import cv2
import time

frequency = 0.0166667
comTime = time.time()


def timer():
    # sets communication to 60Hz
    global comTime

    if time.time() >= (comTime + frequency):
        comTime = time.time()
        return True

    else:
        return False

# w=119, a=97, s=115, d=100, o=111, p=112, q=113
while True:
    cv2.namedWindow('rgb_img', cv2.WINDOW_NORMAL)
    key = cv2.waitKey(1)

    if timer():
        if key == 119:
            Movement.motors(0.5, 0, 0)
