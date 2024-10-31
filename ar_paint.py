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