# All camera operations

import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
# Start streaming
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
pipeline.start(config)


def stop():  # stop pipeline at the end
    pipeline.stop()


def load_preset(file):
    DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07"]
    try:
        dev = None
        devices = rs.context().query_devices()
        for d in devices:
            if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
                dev = d
        print(dev)
        advnc_mode = rs.rs400_advanced_mode(dev)
        json_string = str(file).replace("'", '\"')
        advnc_mode.load_json(json_string)
    finally:
        print("preset loaded")


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
        print("ball: " + str(ball))
        return ball
    except:
        print('No balls')
        return []
