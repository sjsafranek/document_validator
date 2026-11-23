import logging
import concurrent.futures

from models import SearchResult
import pdfutils
import imageutils
from page_analyzer import PageAnalyzer


logger = logging.getLogger(__name__)


class DocumentAnalyzer(object):
    
    def __init__(self, infile):
        self.infile = infile

        if infile.endswith('.pdf'):
            images = [image for image in pdfutils.readPdfPagesAsArray(infile)]
            self.pages = [page for page in _processPages(images)]
        else:
            image = imageutils.read(infile)
            self.pages = [PageAnalyzer(image)]

    def search(self, *args, **kwargs):
        n = len(self.pages)
        for i in range(n):
            page = self.pages[i]
            for path, distance in page.search(*args, **kwargs):
                yield SearchResult(i + 1, path, distance)


def _processPages(images):
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        for page in executor.map(PageAnalyzer, images):
            yield page

