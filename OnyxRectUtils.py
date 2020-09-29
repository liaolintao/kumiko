import functools
import itertools

# my Rectangle = (x1, y1, x2, y2), a bit different from OP's x, y, w, h
def intersection(rectA, rectB): # check if rect A & B intersect
    if not is_intersect(rectA, rectB):
        return False

    a, b = rectA, rectB
    startX = max(min(a[0], a[2]), min(b[0], b[2]))
    startY = max(min(a[1], a[3]), min(b[1], b[3]))
    endX = min(max(a[0], a[2]), max(b[0], b[2]))
    endY = min(max(a[1], a[3]), max(b[1], b[3]))

    if startX < endX and startY < endY:
        # if True:
        #     return True
        intesectRect = [startX, startY, endX, endY]
        if is_same_rect(intesectRect, rectA):
            print("contain rect, parent : {}".format(rectA))
            return True
        elif is_same_rect(intesectRect, rectB):
            print("contain rect, parent : {}".format(rectB))
            return True

        intesectAreaSize = getArea(intesectRect)
        maxIntersectPercent = intesectAreaSize / min(getArea(rectA), getArea(rectB))
        print("maxIntersectPercent :{}".format(maxIntersectPercent))
        return maxIntersectPercent > 0.1
    else:
        return False


def is_intersect(rectA, rectB):
    return rectA[0] < rectB[2] and rectB[0] < rectA[2] \
           and rectA[1] < rectB[3] and rectB[1] < rectA[3]


def is_same_rect(rect1, rect2):
    return rect1[0] == rect2[0] \
           and rect1[1] == rect2[1] \
           and rect1[2] == rect2[2] \
           and rect1[3] == rect2[3]


def getArea(rect):
    startX = rect[0]
    startY = rect[1]
    endX = rect[2]
    endY = rect[3]
    return (endX - startX) * (endY - startY)


def combineRect(rectA, rectB): # create bounding box for rect A & B
    a, b = rectA, rectB
    startX = min(a[0], b[0])
    startY = min(a[1], b[1])
    endX = max(a[2], b[2])
    endY = max(a[3], b[3])
    return [startX, startY, endX, endY]


def checkIntersectAndCombine(rects):
    print("before checkIntersectAndCombineImpl srcRect size : {}".format(len(rects)))
    mergedList = checkIntersectAndCombineImpl(rects)
    print("after checkIntersectAndCombineImpl mergedRect size : {}".format(len(mergedList)))
    mergedList.sort(key=functools.cmp_to_key(sortRect))
    return mergedList


def checkIntersectAndCombineImpl(rects):
    mergedList = []
    if len(rects) is 0:
        return mergedList

    for src in rects:
        merged = False
        for toMerge in mergedList:
            if intersection(src, toMerge):
                merged = True
                newMerge = combineRect(src, toMerge)
                toMerge[0] = newMerge[0]
                toMerge[1] = newMerge[1]
                toMerge[2] = newMerge[2]
                toMerge[3] = newMerge[3]
                break

        if merged:
            mergedList = checkIntersectAndCombineImpl(mergedList)
        else:
            newSrc = [src[0], src[1], src[2], src[3]]
            mergedList.append(newSrc)

    return mergedList


def sortRect(rect1, rect2):

    p1x = rect1[0]
    p1y = rect1[1]
    p1r = rect1[2]  # p1's right side
    p1b = rect1[3]  # p1's bottom
    p2x = rect2[0]
    p2y = rect2[1]
    p2r = rect2[2]
    p2b = rect2[3]

    # TODO sum(infos['size']) / 2 / 20
    gutterThreshold = 0

    # p1 is above p2
    if p2y >= p1b - gutterThreshold and p2y >= p1y - gutterThreshold:
        return -1

    # p1 is below p2
    if p1y >= p2b - gutterThreshold and p1y >= p2y - gutterThreshold:
        return 1

    # p1 is left from p2
    if p2x >= p1r - gutterThreshold and p2x >= p1x - gutterThreshold:
        return -1

    # p1 is right from p2
    if p1x >= p2r - gutterThreshold and p1x >= p2x - gutterThreshold:
        return 1

    return 0  # should we really fall into this case?


# android impl
def cutRectByExcludingRegions(sourceRect: list, excludingRectList: list):
    result = []
    if len(excludingRectList) == 0:
        result.append(sourceRect.copy())
        return result

    excludeByLeft = []
    for rect in excludingRectList:
        excludeByLeft.append(rect.copy())

    excludeByLeft.sort(key=functools.cmp_to_key(sortRectLeft))

    outBound = sourceRect.copy()

    while len(excludeByLeft) > 0:
        leftMost = excludeByLeft[0]

        innerBound = leftMost.copy()
        for r in excludeByLeft:
            innerBound = combineRect(innerBound, r)

        # out bounding rectangles of regions to exclude
        if innerBound[0] > outBound[0]:
            result.append([outBound[0], outBound[1], innerBound[0], outBound[3]])
        if innerBound[2] < outBound[2]:
            result.append([innerBound[2], outBound[1], outBound[2], outBound[3]])
        if innerBound[1] > outBound[1]:
            result.append([innerBound[0], outBound[1], innerBound[2], innerBound[1]])
        if innerBound[3] < outBound[3]:
            result.append([innerBound[0], innerBound[3], innerBound[2], outBound[3]])

        nextLeft = []
        leftList = []
        for rect in excludeByLeft:
            if rect[0] == leftMost[0]:
                leftList.append(rect)
            else:
                nextLeft = rect
                break

        leftList.sort(key=functools.cmp_to_key(sortRectRight))

        right = leftList[0][2]
        if len(nextLeft) != 0:
            right = min(right, nextLeft[0])

        topList = leftList.copy()
        topList.sort(key=functools.cmp_to_key(sortRectTop))

        segmentsByY = []
        for rect in topList:
            if len(segmentsByY) == 0:
                segmentsByY.append([rect[1], rect[3]])
                continue

            combined = False
            for segment in segmentsByY:
                if rect[3] < segment[0] or rect[1] > segment[1]:
                    continue

                if rect[1] < segment[0]:
                    segment[0] = rect[1]
                if rect[3] > segment[1]:
                    segment[1] = rect[3]
                combined = True
                break

            if not combined:
                segmentsByY.append([rect[1], rect[3]])

        segmentsByY.sort(key=functools.cmp_to_key(sortSegmentFirst))

        top = segmentsByY[0]
        if top[0] > innerBound[1]:
            result.append([innerBound[0], innerBound[1], right, top[0]])

        for i in range(1, len(segmentsByY)):
            above = segmentsByY[i - 1]
            below = segmentsByY[i]
            if below[0] > above[1]:
                result.append([innerBound[0], above[1], right, below[0]])

        segmentsByY.sort(key=functools.cmp_to_key(sortSegmentSecond))

        bottom = segmentsByY[len(segmentsByY) - 1]
        if bottom[1] < innerBound[3]:
            result.append([innerBound[0], bottom[1], right, innerBound[3]])

        removeList = []
        for rect in leftList:
            if rect[2] - right <= 0:
                removeList.append(rect)
            else:
                rect[0] = right

        for rect in removeList:
            excludeByLeft.remove(rect)

        outBound = innerBound.copy()
        outBound[0] = right

    print("size = {}".format(len(result)))
    for rect in result:
        print("cutRectByExcludingRegions: {}".format(rect))
    return result


# split vertical, row by row
def cutRectByExcludingRegions2(sourceRect: list, excludingRectList: list):
    result = []
    if len(excludingRectList) == 0:
        result.append(sourceRect.copy())
        return result

    excludeByTop = []
    for rect in excludingRectList:
        excludeByTop.append(rect.copy())

    excludeByTop.sort(key=functools.cmp_to_key(sortRectTop))

    outBound = sourceRect.copy()

    while len(excludeByTop) > 0:
        topMost = excludeByTop[0]

        innerBound = topMost.copy()
        for r in excludeByTop:
            innerBound = combineRect(innerBound, r)

        # out bounding rectangles of regions to exclude
        if innerBound[0] > outBound[0]:
            result.append([outBound[0], innerBound[1], innerBound[0], innerBound[3]])
        if innerBound[2] < outBound[2]:
            result.append([innerBound[2], innerBound[1], outBound[2], innerBound[3]])
        if innerBound[1] > outBound[1]:
            result.append([outBound[0], outBound[1], outBound[2], innerBound[1]])
        if innerBound[3] < outBound[3]:
            result.append([outBound[0], innerBound[3], outBound[2], outBound[3]])

        nextTop = []
        topList = []
        for rect in excludeByTop:
            if rect[1] == topMost[1]:
                topList.append(rect)
            else:
                nextTop = rect
                break

        topList.sort(key=functools.cmp_to_key(sortRectBottom))

        bottom = topList[0][3]
        if len(nextTop) != 0:
            bottom = min(bottom, nextTop[1])

        leftList = topList.copy()
        leftList.sort(key=functools.cmp_to_key(sortRectLeft))

        segmentsByX = []
        for rect in leftList:
            if len(segmentsByX) == 0:
                segmentsByX.append([rect[0], rect[2]])
                continue

            combined = False
            for segment in segmentsByX:
                if rect[2] < segment[0] or rect[0] > segment[1]:
                    continue

                if rect[0] < segment[0]:
                    segment[0] = rect[0]
                if rect[2] > segment[1]:
                    segment[1] = rect[2]
                combined = True
                break

            if not combined:
                segmentsByX.append([rect[0], rect[2]])

        segmentsByX.sort(key=functools.cmp_to_key(sortSegmentFirst))

        left = segmentsByX[0]
        if left[0] > innerBound[0]:
            result.append([innerBound[0], innerBound[1], left[0], bottom])

        for i in range(1, len(segmentsByX)):
            toLeft = segmentsByX[i - 1]
            toRight = segmentsByX[i]
            if toRight[0] > toLeft[1]:
                result.append([toLeft[1], innerBound[1], toRight[0], bottom])

        segmentsByX.sort(key=functools.cmp_to_key(sortSegmentSecond))

        right = segmentsByX[len(segmentsByX) - 1]
        if right[1] < innerBound[2]:
            result.append([right[1], innerBound[1], innerBound[2], bottom])

        removeList = []
        for rect in topList:
            if rect[3] - bottom <= 0:
                removeList.append(rect)
            else:
                rect[1] = bottom

        for rect in removeList:
            excludeByTop.remove(rect)

        outBound = innerBound.copy()
        outBound[1] = bottom

    print("size = {}".format(len(result)))
    result.sort(key=functools.cmp_to_key(sortRect))
    for rect in result:
        print("cutRectByExcludingRegions: {}".format(rect))
    return result


def sortRectLeft(rect1, rect2):

    p1x = rect1[0]
    p1y = rect1[1]
    p1r = rect1[2]  # p1's right side
    p1b = rect1[3]  # p1's bottom
    p2x = rect2[0]
    p2y = rect2[1]
    p2r = rect2[2]
    p2b = rect2[3]

    return p1x - p2x

def sortRectRight(rect1, rect2):

    p1x = rect1[0]
    p1y = rect1[1]
    p1r = rect1[2]  # p1's right side
    p1b = rect1[3]  # p1's bottom
    p2x = rect2[0]
    p2y = rect2[1]
    p2r = rect2[2]
    p2b = rect2[3]

    return p1r - p2r


def sortRectTop(rect1, rect2):

    p1x = rect1[0]
    p1y = rect1[1]
    p1r = rect1[2]  # p1's right side
    p1b = rect1[3]  # p1's bottom
    p2x = rect2[0]
    p2y = rect2[1]
    p2r = rect2[2]
    p2b = rect2[3]

    return p1y - p2y


def sortRectBottom(rect1, rect2):

    p1x = rect1[0]
    p1y = rect1[1]
    p1r = rect1[2]  # p1's right side
    p1b = rect1[3]  # p1's bottom
    p2x = rect2[0]
    p2y = rect2[1]
    p2r = rect2[2]
    p2b = rect2[3]

    return p1b - p2b


def sortSegmentFirst(map1, map2):
    return map1[0] - map2[0]


def sortSegmentSecond(map1, map2):
    return map1[1] - map2[1]

