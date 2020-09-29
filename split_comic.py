#!/usr/bin/env python
import os
import sys

import cv2 as cv
import numpy as np

import onyx_img_utils


def splitFile(filePath, show):
    if not onyx_img_utils.is_img(filePath):
        return 0
    img = onyx_img_utils.cvImRead(filePath)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_OTSU + cv.THRESH_BINARY_INV)
    # binary = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 3, 0)

    #
    # blur = cv.GaussianBlur(gray, (5, 5), 0)
    # if show:
    #     onyx_img_utils.cvShowWait(blur)
    # rect, binary = cv.threshold(blur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

    if show:
        onyx_img_utils.cvShowWait(binary)

    contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # may be dark background
    if len(contours) == 1:
        ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_OTSU + cv.THRESH_BINARY)
        contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if show:
        onyx_img_utils.cvShowWait(binary)

    # if show:
    #     contourSize = onyx_img_utils.getContourSize(img)
    #     cv.drawContours(img, contours, -1, (0, 255, 0), contourSize)
    #     onyx_img_utils.cvShowWait(img)

    # if show:
    #     onyx_img_utils.cvRectangle(contours, img)
    #     onyx_img_utils.cvShowWait(img)

    blockRectList = onyx_img_utils.analyzeContours(contours, img, show)
    if show:
        onyx_img_utils.cvShowWait(img)

    onyx_img_utils.checkBlockRectList(blockRectList, img)
    if show:
        onyx_img_utils.cvShowWait(img)
        cv.destroyAllWindows()
    else:
        onyx_img_utils.cvImWriteSplitResult(filePath, img, "comic", blockRectList)
    return len(blockRectList)


def splitDir(dir):
    onyx_img_utils.clearDebugDir()
    inputJsonPath = os.path.join(dir, onyx_img_utils.comicJsonFileName)
    inputDict = onyx_img_utils.json_file_to_dict(inputJsonPath)

    files = onyx_img_utils.listAllFile(dir)
    outputDict = {}
    for file in files:
        blockSize = splitFile(file, False)
        if blockSize >= 0:
            outputDict[file] = blockSize

    outputJsonPath = os.path.join(onyx_img_utils.debugRootDir, onyx_img_utils.comicJsonFileName)
    onyx_img_utils.dict_to_json_write_file(outputDict, outputJsonPath)

    onyx_img_utils.checkSplitResultDict(inputDict, outputDict)


# main start


fileOrDir = sys.argv[1]

if os.path.isdir(fileOrDir):
    splitDir(fileOrDir)
elif os.path.isfile(fileOrDir):
    splitFile(fileOrDir, True)
else:
    file = 'C:\onyx\github\python\kumiko\comic\img (1).png'
    splitFile(file, True)



