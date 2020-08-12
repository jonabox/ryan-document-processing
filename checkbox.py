
import cv2
import math
import numpy as np


# Check if approx is inside a larger checkbox
def find_inner_checkbox(checkboxes, approx, thold=2):
    for i in range(len(checkboxes) - 1, -1, -1):
        box_X, box_Y = split_X_Y(checkboxes[i])
        box_avg = (np.average([max(box_X), min(box_X)]), np.average([max(box_Y), min(box_Y)]))
        box_area = (max(box_X) - min(box_X)) * (max(box_Y) - min(box_Y))

        approx_X, approx_Y = split_X_Y(approx.ravel())
        approx_avg = (np.average([max(approx_X), min(approx_X)]), np.average([max(approx_Y), min(approx_Y)]))
        approx_area = (max(approx_X) - min(approx_X)) * (max(approx_Y) - min(approx_Y))

        # if centers of boxes are within the threshold, delete the larger box
        if abs(box_avg[0] - approx_avg[0]) <= thold and abs(box_avg[1] - approx_avg[1]) <= thold:
            if approx_area < box_area:
                del checkboxes[i]
                return True
            else:
                return False
    return True


# Split the X and Y pixel coordinates from the checkbox
def split_X_Y(box):
    x = [box[i] for i in range(len(box)) if i%2 == 0]
    y = [box[i] for i in range(len(box)) if i%2 == 1]
    return x, y


# Find the minimum dimensions of the checkboxes
def minimum_box_dimensions(checkboxes):
    min_height = None
    min_width = None
    for box in checkboxes:
        x, y = split_X_Y(box)
        h = max(y) - min(y)
        w = max(x) - min(x)
        if not min_height or h < min_height:
            min_height = h
        if not min_width or w < min_width:
            min_width = w
    return int(min_height), int(min_width)


# Detect square checkboxes
#   ratio - increase for more detection outside of box
#   delta - increase for more rectangular boxes
def square_detection(im, ratio=0.03, delta=13, side_length_range=(17,42), plot=False):
    # find checkboxes in image
    output = im.copy()
    checkboxes = []
    contours = cv2.findContours(im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, ratio*cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            X, Y = split_X_Y(approx.ravel())
            width = max(X) - min(X)
            height = max(Y) - min(Y)
            # check if polygon is correct dimensions to be a checkbox
            if abs(height - width) < delta and side_length_range[0] < width < side_length_range[1] and side_length_range[0] < height < side_length_range[1]:
                if not checkboxes or find_inner_checkbox(checkboxes, approx):
                    checkboxes.append(list(approx.ravel()))

    # create dicts for checkboxes sorted in descending order
    checkbox_dicts = []
    for i in range(len(checkboxes)-1, -1, -1):
        new_dic = {}
        new_dic['number'] = len(checkboxes)-i
        new_dic['coordinates'] = checkboxes[i]
        checkbox_dicts.append(new_dic)

    # find percent filled
    min_height, min_width = minimum_box_dimensions(checkboxes)
    w = int(min_width / 2)
    h = int(min_height / 2)
    total = 2 * w * 2 * h
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    for box in checkboxes:
        count = 0
        x, y = split_X_Y(box)
        x_range = (min(x), max(x))
        y_range = (min(y), max(y))
        center = (int((x_range[0] + x_range[1]) / 2), int((y_range[0] + y_range[1]) / 2))
        for i in range(center[0] - w, center[0] + w):
            for j in range(center[1] - h, center[1] + h):
                # fill in area if white - used for debugging
                if im[j][i] > 200:
                    output[j][i] = 100
                # if pixel is black, add to count
                if im[j][i] < 5:
                    count += 1
        percent = round(count / total, 2)
        for dic in checkbox_dicts:
            if dic['coordinates'] == box:
                dic['percent_filled'] = percent
        if plot: # for debugging purposes
            txt = str(percent)
            cv2.putText(output, txt, (center[0] - 15, center[1] + 5), font, 1, (0, 0, 255))
    
    if plot:
        cv2.imshow('output', output)
        cv2.waitKey(0)
    
    return checkbox_dicts


# List of indices within the given circle parameters
def circle_coverage(x, y, r):
    indices = []
    for i in range(x-r, x+r):
        for j in range(y-r, y+r):
            dx = x-i
            dy = y-j
            dist = math.sqrt((dx ** 2) + (dy** 2))
            if dist <= r:
                indices.append((i,j))
    return indices


# Detect circle checkboxes
#   dp - increase to find more circles
def circle_detection(im, dp=2, minDist=20, param1=100, param2=50, minRadius=15, maxRadius=30, plot=False):
    # find checkboxes in image
    output = im.copy()
    circles = cv2.HoughCircles(im, cv2.HOUGH_GRADIENT, dp, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    detected_circles = np.uint16(np.around(circles))

    # create dicts for checkboxes sorted by increasing centers
    checkbox_dicts = []
    for i in range(len(detected_circles[0, :])-1, -1, -1):
        new_dic = {}
        (x,y,r) = detected_circles[0, :][i]
        new_dic['center'] = (x,y)
        new_dic['radius'] = r
        checkbox_dicts.append(new_dic)
    checkbox_dicts = sorted(checkbox_dicts, key = lambda i:i['center'])
    for i in range(len(checkbox_dicts)):
        checkbox_dicts[i]['number'] = i+1

    # find percent filled
    radii = []
    for (x,y,r) in detected_circles[0, :]:
        radii.append(r)
    min_r = min(radii)
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    for (x, y, r) in detected_circles[0, :]:
        count = 0
        circle_coords = circle_coverage(x, y, min_r-int(min_r/4))
        for (i,j) in circle_coords:
            # fill in area if white - used for debugging
            if im[j][i] > 200:
                output[j][i] = 100
            # if pixel is black, add to count
            if im[j][i] < 5:
                count += 1
        total = len(circle_coords)
        percent = round(count / total, 2)
        for dic in checkbox_dicts:
            if dic['center'] == (x,y):
                dic['percent_filled'] = percent
        if plot: # for debugging purposes
            txt = str(percent)
            cv2.putText(output, txt, (x-70, y), font, 1, (0, 0, 255))

    if plot:
        cv2.imshow('output',output)
        cv2.waitKey(0)

    return checkbox_dicts

