# parse_label_studio.py
import json
import os

def parse_label_studio_export(json_filepath):
    """
    Parses a Label Studio JSON export to extract ground truth text and bounding boxes.
    It links text and box annotations by their shared 'id'.
    """
    ground_truth_data = {}
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print(f"Error: The ground truth file was not found at {json_filepath}")
        return {}

    for task in tasks:
        file_upload_name = task.get('file_upload')
        if not file_upload_name:
            continue
        
        # This handles cases where the original filename might contain hyphens.
        # It assumes the format is "uuid-original_filename.jpg"
        parts = file_upload_name.split('-')
        if len(parts) > 1:
            original_filename = '-'.join(parts[1:])
        else:
            original_filename = file_upload_name

        annotations = task.get('annotations', [{}])[0].get('result', [])
        if not annotations:
            continue

        grouped_results = {}
        for ann in annotations:
            ann_id = ann.get('id')
            if ann_id:
                if ann_id not in grouped_results:
                    grouped_results[ann_id] = {}
                # Merge the data for the same ID
                if 'text' in ann.get('value', {}):
                    grouped_results[ann_id]['text'] = ann['value']['text'][0]
                if ann.get('type') == 'rectangle':
                    grouped_results[ann_id].update(ann)

        boxes_with_text = []
        for ann_id, data in grouped_results.items():
            if data.get('type') == 'rectangle' and 'value' in data:
                coords = data['value']
                boxes_with_text.append({
                    'coords': {
                        'x': coords['x'],
                        'y': coords['y'],
                        'width': coords['width'],
                        'height': coords['height'],
                        'rotation': coords.get('rotation', 0)
                    },
                    'gt_text': data.get('text', '') # Get text from the grouped data
                })
        
        if boxes_with_text:
            ground_truth_data[original_filename] = {'boxes': boxes_with_text}

    return ground_truth_data
