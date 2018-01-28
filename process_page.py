#! /usr/local/bin/python3

import sys
import cv2
import numpy as np
import glob, os

def main(args):
	os.chdir(args[1])
	os.makedirs("_headers", exist_ok=True)
	os.makedirs("_pages", exist_ok=True)
	for file in glob.glob("*.ppm"):
		process(file)

def process(file):
	print(f"---------------------------------------")
	print(f"Processing file: {file}")
	img = cv2.imread(file, 0)

	## Threshold and Box-filter for noise
	data = remove_noise(img)
	# Deskew
	data, result = deskew(data, img)
	# Crop
	data, result = crop(data, result)

	# Dilation vertical
	kernel = np.zeros((3,3), dtype=np.uint8)
	kernel[:,2] = 1
	data = cv2.dilate(data, kernel, iterations=2)
	# Dilation Horizontal
	kernel = np.zeros((5,5), dtype=np.uint8)
	kernel[2,:] = 1
	data = cv2.dilate(data, kernel, iterations=3)

	y_sum = np.mean(data, axis=1)

	Y,X = data.shape[:2]
	yth = 0

	lower_bounds = [y for y in range(Y-1) if y_sum[y]<=yth and y_sum[y-1]>yth]
	upper_bounds = [y for y in range(Y-1) if y_sum[y]<=yth and y_sum[y+1]>yth]

	headline = lower_bounds[0]
	pageline = upper_bounds[0]

	# Do REAL Image Manipulations
	header = result[0:headline,:]
	page = result[pageline:,:]

	write_header(file, header)

	col_a, col_b = split_cols(page)
	write_cols(file, (col_a, col_b))

def split_cols(page):
	data = remove_noise(page)

	x_sum = np.mean(data, axis=0)

	Y,X = data.shape[:2]
	xth = 10

	end_cols = [x for x in range(X-1) if x_sum[x]<=xth and x_sum[x-1]>xth]
	start_cols = [x for x in range(X-1) if x_sum[x]<=xth and x_sum[x+1]>xth]

	end_col_l = end_cols[0]
	start_col_r = start_cols[0]

	# Do REAL Image Manipulations
	col_a = page[:,0:end_col_l]
	col_b = page[:,start_col_r:]

	return (col_a, col_b)

def write_cols(file, cols):
	page_num = get_page_num(file)
	col_a, col_b = cols
	cv2.imwrite(f"_pages/page_{page_num}a.png", col_a)
	cv2.imwrite(f"_pages/page_{page_num}b.png", col_b)

def write_header(file, header):
	page_num = get_page_num(file)
	cv2.imwrite(f"_headers/header_{page_num}.png", header)

def get_page_num(file):
	return file.split("-")[1].split(".")[0]

def remove_noise(data):
	data = cv2.medianBlur(data, 9)
	th, data = cv2.threshold(data, 55, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)
	data = cv2.boxFilter(data, -1, (30,30))
	th, data = cv2.threshold(data, 25, 255, cv2.THRESH_BINARY)
	return data

def deskew(data, img):
	## Find MinArea for Rotation
	pts = cv2.findNonZero(data)
	ret = cv2.minAreaRect(pts)

	(cx,cy), (w,h), ang = ret
	if w>h:
		w,h = h,w
		ang += 90

	## Find Matrix and do Rotation
	M = cv2.getRotationMatrix2D((cx,cy), ang, 1.0)
	data = cv2.warpAffine(data, M, (img.shape[1], img.shape[0]))
	result = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
	return (data, result)

def crop(data, img):
	## Find MinRectArea for Cropping
	pts = cv2.findNonZero(data)
	ret = cv2.minAreaRect(pts)
	box = cv2.boxPoints(ret)


	## Crop by slicing
	start_x = int(box[0,0])
	end_x = int(box[2,0])

	start_y = int(box[1,1])
	end_y = int(box[0,1])

	img = img[start_y:end_y, start_x:end_x]
	data = data[start_y:end_y, start_x:end_x]
	return (data, img)

main(sys.argv)