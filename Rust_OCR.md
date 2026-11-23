# OCRS
https://github.com/robertknight/ocrs

## Installation
```bash
$ cargo install ocrs-cli --locked --features clipboard
```

## Usage
```bash
$ ocrs data/test_invoice.png --json -o workspace/content.json
```

## Debugging
```
ocrs data/test_invoice.png --png -o workspace/annotated.png
```






# OAR OCR
https://lib.rs/crates/oar-ocr-cli

## Installation
```bash
$ cargo install oar-ocr-cli
```

## Usage
```bash
# Standard OCR
# oar ocr data/test_invoice.png --pages 1 --dpi 300 --format json
oar ocr data/test_invoice.png --format json

# Document structure analysis (specific PDF pages)
oar structure data/test_invoice.png --format json

# Indra OCR or VLM parsing
oar parse --model PaddlePaddle/PaddleOCR-VL-1.5 data/test_invoice.png --pages 1 --format json

```