import cv2 as cv
import numpy as np
import argparse

def detect_pieces_live(cap):
    ret, frame = cap.read()
    detected = frame.copy()

    # frame = adjust_gamma(frame, gamma=0.7)

    # cv.normalize(frame, frame, 0, 255, cv.NORM_MINMAX)
    # Load frame, grayscale, median blur, Otsus threshold
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5,5), 0)
    blur = cv.medianBlur(blur, 5)
    # thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]
    # ret, thresh = cv.threshold(blur,100,255,cv.THRESH_BINARY)
    thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
        cv.THRESH_BINARY, 3, 2.6)

    # Morph open 
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9,9))
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=3)

    # Find contours and filter using contour area and aspect ratio
    cnts = cv.findContours(opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.04 * peri, True)
        area = cv.contourArea(c)
        if len(approx) > 5 and area > 800 and area < 1800:
            ((x, y), r) = cv.minEnclosingCircle(c)
            cv.circle(detected, (int(x), int(y)), int(r), (0, 0, 255), 2)

    # cv.imshow('thresh', thresh)
    cv.imshow('detected', detected)
    # cv.imshow('original', frame)

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv.LUT(image, table)