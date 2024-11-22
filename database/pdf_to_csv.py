import pdfplumber
import pandas as pd
import re

def extract_pdf_to_csv(pdf_path, output_csv_path):
    """
    Trích xuất văn bản từ file PDF và lưu vào file CSV.

    Args:
        pdf_path (str): Đường dẫn đến file PDF cần trích xuất.
        output_csv_path (str): Đường dẫn đến file CSV để lưu dữ liệu trích xuất.

    Returns:
        None
    """
    # Bước 1: Mở tệp PDF và trích xuất văn bản
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text()

    # Bước 2: Phân tích và tái cấu trúc nội dung
    """ 1 văn bản pháp luật thường sẽ có cấu trúc như sau:
    Chương: Chia văn bản thành các phần chính, mỗi chương có thể bao gồm nhiều mục.
    Mục: Các phần nhỏ hơn trong chương, định nghĩa các khái niệm và quy định chi tiết.
    Điều: Quy định cụ thể, điều khoản của văn bản pháp luật.
    Khoản: Các phần nhỏ hơn trong điều, nếu cần thiết.
    Điểm: Các phân đoạn nhỏ hơn trong khoản, nếu cần thiết.
    """
    chapters = []
    items = []
    articles = []
    contents = []
    parts = []

    current_chapter = ""
    current_item = ""
    current_article = ""
    current_content = ""
    current_part = ""

    for line in all_text.split("\n"):
        line = line.strip()
        if line.startswith("Chương"):
            # Lưu chương hiện tại nếu có
            if current_chapter:
                chapters.append(current_chapter)
                items.append(current_item)
                articles.append(current_article)
                contents.append(current_content)
                parts.append(current_part)

            current_chapter = line
            current_item = ""
            current_article = ""
            current_content = ""
            current_part = ""
        elif line.startswith("Mục"):
            if current_item:
                chapters.append(current_chapter)
                items.append(current_item)
                articles.append(current_article)
                contents.append(current_content)
                parts.append(current_part)

            current_item = line
            current_article = ""
            current_content = ""
            current_part = ""

        elif line.startswith("Điều"):
            if current_article:
                chapters.append(current_chapter)
                items.append(current_item)
                articles.append(current_article)
                contents.append(current_content)
                parts.append(current_part)

            current_article = line
            current_content = ""
            current_part = ""
        
        elif re.match(r'^\d+(\.\s+|\.)', line):
            if current_article:
                # Lưu thông tin hiện tại trước khi bắt đầu mục mới
                chapters.append(current_chapter)
                items.append(current_item)
                articles.append(current_article)
                contents.append(current_content)
                parts.append(current_part)

            # Tách số mục và nội dung
            match = re.match(r'^(\d+)(\.\s+|\.)\s*(.*)', line)
            if match:
                current_part = match.group(1)  # Số của mục
                current_content = match.group(3)  # Nội dung mục

        else:
            # Nếu có nội dung đang được xử lý, thêm nó vào nội dung hiện tại
            if current_article:
                current_content += " " + line

    # Thêm chương cuối cùng
    if current_article:
        chapters.append(current_chapter)
        items.append(current_item)
        articles.append(current_article)
        contents.append(current_content)
        parts.append(current_part)

    # Bước 3: Tạo DataFrame và lưu thành file CSV
    data = {
        "Chương": chapters,
        "Mục": items,
        "Điều": articles,
        "Phần": parts,
        "Nội dung": contents
    }

    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

    print(f'Tệp CSV đã được lưu tại: {output_csv_path}')

# Ví dụ sử dụng hàm
# if __name__ == "__main__":
#     pdf_path = '/content/VanBanGoc_52.2014.QH13.pdf'
#     output_csv_path = 'van_ban_phap_luat_5.csv'
#     extract_pdf_to_csv(pdf_path, output_csv_path)
