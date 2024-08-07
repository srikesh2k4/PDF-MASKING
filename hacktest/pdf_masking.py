import fitz  # PyMuPDF
import spacy
import phonenumbers
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Load the custom spaCy model
try:
    nlp = spacy.load('custom_ner_model')
except OSError:
    nlp = spacy.load('en_core_web_sm')

def extract_text_and_positions_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_and_positions = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        for b in blocks:
            block_text = b[4]
            rect = fitz.Rect(b[:4])
            text_and_positions.append((block_text, rect, page_num))
    return text_and_positions, doc

def mask_sensitive_information(text_and_positions, doc):
    sensitive_info = []
    for text, rect, page_num in text_and_positions:
        doc_page = nlp(text)
        for ent in doc_page.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'EMAIL', 'PHONE_NUMBER']:
                sensitive_info.append((ent.text, rect, page_num))

        # Detect phone numbers using phonenumbers library
        phone_numbers = phonenumbers.PhoneNumberMatcher(text, "US")
        for match in phone_numbers:
            phone_number = text[match.start:match.end]
            sensitive_info.append((phone_number, rect, page_num))

        # Detect emails using regex
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        emails = re.findall(email_pattern, text)
        for email in emails:
            sensitive_info.append((email, rect, page_num))

        # Detect "Name:" and "Phone Number:" fields
        name_pattern = r'Name\s*:\s*\w+'
        names = re.findall(name_pattern, text)
        for name in names:
            sensitive_info.append((name, rect, page_num))

        phone_pattern = r'Phone\s*Number\s*:\s*\d+|Ph\s*no\s*:\s*\d+'
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            sensitive_info.append((phone, rect, page_num))

    for sensitive_text, rect, page_num in sensitive_info:
        page = doc.load_page(page_num)
        page.add_redact_annot(rect, text='', fill=(0, 0, 0))
        page.apply_redactions()

def select_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        entry_pdf_path.delete(0, tk.END)
        entry_pdf_path.insert(0, file_path)

def process_pdf():
    pdf_path = entry_pdf_path.get()
    if not pdf_path:
        messagebox.showerror("Error", "Please select a PDF file")
        return

    text_and_positions, doc = extract_text_and_positions_from_pdf(pdf_path)
    mask_sensitive_information(text_and_positions, doc)

    output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if output_pdf_path:
        doc.save(output_pdf_path)
        messagebox.showinfo("Success", "Masked PDF created successfully!")

# Create GUI
root = tk.Tk()
root.title("PDF Masking Tool By Sriram ")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

label_pdf_path = tk.Label(frame, text="PDF File:")
label_pdf_path.grid(row=0, column=0, sticky=tk.W)

entry_pdf_path = tk.Entry(frame, width=50)
entry_pdf_path.grid(row=0, column=1, padx=5, pady=5)

button_browse = tk.Button(frame, text="Browse...", command=select_pdf)
button_browse.grid(row=0, column=2, padx=5, pady=5)

button_process = tk.Button(frame, text="Process PDF", command=process_pdf)
button_process.grid(row=1, column=0, columnspan=3, pady=10)

root.mainloop()


# COPYRIGHTS Kotipalli Srikesh RA221003010979 SRMIST
