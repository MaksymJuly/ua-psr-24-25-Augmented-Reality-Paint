#!/usr/bin/env python
import cv2
import numpy as np
import json
import os

class JsonHandler:
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        """Read JSON data from the specified file."""
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print(f"Error: The file '{self.filename}' does not exist.")
            return None
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON.")
            return None

    def write(self, data):
        """Write JSON data to the specified file."""
        try:
            with open(self.filename, 'w') as file:
                json.dump(data, file, indent=4)
                print(f"Data successfully written to '{self.filename}'.")
        except Exception as e:
            print(f"Error: {e}")

    def get_limits(self, hsv_min, hsv_max):

        limits = {
                    'HSV_min': [int(hsv_min[0]), int(hsv_min[1]), int(hsv_min[2])],
                    'HSV_max': [int(hsv_max[0]), int(hsv_max[1]), int(hsv_max[2])]
                 }
        
        return limits
    
    def get_hsv_min_max(self, limits):
        hsv_min, hsv_max = np.array([0, 0, 0]), np.array([255, 255, 255])

        if limits != None:
            hsv_min = np.array([
                                    limits['HSV_min'][0],
                                    limits['HSV_min'][1],
                                    limits['HSV_min'][2]
                                ])
            hsv_max = np.array([
                                    limits['HSV_max'][0],
                                    limits['HSV_max'][1],
                                    limits['HSV_max'][2]
                                ])

        return hsv_min, hsv_max

def mirror_img(image):
    # Check if the image is valid
    if image is None:
        return None
    # Flip the image horizontally (mirror effect)
    return cv2.flip(image, 1)

def resize_window(window_handel, image):
        _, _, screen_width, screen_height = cv2.getWindowImageRect(window_handel)

        # Resize the image to fit the screen while keeping the aspect ratio
        height, width = image.shape[:2]
        scale_width = screen_width / width
        scale_height = screen_height / height
        scale = min(scale_width, scale_height) * 2  # Keep aspect ratio

        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        return image, new_width, new_height

def sliders(sliders_exist, js, window_handel):

    if not sliders_exist:
        # Create sliders (trackbars)
        cv2.createTrackbar('H min', window_handel, 0, 255, update_matrix)
        cv2.createTrackbar('H max', window_handel, 0, 255, update_matrix)
        cv2.createTrackbar('S min', window_handel, 0, 255, update_matrix)
        cv2.createTrackbar('S max', window_handel, 0, 255, update_matrix)
        cv2.createTrackbar('V min', window_handel, 0, 255, update_matrix)
        cv2.createTrackbar('V max', window_handel, 0, 255, update_matrix)

        hsv_min, hsv_max = js.get_hsv_min_max(js.read())
        
        cv2.setTrackbarPos('H min', window_handel, hsv_min[0])
        cv2.setTrackbarPos('S min', window_handel, hsv_min[1])
        cv2.setTrackbarPos('V min', window_handel, hsv_min[2])

        cv2.setTrackbarPos('H max', window_handel, hsv_max[0])
        cv2.setTrackbarPos('S max', window_handel, hsv_max[1])
        cv2.setTrackbarPos('V max', window_handel, hsv_max[2])

        sliders_exist = True
    
    hsv_min = np.array([
                            cv2.getTrackbarPos('H min', window_handel),
                            cv2.getTrackbarPos('S min', window_handel),
                            cv2.getTrackbarPos('V min', window_handel)
                        ])  # Minimum HSV values
    
    hsv_max = np.array([
                            cv2.getTrackbarPos('H max', window_handel),
                            cv2.getTrackbarPos('S max', window_handel),
                            cv2.getTrackbarPos('V max', window_handel)
                        ])  # Maximum HSV values

    return sliders_exist, hsv_min, hsv_max

def update_matrix(x):
    pass

def run(js):
    mirror_on = True
    sliders_exist = False

    # Initial setup
    capture = cv2.VideoCapture(0)
    window = 'window'

    # Create the window
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Show acquired image
    while True:
        # Get an image from the camera
        _, image = capture.read()

        # Mirror image
        if mirror_on:
            image = mirror_img(image)
        
        # Do image full screen
        image, _, _ = resize_window(window, image)
        
        # Init sliders / get valuse from them
        sliders_exist, hsv_min, hsv_max = sliders(sliders_exist, js, window)

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create a mask using the defined color range
        mask = cv2.inRange(hsv_image, hsv_min, hsv_max)

        masked_region = cv2.bitwise_and(image, image, mask=mask)

        alpha = 0.8  # Transparency level for blending
        image = cv2.addWeighted(image, 1 - alpha, masked_region, alpha, 0)

        # Show frame
        cv2.imshow(window, image)            

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC or q key to exit
            break
        elif key == ord('m'):
            mirror_on = False if mirror_on else True
        elif key == ord('w'):
            js.write(js.get_limits(hsv_min, hsv_max))

    capture.release()
    cv2.destroyAllWindows()

def main():
    js = JsonHandler(os.path.join(os.getcwd(), 'limits.json'))

    run(js)

    print('\n Bye!')

if __name__ == '__main__':
    main()