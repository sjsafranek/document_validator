import cv2

import lib


infile = 'MagicTheGathering_IsTuringComplete.pdf'



def display(image, data):
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        text = data['text'][i]
        confidence = data['conf'][i]
        if not text:
            continue
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
    cv2.imshow('img', image)
    cv2.waitKey(0)



for image in lib.readPdfPages(infile):
    data = lib.parseImage(image)
    display(image, data)
    break
