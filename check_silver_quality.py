from deltalake import DeltaTable
import pandas as pd

BRONZE_PATH = r".\delta-tables\bronze_raw_text"
SILVER_PATH = r".\delta-tables\silver_cleaned"

print("=" * 70)
print("KIỂM TRA CHẤT LƯỢNG SILVER")
print("=" * 70)

bronze = DeltaTable(BRONZE_PATH).to_pandas()
silver = DeltaTable(SILVER_PATH).to_pandas()

print(f"\nBronze : {len(bronze)} dòng")
print(f"Silver : {len(silver)} dòng")

print("\n" + "=" * 70)
print("1. SO SÁNH THEO FILE")
print("=" * 70)

bronze_count = bronze.groupby("file_name").size().rename("bronze_count")
silver_count = silver.groupby("file_name").size().rename("silver_count")

comparison = pd.concat([bronze_count, silver_count], axis=1).fillna(0)
comparison["removed"] = (
    comparison["bronze_count"] - comparison["silver_count"]
)

print(comparison.to_string())

print("\n" + "=" * 70)
print("2. KIỂM TRA SRC-03")
print("=" * 70)

src03_bronze = bronze[
    bronze["file_name"] == "SRC-03_CayThuocNam_2003.pdf"
]

src03_silver = silver[
    silver["file_name"] == "SRC-03_CayThuocNam_2003.pdf"
]

print(f"SRC-03 Bronze : {len(src03_bronze)}")
print(f"SRC-03 Silver : {len(src03_silver)}")

print("\n5 passage đầu của SRC-03 Bronze:")

for i, text in enumerate(src03_bronze["raw_text"].head(5), 1):
    print(f"\n--- Passage {i} ---")
    print(str(text)[:500])

print("\n" + "=" * 70)
print("3. KIỂM TRA SRC-02")
print("=" * 70)

src02_bronze = bronze[
    bronze["file_name"] == "SRC-02_SoTayThuocNam_2005.pdf"
]

src02_silver = silver[
    silver["file_name"] == "SRC-02_SoTayThuocNam_2005.pdf"
]

print(f"SRC-02 Bronze : {len(src02_bronze)}")
print(f"SRC-02 Silver : {len(src02_silver)}")

print("\nPassage Silver của SRC-02:")

for text in src02_silver["cleaned_text"]:
    print("\n---")
    print(text[:1500])

print("\n" + "=" * 70)
print("4. KIỂM TRA DUPLICATE TRONG BRONZE")
print("=" * 70)

duplicates = bronze[
    bronze.duplicated(
        subset=["raw_text"],
        keep=False
    )
].copy()

print(f"Số dòng Bronze nằm trong nhóm duplicate: {len(duplicates)}")

if len(duplicates) > 0:
    print("\nDuplicate theo file:")

    print(
        duplicates.groupby("file_name")
        .size()
        .sort_values(ascending=False)
        .to_string()
    )

print("\n" + "=" * 70)
print("HOÀN TẤT KIỂM TRA")
print("=" * 70)