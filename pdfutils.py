import PIL
import numpy
import pypdfium2


def readPdfPages(infile: str) -> pypdfium2._helpers.page.PdfPage:
    pdf = pypdfium2.PdfDocument(infile)
    for page in pdf:
        yield page


def readPdfPagesAsImage(infile: str) -> PIL.Image.Image:
    for page in readPdfPages(infile):
        yield page.render(scale=2).to_pil()


def readPdfPagesAsArray(infile: str) -> numpy.array:
    for page in readPdfPages(infile):
        yield page.render(scale=2).to_numpy()


