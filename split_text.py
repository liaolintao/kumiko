#!/usr/bin/env python
import os
import sys

import cv2 as cv

import onyx_img_utils

filePath = sys.argv[1]
# filePath = 'C:\onyx\github\python\kumiko\longzhu\longzhu (10).png'

img = onyx_img_utils.cvImRead(filePath)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
tmin = 0
tmax = 255
ret, binary = cv.threshold(gray, tmin, tmax, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)

# cv.imshow("img", binary)
# cv.waitKey(0)

# Specify structure shape and kernel size.
# Kernel size increases or decreases the area
# of the rectangle to be detected.
# A smaller value like (10, 10) will detect
# each word instead of a sentence.
rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (18, 18))

# Appplying dilation on the threshold image
dilation = cv.dilate(binary, rect_kernel, iterations=1)

contours, hierarchy = cv.findContours(dilation, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
# cv.drawContours(img, contours, -1, (0, 0, 255), 3)

onyx_img_utils.cvRectangle(contours, img)

cv.imshow("img", img)

cv.waitKey(0)
cv.destroyAllWindows()

#onyx_img_utils.cvImWrite(cv, filePath, img)

