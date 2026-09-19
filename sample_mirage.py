import json
import random
# ============================================================
# 1. Đọc toàn bộ MIRAGE benchmark
# ============================================================

with open("MIRAGE/benchmark.json", "r", encoding="utf-8") as f:
    full_data = json.load(f)
# ============================================================
# 2. Gom tất cả câu hỏi từ 5 dataset thành một danh sách
# ============================================================
all_questions = []
for dataset_name, dataset_data in full_data.items():
    for question_id, question_data in dataset_data.items():
        all_questions.append({
            "dataset": dataset_name,
            "question_id": question_id,
            **question_data
        })
print(f"Tổng số câu trong MIRAGE: {len(all_questions)}")
# ============================================================
# 3. Lấy ngẫu nhiên tối đa 300 câu
# ============================================================
random.seed(42)
sample_size = min(300, len(all_questions))
subset = random.sample(
    all_questions,
    sample_size
)
# ============================================================
# 4. Lưu tập con
# ============================================================
output_path = "bronze/mirage-medrag/v1/mirage_subset_300.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        subset,
        f,
        ensure_ascii=False,
        indent=2
    )
print(f"Đã lấy {len(subset)} câu.")
print(f"Đã lưu tại: {output_path}")