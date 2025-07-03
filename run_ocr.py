# run_ocr.py
import os
import pytesseract
import cv2
import numpy as np

# --- Pre-processing Functions ---
def rescale_image(image, scale_factor=2.0):
    """Rescales an image by a given factor. A minimum of 300 DPI is recommended for Tesseract."""
    # A scale factor of 2 is a good starting point for small text regions.
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_CUBIC)

def binarize_image(image):
    """Converts an image to grayscale and applies adaptive thresholding."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    return binary

def deskew_image(image):
    """Detects and corrects skew in an image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray) # Invert colors for contour finding
    
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def run_ocr_on_boxes(image_dir, ground_truth_data, psm=7, oem=3, lang='eng', 
                     apply_rescaling=False, apply_binarization=True, apply_deskew=False):
    """
    Takes parsed ground truth data, runs OCR on each bounding box, and returns the
    enriched data structure with the ocr_text added. Includes optional pre-processing.
    """
    print("--- Running OCR on specific bounding boxes ---")
    
    tess_config = f'--oem {oem} --psm {psm}'
    
    processed_count = 0
    for filename, data in ground_truth_data.items():
        image_path = os.path.join(image_dir, filename)
        if not os.path.exists(image_path):
            print(f"  [Warning] Image file not found, skipping: {image_path}")
            continue
            
        processed_count += 1
        print(f"  Processing {filename}...")
        full_image = cv2.imread(image_path)
        if full_image is None:
            continue

        # --- OPTIONAL DESKEWING OF FULL IMAGE ---
        # Deskewing should be done on the full image before cropping.
        if apply_deskew:
            print("    - Applying deskew...")
            full_image = deskew_image(full_image)
        # ---

        original_height, original_width, _ = full_image.shape

        for box_info in data.get('boxes', []):
            coords = box_info['coords']
            
            x = int(coords['x'] * original_width / 100)
            y = int(coords['y'] * original_height / 100)
            w = int(coords['width'] * original_width / 100)
            h = int(coords['height'] * original_height / 100)

            try:
                cropped_image = full_image[y:y+h, x:x+w]
                if cropped_image.size == 0:
                    box_info['ocr_text'] = ""
                    continue

                processed_crop = cropped_image
                

                if apply_rescaling:
                    processed_crop = rescale_image(processed_crop)
                
                if apply_binarization:
                    processed_crop = binarize_image(processed_crop)

                
                text = pytesseract.image_to_string(processed_crop, lang=lang, config=tess_config).strip()
                box_info['ocr_text'] = text

            except Exception as e:
                print(f"    Error processing a region in {filename}: {e}")
                box_info['ocr_text'] = "[OCR_ERROR]"

    print(f"\n--- OCR processing complete. Processed {processed_count} files. ---")
    return ground_truth_data
