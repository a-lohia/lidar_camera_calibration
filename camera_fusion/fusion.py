import numpy as np
import cv2
from helper import plotMatches
from matchPics import matchPics
from calibration import undistort_image


class Border:
    """Border class is defined to store the border coordinate. Only for purposes of CV Callback."""
    def __init__(self):
        self.border = None


def click_event(event, x, y, flags, user_data: Border):
    """OpenCV mouse left click callback that saves the pixel to a variable"""
    if event == cv2.EVENT_LBUTTONDOWN:
        user_data.border = x
        print("Clicked point:", (x, y))


def pad_and_concat(im1: np.ndarray, im2: np.ndarray) -> np.ndarray:
    """takes two images and pads the smaller one to the same height as the bigger
    Assumes the shape of the image (Y, X, C)
    """
    # print(im1.T.shape)

    y1, _, _ = im1.shape
    y2, _, _ = im2.shape
    diff = abs(y1 - y2)

    if y1 == y2:
        # print(np.hstack((im1, im2)).shape)
        return np.hstack((im1, im2))
    elif y1 > y2:
        if diff % 2 == 0:
            im2 = np.pad(im2, ((diff/2, diff/2), (0, 0)), "constant")
        else:
            im2 = np.pad(im2, ((diff//2, diff//2+1), (0, 0)), "constant")
    else:
        if diff % 2 == 0:
            im1 = np.pad(im1, ((diff/2, diff/2), (0, 0)), "constant")
        else:
            im1 = np.pad(im1, ((diff//2, diff//2+1), (0, 0)), "constant")
    # print(np.hstack((im1, im2)).shape)

    return np.hstack((im1, im2))
    

def fuse_two_frames(im_one_path: str, im_two_path: str, im_one_calib_path: str, im_two_calib_path: str) -> np.ndarray:
    """ takes two images (left, and right) and homographically projects the right image onto the left.

    Inputs:
    im_one_path str: path to the left image (should end in '.jpg')
    im_two_path str: path to the right image (should end in '.jpg')
    im_one_calib_path str: path to the folder of calibration images for the left camera (should end in path_to_folder/)
    im_two_calib_path str: path to the folder of calibration images for the right camera (should end in path_to_folder/)

    Output:
    warped_cover np.ndarray: overlapping projected image
    """

    left = undistort_image(cv2.imread(im_one_path), im_one_calib_path)
    right = undistort_image(cv2.imread(im_two_path), im_two_calib_path)

    left_border = Border()
    right_border = Border()

    # CV2 code that allows you to click on each image where you want to cut it off. The goal is to select the overlapping region
    cv2.imshow("Left Image", left)
    cv2.setMouseCallback("Left Image", click_event, left_border)
    cv2.imshow("Right Image", right)
    cv2.setMouseCallback("Right Image", click_event, right_border)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Crops the image based on clicks in previous code
    left[:, :left_border.border] = [0, 0, 0]
    right[:, right_border.border:] = [0, 0, 0]
    # Displays cropped image
    cv2.imshow("Cropped Images", pad_and_concat(left, right))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Extracts features in the overlapping region and maps them
    matches, locs1, locs2 = matchPics(left, right)


    x1 = np.fliplr(locs1[matches[:, 0]])
    x2 = np.fliplr(locs2[matches[:, 1]])

    # plotMatches(left, right, matches, locs1, locs2)

    # Find homography matrix that takes right image to left
    H, _ = cv2.findHomography(x2, x1, method=cv2.RANSAC)
    print(H)

    left = undistort_image(cv2.imread(im_one_path), im_one_calib_path)
    right = undistort_image(cv2.imread(im_two_path), im_two_calib_path)

    # Takes the right image and transforms it via H into left space (modifies "right" variable)
    # The shape is larger as the warped image's size increases
    warped_cover = cv2.warpPerspective(right, H, (2*right.shape[1], right.shape[0] + 1000))

    # Paste the images together
    warped_cover[0:right.shape[0], 0:right.shape[1]] = left

    # Display the final result
    cv2.imwrite("homography_result.jpg", warped_cover)
    cv2.imshow(" ", warped_cover)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return warped_cover
