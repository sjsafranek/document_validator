import numpy
import pypdfium2
import pytesseract
from pytesseract import Output


def parseImage(image: numpy.array, config='--psm 3 -l eng', tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
    return data

