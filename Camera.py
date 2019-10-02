# All camera operations

import pyrealsense2 as rs
import numpy as np
import cv2

# values for image processing
greenThreshold = [11, 0, 46, 43, 255, 175]
greenKernelErode = np.ones((1, 1), np.uint8)
greenKernelDilate = np.ones((7, 7), np.uint8)

# colour detection limits
lowerLimitsGreen = np.array([greenThreshold[0], greenThreshold[1], greenThreshold[2]])
upperLimitsGreen = np.array([greenThreshold[3], greenThreshold[4], greenThreshold[5]])

#blobparams
blobparams = cv2.SimpleBlobDetector_Params()
blobparams.minArea = 15
blobparams.maxArea = 10000000
blobparams.minDistBetweenBlobs = 60
blobparams.filterByColor = True # filter by color
blobparams.blobColor = 255  # 255 is white
blobparams.filterByCircularity = False
blobparams.filterByConvexity = False
#filterByInertia = False
detector = cv2.SimpleBlobDetector_create(blobparams)

# Configure depth and color streams
pipeline = rs.pipeline()

# Start streaming
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
profile = pipeline.start(config)
####

# stop pipeline at the end

####
def stop():
    pipeline.stop()

def get_frame():
    while True:        
        # Wait for a coherent pair of frames: color
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        else:
            break
    
    # Convert images to numpy arrays
    color_frame = np.asanyarray(color_frame.get_data())
    # blur the frame
    blurred = cv2.GaussianBlur(color_frame, (5, 5), 1)
    # crop from 1280, 720 because corners are foggy
    cropped = blurred[0:680, 50:1230]
    return cropped


def processed_frame_green(color_frame, lowerLimits = lowerLimitsGreen,
                          upperLimits = upperLimitsGreen):
    #convert to hsv
    hsv_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
    
    # Our operations on the frame come here
    thresholded = cv2.inRange(hsv_frame, lowerLimits, upperLimits)

    # in case morphing is needed
    #morphed = cv2.erode(thresholded,kernel1,iterations = 1)
    #morphed = cv2.dilate(morphed, kernel2, iterations = 1)

    return thresholded

def green_finder(frame):
    coordinates = []
    # finding blobs
    keypoints = detector.detect(frame)
    for i in keypoints:
        coordinates += [[int(i.pt[0]), int(i.pt[1])]]
    print(str(len(coordinates))+'dots')
    if len(coordinates) == 0:
        return []
    else:
        # find closest ball
        closest = coordinates[0]
        print(str(closest)+'ball')
        for ball in coordinates:
            if ball[1] < closest[1]:
                closest = ball
        return closest

def getDetector():
    return detector

def ball_to_middle(ball):
    if ball[0] < 700:
        return [0, 0, -1]
    elif ball[0] > 730:
        return [0, 0, 1]
    else:
        return [0, 0, 0]
    
    
