import Movement
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
Movement.thrower(1100)

# angle 0 = right 90 = forward (convert to rad)
while True:
    cv2.namedWindow('rgb_img', cv2.WINDOW_NORMAL)
    key = cv2.waitKey(1)
    if key != -1:
        print(key)
    if key == 116:  # t
        throwing = not throwing
    elif timer(frequency):
        if key == 113:
            break
        elif key == 119:  # w
            Movement.motors(0.3, 1.57, 0)
        elif key == 97:  # a
            Movement.motors(0.3, 3.14, 0)
        elif key == 115:  # s
            Movement.motors(0.3, 4.71, 0)
        elif key == 100:  # d
            Movement.motors(0.3, 0, 0)
        elif key == 111:  # o
            Movement.motors(0, 0, 2)
        elif key == 112:  # p
            Movement.motors(0, 0, -2)
        else:
            Movement.motors(0, 0, 0)

    if timer(throwing_frequency) and throwing:
        Movement.thrower(1900)

cv2.destroyAllWindows()
Movement.close()
