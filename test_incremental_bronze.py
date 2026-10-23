from deltalake import DeltaTable

from api.services.manifest_service import (
    find_by_source_id,
)

from api.services.minio_service import (
    download_to_temp,
    cleanup_temp_file,
)

from ingest_bronze import (
    ingest_single_document,
    manifest_already_ingested,
)


DOCUMENT_ID = "SRC-10"
VERSION = "v2.0"
DELTA_PATH = "delta-tables/bronze_raw_text"


# ============================================================
# 1. BRONZE BEFORE
# ============================================================

before_df = DeltaTable(
    DELTA_PATH
).to_pandas()

before_total = len(
    before_df
)

before_src10 = len(
    before_df[
        before_df["document_id"]
        == DOCUMENT_ID
    ]
)

print("=" * 60)
print("BEFORE")
print("=" * 60)

print(
    "Bronze total:",
    before_total
)

print(
    "SRC-10 rows:",
    before_src10
)


# ============================================================
# 2. FIND MANIFEST ROW
# ============================================================

rows = find_by_source_id(
    DOCUMENT_ID
)

matches = [
    row
    for row in rows
    if row["version"] == VERSION
]

if len(matches) != 1:

    raise RuntimeError(
        f"Cần đúng 1 manifest row "
        f"cho {DOCUMENT_ID} {VERSION}, "
        f"nhưng tìm thấy {len(matches)}."
    )

manifest_row = matches[0]

manifest_id = (
    manifest_row["manifest_id"]
)

file_name = (
    manifest_row["file_name"]
)

storage_path = (
    manifest_row["storage_path"]
)


print()
print("=" * 60)
print("TARGET")
print("=" * 60)

print(
    "document_id :",
    DOCUMENT_ID
)

print(
    "version     :",
    VERSION
)

print(
    "manifest_id :",
    manifest_id
)

print(
    "file_name   :",
    file_name
)

print(
    "storage_path:",
    storage_path
)


# ============================================================
# 3. IDEMPOTENCY CHECK
# ============================================================

already = (
    manifest_already_ingested(
        manifest_id
    )
)

print()
print(
    "Already ingested:",
    already
)

if already:

    raise RuntimeError(
        f"{manifest_id} đã tồn tại "
        "trong Bronze. Dừng để tránh duplicate."
    )


# ============================================================
# 4. DOWNLOAD FROM MINIO
# ============================================================

local_path = None

try:

    local_path = (
        download_to_temp(
            storage_path
        )
    )

    print()
    print(
        "Downloaded:",
        local_path
    )

    # ========================================================
    # 5. INGEST ONLY SRC-10 V2
    # ========================================================

    result = (
        ingest_single_document(
            document_id=
                DOCUMENT_ID,

            manifest_id=
                manifest_id,

            file_name=
                file_name,

            local_file_path=
                local_path,
        )
    )

    print()
    print("=" * 60)
    print("INGEST RESULT")
    print("=" * 60)

    print(
        result
    )

finally:

    if local_path:

        cleanup_temp_file(
            local_path
        )


# ============================================================
# 6. BRONZE AFTER
# ============================================================

after_df = DeltaTable(
    DELTA_PATH
).to_pandas()

after_total = len(
    after_df
)

after_src10 = len(
    after_df[
        after_df["document_id"]
        == DOCUMENT_ID
    ]
)

print()
print("=" * 60)
print("AFTER")
print("=" * 60)

print(
    "Bronze total:",
    after_total
)

print(
    "SRC-10 rows:",
    after_src10
)

print(
    "Rows added:",
    after_total - before_total
)


# ============================================================
# 7. VALIDATION
# ============================================================

expected_added = (
    result["records"]
)

actual_added = (
    after_total
    - before_total
)

if actual_added != expected_added:

    raise RuntimeError(
        "Số row Bronze tăng không khớp "
        "số segment parser."
    )

if after_src10 != expected_added:

    raise RuntimeError(
        "Số row SRC-10 không khớp "
        "số segment đã ingest."
    )

print()
print(
    "✅ INCREMENTAL BRONZE TEST PASS"
)