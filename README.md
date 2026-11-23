

Using Dijkstra and Weighted Graphs over OCR Results


IronOCR (Tesseract) (https://ironsoftware.com/ocr/csharp)
Pytesseract (https://pypi.org/project/pytesseract/)
OCRS (https://github.com/robertknight/ocrs)

Zonal OCR
I have had great results using zonal/template OCR methodology for document validation processes. It tends to be faster and it keeps results from data extraction fairly clean due to the targeted nature of the zonal process. The main downsides are dealing with skewed scans, and the ongoing template maintenance as document layouts change. Perhaps the biggest limitation to this OCR technique, is how to deal with documents coming from 3rd and 4th parties, whose layouts vary wildly, yet still contain the same basic information.




however this doesn’t help with documents with varying or inconsistent layout/formatting.


OCR results are words within 2 dimensional space, similar to a road network.







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