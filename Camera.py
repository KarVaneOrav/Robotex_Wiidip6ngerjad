# All camera operations

import pyrealsense2 as rs
import numpy as np
import cv2

# values for image processing green
green = [16, 163, 93, 124, 255, 255]
# greenKernelErode = np.ones((1, 1), np.uint8)
# greenKernelDilate = np.ones((3, 3), np.uint8)
# colour detection limits
lowerLimitsGreen = np.array([green[0], green[1], green[2]])
upperLimitsGreen = np.array([green[3], green[4], green[5]])

# values to process pink
pink = [95, 203, 61, 255, 255, 255, 3]
# values to process blue
blue = [35, 0, 29, 255, 91, 255, 3]
# values for processing
lowerLimitsTarget = None
upperLimitsTarget = None
targetKernelDilate = None

# Configure depth and color streams
pipeline = rs.pipeline()
# Start streaming
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
pipeline.start(config)


####

# stop pipeline at the end

####
def stop():
    pipeline.stop()


def get_target_basket(opponent):
    global lowerLimitsTarget
    global upperLimitsTarget
    global targetKernelDilate

    if opponent == 'pink':
        target = pink
    elif opponent == 'blue':
        target = blue
    else:
        print("Unknown target")
        raise Exception

    lowerLimitsTarget = np.array([target[0], target[1], target[2]])
    upperLimitsTarget = np.array([target[3], target[4], target[5]])
    targetKernelDilate = np.ones((target[6], target[6]), np.uint8)


def get_frame():
    # returns the blurred and cropped vanilla frame
    while True:        
        # Wait for a coherent pair of frames: color
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        else:
            break

    color_frame = np.asanyarray(color_frame.get_data())  # Convert images to numpy arrays
    blurred = cv2.GaussianBlur(color_frame, (3, 3), 2)  # blur the frame
    cropped = blurred[0:680, 50:1230]  # crop from 1280, 720 because corners are foggy
    return cropped


def to_hsv(color_frame):  # turns color frame to hsv
    return cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)


def process_balls(hsv_frame, lowerLimits=lowerLimitsGreen, upperLimits=upperLimitsGreen):
    # takes a hsv frame as input, outputs balls as white
    thresholded = cv2.inRange(hsv_frame, lowerLimits, upperLimits)

    # in case morphing is needed
    # morphed = cv2.erode(thresholded,kernelErode,iterations = 1)
    # morphed = cv2.dilate(thresholded, kernelDilate, iterations = 1)
    return thresholded


def process_basket(hsv_frame, lowerLimits=lowerLimitsTarget, upperLimits=upperLimitsTarget
                   , dilate=targetKernelDilate):
    # takes a hsv frame as input, outputs basket as white
    thresholded = cv2.inRange(hsv_frame, lowerLimits, upperLimits)
    morphed = cv2.dilate(thresholded, dilate, iterations=1)
    return morphed


def basket_finder(frame):
    # input processed image, outputs a keypoint on the target
    contours, _hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    keypoints = map(cv2.minEnclosingCircle, contours)
    try:
        keypoints = sorted(keypoints, key=lambda x: x[0])
        circle = keypoints[round(len(keypoints) / 2)]
        spot = [int(circle[0][0]), int(circle[0][1])]
        return spot
    except:
        print("no basket")
        return []

def green_finder(frame):
    # finds the closest ball from a black and white frame. Returns an empty list if no balls, otherwise as [x, y]
    contours, _hierarchy = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    circles = map(cv2.minEnclosingCircle, contours)

    circles = sorted(circles, key=lambda x: x[1])  # sort the list
    try:  # return the closest ball
        circle = circles[-1]
        ball = [int(circle[0][0]), int(circle[0][1])]
        print("ball: " + str(ball))
        return ball
    except:
        print('No balls')
        return []
