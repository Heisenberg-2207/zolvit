# main.py

# ---
# PDF Invoice Data Extraction
# ---

# ### Install necessary libraries and dependencies
# Install the required packages if you are using Google Colab or a new environment.

!pip install pdfplumber Pillow pdf2image pytesseract
!apt-get install -y tesseract-ocr poppler-utils

# ### Import necessary libraries
import os
import re
import pandas as pd
import pytesseract
import pdfplumber
from PIL import Image
from pdf2image import convert_from_path

# ### Set up Tesseract path
# In some environments like Google Colab, you may need to explicitly set the path to the Tesseract engine.
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# ### Define regex patterns for extracting invoice data
patterns = {
    'taxable_value': r'Taxable Amount ₹([0-9,]+\.\d{2})',
    'sgst_amount': r'SGST \d+\.\d+% ₹([0-9,]+\.\d{2})',
    'cgst_amount': r'CGST \d+\.\d+% ₹([0-9,]+\.\d{2})',
    'igst_amount': r'IGST \d+\.\d+% ₹([0-9,]+\.\d{2})',
    'sgst_rate(%)': r'SGST (\d+\.\d+)% ₹[0-9,]+\.\d{2}',
    'cgst_rate(%)': r'CGST (\d+\.\d+)% ₹[0-9,]+\.\d{2}',
    'igst_rate(%)': r'IGST (\d+\.\d+)% ₹[0-9,]+\.\d{2})',
    'final_amount': r'Total\s*₹\s*([0-9,]+\.\d{2})',
    'invoice_number': r'Invoice #: (\S+)',
    'invoice_date': r'Invoice Date: (\d{2} \w{3} \d{4})',
    'place_of_supply': r'Place of Supply:\s*(\d+-[A-Z\s]+)',
    'place_of_origin': r'Place of Origin:\s*(\d+-[A-Z\s]+)',
    'gstin_supplier': r'GSTIN\s+([0-9A-Z]{15})',
    'gstin_recipient': r'GSTIN\s+([0-9A-Z]{15})',
    'total_discount': r'Total Discount\s*₹\s*([0-9,]+\.\d{2})'
}

# ### Define the function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])
        return text.strip() if text else None
    except Exception as e:
        print(f"Error reading {pdf_path} with pdfplumber: {e}")
        return None

# ### Define the fallback OCR function using Tesseract
def extract_text_with_ocr(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        text = ''.join([pytesseract.image_to_string(image) for image in images])
        return text
    except Exception as e:
        print(f"Error extracting OCR from {pdf_path}: {e}")
        return None

# ### Define the function to extract data using regex patterns
def extract_data_from_text(text):
    data = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text)
        data[field] = match.group(1) if match else 'not found'
    
    # Handle tax calculations
    try:
        sgst_amount = float(data.get('sgst_amount', '0').replace(',', ''))
        cgst_amount = float(data.get('cgst_amount', '0').replace(',', ''))
        igst_amount = float(data.get('igst_amount', '0').replace(',', ''))
        data['tax_amount'] = f"{sgst_amount + cgst_amount + igst_amount:.2f}"
    except ValueError:
        data['tax_amount'] = '0'
    
    return data

# ### Process all PDFs in the folder and extract data to CSV
def process_pdfs_in_folder(folder_path, output_csv_path):
    fieldnames = [
        'taxable_value', 'sgst_amount', 'cgst_amount', 'igst_amount', 'sgst_rate(%)',
        'cgst_rate(%)', 'igst_rate(%)', 'tax_amount', 'final_amount', 'invoice_number',
        'invoice_date', 'place_of_supply', 'place_of_origin', 'gstin_supplier',
        'gstin_recipient', 'total_discount'
    ]

    extracted_data_list = []
    
    for pdf_file_name in os.listdir(folder_path):
        if pdf_file_name.endswith('.pdf'):
            pdf_file_path = os.path.join(folder_path, pdf_file_name)
            print(f"Processing: {pdf_file_name}")

            text = extract_text_from_pdf(pdf_file_path) or extract_text_with_ocr(pdf_file_path)
            
            if text:
                extracted_data = extract_data_from_text(text)
                extracted_data_list.append(extracted_data)
            else:
                print(f"Failed to extract text from {pdf_file_name}")
    
    # Save extracted data to CSV
    df = pd.DataFrame(extracted_data_list)
    df.to_csv(output_csv_path, index=False)
    print(f"Data saved to {output_csv_path}")

# ### Run the extraction process
folder_path = './pdf_invoices/'  # Path to folder containing PDF files
output_csv_path = './extracted_invoice_data.csv'  # Output CSV file

process_pdfs_in_folder(folder_path, output_csv_path)
