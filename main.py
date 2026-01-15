# import itertools
import re

import ocr
import pdfutils
from logger import logger
from document_analyzer import DocumentAnalyzer


# infile = 'MagicTheGathering_IsTuringComplete.pdf'
infile = 'test_invoice.png'

# PATH_WORDS_THRESHOLD = 5
# DISTANCE_THRESHOLD = width * 0.25


if __name__ == '__main__':

    infile = 'test_invoice.png'
    analyzer = DocumentAnalyzer(infile)
    page = analyzer.pages[0]


    print(page.search('sub total'))


    for path in page.search('sub total'):
        start = path[0][0]
        ends = [end for end in page.getTokensByPattern(r"^[-+]?\d+$")]
        paths = [item for item in page.search(start, ends)]
        paths = sorted(paths, key=lambda path: path[1])
        for path in paths:
            if 3 == len(path[0]):
                print([item.raw for item in path[0]])
                print([item.centroid for item in path[0]])

    for path in page.search('shipping charges'):
        start = path[0][0]
        ends = [end for end in page.getTokensByPattern(r"^[-+]?\d+$")]
        paths = [item for item in page.search(start, ends)]
        paths = sorted(paths, key=lambda path: path[1])
        for path in paths:
            if 3 == len(path[0]):
                print([item.raw for item in path[0]])
                print([item.centroid for item in path[0]])

    for path in page.search('insurance'):
        start = path[0][-1]
        ends = [end for end in page.getTokensByPattern(r"^[-+]?\d+$")]
        paths = [item for item in page.search(start, ends)]
        paths = sorted(paths, key=lambda path: path[1])
        print([item.raw for item in paths[0][0]])

    for path in page.search('vat'):
        start = path[0][-1]
        ends = [end for end in page.getTokensByPattern(r"^[-+]?\d+$")]
        paths = [item for item in page.search(start, ends)]
        paths = sorted(paths, key=lambda path: path[1])
        print([item.raw for item in paths[0][0]])

    # for end in page.getTokensByPattern(r"^[-+]?\d+$"):
    #     print(end.raw)




    # infile = 'MagicTheGathering_IsTuringComplete.pdf'

    # analyzer = DocumentAnalyzer(infile)

    # phrase = 'Magic The Gathering'
    # for result in analyzer.search(phrase):
    #     print(result['page_number'], result['distance'], [word.text for word in result['path']])

    # phrase = 'Super Smash Bros Melee'
    # for result in analyzer.search(phrase):
    #     print(result['page_number'], result['distance'], [word.text for word in result['path']])

    # anchor = 'Super'
    # neighbors = ['smash', 'bros', 'melee']
    # for result in analyzer.search(phrase, neighbors):
    #     print(result['page_number'], result['distance'], [word.text for word in result['path']])

    # #print([token for token in analyzer.getTokensByPattern(r'\b(?:([Ss]u)|([Mm]a))\w*')])