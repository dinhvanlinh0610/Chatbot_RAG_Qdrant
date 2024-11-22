import pdfplumber
import pandas as pd
import re

pdf_path = 'C:\\Users\\linh.dinh\\Downloads\\code\\Chat\Women’s Charter 1961.pdf'



with pdfplumber.open(pdf_path) as pdf:
    all_text = ""
    for page in pdf.pages:
        all_text += page.extract_text()

print(all_text)
#     # Bước 2: Phân tích và tái cấu trúc nội dung