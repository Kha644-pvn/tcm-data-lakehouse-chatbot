from api.services.manifest_service import (
    find_by_source_id,
)

from api.services.processing_log_service import (
    append_processing_log,
    get_processing_history,
)

from check_silver_quality import (
    check_single_document_quality,
)


DOCUMENT_ID = "SRC-10"
VERSION = "v2.0"


# ============================================================
# 1. FIND MANIFEST
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
        f"Cần đúng 1 manifest cho "
        f"{DOCUMENT_ID} {VERSION}, "
        f"nhưng tìm thấy {len(matches)}."
    )


manifest_row = matches[0]

manifest_id = (
    manifest_row["manifest_id"]
)


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
# 2. RUN QA AGAIN
# ============================================================

qa = check_single_document_quality(
    document_id=
        DOCUMENT_ID,

    manifest_id=
        manifest_id,
)


print()
print("=" * 60)
print("QA RESULT")
print("=" * 60)

print(
    "passed:",
    qa["passed"]
)

print(
    "bronze_count:",
    qa["bronze_count"]
)

print(
    "silver_count:",
    qa["silver_count"]
)

print(
    "empty_cleaned:",
    qa["empty_cleaned"]
)

print(
    "short_passages:",
    qa["short_passages"]
)

print(
    "duplicate_cleaned:",
    qa["duplicate_cleaned"]
)


if not qa["passed"]:

    raise RuntimeError(
        "Silver QA FAILED. "
        "Không được đánh dấu rag_ready."
    )


# ============================================================
# 3. GET PROCESSING HISTORY
# ============================================================

history = get_processing_history(
    DOCUMENT_ID
)


version_history = [
    row
    for row in history
    if row["version"] == VERSION
]


if not version_history:

    raise RuntimeError(
        f"Không có processing history "
        f"cho {DOCUMENT_ID} {VERSION}."
    )


# ============================================================
# 4. FIND RUN_ID
# ============================================================

bronze_events = [
    row
    for row in version_history
    if row["stage"]
    == "bronze_ingested"
]


if not bronze_events:

    raise RuntimeError(
        "Chưa có stage bronze_ingested. "
        "Không thể finalize Silver."
    )


run_id = (
    bronze_events[-1]["run_id"]
)


print()
print(
    "run_id:",
    run_id
)


# ============================================================
# 5. HELPER CHECK STAGE
# ============================================================

def stage_exists(
    stage: str,
) -> bool:

    current_history = (
        get_processing_history(
            DOCUMENT_ID
        )
    )

    return any(
        row["version"] == VERSION
        and row["run_id"] == run_id
        and row["stage"] == stage
        for row in current_history
    )


# ============================================================
# 6. SILVER CLEANED
# ============================================================

if not stage_exists(
    "silver_cleaned"
):

    append_processing_log(
        document_id=
            DOCUMENT_ID,

        run_id=
            run_id,

        version=
            VERSION,

        stage=
            "silver_cleaned",

        status_detail=(
            f"{qa['silver_count']} "
            "Silver passages đã được "
            "clean và lưu vào Delta."
        ),

        processed_by=
            "pipeline",
    )

    print(
        "✅ Logged: silver_cleaned"
    )

else:

    print(
        "⏭️ silver_cleaned đã tồn tại"
    )


# ============================================================
# 7. SILVER QA PASSED
# ============================================================

if not stage_exists(
    "silver_qa_passed"
):

    append_processing_log(
        document_id=
            DOCUMENT_ID,

        run_id=
            run_id,

        version=
            VERSION,

        stage=
            "silver_qa_passed",

        status_detail=(
            "Silver QA PASS: "
            f"{qa['silver_count']} passages; "
            f"empty={qa['empty_cleaned']}; "
            f"short={qa['short_passages']}; "
            f"duplicate={qa['duplicate_cleaned']}."
        ),

        processed_by=
            "qa",
    )

    print(
        "✅ Logged: silver_qa_passed"
    )

else:

    print(
        "⏭️ silver_qa_passed đã tồn tại"
    )


# ============================================================
# 8. RAG READY
# ============================================================

if not stage_exists(
    "rag_ready"
):

    append_processing_log(
        document_id=
            DOCUMENT_ID,

        run_id=
            run_id,

        version=
            VERSION,

        stage=
            "rag_ready",

        status_detail=(
            "Silver QA đã PASS. "
            "Dữ liệu sẵn sàng cho "
            "chunking/embedding/Qdrant."
        ),

        processed_by=
            "pipeline",
    )

    print(
        "✅ Logged: rag_ready"
    )

else:

    print(
        "⏭️ rag_ready đã tồn tại"
    )


# ============================================================
# 9. FINAL HISTORY
# ============================================================

final_history = (
    get_processing_history(
        DOCUMENT_ID
    )
)


print()
print("=" * 60)
print("FINAL HISTORY - V2")
print("=" * 60)


for row in final_history:

    if (
        row["version"]
        == VERSION
    ):

        print(
            row["version"],
            "|",
            row["stage"],
            "|",
            row["run_id"],
        )


print()
print(
    "✅ SRC-10 v2.0 IS RAG READY"
)