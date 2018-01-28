#! /bin/python3
import sys
import cv2
import numpy as np
import glob, os

def process(file):
	print(file)
	img = cv2.imread(file, 0)

	## Threshold and Box-filter for noise
	data = cv2.medianBlur(img, 9)
	th, data = cv2.threshold(data, 55, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)
	data = cv2.boxFilter(data, -1, (30,30))
	th, data = cv2.threshold(data, 25, 255, cv2.THRESH_BINARY)

	# ## SHOW DENOISED
	# cv2.imshow("Denoised", data)
	# cv2.imshow("Original", img)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

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
	
	## Find MinRectArea for Cropping
	pts = cv2.findNonZero(data)
	ret = cv2.minAreaRect(pts)
	box = cv2.boxPoints(ret)


	## Crop by slicing
	start_x = int(box[0,0])
	end_x = int(box[2,0])

	start_y = int(box[1,1])
	end_y = int(box[0,1])

	result = result[start_y:end_y, start_x:end_x]
	data = data[start_y:end_y, start_x:end_x]

	# # # SHOW CROPPED
	# cv2.imshow("Cropped", result)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

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
	bodyline = upper_bounds[0]

	# Do DAtA Image Manipulations
	data_header = data[0:headline,:]

	# Do REAL Image Manipulations
	header = result[0:headline,:]
	body = result[bodyline:,:]

	# cv2.imshow("DATA", data)
	# cv2.imshow("HEAD", header)
	# cv2.imshow("BODY", body)

	cv2.waitKey(0)
	cv2.destroyAllWindows()

	page_num = file.split("-")
	page_num = page_num[1].split(".")[0]
	
	cv2.imwrite(f"../image_processing/_headers/{page_num}_header.png", header)
	cv2.imwrite(f"../image_processing/_pages/{page_num}.png", body)


os.chdir("test_pages")
for file in glob.glob("*.ppm"):
	process(file)