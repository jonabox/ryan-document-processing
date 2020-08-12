
import cv2
import json
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from checkbox import square_detection, circle_detection


# convert one pdf into one image per page
def pdf_to_image(pdf_path):
	images = convert_from_path(pdf_path)
	paths = []
	for i in range(len(images)):
		images[i].save(str(i) + '.jpg', 'JPEG')
		paths.append(str(i) + '.jpg')
	return paths


# scale image by factor
def scale_image(im, factor):
	return cv2.resize(im, (int(im.shape[1] * factor), int(im.shape[0] * factor)), interpolation = cv2.INTER_AREA)


# correct skewed images, UNUSED
def deskew(image):
	gray = cv2.bitwise_not(image)
	coords = np.column_stack(np.where(gray > 0))
	angle = cv2.minAreaRect(coords)[-1]
	if angle < -45:
		angle = -(90 + angle)
	else:
		angle = -angle
	print(angle)
	(h, w) = image.shape[:2]
	center = (w // 2, h // 2)
	M = cv2.getRotationMatrix2D(center, angle, 1.0)
	rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
	cv2.putText(rotated, "Angle: {:.2f} degrees".format(angle),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	return rotated


# threshold image to be black and white
def thresholding(image):
	return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# scan image using template and read everything
def template_scan(images, all_rois, factors):
	texts = []
	for i in range(len(images)):
		page = all_rois[i]
		p = {'text': [], 'checkbox': [], 'signature': []}

		# read text
		for box in page['text']:
			crop = images[i][int(box[1]/factors[i]) : int((box[1]+box[3])/factors[i]), int(box[0]/factors[i]) : int((box[0]+box[2])/factors[i])]
			### for demo
			cv2.imshow('crop', crop)
			cv2.waitKey(0)
			###
			t = pytesseract.image_to_string(crop, lang="eng")
			print(t)
			p['text'].append(t)

		# find checked boxes
		for box in page['checkbox']:
			crop = images[i][int(box[1]/factors[i]) : int((box[1]+box[3])/factors[i]), int(box[0]/factors[i]) : int((box[0]+box[2])/factors[i])]
			### for demo
			cv2.imshow('crop', crop)
			cv2.waitKey(0)
			###
			try: # square/rectangle checkbox
				checkbox_dicts = square_detection(crop)
			except: # circle checkbox
				checkbox_dicts = circle_detection(crop)
			checkbox_num = 0 # 0 if no boxes are checked
			for checkbox in checkbox_dicts:
				if checkbox['percent_filled'] > 0.05:
					if checkbox_num == 0: # number if one box is checked
						checkbox_num = checkbox['number']
					else: # None if more than one box is checked
						checkbox_num = None
			print(checkbox_num)
			p['checkbox'].append(checkbox_num)

		# check if a signature exists
		for box in page['signature']:
			crop = images[i][int(box[1]/factors[i]) : int((box[1]+box[3])/factors[i]), int(box[0]/factors[i]) : int((box[0]+box[2])/factors[i])]
			### for demo
			cv2.imshow('crop', crop)
			cv2.waitKey(0)
			###
			if len(np.where(crop == 0)[0]) < 20: # 20 is a random low enough number of pixels
				p['signature'].append(False)
			else:
				p['signature'].append(True)

		texts.append(p)
	return texts


def main(region, pdf_path):
	# load template
	with open('test.json') as json_file:
		temps = json.load(json_file)
	if region not in temps:
		print('no template on record for ' + region)
		return

	# read pdf using template for given region
	im_paths = pdf_to_image(pdf_path)
	images = []
	factors = []
	for path in im_paths:
		im = cv2.imread(path, 0) # load image in grayscale
		thresh = thresholding(im) # convert to black and white
		images.append(thresh)
		factors.append(700/im.shape[0]) # conversion factors
	texts = template_scan(images, temps[region], factors)
	print(texts)


if __name__ == "__main__":
	region = input("Enter region: ")
	# path = input('Enter path to pdf: ')
	# path = './Certificates_summer/VCTRRESALE_06112020_3de18717-47c0-4363-bdc8-371798cd2ad3.pdf'
	path = './Certificates_summer/VAZRRESALE_06112020_5dc53cdc-7734-4824-8ad2-ede9c1c93504.pdf'
	# path = './Certificates_summer/VALECERTEXEMPTEX1.PDF_06112020_3c54347a-dd95-40b4-9934-c314b25f0730.pdf'
	# path = './Certificates_spring/TX -Resale -Valid -Handwritten.pdf'
	main(region, path)

