import numpy as np
import cv2 as cv

from matplotlib import pyplot as plt
import numpy as np
import onyx_img_utils

# file = 'C:\onyx\github\python\kumiko\comic-raw\dark_bg_2.png'
file = 'C:\onyx\github\python\kumiko\comic\longzhu (54).png'

# img = cv.imread(file, 0)
# img = cv.imread(file)

# cv -> matplotlib : BGR -> RGB
# b,g,r = cv.split(img)
# img = cv.merge([r,g,b])


# onyx_img_utils.cvShowWait(img)

# kernel = np.ones((5,5),np.uint8)
# edges = cv.erode(img,kernel,iterations = 1)
# edges = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
# edges = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)
# edges = cv.morphologyEx(img, cv.MORPH_GRADIENT, kernel)
# onyx_img_utils.cvShowWait(edges)

# img = cv.Canny(img, 100, 200)
# onyx_img_utils.cvShowWait(img)
# contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

# img = cv.bilateralFilter(img,9,75,75)
# onyx_img_utils.cvShowWait(img)
# img = cv.blur(img, (2, 2))
# onyx_img_utils.cvShowWait(img)

# ret, binary = cv.threshold(img, 70, 255, cv.THRESH_BINARY)
# onyx_img_utils.cvShowWait(binary)
# rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (7, 7))
# cv.dilate(binary, rect_kernel, iterations=1)
# onyx_img_utils.cvShowWait(binary)
# contours, hierarchy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
# filterContours = onyx_img_utils.filterSmallContour(contours, binary)
# filterContours = contours

# imgColor = onyx_img_utils.cvImRead(file)
# cv.drawContours(imgColor, contours, -1, (0,0,255),3)
# blockRectList = onyx_img_utils.cvRectangleWithCombineIntersect(filterContours, imgColor)
# blockRectList = onyx_img_utils.cvRectangle(filterContours, imgColor)
# onyx_img_utils.cvShowWait(imgColor)

# plt.subplot(221), plt.imshow(img, cmap='gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(222), plt.imshow(edges, cmap='gray')
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(223), plt.imshow(binary)
# plt.title('binary Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(224), plt.imshow(imgColor)
# plt.title('contours Image'), plt.xticks([]), plt.yticks([])
# plt.show()

# gray = img
# edges = cv.Canny(gray,50,150,apertureSize = 3)
# lines = cv.HoughLines(edges,1,np.pi/180,200)
# for line in lines:
#     rho,theta = line[0]
#     a = np.cos(theta)
#     b = np.sin(theta)
#     x0 = a*rho
#     y0 = b*rho
#     x1 = int(x0 + 1000*(-b))
#     y1 = int(y0 + 1000*(a))
#     x2 = int(x0 - 1000*(-b))
#     y2 = int(y0 - 1000*(a))
#     cv.line(img,(x1,y1),(x2,y2),(0,0,255),2)
# onyx_img_utils.cvShowWait(img)


# 分水岭算法
# file = 'C:\onyx\github\python\kumiko\comic-raw\dark.jpg'
# img = cv.imread(file)
# gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
# ret, thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
# onyx_img_utils.cvShowWait(thresh)
#
# # 噪声去除
# kernel = np.ones((3,3),np.uint8)
# opening = cv.morphologyEx(thresh,cv.MORPH_OPEN,kernel, iterations = 2)
# onyx_img_utils.cvShowWait(opening)
#
# # 确定背景区域
# sure_bg = cv.dilate(opening,kernel,iterations=3)
# onyx_img_utils.cvShowWait(sure_bg)
#
# # 寻找前景区域
# dist_transform = cv.distanceTransform(opening,cv.DIST_L2,5)
# onyx_img_utils.cvShowWait(dist_transform)
# ret, sure_fg = cv.threshold(dist_transform,0.7*dist_transform.max(),255,0)
# onyx_img_utils.cvShowWait(sure_fg)
#
# # 找到未知区域
# sure_fg = np.uint8(sure_fg)
# unknown = cv.subtract(sure_bg,sure_fg)
# onyx_img_utils.cvShowWait(unknown)
#
# # 类别标记
# ret, markers = cv.connectedComponents(sure_fg)
# onyx_img_utils.cvShowWait(sure_fg)
# # 为所有的标记加1，保证背景是0而不是1
# markers = markers+1
# # 现在让所有的未知区域为0
# markers[unknown==255] = 0
# onyx_img_utils.cvShowWait(sure_fg)
#
# markers = cv.watershed(img,markers)
# img[markers == -1] = [0,0,255]
#
# onyx_img_utils.cvShowWait(img)


# 图像梯度
# file = 'C:\onyx\github\python\kumiko\comic-raw\dark_bg_2.png'
#
# img = cv.imread(file,0)
# laplacian = cv.Laplacian(img,cv.CV_64F)
# sobelx = cv.Sobel(img,cv.CV_64F,1,0,ksize=5)
# sobely = cv.Sobel(img,cv.CV_64F,0,1,ksize=5)
# plt.subplot(2,2,1),plt.imshow(img,cmap = 'gray')
# plt.title('Original'), plt.xticks([]), plt.yticks([])
# plt.subplot(2,2,2),plt.imshow(laplacian,cmap = 'gray')
# plt.title('Laplacian'), plt.xticks([]), plt.yticks([])
# plt.subplot(2,2,3),plt.imshow(sobelx,cmap = 'gray')
# plt.title('Sobel X'), plt.xticks([]), plt.yticks([])
# plt.subplot(2,2,4),plt.imshow(sobely,cmap = 'gray')
# plt.title('Sobel Y'), plt.xticks([]), plt.yticks([])
# plt.show()


# canny边缘检测
# file = 'C:\onyx\github\python\kumiko\comic-raw\dark_bg_2.png'
# img = cv.imread(file,0)
# edges = cv.Canny(img,100,200)
# plt.subplot(121),plt.imshow(img,cmap = 'gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(edges,cmap = 'gray')
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
# plt.show()

