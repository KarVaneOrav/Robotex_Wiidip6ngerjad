import camera
import numpy as np
import cv2

pink = [95, 203, 61, 255, 255, 255, 3]
blue = [35, 0, 29, 255, 91, 255, 3]
opponent = 'pink'  # 'blue' or 'pink'


def set_target_basket(op):
    global targetValues
    if op == 'blue':
        target = blue
    else:
        target = pink

    targetValues['lowerLimits'] = np.array([target[0], target[1], target[2]])
    targetValues['upperLimits'] = np.array([target[3], target[4], target[5]])
    targetValues['targetKerne'] = np.ones((target[6], target[6]), np.uint8)


targetValues = {'lowerLimits': None, 'upperLimits': None, 'kernelDilate': None}
set_target_basket(opponent)
cv2.namedWindow('rgb_img', cv2.WINDOW_NORMAL)
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    depth_frame, frame = camera.get_frame()
    hsv_frame = camera.to_hsv(frame)

    basket = camera.basket_finder(hsv_frame, targetValues)

    if basket:
        distance = round(depth_frame.get_distance(basket[0], basket[1]), 1)
        print("Distance: " + str(distance))

camera.stop()
cv2.destroyAllWindows()
