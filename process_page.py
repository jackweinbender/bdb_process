#! /usr/local/bin/python3

import sys
import cv2
import numpy as np
import glob, os

def main(args):
	current_dir = sys.path[0]

	for file in glob.glob(f"{args[1]}/*.ppm"):
		page_num = get_page_num(file)
		filename = file.split("/")[-1]
		print(f'Page: {page_num}')
		head, page, col_a, col_b, original = process(file)

		if head == []:
			os.makedirs("_OUTPUT/_PROBLEMS", exist_ok=True)
			os.rename(file, f"_OUTPUT/_PROBLEMS/{filename}")
			continue

		## Write-out Files
		current = f"{current_dir}/_pages/page_{page_num}"
		os.makedirs(current, exist_ok=True)

		cv2.imwrite(f"{current}/{page_num}_original.png", original)
		cv2.imwrite(f"{current}/{page_num}_head.png", head)
		cv2.imwrite(f"{current}/{page_num}_page.png", page)
		cv2.imwrite(f"{current}/{page_num}_col_a.png", col_a)
		cv2.imwrite(f"{current}/{page_num}_col_b.png", col_b)

		complete = "_OUTPUT/complete"
		os.makedirs(complete, exist_ok=True)
		os.rename(file, f"{complete}/{filename}")

def process(file):
	img = cv2.imread(file, 0)

	## Threshold and Box-filter for noise
	data = remove_noise(img)
	# Deskew
	data, result = deskew(data, img)
	# Crop
	data, cropped = crop(data, result)

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
	header = cropped[0:headline,:]
	page = cropped[pageline:,:]
	
	col_a, col_b = split_cols(page, file)
	if col_a == [] or col_b == []:
		return ([], [], [], [], [])

	return (header, page, col_a, col_b, cropped)


def split_cols(page, file):
	data = remove_noise(page)

	x_sum = np.mean(data, axis=0)

	Y,X = data.shape[:2]
	xth = 10

	

	end_cols = [x for x in range(X-1) if x_sum[x]<=xth and x_sum[x-1]>xth and x > 420 and x < 460]
	start_cols = [x for x in range(X-1) if x_sum[x]<=xth and x_sum[x+1]>xth and x > 440 and x < 480]

	print(end_cols, start_cols)

	if len(end_cols) < 1 or len(start_cols) < 1:
		return ([], [])

	end_col_l = end_cols[0]
	start_col_r = start_cols[0]

	# Do REAL Image Manipulations
	col_a = page[:,0:end_col_l]
	col_b = page[:,start_col_r:]

	# cv2.imshow("DATA", data)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

	if len(col_a[0]) < 10:
		raise Exception(f"Col A")
	elif len(col_b[0]) < 10:
		raise Exception(f"Col B")
	else:
		return (col_a, col_b)

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