import cv2
from functools import partial
import config


def start():
    # Ask for color name to threshold
    color_name = input("Enter color name: ")

    # Try to get saved range from config file, use whole color space as default if not saved
    # Color ranges are saved as { "min": (hmin, smin, vmin), "max": (hmax, smax, vmax) }
    color_range = config.get("colors", color_name, default={ "min": (0, 0, 0), "max": (179, 255, 255) })

    # Create trackbars (sliders) for HSV channels
    cv2.namedWindow("frame")

    def update_range(i, j, value):
        values = list(color_range[i])
        values[j] = value
        color_range[i] = tuple(values)

    cv2.createTrackbar("h_min", "frame", color_range["min"][0], 179, partial(update_range, "min", 0))
    cv2.createTrackbar("s_min", "frame", color_range["min"][1], 255, partial(update_range, "min", 1))
    cv2.createTrackbar("v_min", "frame", color_range["min"][2], 255, partial(update_range, "min", 2))
    cv2.createTrackbar("h_max", "frame", color_range["max"][0], 179, partial(update_range, "max", 0))
    cv2.createTrackbar("s_max", "frame", color_range["max"][1], 255, partial(update_range, "max", 1))
    cv2.createTrackbar("v_max", "frame", color_range["max"][2], 255, partial(update_range, "max", 2))

    # Capture camera
    device = config.get("vision", "video_capture_device")
    cap = cv2.VideoCapture(device)

    while cap.isOpened():
        # Read BGR frame
        _, bgr = cap.read()

        # Convert to HSV
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        # TODO: also apply all the filters you do when actually running the robot (eg noise removal)
        # Apply color mask to HSV image
        mask = cv2.inRange(hsv, color_range["min"], color_range["max"])

        # Display filtered image
        cv2.imshow("frame", cv2.bitwise_and(bgr, bgr, mask=mask))

        # Handle keyboard input
        key = cv2.waitKey(1)

        if key & 0xFF == ord("q"):
            break

    # Overwrite color range
    config.set("colors", color_name, color_range)
    config.save()

    # Exit cleanly
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start()