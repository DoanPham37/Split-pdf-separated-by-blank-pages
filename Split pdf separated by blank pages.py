import fitz
import os

def is_blank_page_pdf(pdf_document, page_number):
    page = pdf_document.load_page(page_number)
    pix = page.get_pixmap()
    white_pixels = 0
    total_pixels = pix.width * pix.height
    for x in range(pix.width):
        for y in range(pix.height):
            pixel = pix.pixel(x, y)
            if pixel == (255, 255, 255):  # Màu trắng có mã màu (255, 255, 255)
                white_pixels += 1
    white_percentage = white_pixels / total_pixels * 100
    return white_percentage > 99  # Xác định trang có trống dựa trên tỷ lệ pixel trắng

def find_separator_indices_and_number_total_pages(pdf):
    separators = []
    pdf_document = fitz.open(pdf)
    for i in range(pdf_document.page_count):
        if is_blank_page_pdf(pdf_document, i):
            separators.append(i)
    return (separators, pdf_document.page_count)

def create_page_ranges(cuts, num_total_pages):
    pages = list(range(num_total_pages))
    slices = [
        (lhs, rhs)
        for lhs, rhs in zip([0, *cuts], [*cuts, num_total_pages])
    ]
    return slices

def do_split(input_doc, ranges):
    pdf_document = fitz.open(input_doc)
    for i, part in enumerate(ranges, start=1):
        outdata = fitz.open()
        non_empty_page = False
        for pagenum in range(*part):
            if not is_blank_page_pdf(pdf_document, pagenum):  
                outdata.insert_pdf(pdf_document, from_page=pagenum, to_page=pagenum)
                non_empty_page = True
        if non_empty_page:
            outdata_path = new_document_name(input_doc, i)
            outdata.save(outdata_path)
        outdata.close()

def new_document_name(input_doc, i):
    file_name, extension = os.path.splitext(input_doc)
    return f"{file_name}_part_{i}{extension}"

def split_document(input_doc):
    if not os.path.isfile(input_doc):
        print(f"File '{input_doc}' not found")
        return

    info = find_separator_indices_and_number_total_pages(input_doc)

    if not info[0] or info[1] <= 1:
        print(f"No separators found in '{input_doc}'")
        return

    page_ranges = create_page_ranges(info[0], info[1])

    do_split(input_doc, page_ranges)

def process_directory(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".pdf"):
                file_path = os.path.join(root, file_name)
                split_document(file_path)

folder_path = r'C:\Users\PC\Desktop\'  # Thay đổi đường dẫn đến thư mục chứa tất cả các tệp PDF cần chia
process_directory(folder_path)
