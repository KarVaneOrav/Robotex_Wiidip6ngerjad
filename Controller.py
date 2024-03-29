import mainboard
import cv2
import time

frequency = 0.0166667
throwing_frequency = 0.002
comTime = time.time()


def timer(freq):
    # sets communication to 60Hz
    global comTime

    if time.time() >= (comTime + freq):
        comTime = time.time()
        return True

    else:
        return False


throwing = False
mainboard.thrower(1100)

# angle 0 = right 90 = forward (convert to rad)
while True:
    cv2.namedWindow('rgb_img', cv2.WINDOW_NORMAL)
    key = cv2.waitKey(0)
    if key != -1:
        print(key)
    if key == 116:  # t
        throwing = not throwing
    elif timer(frequency):
        if key == 113:
            break
        elif key == 119:  # w
            mainboard.motors(0.3, 1.57, 0)
        elif key == 97:  # a
            mainboard.motors(0.3, 3.14, 0)
        elif key == 115:  # s
            mainboard.motors(0.3, 4.71, 0)
        elif key == 100:  # d
            mainboard.motors(0.3, 0, 0)
        elif key == 111:  # o
            mainboard.motors(0, 0, 2)
        elif key == 112:  # p
            mainboard.motors(0, 0, -2)
        else:
            mainboard.motors(0, 0, 0)

    if timer(throwing_frequency) and throwing:
        mainboard.thrower(200)

cv2.destroyAllWindows()
mainboard.close()
