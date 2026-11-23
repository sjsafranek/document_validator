# document_validator
Use OCR to read PDF files

## Install Tesseract
https://github.com/UB-Mannheim/tesseract/wiki
C:\Program Files\Tesseract-OCR


https://medium.com/data-science/top-5-python-libraries-for-extracting-text-from-images-c29863b2f3d



py -3.15 -m pip install numpy
py -3.15 -m pip install opencv-python
py -3.15 -m pip install pypdfium2
py -3.15 -m pip install pytesseract


py -3.15 main.py data/test_invoice.png
py -3.15 main.py data/MagicTheGathering_IsTuringComplete.pdf



## Setup
```bash
py -3.15 -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip setuptools wheel

pip install scikit-image --only-binary :all:

pip install easyocr
```


```bash
pip install numpy
pip install opencv-python
pip install pypdfium2
pip install pytesseract
```