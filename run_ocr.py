# run_ocr.py
import os
import json
import pytesseract
import cv2
import numpy as np

def parse_label_studio_for_boxes(json_filepath):
    """
    Parses a Label Studio JSON export. It extracts the original filename from
    the 'file_upload' field and maps it to its bounding box annotations.
    """
    annotations = {}
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print(f"Error: The ground truth file was not found at {json_filepath}")
        return annotations

    for task in tasks:
        # --- THIS IS THE NEW LOGIC BASED ON YOUR FINDING ---
        file_upload_name = task.get('file_upload')
        if not file_upload_name:
            continue
        
        # Extract the original filename from the 'file_upload' field.
        # This assumes the format is "uuid-original_filename.jpg"
        # We split once on the first hyphen and take the second part.
        try:
            original_filename = file_upload_name.split('-', 1)[1]
        except IndexError:
            print(f"Warning: Could not extract original filename from '{file_upload_name}'. Skipping task.")
            continue
            
        annotations[original_filename] = []
        # --- END OF NEW LOGIC ---

        if 'annotations' in task and task['annotations']:
            for ann in task['annotations'][0]['result']:
                if ann.get('type') == 'rectangle':
                    val = ann['value']
                    w = int(val['width'] * ann['original_width'] / 100)
                    h = int(val['height'] * ann['original_height'] / 100)
                    x = int(val['x'] * ann['original_width'] / 100)
                    y = int(val['y'] * ann['original_height'] / 100)
                    annotations[original_filename].append({'box': [x, y, w, h]})
    
    return annotations

def binarize_image(image):
    """Converts an image to grayscale and applies adaptive thresholding."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    return binary

def batch_ocr_with_bounding_boxes(image_dir, json_filepath, psm=6, oem=3, lang='eng', apply_preprocessing=True):
    """
    Performs OCR on cropped regions of images as defined by bounding boxes
    from a Label Studio export file.
    """
    print("--- Starting OCR process based on bounding box annotations ---")
    
    annotations = parse_label_studio_for_boxes(json_filepath)
    if not annotations:
        print("Could not parse any annotations. Exiting.")
        return {}
        
    ocr_results = {}
    tess_config = f'--oem {oem} --psm {psm}'

    for filename, boxes in annotations.items():
        if not boxes:
            print(f"  Skipping {filename} (no bounding boxes found).")
            continue
        
        image_path = os.path.join(image_dir, filename)
        if not os.path.exists(image_path):
            print(f"  Warning: Image file not found at {image_path}. Skipping.")
            continue
            
        print(f"Processing {filename} with {len(boxes)} text region(s)...")
        full_image = cv2.imread(image_path)
        if full_image is None:
            print(f"  Warning: Could not read image {filename}. Skipping.")
            continue

        ocr_texts_for_image = []

        for box_info in boxes:
            try:
                x, y, w, h = box_info['box']
                cropped_image = full_image[y:y+h, x:x+w]

                if cropped_image.size == 0:
                    continue

                processed_crop = cropped_image
                if apply_preprocessing:
                    processed_crop = binarize_image(processed_crop)
                
                text = pytesseract.image_to_string(processed_crop, lang=lang, config=tess_config).strip()
                ocr_texts_for_image.append(text)

            except Exception as e:
                print(f"    Error processing a region in {filename}: {e}")

        ocr_results[filename] = " ".join(ocr_texts_for_image)

    print("\n--- OCR processing complete. ---")
    return ocr_results


if __name__ == '__main__':
    input_directory = 'images'
    ground_truth_file = os.path.join('ground_truth', 'project-1-at-2025-07-02-07-34-c2be24bf.json')
    
    results = batch_ocr_with_bounding_boxes(input_directory, ground_truth_file, psm=7)

    if results:
        print("\n--- OCR Results Sample ---")
        for i, (filename, text) in enumerate(results.items()):
            if i >= 5: break
            print(f"\nFilename: {filename}")
            print(f"OCR Output: {text[:200]}...")
    else:
        print("\nNo results were generated. Please check warnings in the log above.")