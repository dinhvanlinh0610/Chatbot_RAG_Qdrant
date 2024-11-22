import pandas as pd
import re
import docx2txt

def extract_docx_to_csv(docx_path, output_csv_path):
    """
    Trích xuất văn bản từ file DOCX và lưu vào file CSV.

    Args:
        docx_path (str): Đường dẫn đến file DOCX cần trích xuất.
        output_csv_path (str): Đường dẫn đến file CSV để lưu dữ liệu trích xuất.

    Returns:
        None
    """
    # Bước 1: Mở tệp DOCX và trích xuất văn bản
    all_text = docx2txt.process(docx_path)

    # Bước 2: Phân tích và tái cấu trúc nội dung
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
#     docx_path = '/content/VanBanGoc_52.2014.QH13 (3).docx'  # Thay đổi đường dẫn đến tệp DOCX của bạn
#     output_csv_path = 'van_ban_phap_luat_10.csv'
#     extract_docx_to_csv(docx_path, output_csv_path)
