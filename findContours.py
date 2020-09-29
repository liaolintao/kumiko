#!/usr/bin/env python
import sys

import cv2 as cv

import onyx_img_utils

filePath = sys.argv[1]
# filePath = 'C:\onyx\github\python\kumiko\longzhu\longzhu (10).png'

img = onyx_img_utils.cvImRead(filePath)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, binary = cv.threshold(gray, 127, 255, cv.THRESH_BINARY_INV)
# onyx_img_utils.cvShowWait(binary)
contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

contourSize = onyx_img_utils.getContourSize(img)
cv.drawContours(img, contours, -1, (0, 0, 255), contourSize)

onyx_img_utils.cvShowWait(img)
cv.destroyAllWindows()
