import cv2
import PIL
import numpy
import pypdfium2
import pytesseract
from pytesseract import Output


def normalizeText(text):
    # characters = [char.lower() for char in text if char.isalnum()]
    characters = [char.lower() for char in text if not char.isspace()]
    if 0 == len(characters):
        return ''
    if characters[-1] in '.,;!?':
        characters = characters[:-1]
    normalized = "".join(characters)
    return normalized


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


def image2array(image: PIL.Image.Image) -> numpy.array:
    return numpy.array(image)


def cleanImage(image: numpy.array):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image (black text on white background)
    # Adjust the threshold value (e.g., 150) based on your specific image
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

    # Optional: Apply Gaussian blur to reduce noise
    kernel = (5, 5)
    blur = cv2.GaussianBlur(thresh, kernel, 0)

    # Define the sharpening kernel (3x3)
    # This specific kernel emphasizes the center pixel relative to its neighbors
    sharpening_kernel = numpy.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])

    # Apply the kernel to the image using filter2D
    # The '-1' indicates that the depth of the output image will be the same as the input
    sharpened_image_kernel = cv2.filter2D(blur, -1, sharpening_kernel)

    return sharpened_image_kernel


def parseImage(image: numpy.array, config='--psm 3 -l eng', tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
    return data

