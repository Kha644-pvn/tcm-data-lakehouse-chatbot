from deltalake import DeltaTable

from api.services.manifest_service import (
    find_by_source_id,
)

from transform_silver import (
    manifest_already_in_silver,
    transform_single_document,
)


DOCUMENT_ID = "SRC-10"
VERSION = "v2.0"

SILVER_PATH = (
    r".\delta-tables\silver_cleaned"
)


# ============================================================
# BEFORE
# ============================================================

before_df = DeltaTable(
    SILVER_PATH
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
    "Silver total:",
    before_total
)

print(
    "SRC-10 rows:",
    before_src10
)


# ============================================================
# FIND MANIFEST V2
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
        f"Cần đúng 1 manifest "
        f"cho {DOCUMENT_ID} {VERSION}; "
        f"tìm thấy {len(matches)}."
    )

manifest_row = matches[0]

manifest_id = (
    manifest_row["manifest_id"]
)

print()
print("=" * 60)
print("TARGET")
print("=" * 60)

print(
    "document_id:",
    DOCUMENT_ID
)

print(
    "version:",
    VERSION
)

print(
    "manifest_id:",
    manifest_id
)


# ============================================================
# CHECK BEFORE
# ============================================================

already = (
    manifest_already_in_silver(
        manifest_id
    )
)

print()
print(
    "Already in Silver:",
    already
)

if already:

    raise RuntimeError(
        f"{manifest_id} đã tồn tại "
        "trong Silver."
    )


# ============================================================
# TRANSFORM
# ============================================================

result = (
    transform_single_document(
        document_id=
            DOCUMENT_ID,

        manifest_id=
            manifest_id,
    )
)

print()
print("=" * 60)
print("TRANSFORM RESULT")
print("=" * 60)

print(result)


# ============================================================
# AFTER
# ============================================================

after_df = DeltaTable(
    SILVER_PATH
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

rows_added = (
    after_total
    - before_total
)

print()
print("=" * 60)
print("AFTER")
print("=" * 60)

print(
    "Silver total:",
    after_total
)

print(
    "SRC-10 rows:",
    after_src10
)

print(
    "Rows added:",
    rows_added
)


# ============================================================
# VALIDATE
# ============================================================

if (
    result["status"]
    != "transformed"
):

    raise RuntimeError(
        "Incremental Silver không "
        "trả status=transformed."
    )

if (
    rows_added
    != result["records"]
):

    raise RuntimeError(
        "Số row Silver tăng không khớp "
        "result['records']."
    )

if (
    after_src10
    != result["records"]
):

    raise RuntimeError(
        "SRC-10 Silver rows không khớp "
        "result['records']."
    )

print()
print(
    "✅ INCREMENTAL SILVER TEST PASS"
)