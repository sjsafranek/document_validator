import cv2
import easyocr
import numpy as np
from PIL import Image


# def openImage(filename):
#     # Read image and increase size
#     img = Image.open(filename)

#     # Increase size (e.g., double width and height)
#     new_size = (img.width * 2, img.height * 2)
#     resized_img = img.resize(new_size, resample=Image.Resampling.BICUBIC)

#     # Convert to a NumPy array (Shape: height, width, channels)
#     arr = np.array(resized_img)
#     return arr

def openImage(filename):
    # 1. Read PNG directly as a NumPy array (IMREAD_UNCHANGED keeps alpha/transparency)
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    # 2. Convert to grey scale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 3. Increase size using scale factors (fx, fy)
    img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    # img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LANCZOS4)

    # # Apply blur
    # img = cv2.GaussianBlur(img, (3, 3), 0)
    # _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 4. Sharpen
    # Define a standard sharpening kernel (sum = 1)
    kernel = np.array([[ 0, -1,  0],
                       [-1,  5, -1],
                       [ 0, -1,  0]])

    # Apply the sharpening filter (-1 keeps the original image depth)
    img = cv2.filter2D(img, -1, kernel)

    return img


# Initialize reader for English and/or other supported languages
reader = easyocr.Reader(['en']) 

# Open image
img = openImage('data/test_invoice.png')
cv2.imwrite("workspace/test_invoice.clean.png", img)

# Read text from an image
results = reader.readtext(img)

for (bbox, text, confidence) in results:
    print(f"Text: {text} {bbox} (Confidence: {confidence:.2f})")

