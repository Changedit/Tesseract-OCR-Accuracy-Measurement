# app.py
import os
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
import json
from datetime import datetime

# Import the functions from your existing scripts
from parse_label_studio import parse_label_studio_export
from run_ocr import run_ocr_on_boxes
from evaluate import evaluate_tesseract_performance

# --- Flask App Configuration ---
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
ALLOWED_JSON_EXTENSIONS = {'json'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.secret_key = 'super-secret-key'

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'json_file' not in request.files or 'image_folder_path' not in request.form:
            flash('Error: Both a JSON file and an image folder path are required.', 'danger')
            return redirect(request.url)
        
        json_file = request.files['json_file']
        image_folder_path = request.form['image_folder_path'].strip()

        # Get optimization options from checkboxes
        apply_rescaling = 'apply_rescaling' in request.form
        apply_binarization = 'apply_binarization' in request.form
        apply_deskew = 'apply_deskew' in request.form

        if json_file.filename == '' or not image_folder_path or not os.path.isdir(image_folder_path):
            flash('Error: Please provide a valid JSON file and a valid directory path.', 'danger')
            return redirect(request.url)

        if json_file and allowed_file(json_file.filename, ALLOWED_JSON_EXTENSIONS):
            json_filename = secure_filename(json_file.filename)
            json_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
            json_file.save(json_path)

            # Store image directory in session for the /images/<path> route to work
            session['image_dir'] = image_folder_path
            
            # --- CONSOLIDATED BACKEND PROCESSING ---
            ground_truth_data = parse_label_studio_export(json_path)
            if not ground_truth_data:
                flash('Error: Could not parse ground truth data from JSON file.', 'danger')
                return redirect(url_for('index'))

            processed_data = run_ocr_on_boxes(
                image_folder_path, 
                ground_truth_data, 
                psm=7,
                apply_rescaling=apply_rescaling,
                apply_binarization=apply_binarization,
                apply_deskew=apply_deskew
            )
            if not processed_data:
                flash('Error: OCR processing returned no results.', 'danger')
                return redirect(url_for('index'))

            evaluation_df = evaluate_tesseract_performance(processed_data)
            if evaluation_df.empty:
                flash('Error: Evaluation produced no results.', 'danger')
                return redirect(url_for('index'))

            detailed_results = evaluation_df.iloc[:-1].to_dict(orient='records')
            aggregate_results = evaluation_df.iloc[-1].to_dict()

            # Directly render the results page with all the necessary data.
            return render_template('results.html', 
                                   detailed_results=detailed_results, 
                                   aggregate_results=aggregate_results,
                                   full_data_json=json.dumps(processed_data))
        else:
            flash('Error: Invalid JSON file type.', 'danger')
            return redirect(request.url)
            
    return render_template('index.html')

# Route to serve images for the modal viewer
@app.route('/images/<path:filename>')
def serve_image(filename):
    image_dir = session.get('image_dir')
    if not image_dir or not os.path.isdir(image_dir):
        return "Image directory not found or is invalid.", 404
    return send_from_directory(image_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)
