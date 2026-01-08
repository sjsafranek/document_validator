import cv2
import PIL
import numpy
import pypdfium2
import pytesseract
from pytesseract import Output


def readPdfPages(infile):
    pdf = pypdfium2.PdfDocument(infile)
    pages = [pdf[i] for i in range(len(pdf))]
    # images = [page.render(scale=2).to_pil() for page in pages]
    # return [image2array(image) for image in images]
    images = [page.render(scale=2).to_numpy() for page in pages]
    return images


def image2array(image):
    return numpy.array(image)


def cleanImage(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image (black text on white background)
    # Adjust the threshold value (e.g., 150) based on your specific image
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    # # Optional: Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(thresh, (5, 5), 0)
    
    return blur


def parseImage(image, config='--psm 3 -l eng', tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe', clean=False):

    if clean:
        image = cleanImage(image)

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
    return data

