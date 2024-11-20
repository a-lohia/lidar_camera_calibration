import numpy as np
import cv2 as cv
import glob
import os

def undistort_image(img, data_path: str):

    ret, mtx, dist, rvecs, tvecs = calibrate(data_path=data_path)

    h,  w = img.shape[:2]
    
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 0, (w,h))

    # ---
    # METHOD 1 
    # ---

    # undistort
    dst = cv.undistort(img, mtx, dist, None, newcameramtx)
    # crop the image
    x, y, w, h = roi
    dst = dst[y:y+h, x:x+w]
    # cv.imwrite('calibresult.png', dst)

    print(dst.shape)

    return dst

def calibrate(data_path: str) -> np.ndarray | bool:

    if not os.path.exists(data_path):
        return False
    data_path = os.path.join(data_path, "*.jpg")

    SQUARE_SIZE = 1 # mm
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((10*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:10,0:7].T.reshape(-1,2) # * SQUARE_SIZE
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    images = glob.glob(data_path)
    # print(images)
    for fname in images:
        img = cv.imread(fname)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (10,7), None)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
            # Draw and display the corners
            cv.drawChessboardCorners(img, (10,7), corners2, ret)
            # cv.imshow('img', img)
            # cv.waitKey(500)

    cv.destroyAllWindows()

    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    return ret, mtx, dist, rvecs, tvecs