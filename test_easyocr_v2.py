import cv2
import easyocr
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F


def openImage(filename):
    # 1. Read PNG directly as a NumPy array (IMREAD_UNCHANGED keeps alpha/transparency)
    img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    # 2. Increase size using scale factors (fx, fy)
    img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    # 3. Convert to grey scale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


# Initialize reader for English and/or other supported languages
reader = easyocr.Reader(['en']) 

# Open image
img = openImage('data/test_invoice.png')

# Read text from an image
results = reader.readtext(img)

# Loop through results
for (bbox, text, confidence) in results:
    # Crop the bounding box
    pts = np.array(bbox, dtype=np.int32)
    x_min, y_min = max(0, pts[:, 0].min()), max(0, pts[:, 1].min())
    x_max, y_max = pts[:, 0].max(), pts[:, 1].max()
    crop = img[y_min:y_max, x_min:x_max]

    # 2. Preprocess crop to match EasyOCR's recognizer input (height = 64)
    h, w = crop.shape
    new_w = max(1, int(w * (64 / h)))
    resized = cv2.resize(crop, (new_w, 64))

    # Normalize to [-1, 1] and convert to tensor [Batch, Channel, Height, Width]
    tensor = torch.from_numpy(resized).float() / 255.0
    tensor = (tensor - 0.5) / 0.5
    tensor = tensor.unsqueeze(0).unsqueeze(0).to(reader.device)

    # 3. Forward pass through the recognizer
    with torch.no_grad():
        # Dummy text input required by EasyOCR's forward signature
        dummy_text = torch.LongTensor(1, 26).fill_(0).to(reader.device)
        # preds = reader.recognizer(tensor, dummy_text, is_train=False)
        preds = reader.recognizer(tensor, dummy_text)

        # Calculate softmax probabilities across the character vocabulary
        probs = F.softmax(preds, dim=2)
        max_probs, max_indices = probs.max(dim=2)

    # 4. Decode CTC output to map probabilities to individual characters
    char_list = reader.character    # Index 0 is the CTC [blank] token
    indices = max_indices[0].cpu().numpy()
    scores = max_probs[0].cpu().numpy()

    char_confidences = []
    prev_idx = -1
    for idx, score in zip(indices, scores):
        # Collapse repeated indices and ignore CTC blank (0)
        if idx != 0 and idx != prev_idx:
            # char_confidences.append((char_list[idx], float(score)))
            char_confidences.append((char_list[idx-1], float(score)))
        prev_idx = idx

    print(f"Word: '{text}' (Overall: {confidence:.4f})")
    for char, c_conf in char_confidences:
        print(f'    {char}: {c_conf:.4f}')

