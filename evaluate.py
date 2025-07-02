# evaluate.py
import jiwer
import pandas as pd

def evaluate_tesseract_performance(ground_truth, ocr_output):
    """
    Evaluates Tesseract OCR performance against ground truth data using CER and WER.
    This version uses the latest jiwer API and applies transformations manually.
    """
    evaluation_results = []
    
    transformation = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.RemovePunctuation(),
        jiwer.Strip()
    ])

    all_gt_sents = []
    all_hyp_sents = []

    for filename, gt_text in ground_truth.items():
        if filename not in ocr_output:
            print(f"Warning: No OCR output found for ground truth file: {filename}")
            continue
        
        hyp_text = ocr_output.get(filename, "")

        gt_text = "" if gt_text is None else str(gt_text)
        hyp_text = "" if hyp_text is None else str(hyp_text)

        # --- THIS IS THE CORRECTED LOGIC ---
        # Manually apply the transformation to the text first
        transformed_gt = transformation(gt_text)
        transformed_hyp = transformation(hyp_text)
        
        # Now, call the functions with the pre-processed text
        word_error_rate = jiwer.wer(transformed_gt, transformed_hyp)
        char_error_rate = jiwer.cer(transformed_gt, transformed_hyp)
        # --- END OF CORRECTION ---

        # Store sentences for aggregate calculation
        all_gt_sents.append(transformed_gt)
        all_hyp_sents.append(transformed_hyp)

        evaluation_results.append({
            'Image Filename': filename,
            'Word Count (GT)': len(transformed_gt.split()),
            'Character Count (GT)': len(transformed_gt),
            'WER (%)': word_error_rate * 100,
            'CER (%)': char_error_rate * 100,
        })

    if not evaluation_results:
        print("No results to evaluate.")
        return pd.DataFrame()

    results_df = pd.DataFrame(evaluation_results)

    # Calculate true aggregate statistics by processing the whole corpus at once
    aggregate_wer = jiwer.wer(all_gt_sents, all_hyp_sents) * 100
    aggregate_cer = jiwer.cer(all_gt_sents, all_hyp_sents) * 100
    
    summary = {
        'Image Filename': '--- AGGREGATE ---',
        'Word Count (GT)': results_df['Word Count (GT)'].sum(),
        'Character Count (GT)': results_df['Character Count (GT)'].sum(),
        'WER (%)': aggregate_wer,
        'CER (%)': aggregate_cer,
    }

    summary_df = pd.DataFrame([summary])
    final_df = pd.concat([results_df, summary_df], ignore_index=True)
    
    return final_df

if __name__ == '__main__':
    mock_gt_data = {
        'image_01.png': 'This is a perfectly recognized sentence.',
        'image_02.png': 'This sentence has one substitution error.',
        'image_05.png': 'a bad ocr result with meny erors'
    }
    mock_ocr_data = {
        'image_01.png': 'This is a perfectly recognized sentence.',
        'image_02.png': 'This sentence has one substiturion error.',
        'image_05.png': 'a bad ocr reslt wit meny erorss'
    }

    evaluation_df = evaluate_tesseract_performance(mock_gt_data, mock_ocr_data)

    if not evaluation_df.empty:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 120)
        
        print("\n--- OCR Evaluation Report (Mock Data) ---")
        print(evaluation_df.round(2))