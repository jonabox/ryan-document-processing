
import cv2
import json
from json import JSONEncoder
from main import pdf_to_image, scale_image
import numpy


# for saving nested arrays into a json file
class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


# manually draw boxes for template
def draw_boxes(images):
    all_rois = []
    for im in images:
        rois = {}
        for roi_type in ['text', 'checkbox', 'signature']:
            print(roi_type)
            rois[roi_type] = cv2.selectROIs("Image", im, False, False)
        all_rois.append(rois)
    return all_rois


def main(region, pdf_path):
    # create template
    im_paths = pdf_to_image(pdf_path)
    images = []
    scaled_images = []
    for path in im_paths:
        im = cv2.imread(path, 0)
        images.append(im)
        factor = 700/im.shape[0] #540 by 700 seems to work well for my screen
        scaled_images.append(scale_image(im, factor))
    all_rois = draw_boxes(scaled_images)

    # save to json file
    try:
        with open('test.json') as json_file:
            temps = json.load(json_file)
    except: # either json file doesn't exist yet, or it's empty
        temps = {}
    with open("test.json", "w") as outfile:
        temps[region] = all_rois
        json.dump(temps, outfile, cls=NumpyArrayEncoder)
    print("template successfully created for " + region)


if __name__ == "__main__":
    region = input("Enter region: ")
    # path = input('Enter path to pdf: ')
    path = './Certificates_summer/VAZRRESALE_06112020_5dc53cdc-7734-4824-8ad2-ede9c1c93504.pdf'
    # path = './Certificates_summer/VCTRRESALE_06112020_3de18717-47c0-4363-bdc8-371798cd2ad3.pdf'
    main(region, path)
