# parse_label_studio.py
import json
import os

def parse_label_studio_export(json_filepath):
    """
    Parses a Label Studio JSON export to extract ground truth text for OCR evaluation,
    using the 'file_upload' field to get the original filename.
    """
    ground_truth_data = {}
    
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print(f"Error: The ground truth file was not found at {json_filepath}")
        return ground_truth_data
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_filepath}")
        return ground_truth_data

    for task in tasks:
        # --- THIS IS THE CORRECTED FILENAME LOGIC ---
        file_upload_name = task.get('file_upload')
        if not file_upload_name:
            continue
        
        try:
            original_filename = file_upload_name.split('-', 1)[1]
        except IndexError:
            print(f"Warning: Could not extract original filename from '{file_upload_name}'. Skipping task.")
            continue
        # --- END OF CORRECTED LOGIC ---

        if 'annotations' not in task or not task['annotations'] or 'result' not in task['annotations'][0]:
            print(f"Warning: No valid annotations found for {original_filename}")
            continue
        
        annotations = task['annotations'][0]['result']
        
        transcribed_texts = []
        for ann in annotations:
            # We only care about the 'textarea' type for the ground truth text
            if ann.get('type') == 'textarea' and 'text' in ann.get('value', {}):
                transcribed_texts.extend(ann['value']['text'])
        
        full_text = " ".join(transcribed_texts)
        ground_truth_data[original_filename] = full_text

    return ground_truth_data

if __name__ == '__main__':
    exported_file = os.path.join('ground_truth', 'project-1-at-2025-07-02-07-34-c2be24bf.json')

    if os.path.exists(exported_file):
        gt_data = parse_label_studio_export(exported_file)
        
        print(f"Successfully parsed ground truth for {len(gt_data)} tasks.")
        
        print("\n--- Ground Truth Sample ---")
        for i, (filename, text) in enumerate(gt_data.items()):
            if i >= 5: break
            print(f"\nFilename: {filename}")
            print(f"Ground Truth: {text[:100]}...")
    else:
        print(f"Error: Export file not found at '{exported_file}'")