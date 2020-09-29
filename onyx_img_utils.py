#!/usr/bin/env python
import json
import shutil
import sys
import os
import subprocess

import cv2 as cv

import OnyxRectUtils

debugRootDir = 'debug'
comicJsonFileName = 'comic.json'
maxBlockCount = 14
imgExpectSize = 900

def scaleToViewport(imgWidth, imgHeight, viewportWidth, viewportHeight):
    scale = 1
    while imgWidth > viewportWidth or imgHeight > viewportHeight:
        imgWidth = imgWidth * 0.9
        imgHeight = imgHeight * 0.9
        scale = scale / 0.9
    return scale


def cvImRead(filePath):
    img, scale = cvImReadImp(filePath)
    return img


def cvImReadImp(filePath):
    img = cv.imread(filePath)
    imgSize = getImgSize(img)
    print("filePath: {}, img size: {}, {}".format(filePath, imgSize[0], imgSize[1]))

    width = imgSize[0]
    height = imgSize[1]
    scale = scaleToViewport(width, height, imgExpectSize, imgExpectSize)
    if scale != 1:
        img = cv.resize(img, (0, 0), fx=1.0 / scale, fy=1.0 / scale, interpolation=cv.INTER_NEAREST)
        imgSize = getImgSize(img)

    print("scale:{}, img size: {}, {}".format(scale, imgSize[0], imgSize[1]))
    return img, scale


def saveScaleImg(filePath):
    img, scale = cvImReadImp(filePath)
    cv.imwrite(os.path.join('comic', os.path.basename(filePath)), img)


def getImgSize(img):
    imgSize = list(img.shape[:2])
    imgSize.reverse()  # get a [width,height] list
    return imgSize


def getContourSize(img):
    imgSize = getImgSize(img)
    contourSize = int(sum(imgSize) / 2 * 0.004)
    return contourSize


def cvImWriteSplitResult(filePath, img, tag, blockRectList):
    blockListSize = len(blockRectList)
    outputDir = getBlockDir(blockListSize)
    outputPath = os.path.join(outputDir, os.path.basename(filePath) + '-split-{}.jpg'.format(tag))
    print("outputPath: {}".format(outputPath))
    ensure_parent_directory(outputPath)
    cv.imwrite(outputPath, img)
    return


def getBlockDir(blockListSize):
    outputDir = '{}\\{}'.format(debugRootDir, blockListSize)
    return outputDir


def cvRectangle(contours, img):
    contourSize = getContourSize(img)

    # Get (square) panels out of contours
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)

        # Drawing a rectangle on copied image
        rect = cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), contourSize)
        # cvShowWait(img)
    return


def cvRectList(rects, img, putText=True):
    contourSize = getContourSize(img)
    index = 0
    for rect in rects:
        index += 1
        x1 = rect[0]
        y1 = rect[1]
        x2 = rect[2]
        y2 = rect[3]
        cv.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), contourSize)
        text = '{}'.format(index)
        width = x2 - x1
        height = y2 - y1
        position = (int(x1 + width * 0.5), int(y1 + height * 0.55))
        if putText:
            cvPutText(img, position, text)
        print("rect: {}".format(rect))


def cvPutText(img, position, text):
    # write panel numbers on debug img
    imgSize = getImgSize(img)
    fontRatio = sum(imgSize) / 2 / 400
    font = cv.FONT_HERSHEY_SIMPLEX
    fontScale = 1 * fontRatio
    fontColor = (0, 0, 255)
    lineType = 2
    cv.putText(img, text, position, font, fontScale, fontColor, lineType)


def checkBlockRectList(blockRectList, img):
    if len(blockRectList) == 0:
        print('empty block, use img size')
        imgSize = getImgSize(img)
        rect = [0, 0, imgSize[0], imgSize[1]]
        blockRectList.append(rect)
        x1 = rect[0]
        y1 = rect[1]
        width = rect[2]
        height = rect[3]
        position = (int(x1), int(y1 + height * 0.55))
        cvPutText(img, position, 'empty block')


def analyzeContours(contours, img, debug):
    print("total contours:{}".format(len(contours)))

    contentBoundingRect = getContentBoundingRect(contours)
    imgSize = [contentBoundingRect[2] - contentBoundingRect[0], contentBoundingRect[3] - contentBoundingRect[1]]

    mainContours = []
    contentBoundingContours = []
    smallBoundingContours = []
    smallBoundingRects = []
    for contour in contours:
        arclength = cv.arcLength(contour, True)

        epsilon = 0.01 * arclength
        approx = cv.approxPolyDP(contour, epsilon, True)

        x, y, w, h = cv.boundingRect(approx)

        # exclude very small panels
        if w < imgSize[0] / maxBlockCount or h < imgSize[1] / maxBlockCount:
            smallBoundingContours.append(contour)
            smallBoundingRects.append([x, y, x + w, y + h])
            continue

        percent = (w * h) / (imgSize[0] * imgSize[1])
        if percent >= 0.98:
            contentBoundingContours.append(contour)
        else:
            mainContours.append(contour)
    print("findContentBoundingContour, mainContours:{}, contentBoundingContours:{}, smallBoundingContours:{}"
          .format(len(mainContours), len(contentBoundingContours), len(smallBoundingContours)))


    mainBlockRectList = checkIntersectAndCombine(mainContours)
    if debug:
        cvRectList(mainBlockRectList, img)
        cvShowWait(img)

    smallBlockRectList, remainBlockRectList = mergeSmallContours(smallBoundingRects, contentBoundingRect, mainBlockRectList)
    if debug:
        cvRectList(remainBlockRectList, img, False)
        cvShowWait(img)

    # filter small block rect list
    filterSmallBlockRectList = []
    for rect in smallBlockRectList:
        # exclude very small panels
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        if w < imgSize[0] / maxBlockCount or h < imgSize[1] / maxBlockCount:
            continue
        filterSmallBlockRectList.append(rect)

    newBlockRectList = mainBlockRectList + filterSmallBlockRectList
    # blockResultList = OnyxRectUtils.checkIntersectAndCombine(newBlockRectList)
    # print("newBlockRectList blockResultList size: {}".format(len(blockResultList)))
    # for rect in blockResultList:
    #     print("newBlockRectList rect: {}".format(rect))

    # blockResultList = newBlockRectList
    blockResultList = mainBlockRectList
    cvRectList(blockResultList, img)
    return blockResultList


def getContentBoundingRect(contours):
    rect = []
    for contour in contours:
        arclength = cv.arcLength(contour, True)

        epsilon = 0.01 * arclength
        approx = cv.approxPolyDP(contour, epsilon, True)
        x, y, w, h = cv.boundingRect(approx)
        if len(rect) == 0:
            rect = [x, y, x + w, y + h]
        else:
            rect = OnyxRectUtils.combineRect(rect, [x, y, x + w, y + h])
    print("getContentBoundingRect: {}".format(rect))
    return rect


def getAllBoundingRect(contours):
    rects = []

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        rect = [x, y, x + w, y + h]
        rects.append(rect)

    return rects


def mergeSmallContours(smallBoundingRects, contentBoundingRect, mainBlockRectList):
    remainBlockRectList = OnyxRectUtils.cutRectByExcludingRegions2(contentBoundingRect, mainBlockRectList)
    remainBlockRectMap = {}

    index = -1
    for rect in remainBlockRectList:
        index += 1
        for smallRect in smallBoundingRects:
            if OnyxRectUtils.is_intersect(rect, smallRect):
                ensureList(remainBlockRectMap, index).append(smallRect)

    unionRectList = []
    for item in remainBlockRectMap.items():
        unionRect = []
        for rect in item[1]:
            if len(unionRect) == 0:
                unionRect = rect.copy()
            else:
                unionRect = OnyxRectUtils.combineRect(unionRect, rect)

        unionRectList.append(unionRect)

    # smallBlockRectList = unionRectList
    smallBlockRectList = OnyxRectUtils.checkIntersectAndCombine(unionRectList)

    print("mergeSmallContours result size: {}".format(len(smallBlockRectList)))
    for rect in smallBlockRectList:
        print("mergeSmallContours rect: {}".format(rect))

    return smallBlockRectList, remainBlockRectList


def ensureList(map, key):
    if key not in map:
        map[key] = []
    return map[key]

def checkIntersectAndCombine(contours):
    rects = getAllBoundingRect(contours)
    resultRects = OnyxRectUtils.checkIntersectAndCombine(rects)
    return resultRects


def openWithChrome(filePath):
    abslouteFilePath = '\"' + os.path.abspath(filePath) + '\"'
    print("filePath : {}".format(abslouteFilePath))
    cmd = '"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" --allow-file-access-from-files ' + '--app=' + abslouteFilePath
    print("cmd = " + cmd)
    subprocess.Popen(cmd)


def is_img(filename):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        return True
    else:
        return False


def listAllFile(directory):
    filenames = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if is_img(filename):
                filenames.append(os.path.join(root, filename))
    filenames.sort()
    return filenames


def cvShowWait(img):
    cv.imshow("img",img)
    cv.waitKey(0)


def clearDebugDir():
    if os.path.exists(debugRootDir):
         shutil.rmtree(debugRootDir)
    ensure_dir(debugRootDir)


def ensure_parent_directory(path):
    """Ensure that the parent directory of `path` exists"""
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


def ensure_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def dict_to_json_write_file(dict, jsonPath):
    with open(jsonPath, 'w') as f:
        json.dump(dict, f)


def json_file_to_dict(jsonPath):
    with open(jsonPath, 'r') as f:
        dict = json.load(fp=f)
        print(dict)
        return dict


def checkSplitResultDict(inputDict, outputDict):
    hitCount = 0
    result = {}
    for file in inputDict.keys():
        if outputDict[file] == inputDict[file]:
            hitCount += 1
        else:
            blockListSize = outputDict[file]
            outputDir = getBlockDir(blockListSize)
            dstPath = os.path.join(outputDir + '-fail-origin', os.path.basename(file))
            ensure_parent_directory(dstPath)
            shutil.copy(file, dstPath)

            if result.__contains__(blockListSize):
                failList = result[blockListSize]
            else:
                failList = []
                result[blockListSize] = failList
            failList.append({
                'filePath': file,
                'expectBlockSize': inputDict[file],
                'actualBlockSize': outputDict[file]
            })

    total = len(inputDict)
    result['total'] = total
    result['hitCount'] = hitCount
    result['failCount'] = total - hitCount
    result['hitPercent'] = '{}'.format(hitCount / total)
    print('hitCount:{}, failCount:{}, hitPercent:{}'.format(result['hitCount'], result['failCount'], result['hitPercent']))
    resultPath = os.path.join(debugRootDir, 'report.json')
    dict_to_json_write_file(result, resultPath)
