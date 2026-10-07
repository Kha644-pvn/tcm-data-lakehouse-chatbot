import pymupdf
from bs4 import BeautifulSoup
from docx import Document as DocxDocument

import pytesseract
from PIL import Image
from io import BytesIO


# ============================================================
# TCVN3 (ABC) -> Unicode
# Dùng cho các font legacy như VnArial, VnTime, VnCenturySchoolbook...
# ============================================================

TCVN3TAB = (
    "µ¸¶·¹¨»¾¼½Æ©ÇÊÈÉË®ÌÐÎÏÑªÒÕÓÔÖ×ÝØÜÞß"
    "ãáâä«åèæçé¬êíëìîïóñòô­õøö÷ùúýûüþ¡¢§£¤¥¦"
)

UNICODETAB = (
    "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệ"
    "ìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữự"
    "ỳýỷỹỵĂÂĐÊÔƠƯ"
)

TCVN3_MAP = dict(zip(TCVN3TAB, UNICODETAB))


# ============================================================
# Legacy Vietnamese fonts
# ============================================================

LEGACY_VIETNAMESE_FONT_PREFIXES = (
    "VnArial",
    "VnTime",
    "VnCentury",
    "VnHelvet",
    "VnTahoma",
    "VnCourier",
    "VnBookman",
    "VnPalatino",
)


def tcvn3_to_unicode(text):
    """Chuyển chuỗi TCVN3/ABC sang Unicode."""
    return "".join(TCVN3_MAP.get(char, char) for char in text)


def is_legacy_vietnamese_font(font_name):
    """Kiểm tra font có thuộc nhóm font TCVN3/ABC hay không."""
    if not font_name:
        return False

    return font_name.startswith(LEGACY_VIETNAMESE_FONT_PREFIXES)


# ============================================================
# Extract PDF text
# ============================================================

def extract_pdf_page(page):
    """
    Trích xuất text theo block -> line -> span.

    Mỗi span có font riêng, cần biết span nào dùng font TCVN3
    để chuyển sang Unicode.
    """
    data = page.get_text("dict")

    blocks_text = []

    for block in data.get("blocks", []):
        if "lines" not in block:
            continue

        lines_text = []

        for line in block["lines"]:
            line_parts = []

            for span in line.get("spans", []):
                text = span.get("text", "")
                font_name = span.get("font", "")

                if is_legacy_vietnamese_font(font_name):
                    text = tcvn3_to_unicode(text)

                line_parts.append(text)

            line_text = "".join(line_parts)

            if line_text.strip():
                lines_text.append(line_text)

        if lines_text:
            blocks_text.append("\n".join(lines_text))

    return "\n\n".join(blocks_text)


# ============================================================
# OCR
# ============================================================

def ocr_page(page, dpi=300):
    """
    OCR một trang PDF scan bằng Tesseract.
    Sử dụng tiếng Việt + tiếng Anh.
    """

    zoom = dpi / 72
    matrix = pymupdf.Matrix(zoom, zoom)

    pix = page.get_pixmap(
        matrix=matrix,
        alpha=False
    )

    image = Image.open(
        BytesIO(pix.tobytes("png"))
    )

    text = pytesseract.image_to_string(
        image,
        lang="vie+eng"
    )

    return text.strip()


# ============================================================
# Kiểm tra text layer có phải watermark hay không
# ============================================================

def is_watermark_only(text):
    """
    Kiểm tra text layer có chỉ chứa watermark hay không.

    Trường hợp đã xác nhận trong SRC-02 và SRC-03:
        www.thuvien247.net
    """

    if not text:
        return True

    normalized = " ".join(text.lower().split())

    watermark_patterns = {
        "www.thuvien247.net",
    }

    return normalized in watermark_patterns


# ============================================================
# PDF parser
# ============================================================

def parse_pdf(filepath):
    """
    Parse PDF:

    - PDF có text layer thực:
        PyMuPDF + TCVN3

    - PDF scan hoặc text layer chỉ là watermark:
        OCR bằng Tesseract
    """

    doc = pymupdf.open(filepath)
    results = []

    try:
        for page_num, page in enumerate(doc, start=1):

            # --------------------------------------------------
            # 1. Thử lấy text layer
            # --------------------------------------------------
            text = page.get_text("text").strip()

            # --------------------------------------------------
            # 2. Nếu text layer thực sự có nội dung
            # --------------------------------------------------
            if text and not is_watermark_only(text):

                parsed_page = extract_pdf_page(page)

                if parsed_page.strip():
                    results.append({
                        "page_or_section": f"trang {page_num}",
                        "raw_text": parsed_page
                    })

            # --------------------------------------------------
            # 3. Không có text layer hoặc chỉ có watermark
            #    -> OCR
            # --------------------------------------------------
            else:
                print(
                    f"OCR: {filepath} - trang {page_num}"
                )

                ocr_text = ocr_page(page)

                if ocr_text:
                    results.append({
                        "page_or_section": f"trang {page_num}",
                        "raw_text": ocr_text
                    })

    finally:
        doc.close()

    return results


# ============================================================
# HTML parser
# ============================================================

def parse_html(filepath):
    """Trả về list theo từng heading/section."""

    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    results = []

    for i, section in enumerate(
        soup.find_all(["h1", "h2", "h3", "p"]),
        start=1
    ):
        text = section.get_text(strip=True)

        if text:
            results.append({
                "page_or_section": f"mục {i}",
                "raw_text": text
            })

    return results


# ============================================================
# DOCX parser
# ============================================================

def parse_docx(filepath):
    """Trả về list theo từng đoạn văn (paragraph)."""

    doc = DocxDocument(filepath)
    results = []

    for i, para in enumerate(doc.paragraphs, start=1):

        if para.text.strip():
            results.append({
                "page_or_section": f"đoạn {i}",
                "raw_text": para.text
            })

    return results


# ============================================================
# File router
# ============================================================

def parse_file(filepath):
    """Router: chọn parser theo phần mở rộng file."""

    ext = filepath.lower().split(".")[-1]

    if ext == "pdf":
        return parse_pdf(filepath)

    elif ext in ("html", "htm"):
        return parse_html(filepath)

    elif ext == "docx":
        return parse_docx(filepath)

    else:
        raise ValueError(
            f"Định dạng không hỗ trợ: {ext}"
        )