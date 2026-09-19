import hashlib
import os
from datetime import date
import pandas as pd
# ============================================================
# CẤU HÌNH
# ============================================================
BRONZE_DIR = "./bronze"
MANIFEST_DIR = "./bronze/_manifest"
OUTPUT_FILE = "./bronze/_manifest/data_manifest_v1.csv"
DOWNLOADED_BY = "Kha"
VERSION = "v1.0"
# ============================================================
# THÔNG TIN SOURCE REGISTRY
# ============================================================
# IMPORTANT:
# - MIRAGE: có thể điền ngay vì bạn đã đọc LICENSE
# - YHCT: phải thay bằng thông tin chính xác từ Source Registry
#   của nhóm, không tự đoán.
#
# Key phải trùng source_id.
# ============================================================
SOURCE_REGISTRY = {
    "MIRAGE": {
        "source_url": "https://github.com/Teddy-XiongGZ/MIRAGE",
        "license_status": "Public Domain - U.S. Government Work",
    },

    "SRC-02": {
        "source_url": "",
        "license_status": "",
    },

    "SRC-03": {
        "source_url": "",
        "license_status": "",
    },

    "SRC-05": {
        "source_url": "",
        "license_status": "",
    },
}
# ============================================================
# HÀM TÍNH SHA-256
# ============================================================
def compute_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
# ============================================================
# LẤY THÔNG TIN SOURCE TỪ ĐƯỜNG DẪN
# ============================================================
def determine_source_and_group(relative_path):
    parts = relative_path.replace("\\", "/").split("/")
    # Ví dụ:
    # mirage-medrag/v1/file.json
    if parts[0] == "mirage-medrag":
        source_id = "MIRAGE"
        dataset_group = "mirage-medrag"

    # Ví dụ:
    # yhct-corpus/SRC-03_giaotrinh/file.pdf
    elif parts[0] == "yhct-corpus":
        dataset_group = "yhct-corpus"

        if len(parts) >= 2:
            folder_name = parts[1]
            source_id = folder_name.split("_")[0]
        else:
            source_id = ""

    else:
        source_id = ""
        dataset_group = ""

    return source_id, dataset_group
# ============================================================
# TẠO MANIFEST
# ============================================================
manifest_rows = []
manifest_id = 1
for root, _, files in os.walk(BRONZE_DIR):
    # Không quét chính thư mục _manifest
    normalized_root = root.replace("\\", "/")
    if "/_manifest" in normalized_root:
        continue
    for filename in files:

        filepath = os.path.join(root, filename)

        if not os.path.isfile(filepath):
            continue

        # Đường dẫn tương đối so với bronze/
        relative_path = os.path.relpath(
            filepath,
            BRONZE_DIR
        ).replace("\\", "/")
        # Xác định source + dataset group
        source_id, dataset_group = determine_source_and_group(
            relative_path
        )
        # Bỏ qua file nếu không xác định được nhóm dữ liệu
        if not source_id:
            print(f"Bỏ qua file không xác định source: {filepath}")
            continue

        # SHA-256
        file_hash = compute_sha256(filepath)

        # Dung lượng
        file_size = os.path.getsize(filepath)

        # Source Registry
        source_info = SOURCE_REGISTRY.get(
            source_id,
            {
                "source_url": "",
                "license_status": "",
            }
        )

        source_url = source_info["source_url"]
        license_status = source_info["license_status"]

        # Trạng thái
        if source_url and license_status:
            status = "verified"
        else:
            status = "pending_license_review"

        manifest_rows.append({
            "manifest_id": f"MF-{manifest_id:04d}",
            "file_name": filename,
            "source_id": source_id,
            "source_url": source_url,
            "license_status": license_status,
            "file_hash_sha256": file_hash,
            "file_size_bytes": file_size,
            "download_date": str(date.today()),
            "downloaded_by": DOWNLOADED_BY,
            "storage_path": f"bronze/{relative_path}",
            "dataset_group": dataset_group,
            "version": VERSION,
            "status": status,
        })

        manifest_id += 1


# ============================================================
# TẠO DATAFRAME
# ============================================================

df = pd.DataFrame(manifest_rows)


# ============================================================
# TẠO THƯ MỤC MANIFEST NẾU CHƯA CÓ
# ============================================================

os.makedirs(MANIFEST_DIR, exist_ok=True)


# ============================================================
# XUẤT CSV
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# IN KẾT QUẢ
# ============================================================

print("=" * 60)
print("ĐÃ TẠO DATA MANIFEST")
print("=" * 60)

print(f"Số dòng manifest: {len(df)}")
print(f"File output: {OUTPUT_FILE}")

if not df.empty:
    print("\nPhân bố dataset:")
    print(df["dataset_group"].value_counts())

    print("\nPhân bố status:")
    print(df["status"].value_counts())