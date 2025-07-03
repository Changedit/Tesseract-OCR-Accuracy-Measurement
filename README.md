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

- **Git**: You must have Git installed to clone the repositories.
- **Conda**: This guide uses conda to manage Python environments. [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html) if you don't have it.
- **Python 3.10 or newer**: This is a strict requirement. The project dependencies, specifically label-studio-sdk, use features only available in Python 3.10+.
- **Tesseract OCR Engine**: You must install Tesseract on your system and ensure its executable is in your system's PATH. You can verify this by running tesseract \--version in your terminal.

### Installation Steps

1. **Clone the Repository**Bash
    
    ```bash
    git clone https://github.com/Changedit/Tesseract-OCR-Accuracy-Measurement
    cd <your-project-repo-folder>
    
    # Clone the Label Studio ML backend repository into the project folder
    git clone https://github.com/humansignal/label-studio-ml-backend
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
    

---

## How to Use the Application

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

### Step 4: Start the Web Application

1. Make sure your `ocr-eval` conda environment is active.
2. Run the `app.py` script from your terminal:Bash
    
    ```bash
    python app.py
    ```
    
3. Open your web browser and navigate to **`http://127.0.0.1:5000`**.

### Step 5: Run an Evaluation

1. On the main page, click the button to upload your **ground truth JSON file**.
2. In the text input field, provide the **full, absolute local path** to your `/images` directory.
3. Select the **pre-processing options** you want to test using the checkboxes.
4. Click **"Start Evaluation"**.

### Step 6: Analyze the Results

The application will process your data and display the interactive results dashboard.

- Review the high-level metrics in the KPI cards.
- Hover over the charts to see error rates and click on any bar to inspect the image.
- Use the search bar to find specific files in the table.
- Click on the table headers to sort the results and find your best or worst-performing images.
- Click on any filename in the table to open the image viewer and perform a detailed, box-by-box comparison of the ground truth vs. the OCR output.
