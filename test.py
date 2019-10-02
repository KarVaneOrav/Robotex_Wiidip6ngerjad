import cv2
import numpy as np
import Camera
from functools import partial

def updateValue(bar, new_value):
    bars[bar] = new_value


# trackbars
bars = [34,16,109,81,124,255, 2, 1]

cv2.namedWindow('Controls', cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar('lB', "Controls", bars[0], 255, partial(updateValue, 0))
cv2.createTrackbar('lG', "Controls", bars[1], 255, partial(updateValue, 1))
cv2.createTrackbar('lR', "Controls", bars[2], 255, partial(updateValue, 2))
cv2.createTrackbar('hB', "Controls", bars[3], 255, partial(updateValue, 3))
cv2.createTrackbar('hG', "Controls", bars[4], 255, partial(updateValue, 4))
cv2.createTrackbar('hR', "Controls", bars[5], 255, partial(updateValue, 5))
cv2.createTrackbar('Dilate', "Controls", bars[6], 20, partial(updateValue, 6))
cv2.createTrackbar('Erode', "Controls", bars[7], 20, partial(updateValue, 7))

while True:
    lowerLimits = np.array([bars[0], bars[1], bars[2]])
    upperLimits = np.array([bars[3], bars[4], bars[5]])

    frame = Camera.get_frame()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    thresh = cv2.inRange(hsv, lowerLimits, upperLimits)

    cv2.imshow("orig", frame)
    cv2.imshow("thresholded", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

Camera.stop()
cv2.destroyAllWindows()