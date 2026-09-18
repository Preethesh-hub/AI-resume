import io
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

def parse_file(file_bytes: bytes, filename: str) -> str:
    """Parses a file and extracts its text based on the extension."""
    if filename.lower().endswith(".pdf"):
        return parse_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        return parse_docx(file_bytes)
    elif filename.lower().endswith(".txt"):
        return parse_txt(file_bytes)
    elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return parse_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def parse_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    # Fallback to OCR if standard parsing yields very little text (likely a scanned PDF)
    if len(text.strip()) < 50:
        try:
            images = convert_from_bytes(file_bytes)
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img) + "\n"
            text = ocr_text
        except Exception as e:
            print(f"OCR failed for PDF. Make sure Tesseract & Poppler are installed: {e}")
            
    return text

def parse_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def parse_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")

def parse_image(file_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"OCR failed for image: {e}")
        return ""
