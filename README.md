# **Tesseract OCR Accuracy Evaluation Framework**

This project provides a complete, end-to-end pipeline for evaluating the accuracy of the Tesseract OCR engine. It includes tools for data acquisition, a manual setup for ML-assisted labeling with Label Studio, a configurable OCR processing script, and a quantitative evaluation module to measure performance using Character Error Rate (CER) and Word Error Rate (WER).

This framework is designed for users who need to benchmark Tesseract's performance on their specific documents and cannot use Docker for the ML backend setup.

### **Core Workflow**

The project follows a systematic, four-stage evaluation pipeline:

1. **Data Acquisition**: Collect a relevant image corpus using the provided web scraper or by adding your own images.
2. **Ground Truth Creation**: Use Label Studio, accelerated by a Tesseract ML backend, to create pixel-perfect ground truth annotations.
3. **OCR Execution**: Run the image corpus through a Tesseract pipeline featuring advanced pre-processing steps.
4. **Quantitative Evaluation**: Compare the OCR output against the ground truth to calculate CER and WER, generating a detailed performance report.

## **Project Structure**

```bash
ocr_evaluation_project/
├── images/                  # <-- Place your images for OCR here.
├── ground_truth/            # <-- Place your Label Studio JSON export here.
├── label-studio-ml-backend/ # <-- Cloned repository for the ML backend.
├── output/                  # <-- Evaluation reports will be saved here.
│   └── ocr_evaluation_report.csv
├── web_scraper.py           # Script to scrape images from the web.
├── parse_label_studio.py    # Parses ground truth data from Label Studio.
├── run_ocr.py               # Contains the main OCR and pre-processing logic.
├── evaluate.py              # Calculates CER/WER and generates the report.
├── main.py                  # Main script to run the final evaluation pipeline.
└── requirements.txt         # Required Python packages for the main project.
```

## **Setup and Installation**

This guide covers the complete manual setup process without Docker.

### **Step 1: Prerequisites**

- **Git**: You must have Git installed to clone the repositories.
- **Conda**: This guide uses conda to manage Python environments. [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html) if you don't have it.
- **Python 3.10 or newer**: This is a strict requirement. The project dependencies, specifically label-studio-sdk, use features only available in Python 3.10+.
- **Tesseract OCR Engine**: You must install Tesseract on your system and ensure its executable is in your system's PATH. You can verify this by running tesseract \--version in your terminal.

### **Step 2: Clone Repositories**

You need to clone two repositories: this project's repository and the one for the Label Studio ML backend.

```bash
# Clone this project's repository
git clone https://github.com/Changedit/Tesseract-OCR-Accuracy-Measurement.git
cd <your-project-repo-folder>

# Clone the Label Studio ML backend repository into the project folder
git clone https://github.com/humansignal/label-studio-ml-backend
```

### **Step 3: Create and Configure the Conda Environment**

We will create a dedicated conda environment with Python 3.10.

```bash
# Create a new environment named 'ocr-eval' with Python 3.10
conda create -n ocr-eval python=3.10

# Activate the new environment
conda activate ocr-eval
```

### **Step 4: Install All Dependencies**

With the environment activated, install all necessary packages. This is a multi-step process.

```bash
# 1. Install the main project's requirements
pip install -r requirements.txt

# 2. Navigate to the ML backend repo's root and install its requirements
cd label-studio-ml-backend
pip install -r requirements.txt

# 3. Install the ML backend package in "editable" mode
pip install -e .

# 4. Install the specific requirements for the Tesseract example
pip install -r label_studio_ml/examples/tesseract/requirements.txt

# 5. Return to the main project directory
cd ../
```

## **Usage Workflow**

Follow these steps to perform an evaluation.

### **Step 1: Prepare Data and Start Label Studio**

1. Place all your images in the `/images` directory.
2. (Optional) Use the `web_scraper.py` to gather more images.
3. **Start Label Studio separately**. If you have it installed locally, run it from its own terminal.

### **Step 2: Start the ML Backend Server**

This step connects your Tesseract model to Label Studio.

1. Open a **new terminal** window.
2. Activate the conda environment: conda activate ocr-eval
3. Navigate to the Tesseract example directory: `cd label-studio-ml-backend/label_studio_ml/examples/tesseract`
4. Run the server script. This command starts the web server that will listen for requests from Label Studio.
    - **On Linux or macOS:**
        
        ```bash
        LOCAL_FILES_SERVING_ENABLED=true python _wsgi.py
        ```
        
    - **On Windows (PowerShell):**
        
        ```powershell
        $env:LOCAL_FILES_SERVING_ENABLED="true"; python _wsgi.py
        ```
        

Keep this terminal open. You will see log output here as you work.

### **Step 3: Annotate Your Data**

1. **Connect the Backend**: In the Label Studio UI, go to your project's **Settings > Machine Learning**. Click "Add Model" and enter the URL of the running backend (e.g., [http://localhost:9090](http://localhost:9090/)).
2. **Enable Interactive Predictions**: Make sure the **"Use for interactive preannotations"** toggle is switched on.
3. **Label Your Images**: Go to the labeling interface. When you draw a bounding box around a piece of text, the ML backend will automatically fill in the recognized text for you to review and correct.
4. **Export Your Data**: Once you're done labeling, export your annotations in **JSON format** and place the file in the `/ground_truth` directory.

### **Step 4: Run the Final Evaluation**

After creating your ground truth, run the main evaluation script to get your final accuracy report.

1. Make sure the path to your ground truth JSON file is correct in main.py.
2. Run the script from your terminal:

```bash
python main.py
```

The script will process all images, compare the results to your ground truth, and save a detailed report to `/output/ocr_evaluation_report.csv` .
