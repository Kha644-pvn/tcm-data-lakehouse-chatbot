import re


def clean_text(raw_text):
    """
    Làm sạch văn bản Bronze để tạo Silver.

    Nguyên tắc:
    - Không thay đổi nội dung chữ.
    - Không tự sửa lỗi OCR.
    - Giữ cấu trúc đoạn văn.
    - Loại ký tự điều khiển và khoảng trắng dư thừa.
    """

    if raw_text is None:
        return ""

    text = str(raw_text)

    # Chuẩn hóa line ending
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Loại một số ký tự điều khiển nhưng giữ \n và \t
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Chuẩn hóa tab thành khoảng trắng
    text = text.replace("\t", " ")

    # Xóa khoảng trắng ở cuối mỗi dòng
    text = "\n".join(
        line.rstrip()
        for line in text.split("\n")
    )

    # Không để quá 2 dòng trống liên tiếp
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Loại khoảng trắng thừa trong từng dòng
    lines = []

    for line in text.split("\n"):
        line = re.sub(r" {2,}", " ", line)
        lines.append(line.strip())

    text = "\n".join(lines).strip()

    return text


def is_valid_passage(cleaned_text, min_length=5):
    """
    Kiểm tra passage có nội dung hay không.

    Không dùng min_length=20 vì các thuật ngữ YHCT
    ngắn vẫn có thể có giá trị.
    """

    if not cleaned_text:
        return False

    return len(cleaned_text.strip()) >= min_length


def deduplicate(df, text_column="cleaned_text"):
    """
    Loại các passage trùng hoàn toàn.
    """

    before = len(df)

    df = df.drop_duplicates(
        subset=[text_column],
        keep="first"
    ).copy()

    after = len(df)

    print(f"Đã loại {before - after} dòng trùng lặp.")

    return df