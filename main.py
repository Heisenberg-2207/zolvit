# main.py

# --- Install necessary libraries ---
!pip install pytesseract pdfplumber Pillow pdf2image
!apt-get install -y tesseract-ocr  # Install Tesseract OCR engine
!apt-get install -y libtesseract-dev  # Install Tesseract development files
!apt-get install -y poppler-utils  # Install poppler-utils for pdf2image

# --- Set the path for Tesseract ---
import pytesseract

# Setting the tesseract path (usually /usr/bin/tesseract in Colab)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# --- Import necessary libraries ---
import os
import re
import csv
import pdfplumber
import pytesseract
import pandas as pd
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

# --- Define regex patterns ---
patterns = {
    'taxable_value': r'Taxable Amount ₹([0-9,]+\.\d{2})',
    'sgst_amount': r'SGST \d+\.\d+% ₹([0-9,]+\.\d{2})',
    'cgst_amount': r'CGST \d+\.\d+% ₹([0-9,]+\.\d{2})',
    'igst_amount': r'IGST \d+\.\d+% ₹([0-9,]+\.\d{2})',
    'sgst_rate(%)': r'SGST (\d+\.\d+)% ₹[0-9,]+\.\d{2}',
    'cgst_rate(%)': r'CGST (\d+\.\d+)% ₹[0-9,]+\.\d{2}',
    'igst_rate(%)': r'IGST (\d+\.\d+)% ₹[0-9,]+\.\d{2}',
    'final_amount': r'Total\s*₹\s*([0-9,]+\.\d{2})',
    'invoice_number': r'Invoice #: (\S+)',
    'invoice_date': r'Invoice Date: (\d{2} \w{3} \d{4})',
    'place_of_supply': r'Place of Supply:\s*(\d+-[A-Z\s]+)',
    'place_of_origin': r'Place of Origin:\s*(\d+-[A-Z\s]+)',
    'gstin_supplier': r'GSTIN\s+([0-9A-Z]{15})',
    'gstin_recipient': r'GSTIN\s+([0-9A-Z]{15})',
    'total_discount': r'Total Discount\s*₹\s*([0-9,]+\.\d{2})'
}

# --- Extract text from PDF using pdfplumber ---
def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages if page.extract_text()])
        if text.strip():  # Check if extracted text is not empty
            return text
        else:
            raise ValueError("Empty text extracted from PDF.")
    except Exception as e:
        print(f"Error reading {pdf_path} with pdfplumber: {e}")
        return None

# --- Extract text using OCR as fallback ---
def extract_text_with_ocr(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        text = ''
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting OCR from {pdf_path}: {e}")
        return None

# --- Function to extract data using regex and calculate weighted average tax rate ---
def extract_data_from_text(text):
    data = {}
    
    # Store multiple values for amounts and rates in lists
    sgst_amounts = re.findall(patterns['sgst_amount'], text)
    cgst_amounts = re.findall(patterns['cgst_amount'], text)
    igst_amounts = re.findall(patterns['igst_amount'], text)

    sgst_rates = re.findall(patterns['sgst_rate(%)'], text)
    cgst_rates = re.findall(patterns['cgst_rate(%)'], text)
    igst_rates = re.findall(patterns['igst_rate(%)'], text)

    # Convert lists into comma-separated strings for CSV storage
    data['sgst_amount'] = ','.join(sgst_amounts) if sgst_amounts else '0'
    data['cgst_amount'] = ','.join(cgst_amounts) if cgst_amounts else '0'
    data['igst_amount'] = ','.join(igst_amounts) if igst_amounts else '0'

    data['sgst_rate(%)'] = ','.join(sgst_rates) if sgst_rates else '0'
    data['cgst_rate(%)'] = ','.join(cgst_rates) if cgst_rates else '0'
    data['igst_rate(%)'] = ','.join(igst_rates) if igst_rates else '0'

    # Sum amounts and rates for tax calculations
    try:
        # Convert amounts from strings to floats
        total_sgst = sum([float(amount.replace(',', '')) for amount in sgst_amounts])
        total_cgst = sum([float(amount.replace(',', '')) for amount in cgst_amounts])
        total_igst = sum([float(amount.replace(',', '')) for amount in igst_amounts])

        # Total tax amount
        total_tax_amount = total_sgst + total_cgst + total_igst
        data['tax_amount'] = f"{total_tax_amount:.2f}"

        # Convert rates from strings to floats
        total_sgst_rate = sum([float(rate) for rate in sgst_rates])
        total_cgst_rate = sum([float(rate) for rate in cgst_rates])
        total_igst_rate = sum([float(rate) for rate in igst_rates])

        # Calculate weighted average tax rate
        weighted_tax_contributions = []
        weighted_rates = []

        # Calculate weighted contributions for SGST
        for i in range(len(sgst_amounts)):
            amount = float(sgst_amounts[i].replace(',', ''))
            rate = float(sgst_rates[i])
            weighted_tax_contributions.append(amount * rate)
            weighted_rates.append(amount)

        # Calculate weighted contributions for CGST
        for i in range(len(cgst_amounts)):
            amount = float(cgst_amounts[i].replace(',', ''))
            rate = float(cgst_rates[i])
            weighted_tax_contributions.append(amount * rate)
            weighted_rates.append(amount)

        # Calculate weighted contributions for IGST
        for i in range(len(igst_amounts)):
            amount = float(igst_amounts[i].replace(',', ''))
            rate = float(igst_rates[i])
            weighted_tax_contributions.append(amount * rate)
            weighted_rates.append(amount)

        # Calculate weighted average rate
        if sum(weighted_rates) > 0:
            weighted_average_rate = sum(weighted_tax_contributions) / sum(weighted_rates)
            data['tax_rate(%)'] = f"{weighted_average_rate:.2f}"
        else:
            data['tax_rate(%)'] = '0'
        
    except ValueError:
        data['tax_amount'] = '0'
        data['tax_rate(%)'] = '0'

    # Extract other fields using regex
    for field, pattern in patterns.items():
        if field not in ['sgst_amount', 'cgst_amount', 'igst_amount', 'sgst_rate(%)', 'cgst_rate(%)', 'igst_rate(%)']:
            match = re.search(pattern, text)
            data[field] = match.group(1) if match else 'not found'

    # Handle "Place of Origin" and "Place of Supply" logic
    place_of_supply = data.get('place_of_supply', 'not found')
    place_of_origin = data.get('place_of_origin', 'not found')

    if place_of_origin == 'not found':
        # If "Place of Origin" is not explicitly found, use "Place of Supply" and note it's inferred
        data['place_of_origin'] = f"{place_of_supply} (inferred from supply)"
    else:
        data['place_of_origin'] = place_of_origin

    # Check if Supplier and Recipient GSTIN are the same
    gstin_supplier = data.get('gstin_supplier', 'not found')
    gstin_recipient = data.get('gstin_recipient', 'not found')

    if gstin_supplier == gstin_recipient:
        data['gstin_recipient'] = 'not present'
        data['gstin_recipient_reason'] = 'Identical to supplier GSTIN, rejected'
    else:
        data['gstin_recipient_reason'] = 'Valid recipient GSTIN'

    return data


# --- Process all PDFs in a folder ---
def process_pdfs_in_folder(folder_path, output_csv_path):
    fieldnames = [
        'taxable_value', 'sgst_amount', 'cgst_amount', 'igst_amount', 'sgst_rate(%)', 'cgst_rate(%)',
        'igst_rate(%)', 'tax_amount', 'tax_rate(%)', 'final_amount', 'invoice_number', 'invoice_date',
        'place_of_supply', 'place_of_origin', 'gstin_supplier', 'gstin_recipient', 'gstin_recipient_reason', 'total_discount'
    ]

    extracted_data_list = []

    # Iterate over all PDF files in the folder
    for pdf_file_name in os.listdir(folder_path):
        if pdf_file_name.endswith('.pdf'):
            pdf_file_path = os.path.join(folder_path, pdf_file_name)
            print(f"Processing: {pdf_file_name}")

            # Read the PDF content
            text = extract_text_from_pdf(pdf_file_path)

            # If PDF reading fails or text is empty, use OCR
            if not text:
                text = extract_text_with_ocr(pdf_file_path)

            if text:
                extracted_data = extract_data_from_text(text)
                extracted_data_list.append(extracted_data)
            else:
                print(f"Failed to extract text from {pdf_file_name}")

    # Save the extracted data to CSV
    df = pd.DataFrame(extracted_data_list)
    df.to_csv(output_csv_path, index=False)
    print(f"Data saved to {output_csv_path}")

# --- Run the process in the /content folder ---
folder_path = '/content/'  # Colab's default directory where uploaded files are placed
output_csv_path = os.path.join(folder_path, 'extracted_invoice_data3.csv')

# Run the processing function
process_pdfs_in_folder(folder_path, output_csv_path)

# Uncomment below if running in Google Colab to download the CSV file:
# from google.colab import files
# files.download(output_csv_path)