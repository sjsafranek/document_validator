# import itertools
import re

import cv2

import ocr
import pdfutils
from logger import logger
from datasource import Datasource

infile = 'MagicTheGathering_IsTuringComplete.pdf'


# PATH_WORDS_THRESHOLD = 5
# DISTANCE_THRESHOLD = width * 0.25


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



if __name__ == '__main__':    
    for image in pdfutils.readPdfPagesAsArray(infile):
        logger.debug('reading page')
        data = ocr.read(image)
    
        logger.debug('building datasource')
        datasource = Datasource(data)
    
        logger.debug('finding path')
        path, distance = datasource.search(start="super", end="melee")
        print(distance, [word.text for word in path])
        
        phrase = 'Magic The Gathering'
        for path, distance in datasource.search(phrase):
            print(distance, [word.text for word in path])

        phrase = 'Super Smash Bros Melee'
        for path, distance in datasource.search(phrase):
            print(distance, [word.text for word in path])            

        print([token for token in datasource.getTokensByPattern(r'\b(?:([Ss]u)|([Mm]a))\w*')])

        break
