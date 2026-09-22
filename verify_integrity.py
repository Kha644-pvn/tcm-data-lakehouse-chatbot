# Tạo script kiểm tra hash
import hashlib
import os
from datetime import datetime
import pandas as pd
# ============================================================
# CẤU HÌNH
# ============================================================
MANIFEST_FILE = "bronze/_manifest/data_manifest_v1.csv"
LOG_FILE = "bronze/_manifest/integrity_test_log.txt"
# ============================================================
# TÍNH SHA-256
# ============================================================
def compute_sha256(filepath):
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()
# ============================================================
# KIỂM TRA 1 FILE
# ============================================================
def verify_integrity(filepath, expected_hash):
    if not os.path.isfile(filepath):
        print(f"✗ KHÔNG TÌM THẤY FILE: {filepath}")
        return False, "missing"

    actual_hash = compute_sha256(filepath)

    if actual_hash != expected_hash:
        print(f"⚠ CẢNH BÁO: File đã thay đổi!")
        print(f"  File: {filepath}")
        print(f"  Manifest hash: {expected_hash}")
        print(f"  Actual hash:   {actual_hash}")

        return False, "modified"

    print(f"✓ File toàn vẹn: {filepath}")
    return True, "verified"


# ============================================================
# ĐỌC MANIFEST
# ============================================================

df = pd.read_csv(MANIFEST_FILE)

print("=" * 70)
print("KIỂM THỬ TÍNH TOÀN VẸN DỮ LIỆU")
print("=" * 70)

log_lines = []

log_lines.append("=" * 70)
log_lines.append("INTEGRITY TEST LOG")
log_lines.append(
    f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
log_lines.append("=" * 70)


# ============================================================
# KIỂM TRA TỪNG FILE
# ============================================================

total = 0
verified = 0
modified = 0
missing = 0

for _, row in df.iterrows():

    total += 1

    # storage_path dạng:
    # bronze/mirage-medrag/v1/xxx.json
    # bronze/yhct-corpus/SRC-03_giaotrinh/xxx.pdf

    storage_path = str(row["storage_path"])

    # Chuyển thành đường dẫn local
    local_path = storage_path.replace("/", os.sep)

    expected_hash = str(row["file_hash_sha256"])

    result, status = verify_integrity(
        local_path,
        expected_hash
    )

    if status == "verified":
        verified += 1
        symbol = "✓"

    elif status == "modified":
        modified += 1
        symbol = "⚠"

    else:
        missing += 1
        symbol = "✗"

    log_lines.append(
        f"{symbol} {row['manifest_id']} | "
        f"{row['file_name']} | "
        f"{status} | "
        f"{local_path}"
    )


# ============================================================
# TỔNG KẾT
# ============================================================

summary = [
    "",
    "=" * 70,
    "SUMMARY",
    "=" * 70,
    f"Total files    : {total}",
    f"Verified       : {verified}",
    f"Modified       : {modified}",
    f"Missing        : {missing}",
]

for line in summary:
    print(line)
    log_lines.append(line)


# ============================================================
# LƯU LOG
# ============================================================

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print()
print(f"Log đã lưu tại: {LOG_FILE}")