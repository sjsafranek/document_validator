import PIL
import numpy
import pypdfium2


def readPdfPages(infile: str) -> pypdfium2._helpers.page.PdfPage:
    pdf = pypdfium2.PdfDocument(infile)
    for page in pdf:
        yield page


def readPdfPagesAsImage(infile: str, scale: int = 2) -> PIL.Image.Image:
    for page in readPdfPages(infile):
        yield page.render(scale=scale).to_pil()


def readPdfPagesAsArray(infile: str, scale: int = 2) -> numpy.array:
    for page in readPdfPages(infile):
        yield page.render(scale=scale).to_numpy()

