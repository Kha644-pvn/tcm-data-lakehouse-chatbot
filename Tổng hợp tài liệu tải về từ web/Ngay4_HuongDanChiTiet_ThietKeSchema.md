# Hướng dẫn chi tiết Ngày 4 — Thiết kế Schema (dành cho người mới bắt đầu)

## Trước khi bắt đầu: "Thiết kế schema" thực chất là làm gì?

Nói đơn giản: bạn đang trả lời câu hỏi **"Mỗi loại thông tin cần được lưu thành bảng nào, mỗi bảng có những cột gì, các bảng liên kết với nhau ra sao?"**

Để không bị trừu tượng, cả ngày hôm nay chúng ta sẽ dùng **một ví dụ thật xuyên suốt**:

> **Bệnh mẫu:** Cảm mạo phong hàn (cảm lạnh theo YHCT)
> **Bài thuốc mẫu:** Quế chi thang
> **Vị thuốc mẫu:** Quế chi, Bạch thược, Sinh khương, Đại táo, Cam thảo
> **Triệu chứng mẫu:** Sợ gió, sợ lạnh, đau đầu, sốt nhẹ, ra mồ hôi

*(Đây chỉ là ví dụ minh họa để luyện thiết kế bảng — dữ liệu thật với trích dẫn nguồn chính thống sẽ được thu thập ở tuần 3, không dùng ví dụ này làm dữ liệu chính thức.)*

Bạn sẽ dùng ví dụ này để **thử điền vào từng bảng ngay khi thiết kế xong cột** — đây là cách tốt nhất để phát hiện thiếu sót ngay lập tức thay vì đợi đến Ngày 6.

---

## Hai khái niệm bạn cần nắm trước khi thiết kế bất kỳ bảng nào

### 1. Khóa chính (Primary Key — PK)
Là cột giúp **phân biệt duy nhất từng dòng** trong bảng. Ví dụ: hai bài thuốc có thể trùng tên gọi dân gian, nhưng `formula_id` (VD: `FML-001`, `FML-002`) sẽ không bao giờ trùng.

**Quy tắc đặt PK đơn giản cho người mới:** luôn đặt tên dạng `<tên_bảng>_id`, kiểu chữ-số ngắn gọn, dễ đọc khi debug. Ví dụ: `disease_id`, `herb_id`, `formula_id`.

### 2. Khóa ngoại (Foreign Key — FK)
Là cột trong bảng này **trỏ tới khóa chính của bảng khác**, thể hiện mối quan hệ. Ví dụ: bảng `herbal_formula` có cột `origin_document_id` trỏ tới `document.document_id` — nghĩa là "bài thuốc này lấy từ tài liệu nào".

**Cách nhận biết cần FK:** mỗi khi bạn viết một câu mô tả có chữ "của", "thuộc về", "lấy từ" → đó là dấu hiệu cần FK. Ví dụ: "bài thuốc này **lấy từ** tài liệu X" → cần FK tới `document`.

---

## Bước 4.1 — Rà soát lại danh sách bệnh (làm trước, 30–45 phút)

### Cách làm cụ thể:
1. Mở lại file `docs/01_disease_scope_v1.md` (danh sách 10–15 bệnh từ Ngày 1) và file `source-registry/source_registry_v1.csv` (nguồn đã kiểm tra ở Ngày 3).
2. Với **từng bệnh** trong danh sách, tự hỏi: *"Nguồn nào trong Source Registry có nhắc đến bệnh này?"* — ghi tên nguồn vào cạnh mỗi bệnh.
3. Nếu một bệnh **không có nguồn nào nhắc tới** → gạch bỏ khỏi danh sách, hoặc đánh dấu "cần tìm thêm nguồn".
4. Mục tiêu cuối bước này: có danh sách bệnh **đã được xác nhận có nguồn thật hỗ trợ**, không còn bệnh "trên giấy".

**Ví dụ cách ghi:**
```
1. Cảm mạo phong hàn — có trong: Giáo trình YHCT (SRC-03), Bệnh viện YHCT TW (SRC-05)
2. Mất ngủ — có trong: Dược điển VN (SRC-02)
3. [Bệnh X] — CHƯA có nguồn nào → cần tìm thêm hoặc loại bỏ
```

---

## Bước 4.2 — Thiết kế từng bảng (phần chính, làm kỹ nhất)

Với **mỗi bảng**, bạn làm theo quy trình 4 bước nhỏ giống nhau:
- (a) Liệt kê mọi thông tin cần lưu (viết tự do, chưa cần chuẩn)
- (b) Chuyển từng thông tin thành 1 cột, đặt tên tiếng Anh ngắn gọn
- (c) Xác định kiểu dữ liệu + ràng buộc
- (d) Thử điền ngay bằng ví dụ mẫu (Quế chi thang) để kiểm tra

Làm lần lượt 6 bảng theo thứ tự sau (thứ tự này quan trọng — làm `document` trước vì các bảng khác sẽ tham chiếu tới nó):

---

### Bảng 1/6: `document` (tài liệu nguồn)

**(a) Thông tin cần lưu:** tên tài liệu, tài liệu này từ nguồn nào, ai viết/ban hành, năm nào, loại tài liệu gì, có được phép dùng không, trang/mục nào chứa thông tin, khi nào nhóm thu thập, đây là phiên bản mấy.

**(b)+(c) Chuyển thành cột:**

| Cột | Kiểu dữ liệu | Bắt buộc? | Giải thích |
|---|---|---|---|
| `document_id` | VARCHAR(20) | PK, bắt buộc | Mã tự đặt, VD: `DOC-001` |
| `title` | TEXT | Bắt buộc | Tên đầy đủ tài liệu |
| `source_id` | VARCHAR(20) | FK → source_registry, bắt buộc | Trỏ tới bảng nguồn đã làm Ngày 3 |
| `author_org` | VARCHAR(255) | Bắt buộc | Tác giả hoặc cơ quan ban hành |
| `publish_year` | INTEGER | Không bắt buộc | Có tài liệu không ghi rõ năm |
| `doc_type` | VARCHAR(50) | Bắt buộc | Chỉ nhận 1 trong các giá trị: `giáo trình`, `dược điển`, `hướng dẫn điều trị`, `bài báo khoa học` |
| `license` | VARCHAR(100) | Bắt buộc | VD: `công khai`, `cần xin phép`, `nội bộ trường` |
| `version` | VARCHAR(20) | Bắt buộc | VD: `v1.0` |

**(d) Thử điền bằng ví dụ mẫu:**
```
document_id: DOC-001
title: Giáo trình Y học cổ truyền
source_id: SRC-03
author_org: Trường Đại học Y Dược
publish_year: 2020
doc_type: giáo trình
license: nội bộ trường - cần xin phép
version: v1.0
```
→ Điền thử xong, bạn thấy đủ chỗ chứa thông tin không? Nếu tài liệu có cả "số trang cụ thể chứa bài thuốc", bạn sẽ cần thêm cột đó — nhưng cột này nên đặt ở bảng `herbal_formula` (vì mỗi bài thuốc nằm ở trang khác nhau trong cùng 1 tài liệu), không đặt ở đây. Đây chính là kiểu quyết định thiết kế bạn sẽ tự gặp — cứ hỏi: *"Thông tin này gắn với TÀI LIỆU nói chung, hay gắn với TỪNG bài thuốc/vị thuốc trong đó?"*

---

### Bảng 2/6: `disease_syndrome` (bệnh/chứng trạng)

**(a) Thông tin cần lưu:** tên bệnh (tiếng Việt), tên Hán-Việt (vì YHCT hay có tên gọi kiểu chữ Hán-Việt), bệnh thuộc nhóm/khoa nào, mô tả ngắn.

**(b)+(c) Cột:**

| Cột | Kiểu dữ liệu | Bắt buộc? | Giải thích |
|---|---|---|---|
| `disease_id` | VARCHAR(20) | PK | VD: `DIS-001` |
| `name_vi` | VARCHAR(255) | Bắt buộc | Tên tiếng Việt thông dụng |
| `name_hanviet` | VARCHAR(255) | Không bắt buộc | Tên gọi Hán-Việt nếu có |
| `category` | VARCHAR(100) | Bắt buộc | VD: `ngoại cảm`, `nội thương` |
| `description` | TEXT | Không bắt buộc | Mô tả ngắn 1-2 câu |

**(d) Thử điền:**
```
disease_id: DIS-001
name_vi: Cảm mạo phong hàn
name_hanviet: Cảm mạo phong hàn chứng
category: Ngoại cảm
description: Chứng cảm lạnh do phong hàn xâm nhập, biểu hiện sợ lạnh, đau đầu
```

**Lưu ý quan trọng cho người mới:** đừng để trống `name_hanviet` là bắt buộc — vì rất nhiều tài liệu chỉ dùng tên tiếng Việt thông thường, ép buộc cột này sẽ khiến bạn nhập liệu ở tuần 3 bị vướng liên tục.

---

### Bảng 3/6: `symptom` (triệu chứng) — bảng riêng, KHÔNG gộp vào bệnh

**Lý do phải tách riêng:** một triệu chứng (VD: "sợ lạnh") có thể xuất hiện ở nhiều bệnh khác nhau. Nếu bạn viết triệu chứng thành một đoạn văn bản dài trong bảng `disease_syndrome`, sau này chatbot sẽ **không thể** tìm câu hỏi kiểu "triệu chứng sợ lạnh là dấu hiệu của bệnh gì" một cách chính xác.

**(b)+(c) Cột:**

| Cột | Kiểu dữ liệu | Bắt buộc? |
|---|---|---|
| `symptom_id` | VARCHAR(20) | PK |
| `name` | VARCHAR(255) | Bắt buộc |
| `description` | TEXT | Không bắt buộc |

**(d) Thử điền (4 triệu chứng của ví dụ mẫu):**
```
SYM-001: Sợ gió
SYM-002: Sợ lạnh
SYM-003: Đau đầu
SYM-004: Sốt nhẹ, ra mồ hôi
```
→ Bạn sẽ nối các triệu chứng này với bệnh `DIS-001` ở bảng quan hệ `disease_symptom` (làm ở Ngày 5, chưa cần làm hôm nay).

---

### Bảng 4/6: `herbal_formula` (bài thuốc)

**(a) Thông tin cần lưu:** tên bài thuốc, tài liệu nào ghi lại, cách bào chế/sắc thuốc, cách dùng (KHÔNG ghi liều lượng cụ thể — đúng nguyên tắc an toàn đã thống nhất).

**(b)+(c) Cột:**

| Cột | Kiểu dữ liệu | Bắt buộc? | Giải thích |
|---|---|---|---|
| `formula_id` | VARCHAR(20) | PK | VD: `FML-001` |
| `name_vi` | VARCHAR(255) | Bắt buộc | Tên bài thuốc |
| `name_hanviet` | VARCHAR(255) | Không bắt buộc | |
| `origin_document_id` | VARCHAR(20) | FK → document, bắt buộc | Trích từ tài liệu nào |
| `preparation_method` | TEXT | Không bắt buộc | Cách sắc/bào chế |
| `usage_note` | TEXT | Không bắt buộc | Cách dùng chung, KHÔNG ghi liều cụ thể |

**(d) Thử điền:**
```
formula_id: FML-001
name_vi: Quế chi thang
origin_document_id: DOC-001
preparation_method: Sắc uống, chia làm nhiều lần trong ngày
usage_note: Dùng khi có triệu chứng ngoại cảm phong hàn, cần tham khảo thầy thuốc
```

**Câu hỏi tự kiểm tra:** vì sao không có cột `dosage` (liều lượng)? → Vì tài liệu định hướng ban đầu đã nói rõ: *"Không tự sinh liều lượng"*. Đây là ví dụ cụ thể cho thấy nguyên tắc an toàn ảnh hưởng trực tiếp đến quyết định thiết kế schema — không phải chỉ là nguyên tắc suông.

---

### Bảng 5/6: `herb` (vị thuốc/dược liệu)

**(a) Thông tin cần lưu:** tên vị thuốc bằng 3 loại tên gọi khác nhau (vì YHCT rất hay có tên đồng nghĩa), nguồn gốc, tính vị.

**(b)+(c) Cột:**

| Cột | Kiểu dữ liệu | Bắt buộc? | Giải thích |
|---|---|---|---|
| `herb_id` | VARCHAR(20) | PK | |
| `name_vi` | VARCHAR(255) | Bắt buộc | Tên tiếng Việt |
| `name_hanviet` | VARCHAR(255) | Không bắt buộc | |
| `name_latin` | VARCHAR(255) | Không bắt buộc | Tên khoa học, nếu tài liệu có |
| `origin` | VARCHAR(100) | Không bắt buộc | Thực vật / động vật / khoáng vật |
| `properties` | VARCHAR(255) | Không bắt buộc | Tính vị: hàn, nhiệt, ôn, lương |

**(d) Thử điền (1 trong 5 vị thuốc mẫu):**
```
herb_id: HRB-001
name_vi: Quế chi
name_hanviet: Quế chi
name_latin: Cinnamomi ramulus
origin: Thực vật
properties: Vị cay, tính ôn
```

---

### Bảng 6/6: `contraindication` (chống chỉ định)

**(a) Thông tin cần lưu:** chống chỉ định này áp dụng cho bài thuốc hay vị thuốc, mô tả cụ thể, mức độ nghiêm trọng.

**Đây là bảng khó nhất với người mới** vì nó cần áp dụng cho **hai loại đối tượng khác nhau** (bài thuốc HOẶC vị thuốc) mà không muốn tạo 2 bảng riêng. Cách giải quyết — dùng 2 cột `target_type` + `target_id`:

| Cột | Kiểu dữ liệu | Bắt buộc? | Giải thích |
|---|---|---|---|
| `contraindication_id` | VARCHAR(20) | PK | |
| `target_type` | VARCHAR(20) | Bắt buộc | Chỉ nhận: `formula` hoặc `herb` |
| `target_id` | VARCHAR(20) | Bắt buộc | Nếu `target_type = formula` → ghi `formula_id`; nếu `= herb` → ghi `herb_id` |
| `description` | TEXT | Bắt buộc | Mô tả chống chỉ định |
| `severity` | VARCHAR(20) | Không bắt buộc | VD: `nhẹ`, `trung bình`, `nghiêm trọng` |

**(d) Thử điền:**
```
contraindication_id: CTR-001
target_type: formula
target_id: FML-001
description: Không dùng cho người đang sốt cao, ra nhiều mồ hôi do biểu hư
severity: trung bình
```

**Giải thích tại sao thiết kế kiểu này (quan trọng để bạn trả lời được khi hội đồng hỏi):** nếu tách 2 bảng `formula_contraindication` và `herb_contraindication` riêng, bạn sẽ phải viết code truy vấn 2 lần mỗi khi hiển thị cảnh báo — cách dùng `target_type`/`target_id` cho phép gộp chung logic cảnh báo an toàn ở một chỗ, dễ bảo trì hơn khi hệ thống mở rộng.

---

## Bước 4.3 — Viết Data Dictionary (30–45 phút)

Sau khi đã thiết kế xong 6 bảng, việc còn lại chỉ là **gom mọi thứ ở trên vào một file** theo định dạng thống nhất. Copy đúng cấu trúc sau cho từng bảng:

```markdown
## Bảng: disease_syndrome
**Mô tả:** Lưu thông tin bệnh/chứng trạng theo YHCT

| Cột | Kiểu dữ liệu | Bắt buộc | Mô tả | Ví dụ |
|---|---|---|---|---|
| disease_id | VARCHAR(20) | PK | Mã định danh | DIS-001 |
| name_vi | VARCHAR(255) | Có | Tên tiếng Việt | Cảm mạo phong hàn |
| name_hanviet | VARCHAR(255) | Không | Tên Hán-Việt | Cảm mạo phong hàn chứng |
| category | VARCHAR(100) | Có | Phân loại | Ngoại cảm |
| description | TEXT | Không | Mô tả ngắn | ... |
```

Lặp lại cho cả 6 bảng → ghép thành file `schema/data_dictionary.md`.

---

## Checklist tự kiểm tra sau khi hoàn thành Ngày 4

- [ ] Đã rà soát và loại bỏ bệnh không có nguồn thật hỗ trợ (Bước 4.1)
- [ ] Cả 6 bảng đều đã thử điền ít nhất 1 dòng dữ liệu mẫu thật (không chỉ thiết kế trên giấy)
- [ ] Mọi cột FK đều xác định rõ trỏ tới bảng nào
- [ ] Bảng `herbal_formula` KHÔNG có cột liều lượng cụ thể
- [ ] Bảng `contraindication` áp dụng được cho cả bài thuốc lẫn vị thuốc
- [ ] File `data_dictionary.md` đã có đủ 6 bảng theo đúng định dạng thống nhất

## Lỗi thường gặp của người mới (để tránh)

1. **Đặt tên cột bằng tiếng Việt có dấu** — nên dùng tiếng Anh không dấu (`name_vi` thay vì `tên tiếng việt`) vì khi viết SQL/code sẽ dễ lỗi với ký tự có dấu.
2. **Gộp nhiều thông tin vào 1 cột dạng text tự do** — ví dụ ghi cả "triệu chứng: sợ lạnh, đau đầu, sốt nhẹ" vào 1 ô — sẽ không truy vấn/lọc được. Luôn tách thành bảng riêng nếu thông tin có thể lặp lại nhiều lần.
3. **Bắt buộc (NOT NULL) quá nhiều cột** — hãy nhớ dữ liệu thật từ nhiều nguồn khác nhau sẽ có tài liệu thiếu năm xuất bản, thiếu tên Hán-Việt... Chỉ bắt buộc những cột thực sự cốt lõi.
4. **Quên thử điền dữ liệu mẫu thật trước khi chuyển sang bảng tiếp theo** — đây là lỗi phổ biến nhất khiến schema phải sửa lại nhiều lần ở tuần 3.
