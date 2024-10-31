# ua-psr-24-25-Augmented-Reality-Paint
Augmented Reality Paint


        PSR Augmented Reality Paint

The aim is to develop a set of applications whose main functionality is to allow the user to draw on an image by moving a colored object in front of the laptop's camera.

The tools to be used for this purpose are those that were introduced in previous classes (eg python, opencv, etc).

You must develop two distinct scripts, one called color_segmenter.pyand the other named ar_paint.py.


        Color Segmentation - color_segmenter.py

The program color_segmenter.py will be used to configure the color detection parameters that will then be used by ar_paint.py. The color_segmenter.py must continuously receive images from the laptop's camera. These images are then processed in order to segment the pixels whose color is between the minimum and maximum R, G and B limits established.

The application must have 6 trackbars that allow these limits to be changed, and the program must, when these values ​​are changed, immediately show the segmentation result using the new limits.

When the user is satisfied with the values ​​indicated, he presses the "w" (write) key to indicate that he wants to save the established limits. The program should save these limits in a json file called limits.json (placed in the local directory) with the following format:
The user can also use the "q" (quit) key to indicate that he wants to end the program without saving the json file.

To facilitate color detection, it is recommended to use a mobile phone with the full screen color light program (or similar) which allows you to place a color on the mobile phone screen, and then turn it towards the laptop camera.

Choose a color to place and then configure color segmentation to detect that color.

NOTE : Color segmentation will have extra value if you use the HSV color space correctly.


        Augmented Reality Drawing - ar_paint.py

The script ar_paint.pyshould continuously receive images from the camera. Each image is processed in order to find the object with the predefined color. Then, the coordinates of the centroid of this object are used to determine the detected position of the pencil. At this position, a point (or a line) with the defined color and size is painted. The process is repeated for each image received.

Initialization
The initialization phase should comprise the following functionalities:

Reading command line arguments.
Just an argument to indicate the name of the json file to be read (the one written by color_segmenter.py).

        $ ./ar_paint.py -j limits.json -h
        usage: ar_paint.py [-h] -j JSON

        Definition of test mode

        optional arguments:
        -h, --help            show this help message and exit
        -j JSON, --json JSON  Full path to json file.

Reading the json file with the limits for color segmentation

Setting up video capture

Create an all white image (canvas) to draw on the same size as the images received from the camera

Other initializations you consider necessary

Continuous operation
Continuous operation is a set of functionalities that are repeated cyclically. In this context, the program must:

Acquire an image from the camera

Process this image to obtain a mask with the pixels that have the desired color

You can display the mask in a dedicated opencv window to make it easy to see if the segmentation is working as intended.

Processes the color segmentation mask to obtain a mask with only the object with the largest area
It is suggested to use opencv's connected components , but there will certainly be other alternatives.

You should highlight the object with the largest area by painting it (for example in green) in the original image.

Calculate the centroid of this object
Show the detected centroid drawn as a red cross superimposed on the original image.

Use the detected centroid to paint, on the image with the canvas, a line or a dot with the color and size defined for the pencil (see below).
Keyboard commands
The program must also listen to keystrokes and implement the described functionalities.

i. "r" key, to change the pencil color to red

ii. "g" key, to change the pencil color to green

iii. "b" key, to change the pencil color to blue

iv. "+" key, to increase the size of the pencil

v. "-" key, to decrease the size of the pencil

vi. "c" key, to clear the screen, making it completely white again

vii. "w" key, to write the current image

Automatically generate the image file name taking into account the current date, eg

        drawing_Tue_Sep_15_10:36:39_2020.png

i. "q" key, to end the program