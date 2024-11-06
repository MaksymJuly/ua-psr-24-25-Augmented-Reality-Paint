#!/usr/bin/env python
import cv2
import numpy as np
import json
import os
import sys
from colorama import Fore, Style, init
import argparse
import color_segmenter
import time
from datetime import datetime

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

def draw_circle(image, mask):
    global radius, color

    area = cv2.countNonZero(mask)
    if area > 1000:
        M = cv2.moments(mask) # Calculate moments of the binary image
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            center_coordinates = (cX, cY)
            cv2.circle(image, center_coordinates, radius, color, -1)

            return image, True, cX, cY
    
    return image, False, None, None

def get_mask(hsv_min, hsv_max, image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv_image_blur = cv2.medianBlur(hsv_image, 5)
    # hsv_image_blur = cv2.blur(hsv_image_blur, (5, 5))

    mask = cv2.inRange(hsv_image_blur, hsv_min, hsv_max)


    masked_region = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)
    hsv_image = cv2.addWeighted(hsv_image, 1, masked_region, 1, 0)
    image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    return image, mask

def change_color(chr):

    if chr == 'r':
        return (0, 0, 255)
    elif chr == 'g':
        return (0, 255, 0)
    elif chr == 'b':
        return (255, 0, 0)

def change_size(chr, radius):
    if chr == '-':
        radius -= 1 if radius >= 2 else 1
    elif chr == '+':
        radius += 1
    
    return radius

def save_pic(image):
    formatted_time = datetime.now().strftime("%a_%b_%d_%H:%M:%S_%Y")
    name = 'drawing_'+formatted_time+'.png'
    
    cv2.imwrite(os.path.join(os.getcwd(), 'drawings', name), image)

    start_time = time.time()
    message = f"Picture {name} is saved."

    return start_time, message

def run(arg):
    global radius, color

    radius = 5
    color = (0, 255, 0)

    js = JsonHandler(os.path.join(os.getcwd(), arg.json))
    hsv_min, hsv_max = js.get_hsv_min_max(js.read())
    
    mirror_on = True

    state = False
    draw = False
    ix, iy = -1, -1

    message = f"Picture ({None}) is saved."
    pic_saved = False
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Initial setup
    capture = cv2.VideoCapture(0)
    window = 'window'

    # Create the window
    cv2.namedWindow(window, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(window, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Create a blank canvas for drawing
    ret, frame = capture.read()
    canvas = np.zeros_like(frame)

    while True:

        # Get an image from the camera
        ret, image = capture.read()
        if not ret:
            break

        # Mirror image
        image = mirror_img(image) if mirror_on else image
        
        image, mask = get_mask(hsv_min, hsv_max, image)

        image, state, x, y = draw_circle(image, mask)

        if state and draw:
            # Draw a line from the last position to the current position
            cv2.line(canvas, (ix, iy), (x, y), color, radius*2)
            ix, iy = x, y  # Update the last position
        elif state:
            ix, iy = x, y
            draw = True
        else:
            draw = False

        image = cv2.addWeighted(image, 1, canvas, 1, 0)

        if pic_saved:
            if time.time() - start_time > 3:
                pic_saved = False
            else:
                cv2.putText(image, message, (12, 32), font, 0.5, (0,0,0), 1, cv2.LINE_AA)
                cv2.putText(image, message, (10, 30), font, 0.5, (100,255,255), 1, cv2.LINE_AA)
            
        # Show frame
        cv2.imshow(window, image)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC or q key to exit
            break
        elif key == ord('m'): # m key to toggle image mirroring
            mirror_on = False if mirror_on else True
        elif key == ord('r') or key == ord('g') or key == ord('b'): # r g b keys to change color
            color = change_color(chr(key))
        elif key == ord('-') or key == ord('+'): # - or + to change brush size
            radius = change_size(chr(key), radius)
        elif key == ord('c'): # c key to clear canvas
            canvas = np.zeros_like(frame)
        elif key == ord('w'):
            if pic_saved == False:
                pic_saved = True
                start_time, message = save_pic(canvas)

    capture.release()
    cv2.destroyAllWindows()

def main():
    color_segmenter.main()

    init()

    run(setup_arg())

    print('\nBye!')

if __name__ == '__main__':
    main()