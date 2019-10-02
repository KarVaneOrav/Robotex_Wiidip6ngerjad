import cv2
from functools import partial
import Camera
import numpy as np


# A callback function for every trackbar
# It is triggered every time the trackbar slider is used
def updateValue(bar, new_value):
    bars[bar] = new_value


# trackbars
bars = [14, 163, 93, 124, 255, 255, 2]

cv2.namedWindow('Controls', cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar('lB', "Controls", bars[0], 255, partial(updateValue, 0))
cv2.createTrackbar('lG', "Controls", bars[1], 255, partial(updateValue, 1))
cv2.createTrackbar('lR', "Controls", bars[2], 255, partial(updateValue, 2))
cv2.createTrackbar('hB', "Controls", bars[3], 255, partial(updateValue, 3))
cv2.createTrackbar('hG', "Controls", bars[4], 255, partial(updateValue, 4))
cv2.createTrackbar('hR', "Controls", bars[5], 255, partial(updateValue, 5))
cv2.createTrackbar('Dilate', "Controls", bars[6], 20, partial(updateValue, 6))
# cv2.createTrackbar('Erode', "Controls", bars[7], 20, partial(updateValue, 7))

try:
    while True:
        # kernel
        kernelDilate = np.ones((bars[6],bars[6]),np.uint8)
        # kernelErode = np.ones((bars[7],bars[7]),np.uint8)
        
        lowerLimits = np.array([bars[0], bars[1], bars[2]])
        upperLimits = np.array([bars[3], bars[4], bars[5]])
        
        frame = Camera.get_frame()
        
        processed_frame = Camera.processed_frame_green(frame, lowerLimits, upperLimits)

        contours, _hierarchy = cv2.findContours(processed_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        circles = map(cv2.minEnclosingCircle, contours)

        # tagging blobs
        for i in circles:
            coordinate = (int(i[0][0]), int(i[0][1]))
            cv2.putText(frame, str(coordinate), coordinate, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show images
        cv2.imshow('Processed', processed_frame)
        cv2.imshow('Original', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('s'):
            with open("threshold.txt", "a") as f:
                f.write(input("Color name: ")+str(bars)+'\n')
                
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:

    # Stop streaming
    Camera.stop()
    cv2.destroyAllWindows()
