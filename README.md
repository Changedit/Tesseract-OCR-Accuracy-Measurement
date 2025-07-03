# Interactive Tesseract OCR Evaluation Dashboard

This project provides a web-based tool built with Flask for a comprehensive, end-to-end evaluation of the Tesseract OCR engine. It allows users to test Tesseract's performance on their own image datasets, interactively experiment with pre-processing options, and analyze the results through a rich, interactive dashboard.

The application moves beyond simple command-line scripts to offer a user-friendly interface for a rigorous and data-driven evaluation workflow.

## Features

- **Web-Based UI**: A clean and simple interface powered by Flask that runs locally in your browser.
- **Local File Integration**: Securely processes images directly from a local folder path, bypassing the need for cumbersome uploads and avoiding file size limits.
- **Interactive Pre-processing**: Toggle pre-processing options like Binarization, Rescaling, and Deskewing directly in the UI to instantly see how they impact OCR accuracy.
- **Advanced Dashboard**: The results are displayed in a comprehensive dashboard, not just a simple table.
    - **KPI Cards**: At-a-glance view of the most important aggregate metrics like overall Word Error Rate (WER) and Character Error Rate (CER).
    - **Interactive Charts**: Bar charts display the top 10 worst-performing images, and clicking on a bar opens the image viewer for detailed analysis.
    - **Search and Sort Table**: The detailed results table can be instantly searched by filename and sorted by any metric with a single click.
- **Visual Image Viewer**: Click on any filename or chart bar to open a modal popup that displays the image with its ground truth bounding boxes overlaid.
- **Detailed Text Comparison**: Click on any bounding box within the image viewer to see a direct side-by-side comparison of the ground truth text and the text produced by the Tesseract OCR pipeline.
- **Static Reports**: Each evaluation automatically saves a self-contained, interactive HTML report to a `/reports`directory for your records.

---

## Project Structure

```bash
ocr_evaluation_project/
├── images/                  # <-- Place your images for OCR here.
├── ground_truth/            # <-- Place your Label Studio JSON export here.
├── reports/                 # <-- Static HTML reports are saved here.
├── templates/               # <-- HTML templates for the Flask app.
│   ├── index.html
│   └── results.html
├── uploads/                 # <-- Temporary storage for the uploaded JSON file.
├── app.py                   # The main Flask web application.
├── evaluate.py              # Calculates CER/WER metrics.
├── parse_label_studio.py    # Parses the ground truth data from Label Studio.
├── run_ocr.py               # Contains the main OCR and pre-processing logic.
└── requirements.txt         # Required Python packages.
```

---

## Setup and Installation

This guide covers the manual setup process required to run the web application.

### Prerequisites

- **Git**: To clone the repository.
- **Conda**: For managing the Python environment.
- **Python 3.10 or newer**: This is a strict requirement for the project's dependencies.
- **Tesseract OCR Engine**: You must have Tesseract installed on your system and available in your system's `PATH`.

### Installation Steps

1. **Clone the Repository**Bash
    
    ```bash
    git clone <your-project-repo-url>
    cd <your-project-repo-folder>
    ```
    
2. **Create and Activate the Conda Environment**Bash
    
    ```bash
    # Create a new environment named 'ocr-eval' with Python 3.10
    conda create --name ocr-eval python=3.10
    
    # Activate the new environment
    conda activate ocr-eval
    ```
    
3. **Install Dependencies** Install all required Python packages using the `requirements.txt` file.Bash
    
    ```bash
    pip install -r requirements.txt
    ```
    

---

## How to Use the Application

### Step 1: Prepare Your Data

1. Place all of your images in the `/images` directory.
2. Place your exported ground truth JSON file from Label Studio into the `/ground_truth` directory.

### Step 2: Start the Web Application

1. Make sure your `ocr-eval` conda environment is active.
2. Run the `app.py` script from your terminal:Bash
    
    ```bash
    python app.py
    ```
    
3. Open your web browser and navigate to **`http://127.0.0.1:5000`**.

### Step 3: Run an Evaluation

1. On the main page, click the button to upload your **ground truth JSON file**.
2. In the text input field, provide the **full, absolute local path** to your `/images` directory.
3. Select the **pre-processing options** you want to test using the checkboxes.
4. Click **"Start Evaluation"**.

### Step 4: Analyze the Results

The application will process your data and display the interactive results dashboard.

- Review the high-level metrics in the KPI cards.
- Hover over the charts to see error rates and click on any bar to inspect the image.
- Use the search bar to find specific files in the table.
- Click on the table headers to sort the results and find your best or worst-performing images.
- Click on any filename in the table to open the image viewer and perform a detailed, box-by-box comparison of the ground truth vs. the OCR output.
