# main.py
import os
import pandas as pd
from parse_label_studio import parse_label_studio_export
from run_ocr import batch_ocr_with_bounding_boxes
from evaluate import evaluate_tesseract_performance

# --- Configuration ---
IMAGE_DIR = 'images'
GROUND_TRUTH_JSON = os.path.join('ground_truth', 'project-1-at-2025-07-02-07-34-c2be24bf.json')
OUTPUT_REPORT_CSV = os.path.join('output', 'ocr_evaluation_report.csv')

# --- Tesseract Settings ---
# For cropped regions, PSM 7 (single text line) or 6 (single block) is usually best.
PSM_SETTING = 7
OEM_SETTING = 3

# --- Main Workflow ---
def run_evaluation_pipeline():
    """
    Executes the full OCR evaluation pipeline.
    """
    print("--- Starting OCR Evaluation Pipeline ---")

    # 1. Load Ground Truth Data
    print(f"\n[Step 1/3] Parsing ground truth text from: {GROUND_TRUTH_JSON}")
    if not os.path.exists(GROUND_TRUTH_JSON):
        print(f"FATAL: Ground truth file not found at '{GROUND_TRUTH_JSON}'.")
        return
    ground_truth_data = parse_label_studio_export(GROUND_TRUTH_JSON)
    if not ground_truth_data:
        print("FATAL: No ground truth data could be parsed. Exiting.")
        return
    print(f"Successfully loaded ground truth for {len(ground_truth_data)} images.")

    # 2. Execute Tesseract OCR on Bounding Box Regions
    print(f"\n[Step 2/3] Running Tesseract OCR on bounding box regions from: {GROUND_TRUTH_JSON}")
    if not os.path.isdir(IMAGE_DIR):
        print(f"FATAL: Image directory not found at '{IMAGE_DIR}'.")
        return
    
    ocr_results = batch_ocr_with_bounding_boxes(
        image_dir=IMAGE_DIR, 
        json_filepath=GROUND_TRUTH_JSON,
        psm=PSM_SETTING, 
        oem=OEM_SETTING,
        apply_preprocessing=True
    )
    
    if not ocr_results:
        print("FATAL: OCR processing returned no results. Exiting.")
        return

    # 3. Quantitative Evaluation
    print("\n[Step 3/3] Evaluating OCR performance...")
    evaluation_df = evaluate_tesseract_performance(ground_truth_data, ocr_results)

    if evaluation_df.empty:
        print("FATAL: Evaluation produced no results.")
        return
        
    # --- Display and Save Results ---
    print("\n--- OCR Evaluation Report ---")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 140)
    print(evaluation_df.round(2))

    os.makedirs(os.path.dirname(OUTPUT_REPORT_CSV), exist_ok=True)
    evaluation_df.to_csv(OUTPUT_REPORT_CSV, index=False)
    print(f"\n--- Pipeline Complete ---")
    print(f"Detailed report saved to: {OUTPUT_REPORT_CSV}")

if __name__ == '__main__':
    run_evaluation_pipeline()