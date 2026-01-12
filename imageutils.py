import PIL
import numpy


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


