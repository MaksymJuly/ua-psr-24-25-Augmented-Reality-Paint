#!/usr/bin/env python
import cv2
import numpy as np
import json
import os
import sys
from colorama import Fore, Style, init
import argparse

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

def quit():
    print("\nGoodbye!")
    sys.exit(0)

def setup_arg():
    os.system('clear')
    parser = argparse.ArgumentParser(description=f'Definition of {Fore.BLUE}test{Style.RESET_ALL} mode',
                                     add_help=False)
    
    parser.add_argument('-h','--help',
                        action="help",
                        help=f'show this {Fore.BLUE}help{Style.RESET_ALL} message and {Fore.BLUE}exit{Style.RESET_ALL}')

    # Game mode options
    parser.add_argument('-j', '--json',
                        metavar=Fore.LIGHTBLACK_EX +'JSON'+ Style.RESET_ALL,
                        type=str,
                        default=os.path.join(os.getcwd(), 'limits.json'),
                        help=f'Name of the {Fore.GREEN}json{Style.RESET_ALL} file with .json'
                        # help=f'Full path to {Fore.GREEN}json{Style.RESET_ALL} file'
                        )
    
    arg = parser.parse_args()

    return arg

def run(arg):
    js = JsonHandler(os.path.join(os.getcwd(), arg.json))
    hsv_min, hsv_max = js.get_hsv_min_max(js.read())
    
    mirror_on = True

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
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Do image full screen
        hsv_image, _, _ = resize_window(window, hsv_image)
        
        # Create a mask using the defined color range
        mask = cv2.inRange(hsv_image, hsv_min, hsv_max)

        masked_region = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)

        alpha = 0.8  # Transparency level for blending
        image = cv2.addWeighted(hsv_image, 1 - alpha, masked_region, alpha, 0)

        # Mirror image
        if mirror_on:
            image = mirror_img(image)

        # Show frame
        cv2.imshow(window, image)            

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC or q key to exit
            break
        elif key == ord('m'):
            mirror_on = False if mirror_on else True
        elif key == ord('r') or key == ord('g') or key == ord('b'):
            print(chr(key))

    capture.release()
    cv2.destroyAllWindows()

def main():

    init()

    run(setup_arg())

    print('\nBye!')

if __name__ == '__main__':
    main()