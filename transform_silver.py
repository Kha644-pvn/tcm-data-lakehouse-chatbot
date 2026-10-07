from datetime import datetime, timezone

import pandas as pd
from deltalake import DeltaTable, write_deltalake

from cleaning import clean_text, is_valid_passage, deduplicate


# ============================================================
# PATH
# ============================================================

BRONZE_PATH = r".\delta-tables\bronze_raw_text"
SILVER_PATH = r".\delta-tables\silver_cleaned"


# ============================================================
# 1. Đọc Bronze
# ============================================================

print("=" * 70)
print("ĐỌC BRONZE")
print("=" * 70)

bronze_table = DeltaTable(BRONZE_PATH)
df = bronze_table.to_pandas()

print(f"Số dòng Bronze: {len(df)}")
print(f"Số document: {df['document_id'].nunique()}")
print(f"Số file: {df['file_name'].nunique()}")


# ============================================================
# 2. Làm sạch text
# ============================================================

print("\n" + "=" * 70)
print("CLEANING")
print("=" * 70)

df["cleaned_text"] = df["raw_text"].apply(clean_text)

print("Đã tạo cleaned_text.")


# ============================================================
# 3. Kiểm tra passage hợp lệ
# ============================================================

df["is_valid"] = df["cleaned_text"].apply(
    is_valid_passage
)

invalid_count = (~df["is_valid"]).sum()

print(f"Passage không hợp lệ: {invalid_count}")


# Chỉ giữ passage hợp lệ
df = df[df["is_valid"]].copy()

# Không cần cột is_valid trong Silver
df.drop(columns=["is_valid"], inplace=True)


# ============================================================
# 4. Deduplicate
# ============================================================

print("\n" + "=" * 70)
print("DEDUPLICATION")
print("=" * 70)

df = deduplicate(
    df,
    text_column="cleaned_text"
)


# ============================================================
# 5. Thêm metadata Silver
# ============================================================

df["silver_processed_at"] = datetime.now(
    timezone.utc
).isoformat()


# ============================================================
# 6. Sắp xếp cột
# ============================================================

preferred_columns = [
    "document_id",
    "manifest_id",
    "file_name",
    "page_or_section",
    "raw_text",
    "cleaned_text",
    "ingest_timestamp",
    "silver_processed_at",
]

existing_columns = [
    col for col in preferred_columns
    if col in df.columns
]

remaining_columns = [
    col for col in df.columns
    if col not in existing_columns
]

df = df[
    existing_columns + remaining_columns
]


# ============================================================
# 7. Kiểm tra kết quả trước khi ghi
# ============================================================

print("\n" + "=" * 70)
print("SILVER PREVIEW")
print("=" * 70)

print(f"Số dòng Silver: {len(df)}")
print(f"Số document: {df['document_id'].nunique()}")
print(f"Số file: {df['file_name'].nunique()}")

print("\nTHEO FILE:")

print(
    df.groupby("file_name")
      .size()
      .to_string()
)


# ============================================================
# 8. Ghi Delta Silver
# ============================================================

print("\n" + "=" * 70)
print("GHI SILVER DELTA")
print("=" * 70)

write_deltalake(
    SILVER_PATH,
    df,
    mode="overwrite"
)

print(f"Đã ghi Silver Delta tại: {SILVER_PATH}")


# ============================================================
# 9. Hoàn tất
# ============================================================

print("\n" + "=" * 70)
print("HOÀN TẤT SILVER")
print("=" * 70)

print(f"Bronze records : {len(bronze_table.to_pandas())}")
print(f"Silver records : {len(df)}")
print(f"Documents      : {df['document_id'].nunique()}")
print(f"Files          : {df['file_name'].nunique()}")