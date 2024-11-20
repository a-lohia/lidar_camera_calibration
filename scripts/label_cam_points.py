# Written by Arya Lohia for Carnegie Mellon Racing. Fall 2024
# Takes a combined camera image and lets you select pixels. Outputs a .npz file to a folder of choice

import numpy as np
import cv2

data_path = "data/fused_image_points/"
img_path = "camera_fusion/homography_result.jpg"  # ends in .jpg

class Image:
    def __init__(self, image: np.ndarray):
        self.image = image
        self.selected_points = []

    
def click_event(event, x, y, flags, user_data: Image):
    """OpenCV mouse left click callback that saves the pixel to a variable"""
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked point:", (x, y))
        user_data.selected_points.append((x, y))
        color = (255, 0, 0)

        # Draw a circle at the clicked point
        cv2.circle(user_data.image, (x, y), 5, color, -1)

img = cv2.imread(img_path)
user_data = Image(img)

cv2.namedWindow('image')
cv2.setMouseCallback('image', click_event, user_data)

while True:
    cv2.imshow('image', user_data.image)
    if cv2.waitKey(1) == ord('q'):
        break

print

cv2.destroyAllWindows()    

