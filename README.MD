## PDF Invoice Data Extraction

This project is designed to extract financial data from PDF invoices and store it in a CSV file. It uses `pdfplumber` to extract text from PDFs, and falls back to OCR (Optical Character Recognition) using `Tesseract` when dealing with image-based PDFs or PDFs with non-extractable text. The extracted information includes details such as taxable amounts, GST amounts, tax rates, invoice numbers, and more.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Output](#output)
- [Dependencies](#dependencies)
- [Implementation Details](#implementation-details)
  - [How the Code Works](#how-the-code-works)
  - [Accuracy and Logic](#accuracy-and-logic)
  - [Scalability and Efficiency](#scalability-and-efficiency)
  - [Error Handling](#error-handling)

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
```plaintext
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

## Implementation Details

### How the Code Works

The extraction process follows these steps:

1. **PDF Text Extraction with `pdfplumber`:**
   The primary method for text extraction is `pdfplumber`, which extracts the text directly from the PDF pages. It handles most text-based PDFs effectively, allowing us to access structured data like invoice numbers, amounts, and dates.
   
2. **Fallback to OCR (Tesseract):**
   If `pdfplumber` fails to extract meaningful text (for example, from scanned or image-based PDFs), the script falls back to OCR using `pytesseract`. The `pdf2image` library is used to convert each page of the PDF into an image, which is then processed by Tesseract to recognize text.

3. **Regex-Based Data Extraction:**
   After extracting the raw text from the PDF, regular expressions (regex) are used to identify and extract relevant fields, such as taxable amounts, SGST, CGST, IGST, tax rates, invoice numbers, GSTINs, and other financial details.

4. **Tax Calculation Logic:**
   - **Summing Tax Amounts:** The script sums the SGST, CGST, and IGST amounts to get the total tax amount.
   - **Weighted Average Tax Rate Calculation:** If there are multiple tax rates, the script calculates a weighted average tax rate using the tax amounts as weights. This ensures accurate reporting of the overall tax rate applied to the invoice.

5. **Data Output:**
   Once the data is extracted, it is stored in a structured format in a CSV file, with each invoice represented as a row and each extracted field as a column.

### Accuracy and Logic

The accuracy of the extraction depends on:
- **The format of the PDF:** If the PDF is well-structured and text-based, `pdfplumber` can extract the text with high accuracy.
- **OCR Quality:** For image-based PDFs, Tesseract's OCR engine performs well but may struggle with complex layouts or poor image quality, which could lead to inaccuracies.
- **Regex Patterns:** The script uses specific regex patterns to capture financial details like tax rates, amounts, and invoice numbers. These patterns are designed to handle a variety of invoice formats, but any deviation from expected formats (such as unusual invoice layouts) may reduce accuracy.

### Scalability and Efficiency

- **Scalability:** The current approach can handle multiple PDF files in a batch. It processes each PDF independently, so scaling to larger datasets can be achieved by increasing compute resources. Parallel processing (e.g., using Python's multiprocessing) could be implemented to further improve scalability when processing large batches of PDFs.
  
- **Efficiency:** `pdfplumber` is generally fast for text-based PDF extraction, but falling back to OCR increases processing time, as converting PDFs to images and performing OCR is computationally expensive. For large-scale invoice extraction tasks, it would be beneficial to optimize the OCR process or cache intermediate results (e.g., extracted images).

### Error Handling

The script implements the following error-handling strategies:

1. **Fallback Mechanism:** If text extraction with `pdfplumber` fails or returns empty results, the script automatically switches to OCR using Tesseract. This ensures that even image-based PDFs are processed.
   
2. **Try-Except Blocks:** Critical functions, such as PDF reading and text extraction, are wrapped in try-except blocks to catch exceptions and handle them gracefully. For example, if OCR fails, the script logs the error and continues processing the next file.

3. **Missing Data Handling:** If specific data points like tax rates or GSTINs are missing or not found in the invoice, default values such as `'not found'` are assigned. This ensures that the output CSV is always well-formed and complete, even if certain fields are unavailable.

4. **Duplicate GSTIN Check:** The script checks if the supplier’s and recipient’s GSTINs are identical, which is flagged as an error and handled accordingly (setting recipient GSTIN as `'not present'`).

### Conclusion

This PDF Invoice Extraction tool provides a robust solution for extracting structured financial data from invoices. By combining `pdfplumber` for text extraction and `Tesseract` for OCR, it can handle a variety of PDF formats. The regex-based data extraction ensures flexibility, and error handling mechanisms make the tool resilient to various PDF structures. 

For scaling, the efficiency of the fallback OCR process could be improved, and parallel processing could be introduced.