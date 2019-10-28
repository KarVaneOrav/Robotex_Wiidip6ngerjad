# All camera operations

import pyrealsense2 as rs
import numpy as np
import cv2


def load_preset(file):
    with open(file, 'r') as f:
        text = f.read()

    dev = None
    try:
        devices = rs.context().query_devices()
        dev = devices[0]
        advnc_mode = rs.rs400_advanced_mode(dev)
        json_string = text.replace("'", '\"')
        advnc_mode.load_json(json_string)
    finally:
        if dev is not None:
            print("preset loaded")
        else:
            print("Preset loading failed")


load_preset('preset.json')  # load camera settings

# Configure depth and color streams
pipeline = rs.pipeline()
# Start streaming
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
profile = pipeline.start(config)


def stop():  # stop pipeline at the end
    pipeline.stop()


def get_depth_scale():
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    return depth_scale


def get_frame():
    # returns the blurred and cropped vanilla frame and the depth frame
    while True:        
        # Wait for a coherent pair of frames
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            continue
        else:
            break

    color_frame = np.asanyarray(color_frame.get_data())  # Convert images to numpy arrays
    #depth_frame = np.asanyarray(depth_frame.get_data())

    blurred = cv2.GaussianBlur(color_frame, (3, 3), 2)  # blur the frame
    cropped_color = blurred[0:680, 50:1230]  # crop from 1280, 720 because corners are foggy
    return depth_frame, cropped_color


def to_hsv(color_frame):  # turns color frame to hsv
    return cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)


def process_balls(hsv_frame, values):
    # takes a hsv frame as input, outputs balls as white
    lowerLimits = values.get('lowerLimits')
    upperLimits = values.get('upperLimits')

    thresholded = cv2.inRange(hsv_frame, lowerLimits, upperLimits)

    # in case morphing is needed
    # morphed = cv2.erode(thresholded,kernelErode,iterations = 1)
    # morphed = cv2.dilate(thresholded, kernelDilate, iterations = 1)
    return thresholded


def process_basket(hsv_frame, values):
    # takes a hsv frame as input, outputs basket as white
    lowerLimits = values.get('lowerLimits')
    upperLimits = values.get('upperLimits')
    dilate = values.get('kernelDilate')

    thresholded = cv2.inRange(hsv_frame, lowerLimits, upperLimits)
    morphed = cv2.dilate(thresholded, dilate, iterations=1)
    return morphed


def basket_finder(hsv_frame, values):
    # input processed image, outputs a keypoint on the target
    processed_frame = process_basket(hsv_frame, values)
    contours, _hierarchy = cv2.findContours(processed_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
        return ball
    except:
        print('No balls')
        return []
