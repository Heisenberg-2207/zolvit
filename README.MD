# PDF Invoice Data Extraction

This project is designed to extract financial data from PDF invoices and store the information in a CSV file. It uses `pdfplumber` to extract text from PDFs and falls back to OCR (Optical Character Recognition) via `Tesseract` for PDFs that contain images or non-extractable text. The extracted information includes details such as taxable amounts, GST amounts, tax rates, invoice numbers, and more.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Output](#output)
- [Dependencies](#dependencies)

## Features

- Extracts key financial details from PDF invoices.
- Uses `pdfplumber` for direct text extraction.
- Falls back to `Tesseract OCR` for image-based PDFs or PDFs where text extraction fails.
- Regex-based extraction of fields like SGST, CGST, IGST, tax rates, taxable value, invoice number, GSTIN, and more.
- Outputs the extracted data into a CSV file.

## Installation

### Prerequisites

Ensure that the following software is installed on your machine:

- Python 3.7+
- Tesseract OCR
- Poppler

### Steps to Install

Clone the repository:
   ```bash
   git clone https://github.com/your-repo/pdf-invoice-extraction.git
   cd pdf-invoice-extraction
   ```
   
Install the required Python packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

Install Tesseract OCR and Poppler:

**Ubuntu:**
   ```bash
   sudo apt-get install -y tesseract-ocr libtesseract-dev poppler-utils
   ```

**Mac: Install tesseract and poppler via Homebrew:**
   ```bash
   brew install tesseract
   brew install poppler
   ```

**Windows:**
- Download and install Tesseract OCR.
- Download Poppler binaries and add them to your system PATH.

## Usage

Place your PDF invoice files in a folder (e.g., `pdf_invoices/`).

Run the Python script `main.py`:
   ```bash
   python main.py
   ```

The script will process all PDFs in the folder and generate a CSV file `extracted_invoice_data.csv` with the extracted information.

### Parameters
- `folder_path`: Path to the folder containing PDF files (default: `./pdf_invoices/`).
- `output_csv_path`: Path to the output CSV file (default: `./extracted_invoice_data.csv`).

## Project Structure
   ```graphql
   .
   ├── main.py                     # Main Python script for PDF processing
   ├── pdf_invoices/               # Folder where the PDF files are located
   ├── extracted_invoice_data.csv  # Output CSV file (generated after running the script)
   ├── requirements.txt            # Python dependencies
   ├── README.md                   # Project documentation
   ```

## Output

The extracted data is saved in a CSV file named `extracted_invoice_data.csv`. The CSV file contains the following columns:

- `taxable_value`: Total taxable value.
- `sgst_amount`: SGST (State Goods and Services Tax) amount.
- `cgst_amount`: CGST (Central Goods and Services Tax) amount.
- `igst_amount`: IGST (Integrated Goods and Services Tax) amount.
- `tax_amount`: Sum of all tax amounts (SGST, CGST, IGST).
- `final_amount`: Total final amount including tax.
- `invoice_number`: The invoice number from the PDF.
- `invoice_date`: The date of the invoice.
- `place_of_supply`: The place where the supply occurred.
- `place_of_origin`: The origin of the supply.
- `gstin_supplier`: Supplier's GSTIN.
- `gstin_recipient`: Recipient's GSTIN.
- `total_discount`: Total discount amount (if available).

## Dependencies

- `pdfplumber`: Extracts text from PDF files.
- `pytesseract`: Python wrapper for Tesseract OCR.
- `pdf2image`: Converts PDF pages to images for OCR.
- `Pillow`: Python Imaging Library used by pdf2image.

Install the required dependencies via pip:
   ```bash
   pip install -r requirements.txt
   ```

## License

This project is licensed under the MIT License.
```





