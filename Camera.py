# All camera operations

import pyrealsense2 as rs
import numpy as np
import cv2

# values for image processing
greenThreshold = [21, 111, 59, 85, 255, 168]
greenKernelErode = np.ones((3, 3),np.uint8)
greenKernelOpen = np.ones((5, 5),np.uint8)

# colour detection limits
lowerLimits = np.array([greenThreshold[0], greenThreshold[1], greenThreshold[2]])
upperLimits = np.array([greenThreshold[3], greenThreshold[4], greenThreshold[5]])

#blobparams
blobparams = cv2.SimpleBlobDetector_Params()
blobparams.minArea = 500
blobparams.maxArea = 10000000
blobparams.filterByColor = True # filter by color
blobparams.blobColor = 255  # 255 is white
blobparams.filterByCircularity = False
blobparams.filterByConvexity = False
#filterByInertia = False
detector = cv2.SimpleBlobDetector_create(blobparams)

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
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
    return color_frame

def processed_frame_green(thresh=greenThreshold, kernel1=greenKernelErode, kernel2=greenKernelOpen):
    color_frame = get_frame()
    
    #convert to hsv
    hsv_frame = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
    
    # Our operations on the frame come here
    thresholded = cv2.inRange(hsv_frame, lowerLimits, upperLimits)
    morphed = cv2.erode(thresholded,kernel1,iterations = 1)
    morphed = cv2.morphologyEx(morphed, cv2.MORPH_OPEN, kernel2)
    
    return morphed

def green_finder(frame):
    coordinates = []
    # finding blobs
    keypoints = detector.detect(frame)
    for i in keypoints:
        coordinates += [[int(i.pt[0]), int(i.pt[1])]]
    
    return coordinates

def ball_to_middle(balls):
    if balls[0][0] < 310:
        return "left"
    elif balls[0][0] >330:
        return "right"
    else:
        return "ok"
    
    
