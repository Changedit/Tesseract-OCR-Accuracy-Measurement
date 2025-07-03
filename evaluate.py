# evaluate.py
import jiwer
import pandas as pd

def evaluate_tesseract_performance(processed_data):
    """
    Takes the fully processed data (with gt_text and ocr_text) and calculates
    per-file and aggregate error rates.
    """
    evaluation_results = []
    
    transformation = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.RemovePunctuation(),
        jiwer.Strip()
    ])

    all_gt_corpus = []
    all_hyp_corpus = []

    for filename, data in processed_data.items():
        gt_full_text = " ".join([box['gt_text'] for box in data['boxes']])
        ocr_full_text = " ".join([box['ocr_text'] for box in data['boxes']])

        # Apply transformations for consistent comparison
        transformed_gt = transformation(gt_full_text)
        transformed_hyp = transformation(ocr_full_text)

        all_gt_corpus.append(transformed_gt)
        all_hyp_corpus.append(transformed_hyp)

        word_error_rate = jiwer.wer(transformed_gt, transformed_hyp)
        char_error_rate = jiwer.cer(transformed_gt, transformed_hyp)

        evaluation_results.append({
            'Image Filename': filename,
            'Word Count (GT)': len(transformed_gt.split()),
            'Character Count (GT)': len(transformed_gt),
            'WER (%)': word_error_rate * 100,
            'CER (%)': char_error_rate * 100,
        })

    if not evaluation_results:
        return pd.DataFrame()

    results_df = pd.DataFrame(evaluation_results)

    aggregate_wer = jiwer.wer(all_gt_corpus, all_hyp_corpus) * 100
    aggregate_cer = jiwer.cer(all_gt_corpus, all_hyp_corpus) * 100
    
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
