import numpy as np
import cv2

im = cv2.imread('lamp.jpg')
hsv_img = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

#Red threshold
red = np.uint8([[[0,0,255]]])
red_hsv= cv2.cvtColor(red, cv2.COLOR_BGR2HSV)
lower_red_hsv = np.array([[[np.subtract(red_hsv[0,0,0],100),100,100]]])
upper_red_hsv = np.array([[[np.add(red_hsv[0,0,0],100),255,255]]])
imgray_r = cv2.inRange(hsv_img, lower_red_hsv, upper_red_hsv)
ret,thresh_r = cv2.threshold(imgray_r,127,255,cv2.THRESH_BINARY)

#Green threshold
green = np.uint8([[[0,255,0]]])
green_hsv= cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
lower_green_hsv = np.array([[[np.subtract(green_hsv[0,0,0],100),100,100]]])
upper_green_hsv = np.array([[[np.add(green_hsv[0,0,0],100),255,255]]])
imgray_g = cv2.inRange(hsv_img, lower_green_hsv, upper_green_hsv)
ret,thresh_g = cv2.threshold(imgray_g,127,255,cv2.THRESH_BINARY)

#Blue threshold
blue = np.uint8([[[255,0,0]]])
blue_hsv= cv2.cvtColor(blue, cv2.COLOR_BGR2HSV)
lower_blue_hsv = np.array([[[np.subtract(blue_hsv[0,0,0],100),100,100]]])
upper_blue_hsv = np.array([[[np.add(blue_hsv[0,0,0],100),255,255]]])
frame_threshed = cv2.inRange(hsv_img, lower_blue_hsv, upper_blue_hsv)
imgray_b = frame_threshed
ret,thresh_b = cv2.threshold(imgray_b,127,255,cv2.THRESH_BINARY)

#Original threshold
imgray_hsv = cv2.cvtColor(hsv_img, cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray_hsv,127,255,cv2.THRESH_BINARY)

#Subtracting thresholds
thresh_subtracted = cv2.subtract(thresh,thresh_b, thresh_r, thresh_g)
#thresh_subtracted = thresh - thresh_b - thresh_r - thresh_g

#Adding thresholds
thresh_added = cv2.add(thresh,thresh_b, thresh_r, thresh_g)
#thresh_added = thresh + thresh_b + thresh_r + thresh_g

#Defining contours and setting bounding box
_, contours, hierarchy = cv2.findContours(thresh_added,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
areas = [cv2.contourArea(c) for c in contours]
max_index = np.argmax(areas)
cnt=contours[max_index]
x,y,w,h = cv2.boundingRect(cnt)
cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2) 

#Show images in windows       
cv2.imshow("Show",im)
cv2.imshow("Show gray scale", imgray_hsv)
cv2.imshow("Show HSV", hsv_img)
cv2.imshow("Show thresh", thresh)
cv2.imshow('red thresh', thresh_r)
cv2.imshow('green thresh', thresh_g)
cv2.imshow('blue thresh', thresh_b)
cv2.imshow("Show subtracted thresh", thresh_subtracted)
cv2.imshow("Show added thresh", thresh_added)
cv2.waitKey()
cv2.destroyAllWindows()