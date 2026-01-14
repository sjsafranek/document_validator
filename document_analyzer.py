import concurrent.futures

import pdfutils
import imageutils
from logger import logger
from page_analyzer import PageAnalyzer


class DocumentAnalyzer(object):
    
    def __init__(self, infile):
        self.infile = infile

        if infile.endswith('.pdf'):
            images = [image for image in pdfutils.readPdfPagesAsArray(infile)]
            self.pages = [page for page in _processPages(images)]
        else:
            image = imageutils.read(infile)
            self.pages = [_processPages(image)]


    def search(self, *args, **kwargs):
        n = len(self.pages)
        for i in range(n):
            page = self.pages[i]
            for path, distance in page.search(*args, **kwargs):
                yield {
                    'page_number': i + 1,
                    'path': path,
                    'distance': distance
                }


def _processPage(image):
    logger.debug('building page page analyzer')
    return PageAnalyzer(image)


def _processPages(images):
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        for page in executor.map(_processPage, images):
            # print(page.shape)
            yield page
