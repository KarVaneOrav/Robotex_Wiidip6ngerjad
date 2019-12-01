import camera
import numpy as np
import cv2

pink = [61, 128, 247, 255, 255, 255, 3]
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

values = []

cv2.namedWindow('rgb_img', cv2.WINDOW_NORMAL)
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    depth_frame, frame = camera.get_frame()
    hsv_frame = camera.to_hsv(frame)

    basket = camera.basket_bottom(hsv_frame, targetValues)
    print("Bottom coordinate:", basket[1])

    if basket:
        cv2.putText(frame, str(basket), tuple(basket),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.imshow("Show", frame)

camera.stop()
cv2.destroyAllWindows()
