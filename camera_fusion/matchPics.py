# Manan's CV HW

import numpy as np
import cv2
import skimage.color
from helper import briefMatch
from helper import computeBrief
from helper import corner_detection

def matchPics(I1, I2):
	#I1, I2 : Images to match

	#Convert Images to GrayScale
	grey_I1 = cv2.cvtColor(I1, cv2.COLOR_BGR2GRAY)
	grey_I2 = cv2.cvtColor(I2, cv2.COLOR_BGR2GRAY)

	# cv2.imshow('Grayscale Image', grey_I2)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()
	
	#Detect Features in Both Images
	locs1 = corner_detection(grey_I1, 0.15)
	locs2 = corner_detection(grey_I2, 0.15)

	print(len(locs1))
	
	#Obtain descriptors for the computed feature locations
	desc1, locs1 = computeBrief(grey_I1, locs1)
	desc2, locs2 = computeBrief(grey_I2, locs2)
	print("number of descriptors is ", len(desc1))

	#Match features using the descriptors
	matches = briefMatch(desc1, desc2, ratio=.8)
	print("number of matches is ", len(matches))

	return matches, locs1, locs2