# import itertools
import re

import ocr
import pdfutils
from logger import logger
from document_analyzer import DocumentAnalyzer

infile = 'MagicTheGathering_IsTuringComplete.pdf'


# PATH_WORDS_THRESHOLD = 5
# DISTANCE_THRESHOLD = width * 0.25


if __name__ == '__main__':
    c = 0

    analyzer = DocumentAnalyzer(infile)

    phrase = 'Magic The Gathering'
    for result in analyzer.search(phrase):
        print(result['page_number'], result['distance'], [word.text for word in result['path']])

    phrase = 'Super Smash Bros Melee'
    for result in analyzer.search(phrase):
        print(result['page_number'], result['distance'], [word.text for word in result['path']])

    anchor = 'Super'
    neighbors = ['smash', 'bros', 'melee']
    for result in analyzer.search(phrase, neighbors):
        print(result['page_number'], result['distance'], [word.text for word in result['path']])

    #print([token for token in datasource.getTokensByPattern(r'\b(?:([Ss]u)|([Mm]a))\w*')])