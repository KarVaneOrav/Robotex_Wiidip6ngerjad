import cv2
from functools import partial
import camera
import numpy as np


# A callback function for every trackbar
# It is triggered every time the trackbar slider is used
def updateValue(bar, new_value):
    bars[bar] = new_value


# trackbars
bars = [43, 0, 0, 163, 92, 147, 3]
values = {'lowerLimits': None, 'upperLimits': None, 'kernelDilate': None}

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
        values['kernelDilate'] = np.ones((bars[6], bars[6]), np.uint8)
        # kernelErode = np.ones((bars[7],bars[7]),np.uint8)
        
        values['lowerLimits'] = np.array([bars[0], bars[1], bars[2]])
        values['upperLimits'] = np.array([bars[3], bars[4], bars[5]])
        
        d, frame = camera.get_frame()
        #frame = frame[600:680, 530:650]
        hsv = camera.to_hsv(frame)

        # for balls
        processed_frame = camera.process_frame(hsv, values)

        # for baskets
        # processed_frame = Camera.process_basket(hsv, lowerLimits, upperLimits, kernelDilate)

        contours, _hierarchy = cv2.findContours(processed_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        circles = map(cv2.minEnclosingCircle, contours)

        # tagging all blobs
        for i in circles:
            coordinate = (int(i[0][0]), int(i[0][1]))
            cv2.putText(frame, str(coordinate), coordinate, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        '''# tag middle blob for baskets
        try:
            circles = sorted(circles, key=lambda x: x[0])
            circle = circles[round(len(circles)/2)]
            spot = [int(circle[0][0]), int(circle[0][1])]
            cv2.putText(frame, str(spot), (int(spot[0]), int(spot[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        except:
            print("no targets")'''

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
    camera.stop()
    cv2.destroyAllWindows()
