import cv2
import numpy as np
import Camera
from functools import partial

def updateValue(bar, new_value):
    bars[bar] = new_value


# trackbars
bars = [20, 100, 30, 1, 30, 5]

cv2.namedWindow('Controls', cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar('minDist', "Controls", bars[0], 100, partial(updateValue, 0))
cv2.createTrackbar('param1', "Controls", bars[1], 255, partial(updateValue, 1))
cv2.createTrackbar('param2', "Controls", bars[2], 255, partial(updateValue, 2))
cv2.createTrackbar('minRadius', "Controls", bars[3], 255, partial(updateValue, 3))
cv2.createTrackbar('maxRadius', "Controls", bars[4], 255, partial(updateValue, 4))
cv2.createTrackbar('blur', "Controls", bars[5], 30, partial(updateValue, 5))

while True:
    src = Camera.get_frame()

    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    gray = cv2.medianBlur(gray, 5)

    cv2.imshow("orig", gray)

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, bars[0],
                              bars[1], bars[2],
                              bars[3], bars[4])

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv2.circle(src, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv2.circle(src, center, radius, (255, 0, 255), 3)

    cv2.imshow("detected circles", src)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

Camera.stop()
cv2.destroyAllWindows()
