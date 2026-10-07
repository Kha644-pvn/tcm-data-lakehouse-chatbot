import os
import pandas as pd
from datetime import datetime, timezone
from deltalake import write_deltalake
from parsers import parse_file


MANIFEST_PATH = "bronze/_manifest/data_manifest_v1.csv"
DELTA_PATH = "delta-tables/bronze_raw_text"


# Đọc manifest v1
manifest_df = pd.read_csv(MANIFEST_PATH)

records = []

for _, row in manifest_df.iterrows():

    file_name = row["file_name"]
    manifest_id = row["manifest_id"]
    storage_path = row["storage_path"]

    # MIRAGE là benchmark riêng, không đưa vào Bronze YHCT raw text
    if row["dataset_group"] != "yhct-corpus":
        print(f"⏭️ Bỏ qua benchmark: {file_name}")
        continue

    # Dùng storage_path trong manifest, không dùng downloads/
    file_path = storage_path

    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        continue

    try:
        parsed = parse_file(file_path)

        for item in parsed:
            records.append({
                "document_id": row["source_id"],
                "manifest_id": manifest_id,
                "file_name": file_name,
                "page_or_section": item["page_or_section"],
                "raw_text": item["raw_text"],
                "ingest_timestamp": datetime.now(timezone.utc).isoformat(),
            })

        print(
            f"✅ Đã xử lý: {file_name} "
            f"({len(parsed)} đoạn)"
        )

    except Exception as e:
        print(f"❌ Lỗi khi xử lý {file_name}: {e}")


# Không ghi Delta nếu không có dữ liệu
if not records:
    raise RuntimeError(
        "Không có dữ liệu Bronze để ghi. "
        "Kiểm tra storage_path và parser."
    )


bronze_df = pd.DataFrame(records)

print()
print("========================================")
print("Bronze ingestion hoàn tất")
print("Số records:", len(bronze_df))
print("Số documents:", bronze_df["document_id"].nunique())
print("========================================")

write_deltalake(
    DELTA_PATH,
    bronze_df,
    mode="overwrite"
)

print(f"✅ Delta Table đã ghi tại: {DELTA_PATH}")