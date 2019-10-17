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
# angle 0 = right 90 = forward
while True:
    cv2.namedWindow('rgb_img', cv2.WINDOW_NORMAL)
    key = cv2.waitKey(1)
    if key != -1:
        print(key)
    if timer():
        if key == 119:
            Movement.motors(0.3, 90, 0)
        elif key == 97:
            Movement.motors(0.3, 180, 0)
        elif key == 115:
            Movement.motors(0.3, 270, 0)
        elif key == 100:
            Movement.motors(0.3, 0, 0)
        elif key == 111:
            Movement.motors(0, 0, 2)
        elif key == 112:
            Movement.motors(0, 0, -2)
        else:
            Movement.motors(0, 0, 0)
