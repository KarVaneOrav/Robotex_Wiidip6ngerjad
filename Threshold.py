# License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
from functools import partial

# A callback function for every trackbar
# It is triggered every time the trackbar slider is used
def updateValue(bar, new_value):
    bars[bar] = new_value

#blobparams
blobparams = cv2.SimpleBlobDetector_Params()
blobparams.minArea = 1000
blobparams.maxArea = 10000000
blobparams.filterByColor = True # filter by color
blobparams.blobColor = 255  # 255 is white
blobparams.filterByCircularity = False
blobparams.filterByConvexity = False
#filterByInertia = False
detector = cv2.SimpleBlobDetector_create(blobparams)

# trackbars
bars = [31, 62, 52, 79, 255, 255, 4, 4]

cv2.namedWindow('Controls', cv2.WINDOW_AUTOSIZE)

cv2.createTrackbar('lB', "Controls", bars[0], 255, partial(updateValue, 0))
cv2.createTrackbar('lG', "Controls", bars[1], 255, partial(updateValue, 1))
cv2.createTrackbar('lR', "Controls", bars[2], 255, partial(updateValue, 2))
cv2.createTrackbar('hB', "Controls", bars[3], 255, partial(updateValue, 3))
cv2.createTrackbar('hG', "Controls", bars[4], 255, partial(updateValue, 4))
cv2.createTrackbar('hR', "Controls", bars[5], 255, partial(updateValue, 5))
cv2.createTrackbar('Open', "Controls", bars[6], 20, partial(updateValue, 6))
cv2.createTrackbar('Erode', "Controls", bars[7], 20, partial(updateValue, 7))


# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)

# Start streaming
pipeline.start(config)

try:
    while True:
        #kernel
        kernelOpen = np.ones((bars[6],bars[6]),np.uint8)
        kernelErode = np.ones((bars[7],bars[7]),np.uint8)
        
        # Wait for a coherent pair of frames: color
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        
        #convert to hsv
        hsv_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        
        # colour detection limits
        lowerLimits = np.array([bars[0], bars[1], bars[2]])
        upperLimits = np.array([bars[3], bars[4], bars[5]])

        # Our operations on the frame come here
        thresholded = cv2.inRange(hsv_frame, lowerLimits, upperLimits)
        thresholded = cv2.erode(thresholded,kernelErode,iterations = 1)
        thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernelOpen)
        
        # finding blobs
        keypoints = detector.detect(thresholded)
        thresholded = cv2.drawKeypoints(thresholded, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        # tagging blobs
        for i in keypoints:
            koordinaat = (int(i.pt[0]), int(i.pt[1]))
            cv2.putText(thresholded, str(koordinaat), koordinaat, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        # Show images
        cv2.imshow('RealSense', thresholded)
        
        if cv2.waitKey(1) & 0xFF == ord('s'):
            with open("threshold.txt", "a") as f:
                f.write(input("Color name: ")+str(bars))
                
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:

    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()