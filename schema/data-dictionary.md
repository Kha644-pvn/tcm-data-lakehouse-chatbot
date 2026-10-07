# GOLD Layer Schema — Hệ thống tra cứu bài thuốc YHCT

## 1. Thông tin tổng quan

| Thông tin    | Giá trị                                                            |
|--------------|--------------------------------------------------------------------|
| Database     | PostgreSQL 15+                                                     |
| Schema       | `yhct_gold`                                                        |
| Phiên bản    | v1.0                                                               |
| Mục đích     | Lưu trữ dữ liệu Gold Layer phục vụ hệ thống tra cứu bài thuốc YHCT |
| Tổng số bảng | 9                                                                  |
| Nhóm bảng    | Bảng thực thể và bảng quan hệ N-N                                  |

### Danh sách bảng

| STT | Tên bảng           | Mô tả                          |
|-----|--------------------|--------------------------------|
| 1   | `document`         | Tài liệu nguồn                 |
| 2   | `disease_syndrome` | Bệnh / chứng trạng             |
| 3   | `symptom`          | Triệu chứng                    |
| 4   | `herbal_formula`   | Bài thuốc                      |
| 5   | `herb`             | Vị thuốc / dược liệu           |
| 6   | `contraindication` | Chống chỉ định                 |
| 7   | `formula_herb`     | Quan hệ Bài thuốc ↔ Vị thuốc   |
| 8   | `formula_disease`  | Quan hệ Bài thuốc ↔ Bệnh/chứng |
| 9   | `disease_symptom`  | Quan hệ Bệnh ↔ Triệu chứng     |

> **Quy ước:**  
> - **Có** = cột `NOT NULL`, bắt buộc phải có giá trị khi thêm bản ghi.  
> - **Không** = cột cho phép `NULL`.  
> - Các cột có `DEFAULT` sẽ được PostgreSQL tự động gán giá trị nếu không truyền vào.

---

# 2. Chi tiết từng bảng

## 2.1. Bảng `document` — Tài liệu nguồn

**Mục đích:** Lưu thông tin về các tài liệu nguồn được sử dụng để trích xuất dữ liệu bài thuốc, dược liệu và bệnh/chứng trạng.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `document_id` | `VARCHAR(20)` | Có | — | Mã định danh duy nhất của tài liệu. Là khóa chính (Primary Key). |
| `title` | `TEXT` | Có | — | Tên/tiêu đề của tài liệu. |
| `source_id` | `VARCHAR(20)` | Có | — | Mã nguồn tài liệu. Đây là khóa ngoại logic tới Source Registry. |
| `author_org` | `VARCHAR(255)` | Có | — | Tác giả hoặc tổ chức chịu trách nhiệm về tài liệu. |
| `publish_year` | `INTEGER` | Không | — | Năm xuất bản tài liệu. |
| `doc_type` | `VARCHAR(50)` | Có | — | Loại tài liệu. Chỉ chấp nhận: `giáo trình`, `dược điển`, `hướng dẫn điều trị`, `bài báo khoa học`. |
| `license` | `VARCHAR(100)` | Có | — | Thông tin giấy phép/quyền sử dụng tài liệu. |
| `version` | `VARCHAR(20)` | Có | `v1.0` | Phiên bản của tài liệu. |
| `created_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được tạo. |
| `updated_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được cập nhật gần nhất. |

### Khóa và ràng buộc

- **Primary Key:** `document_id`
- **CHECK:** `doc_type` chỉ nhận một trong 4 giá trị được quy định.
- `source_id` là **FK logic** tới Source Registry, chưa khai báo `FOREIGN KEY` trực tiếp trong schema này.

---

## 2.2. Bảng `disease_syndrome` — Bệnh / chứng trạng

**Mục đích:** Lưu danh mục các bệnh hoặc chứng trạng theo Y học cổ truyền (YHCT).

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `disease_id` | `VARCHAR(20)` | Có | — | Mã định danh duy nhất của bệnh/chứng trạng. Là khóa chính. |
| `name_vi` | `VARCHAR(255)` | Có | — | Tên bệnh/chứng trạng bằng tiếng Việt. |
| `category` | `VARCHAR(100)` | Có | — | Nhóm/phân loại bệnh hoặc chứng trạng. |
| `description` | `TEXT` | Không | — | Mô tả chi tiết về bệnh/chứng trạng. |
| `Disease prevention methods` | `TEXT` | Không | -| Mô tả cách phòng bệnh |
| `created_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được tạo. |
| `updated_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được cập nhật gần nhất. |

### Khóa và ràng buộc

- **Primary Key:** `disease_id`

---

## 2.3. Bảng `symptom` — Triệu chứng

**Mục đích:** Lưu danh mục các triệu chứng được dùng chung cho nhiều bệnh/chứng trạng.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `symptom_id` | `VARCHAR(20)` | Có | — | Mã định danh duy nhất của triệu chứng. Là khóa chính. |
| `name` | `VARCHAR(255)` | Có | — | Tên triệu chứng. |
| `description` | `TEXT` | Không | — | Mô tả chi tiết về triệu chứng. |
| `created_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được tạo. |
| `updated_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được cập nhật gần nhất. |

### Khóa và ràng buộc

- **Primary Key:** `symptom_id`

---

## 2.4. Bảng `herbal_formula` — Bài thuốc

**Mục đích:** Lưu thông tin về các bài thuốc YHCT. Schema này **không lưu liều lượng cụ thể**.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `formula_id` | `VARCHAR(20)` | Có | — | Mã định danh duy nhất của bài thuốc. Là khóa chính. |
| `name_vi` | `VARCHAR(255)` | Có | — | Tên bài thuốc bằng tiếng Việt. |
| `origin_document_id` | `VARCHAR(20)` | Có | — | Mã tài liệu nguồn chứa/trích dẫn bài thuốc. Là khóa ngoại tới `document.document_id`. |
| `preparation_method`  | `TEXT`| Không | Cách pha chế thuốc|
| `usage_note` | `TEXT` | Không | — | Ghi chú về cách sử dụng ở mức thông tin tham khảo. |
| `created_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được tạo. |
| `updated_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được cập nhật gần nhất. |

### Khóa và ràng buộc

- **Primary Key:** `formula_id`
- **Foreign Key:** `origin_document_id` → `document(document_id)`
- **ON DELETE RESTRICT:** Không cho phép xóa tài liệu nguồn nếu vẫn còn bài thuốc tham chiếu tới tài liệu đó.
- **Index:** `idx_formula_document` trên `origin_document_id`.

---

## 2.5. Bảng `herb` — Vị thuốc / dược liệu

**Mục đích:** Lưu danh mục các vị thuốc/dược liệu được sử dụng trong hệ thống.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `herb_id` | `VARCHAR(20)` | Có | — | Mã định danh duy nhất của vị thuốc/dược liệu. Là khóa chính. |
| `name_vi` | `VARCHAR(255)` | Có | — | Tên vị thuốc/dược liệu bằng tiếng Việt. |
|  ` origin ` |  `VARCHAR(100)` | Có  |Nguồn tài liệu |
|`properties` |  `VARCHAR(255)` | Không| mô tả hoạt tính của vị thuốc( cay, chua, đắng,....) |
| `created_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được tạo. |
| `updated_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được cập nhật gần nhất. |

### Khóa và ràng buộc

- **Primary Key:** `herb_id`

---

## 2.6. Bảng `contraindication` — Chống chỉ định

**Mục đích:** Lưu các thông tin chống chỉ định áp dụng cho bài thuốc hoặc vị thuốc.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `contraindication_id` | `VARCHAR(20)` | Có | — | Mã định danh duy nhất của thông tin chống chỉ định. Là khóa chính. |
| `target_type` | `VARCHAR(20)` | Có | — | Loại đối tượng áp dụng chống chỉ định. Chỉ nhận `formula` hoặc `herb`. |
| `target_id` | `VARCHAR(20)` | Có | — | Mã của đối tượng bị áp dụng chống chỉ định. Được xác định dựa trên `target_type`. |
| `description` | `TEXT` | Có | — | Nội dung/mô tả chi tiết về chống chỉ định. |
| `severity` | `VARCHAR(20)` | Không | — | Mức độ nghiêm trọng: `nhẹ`, `trung bình` hoặc `nghiêm trọng`. |
| `created_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được tạo. |
| `updated_at` | `TIMESTAMP` | Có | `NOW()` | Thời điểm bản ghi được cập nhật gần nhất. |

### Khóa và ràng buộc

- **Primary Key:** `contraindication_id`
- **CHECK:** `target_type` chỉ nhận `formula` hoặc `herb`.
- **CHECK:** `severity` nếu có giá trị thì chỉ nhận `nhẹ`, `trung bình`, `nghiêm trọng`.
- **Index:** `idx_contraindication_target` trên `(target_type, target_id)`.
- `target_id` là **polymorphic reference**: có thể tham chiếu tới `herbal_formula.formula_id` hoặc `herb.herb_id` tùy theo `target_type`. Database hiện không khai báo FK trực tiếp cho cặp này.

---

# 3. Các bảng quan hệ N-N

## 3.1. Bảng `formula_herb` — Bài thuốc ↔ Vị thuốc

**Mục đích:** Biểu diễn quan hệ nhiều-nhiều giữa bài thuốc và vị thuốc.huốc có thể xuất h Một bài thuốc có thể chứa nhiều vị thuốc và một vị tiện trong nhiều bài thuốc.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `formula_id` | `VARCHAR(20)` | Có | — | Mã bài thuốc. Khóa ngoại tới `herbal_formula.formula_id`. |
| `herb_id` | `VARCHAR(20)` | Có | — | Mã vị thuốc. Khóa ngoại tới `herb.herb_id`. |
|`dosage_amount`| `NUMERIC(6,2`)` | Có | Số lượng liều dùng |
|`dosage_unit`|`VARCHAR(20)`| Có |Đơn vị: g, ml, ml,...|
| `note` | `TEXT` | Không | — | Ghi chú bổ sung về vai trò hoặc mối quan hệ giữa vị thuốc và bài thuốc. |



### Khóa và ràng buộc

- **Primary Key kép:** `(formula_id, herb_id)`
- **Foreign Key:** `formula_id` → `herbal_formula(formula_id)`
- **Foreign Key:** `herb_id` → `herb(herb_id)`
- `formula_id` có **ON DELETE CASCADE**: khi bài thuốc bị xóa, các bản ghi liên quan trong bảng này cũng bị xóa.
- `herb_id` có **ON DELETE RESTRICT**: không cho xóa vị thuốc nếu vị thuốc vẫn đang được sử dụng trong một bài thuốc.
- **Index:** `idx_fh_herb` trên `herb_id`.

---

## 3.2. Bảng `formula_disease` — Bài thuốc ↔ Bệnh/chứng

**Mục đích:** Biểu diễn quan hệ nhiều-nhiều giữa bài thuốc và bệnh/chứng trạng. Một bài thuốc có thể được liên kết với nhiều bệnh/chứng và một bệnh/chứng có thể có nhiều bài thuốc.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `formula_id` | `VARCHAR(20)` | Có | — | Mã bài thuốc. Khóa ngoại tới `herbal_formula.formula_id`. |
| `disease_id` | `VARCHAR(20)` | Có | — | Mã bệnh/chứng trạng. Khóa ngoại tới `disease_syndrome.disease_id`. |
| `effectiveness_note` | `TEXT` | Không | — | Ghi chú về hiệu quả hoặc mối liên hệ giữa bài thuốc và bệnh/chứng theo tài liệu nguồn. |

### Khóa và ràng buộc

- **Primary Key kép:** `(formula_id, disease_id)`
- **Foreign Key:** `formula_id` → `herbal_formula(formula_id)`
- **Foreign Key:** `disease_id` → `disease_syndrome(disease_id)`
- `formula_id` có **ON DELETE CASCADE**.
- `disease_id` có **ON DELETE RESTRICT**.
- **Index:** `idx_fd_disease` trên `disease_id`.

---

## 3.3. Bảng `disease_symptom` — Bệnh ↔ Triệu chứng

**Mục đích:** Biểu diễn quan hệ nhiều-nhiều giữa bệnh/chứng trạng và triệu chứng. Một bệnh có thể có nhiều triệu chứng và một triệu chứng có thể xuất hiện ở nhiều bệnh.

| Tên cột | Kiểu dữ liệu | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|---|
| `disease_id` | `VARCHAR(20)` | Có | — | Mã bệnh/chứng trạng. Khóa ngoại tới `disease_syndrome.disease_id`. |
| `symptom_id` | `VARCHAR(20)` | Có | — | Mã triệu chứng. Khóa ngoại tới `symptom.symptom_id`. |
| `is_primary` | `BOOLEAN` | Có | `TRUE` | Xác định triệu chứng có phải triệu chứng chính hay không. `TRUE` = chính, `FALSE` = không chính. |

### Khóa và ràng buộc

- **Primary Key kép:** `(disease_id, symptom_id)`
- **Foreign Key:** `disease_id` → `disease_syndrome(disease_id)`
- **Foreign Key:** `symptom_id` → `symptom(symptom_id)`
- `disease_id` có **ON DELETE CASCADE**.
- `symptom_id` có **ON DELETE RESTRICT**.
- **Index:** `idx_ds_symptom` trên `symptom_id`.

---

# 4. Tổng hợp khóa chính và khóa ngoại

## 4.1. Primary Key

| Bảng | Primary Key |
|---|---|
| `document` | `document_id` |
| `disease_syndrome` | `disease_id` |
| `symptom` | `symptom_id` |
| `herbal_formula` | `formula_id` |
| `herb` | `herb_id` |
| `contraindication` | `contraindication_id` |
| `formula_herb` | `(formula_id, herb_id)` |
| `formula_disease` | `(formula_id, disease_id)` |
| `disease_symptom` | `(disease_id, symptom_id)` |

## 4.2. Foreign Key

| Bảng nguồn | Cột | Bảng đích | Cột đích | ON DELETE |
|---|---|---|---|---|
| `herbal_formula` | `origin_document_id` | `document` | `document_id` | `RESTRICT` |
| `formula_herb` | `formula_id` | `herbal_formula` | `formula_id` | `CASCADE` |
| `formula_herb` | `herb_id` | `herb` | `herb_id` | `RESTRICT` |
| `formula_disease` | `formula_id` | `herbal_formula` | `formula_id` | `CASCADE` |
| `formula_disease` | `disease_id` | `disease_syndrome` | `disease_id` | `RESTRICT` |
| `disease_symptom` | `disease_id` | `disease_syndrome` | `disease_id` | `CASCADE` |
| `disease_symptom` | `symptom_id` | `symptom` | `symptom_id` | `RESTRICT` |

### FK logic / Polymorphic reference

| Bảng | Cột | Cách tham chiếu |
|---|---|---|
| `document` | `source_id` | FK logic tới Source Registry |
| `contraindication` | `target_type`, `target_id` | `target_type = formula` → `herbal_formula.formula_id`; `target_type = herb` → `herb.herb_id` |

---

# 5. Sơ đồ quan hệ tổng quát

```text
                         ┌──────────────────┐
                         │     document     │
                         │──────────────────│
                         │ PK document_id   │
                         └────────┬─────────┘
                                  │
                                  │ 1-N
                                  ▼
                       ┌─────────────────────┐
                       │   herbal_formula    │
                       │─────────────────────│
                       │ PK formula_id       │
                       │ FK origin_document  │
                       └──────┬────────┬─────┘
                              │        │
                       1-N    │        │    1-N
                              ▼        ▼
                    ┌─────────────┐  ┌─────────────────┐
                    │ formula_herb│  │ formula_disease │
                    └──────┬──────┘  └────────┬────────┘
                           │                  │
                         N │                  │ N
                           ▼                  ▼
                    ┌─────────────┐  ┌───────────────────┐
                    │     herb    │  │ disease_syndrome  │
                    │─────────────│  │───────────────────│
                    │ PK herb_id  │  │ PK disease_id     │
                    └─────────────┘  └─────────┬─────────┘
                                               │
                                               │ N-N
                                               ▼
                                      ┌─────────────────┐
                                      │disease_symptom  │
                                      └────────┬────────┘
                                               │
                                               │ N
                                               ▼
                                        ┌─────────────┐
                                        │   symptom   │
                                        │─────────────│
                                        │PK symptom_id│
                                        └─────────────┘

                 ┌──────────────────────┐
                 │   contraindication  │
                 │──────────────────────│
                 │ PK contraindication_id│
                 │ target_type          │
                 │ target_id            │
                 └──────────┬───────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
        target_type=formula      target_type=herb
                │                       │
                ▼                       ▼
       herbal_formula                 herb
```

---

# 6. Tổng quan thiết kế dữ liệu

Schema `yhct_gold` được tổ chức thành ba nhóm chính:

### Nhóm 1 — Dữ liệu thực thể

- `document`: quản lý tài liệu nguồn.
- `disease_syndrome`: quản lý bệnh/chứng trạng.
- `symptom`: quản lý triệu chứng.
- `herbal_formula`: quản lý bài thuốc.
- `herb`: quản lý vị thuốc/dược liệu.
- `contraindication`: quản lý thông tin chống chỉ định.

### Nhóm 2 — Bảng quan hệ nhiều-nhiều

- `formula_herb`: liên kết bài thuốc với vị thuốc.
- `formula_disease`: liên kết bài thuốc với bệnh/chứng.
- `disease_symptom`: liên kết bệnh/chứng với triệu chứng.

### Nhóm 3 — Thông tin thời gian

Các bảng đều có:

- `created_at`: thời điểm tạo bản ghi.
- `updated_at`: thời điểm cập nhật bản ghi.

Hai trường này sử dụng `TIMESTAMP` và mặc định bằng `NOW()`.

---

# 7. Các quy tắc toàn vẹn dữ liệu đáng chú ý

1. **Mã định danh:** Các bảng chính sử dụng mã dạng `VARCHAR(20)` làm Primary Key.
2. **Không cho xóa dữ liệu đang được tham chiếu:** Nhiều quan hệ sử dụng `ON DELETE RESTRICT`, giúp bảo vệ dữ liệu nguồn và dữ liệu danh mục.
3. **Tự động xóa quan hệ:** Các bảng trung gian sử dụng `ON DELETE CASCADE` đối với đối tượng chính như bài thuốc hoặc bệnh/chứng. Khi đối tượng bị xóa, bản ghi quan hệ tương ứng cũng được xóa.
4. **Phân loại tài liệu:** `document.doc_type` được giới hạn bằng `CHECK constraint`.
5. **Phân loại chống chỉ định:** `contraindication.target_type` và `severity` được giới hạn bằng `CHECK constraint`.
6. **Khóa chính kép:** Các bảng quan hệ N-N sử dụng khóa chính kết hợp để ngăn cùng một cặp đối tượng xuất hiện trùng lặp.
7. **Không lưu liều lượng cụ thể:** Bảng `herbal_formula` chỉ lưu thông tin bài thuốc và hướng dẫn/ghi chú sử dụng, không thiết kế trường lưu liều lượng cụ thể.
8. **Polymorphic reference:** `contraindication` sử dụng `target_type` + `target_id` để có thể áp dụng cho cả bài thuốc và vị thuốc. Cách thiết kế này linh hoạt nhưng không được PostgreSQL đảm bảo FK trực tiếp bằng constraint thông thường.
