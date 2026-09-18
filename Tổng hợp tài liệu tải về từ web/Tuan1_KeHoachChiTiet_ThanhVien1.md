# Kế hoạch chi tiết Tuần 1 — Thành viên 1 (Kha)
## Đề tài: Data Lakehouse tích hợp Chatbot RAG tra cứu bài thuốc YHCT

**Mục tiêu tuần 1 theo phân công gốc:** Lập danh sách nguồn YHCT; kiểm tra quyền sử dụng; đề xuất schema tài liệu, bài thuốc, dược liệu, bệnh/chứng trạng, chống chỉ định.

**Gate kiểm soát cuối tuần 1 (bắt buộc đạt):** Chốt phạm vi và ít nhất 5 bài báo đủ thông tin (việc này Thành viên 2 làm, nhưng phạm vi bệnh do bạn đề xuất phải khớp).

**Nguyên tắc xuyên suốt:** Tuần 1 KHÔNG thu thập nội dung bài thuốc thật. Tuần 1 chỉ thiết kế khung (nguồn nào dùng được + cấu trúc dữ liệu). Việc đổ dữ liệu thật là mốc tuần 3.

---

## NGÀY 1 (Thứ 2) — Xác định phạm vi bệnh & khởi tạo workspace

### Bước 1.1 — Họp nhanh với Thành viên 2 và giảng viên hướng dẫn (30 phút)
- Thống nhất sơ bộ tên đề tài (bám theo mức khuyến nghị: Data Lakehouse là trọng tâm, chatbot là lớp ứng dụng).
- Thống nhất tuyên bố phạm vi: **hệ thống hỗ trợ tra cứu, không chẩn đoán, không kê đơn**.
- Ghi biên bản họp vào file `docs/00_scope_statement.md`.

### Bước 1.2 — Đề xuất danh sách 10–15 bệnh/chứng thường gặp
Đây là input bắt buộc để sau này biết cần tìm tài liệu về những bệnh gì. Thực hiện:
1. Liệt kê 20–25 bệnh/chứng phổ biến có tài liệu YHCT công khai dễ tiếp cận (ví dụ nhóm: cảm mạo, mất ngủ, đau đầu, viêm họng, đau lưng, tiêu hóa kém, ho, dị ứng, đau dạ dày, huyết áp nhẹ...).
2. Với mỗi bệnh, tra nhanh xem có xuất hiện trong Dược điển Việt Nam / giáo trình YHCT hay không (search nhanh 5–10 phút/bệnh).
3. Lọc xuống còn 10–15 bệnh có **nhiều nguồn tài liệu chồng lặp nhất** (để dễ đối chiếu, chuẩn hóa).
4. Ưu tiên bệnh **không nhạy cảm về an toàn** (tránh các bệnh cấp cứu, ung thư, bệnh cần chẩn đoán phức tạp) — đúng nguyên tắc "không để chatbot chẩn đoán".

**Deliverable Ngày 1:** File `docs/01_disease_scope_v1.md` — danh sách 10–15 bệnh, mỗi bệnh có 1 dòng lý do chọn.

### Bước 1.3 — Khởi tạo workspace cá nhân
- Tạo thư mục làm việc: `source-registry/`, `schema/`, `docs/`.
- Đồng bộ với Git repository chung (do "Cả hai" phụ trách tạo trong tuần 1) — bạn chỉ cần tạo nhánh `feature/source-schema`.

---

## NGÀY 2 (Thứ 3) — Rà soát và liệt kê nguồn YHCT (vòng 1: thô)

### Bước 2.1 — Xác định các nhóm nguồn cần rà (bám theo tài liệu định hướng)
Rà theo đúng 4 nhóm ưu tiên, mỗi nhóm dành khoảng 45–60 phút tìm kiếm:

| Nhóm nguồn | Việc cụ thể cần làm |
|---|---|
| Cơ quan nhà nước | Tìm website/kho tài liệu của Bộ Y tế và Cục Quản lý Y, Dược cổ truyền. Ghi lại: có danh mục thuật ngữ YHCT không, có văn bản hướng dẫn chẩn đoán/điều trị công khai không |
| Dược điển & giáo trình | Tìm bản Dược điển Việt Nam (bản công khai/bản nhà trường có quyền dùng). Hỏi giảng viên xem trường có giáo trình YHCT dùng được không |
| Bệnh viện YHCT | Tìm website bệnh viện YHCT (trung ương hoặc các bệnh viện YHCT tỉnh/thành) có mục "tài liệu", "cẩm nang sức khỏe" công khai |
| Bài báo khoa học / open access | Tìm trên Google Scholar, các tạp chí y dược trong nước có bài viết open access về bài thuốc cổ truyền |

### Bước 2.2 — Với mỗi nguồn tìm được, ghi nhanh vào bảng nháp
Không cần đánh giá kỹ ở bước này, chỉ ghi nhận sự tồn tại:
- Tên nguồn
- Link/địa chỉ
- Loại tài liệu (PDF/HTML/scan)
- Ấn tượng ban đầu về độ tin cậy

**Deliverable Ngày 2:** File nháp `source-registry/00_raw_source_list.csv` — tối thiểu 12–15 nguồn thô (sẽ lọc xuống 5–10 nguồn chính thức ở Ngày 3).

**Lưu ý phản biện:** Nếu đến cuối ngày 2 bạn tìm được dưới 8 nguồn thô, đây là tín hiệu cảnh báo sớm — báo ngay với Thành viên 2 và giảng viên, vì nó ảnh hưởng trực tiếp đến tính khả thi của "Nhánh B" (nếu không đủ nguồn tiếng Việt đáng tin cậy, phạm vi đề tài cần điều chỉnh ngay từ tuần 1, không nên để đến tuần 3 mới phát hiện).

---

## NGÀY 3 (Thứ 4) — Kiểm tra quyền sử dụng & chính thức hóa Source Registry

### Bước 3.1 — Với từng nguồn trong danh sách thô, kiểm tra 3 câu hỏi bắt buộc
1. Nội dung có ghi rõ là tài liệu công khai / phục vụ mục đích nghiên cứu-giáo dục không?
2. Có yêu cầu trích dẫn nguồn không, hay cấm sao chép toàn văn?
3. Nếu là sách/giáo trình có bản quyền — nhóm có quyền sử dụng hợp pháp không (mua, được cấp, hay chỉ được trích một phần)?

### Bước 3.2 — Phân loại từng nguồn theo mức độ an toàn pháp lý
- **Dùng được ngay:** tài liệu nhà nước ban hành công khai, dữ liệu open access có giấy phép rõ.
- **Dùng có điều kiện:** giáo trình nhà trường (chỉ dùng nếu được phép, không public toàn văn ra ngoài hệ thống demo).
- **Cần hỏi giảng viên trước khi dùng:** nguồn không rõ giấy phép nhưng có giá trị cao.
- **Loại bỏ:** blog sức khỏe không rõ tác giả, trang bán thuốc/thực phẩm chức năng, bài viết sao chép không dẫn nguồn.

### Bước 3.3 — Hoàn thiện bảng Source Registry chính thức
Tạo file `source-registry/source_registry_v1.csv` với đầy đủ các cột:

```
source_id, source_name, source_type, url_or_location, license_status,
access_method, reliability_level, estimated_doc_count, checked_by, check_date, note
```

Mục tiêu: **5–10 dòng nguồn chính thức**, mỗi dòng đã được kiểm tra quyền sử dụng thật (không phải đoán).

**Deliverable Ngày 3:** `source_registry_v1.csv` hoàn chỉnh + ghi chú rõ nguồn nào cần giảng viên duyệt thêm.

---

## NGÀY 4 (Thứ 5) — Thiết kế schema: thực thể cốt lõi

### Bước 4.1 — Rà lại danh sách bệnh (Ngày 1) đối chiếu với nguồn thật (Ngày 3)
Loại khỏi danh sách 10–15 bệnh những bệnh **không có nguồn nào trong Source Registry** đề cập tới — tránh chọn bệnh "trên giấy" nhưng không có dữ liệu thật để nạp ở tuần 3.

### Bước 4.2 — Thiết kế chi tiết 6 bảng thực thể
Với mỗi bảng, xác định: tên cột, kiểu dữ liệu, ràng buộc (NOT NULL / UNIQUE), mô tả ý nghĩa. Thực hiện lần lượt:

1. `document` — tài liệu nguồn
2. `disease_syndrome` — bệnh/chứng trạng
3. `symptom` — triệu chứng (bảng riêng, không gộp vào bệnh)
4. `herbal_formula` — bài thuốc
5. `herb` — vị thuốc/dược liệu
6. `contraindication` — chống chỉ định

Với mỗi thực thể, tự trả lời câu hỏi kiểm tra: *"Nếu hội đồng hỏi trường này dùng để làm gì, tôi có trả lời được không?"* Nếu không, loại bỏ cột đó hoặc bổ sung mô tả rõ ràng.

### Bước 4.3 — Viết Data Dictionary
Tạo file `schema/data_dictionary.md` — mô tả từng bảng, từng cột, kiểu dữ liệu, ví dụ giá trị thật (lấy ví dụ từ 1–2 tài liệu bạn đã thấy ở Ngày 2).

**Deliverable Ngày 4:** `schema/data_dictionary.md` (bản nháp 6 bảng thực thể).

---

## NGÀY 5 (Thứ 6) — Thiết kế quan hệ & viết DDL

### Bước 5.1 — Xác định các bảng quan hệ N-N
- `formula_herb` (bài thuốc ↔ vị thuốc)
- `formula_disease` (bài thuốc ↔ bệnh/chứng)
- `disease_symptom` (bệnh ↔ triệu chứng)

Xác định khóa ngoại, ràng buộc composite key cho từng bảng.

### Bước 5.2 — Viết file DDL SQL hoàn chỉnh (PostgreSQL)
Tạo file `schema/ddl_gold_layer.sql` chứa toàn bộ lệnh `CREATE TABLE` cho 9 bảng (6 bảng thực thể + 3 bảng quan hệ), gồm:
- Kiểu dữ liệu cụ thể (`VARCHAR`, `TEXT`, `INTEGER`, `TIMESTAMP`...)
- Khóa chính, khóa ngoại (`REFERENCES`)
- Ràng buộc `NOT NULL` cho các trường bắt buộc
- Comment mô tả từng bảng (`COMMENT ON TABLE ...`)

### Bước 5.3 — Kiểm tra chéo với sơ đồ ERD đã thống nhất
Đối chiếu DDL với ERD đã vẽ — đảm bảo không thiếu bảng, không sai chiều khóa ngoại.

**Deliverable Ngày 5:** `schema/ddl_gold_layer.sql` — chạy thử được trên PostgreSQL local (dùng Docker nếu đã cài, hoặc để dành thao tác chạy thật vào tuần 3, miễn cú pháp không lỗi).

---

## NGÀY 6 (Thứ 7) — Kiểm thử schema bằng dữ liệu mẫu thật (dry-run)

### Bước 6.1 — Chọn 1 bài thuốc + 1 bệnh + 2–3 vị thuốc thật từ nguồn đã kiểm tra
Lấy ví dụ thật từ một tài liệu trong Source Registry (không cần nhiều, chỉ cần đủ để test).

### Bước 6.2 — Thử điền tay dữ liệu mẫu vào từng bảng (trên giấy hoặc file Excel/CSV nháp)
Đây là bước **quan trọng nhất để phát hiện lỗi thiết kế sớm**. Khi điền tay, tự hỏi:
- Có cột nào không đủ chỗ chứa thông tin thật không? (VD: tên bài thuốc có cả tên Hán-Việt dài, cột có đủ không?)
- Có thông tin nào trong tài liệu gốc mà schema hiện tại không có chỗ lưu không?
- Chống chỉ định có mô tả được đúng bằng cấu trúc `target_type`/`target_id` không, hay cần điều chỉnh?

### Bước 6.3 — Điều chỉnh schema nếu phát hiện thiếu sót
Cập nhật lại `ddl_gold_layer.sql` và `data_dictionary.md` nếu cần.

**Deliverable Ngày 6:** `schema/sample_data_dryrun.csv` (dữ liệu mẫu điền tay) + schema đã điều chỉnh lần cuối (nếu có).

---

## NGÀY 7 (Chủ nhật) — Tổng hợp, tích hợp nhóm, chuẩn bị trình giảng viên

### Bước 7.1 — Họp với Thành viên 2 để tích hợp sản phẩm tuần 1
- Đối chiếu: danh sách bệnh (của bạn) có khớp với danh sách 5 bài báo cốt lõi (của Thành viên 2) không.
- Thống nhất 4 câu hỏi nghiên cứu (RQ1–RQ4) — việc chung của cả nhóm.
- Cùng dựng **kiến trúc v0** (sơ đồ tổng thể Bronze–Silver–Gold ở mức khái niệm, chưa cần chi tiết).

### Bước 7.2 — Đóng gói toàn bộ sản phẩm tuần 1 vào Git repository
Cấu trúc thư mục đề xuất:
```
repo/
├── docs/
│   ├── 00_scope_statement.md
│   └── 01_disease_scope_v1.md
├── source-registry/
│   ├── 00_raw_source_list.csv
│   └── source_registry_v1.csv
└── schema/
    ├── data_dictionary.md
    ├── ddl_gold_layer.sql
    └── sample_data_dryrun.csv
```
Commit với message rõ ràng, tạo tag `week1-milestone`.

### Bước 7.3 — Viết báo cáo tiến độ tuần 1 (theo mẫu chuẩn của nhóm)
Điền đầy đủ theo mẫu:
- Mục tiêu tuần: đạt/không đạt phần nào
- Công việc đã hoàn thành (liệt kê theo 6 ngày trên)
- Minh chứng: commit/tag, file đính kèm
- Vấn đề/rủi ro: ví dụ nguồn nào còn chờ giảng viên duyệt quyền sử dụng
- Quyết định cần giảng viên góp ý: phạm vi bệnh đã chọn có phù hợp không, nguồn nào cần xin phép thêm

### Bước 7.4 — Tự kiểm tra trước khi nộp (checklist hoàn thành)
- [ ] Có ít nhất 5–10 nguồn trong Source Registry, mỗi nguồn đã ghi rõ `license_status`
- [ ] Có 10–15 bệnh/chứng đã chốt, khớp với nguồn thật đang có
- [ ] Có ERD + DDL SQL đầy đủ 9 bảng (6 thực thể + 3 quan hệ)
- [ ] Data dictionary mô tả rõ từng cột
- [ ] Đã thử điền dữ liệu mẫu thật và không phát hiện lỗi thiết kế nghiêm trọng
- [ ] Đã họp thống nhất với Thành viên 2 về phạm vi chung
- [ ] Báo cáo tiến độ tuần 1 đã hoàn thành theo đúng mẫu

**Deliverable cuối cùng Tuần 1:** Toàn bộ 7 file trên đã commit lên Git, báo cáo tiến độ đã sẵn sàng nộp/trình bày với giảng viên.

---

## Rủi ro cần lường trước (đưa vào Risk Register chung của nhóm)

| Rủi ro | Khả năng xảy ra | Cách xử lý |
|---|---|---|
| Không đủ nguồn tiếng Việt đáng tin cậy cho 10–15 bệnh đã chọn | Trung bình | Phát hiện sớm ở Ngày 2, thu hẹp phạm vi bệnh nếu cần, ưu tiên bệnh có nhiều nguồn nhất |
| Giáo trình/tài liệu có bản quyền chưa rõ được phép dùng đến đâu | Cao | Không tự quyết, luôn hỏi giảng viên trước khi đưa vào hệ thống demo |
| Schema thiếu trường khi thử điền dữ liệu thật (Ngày 6) | Trung bình | Đây là lý do có bước dry-run — phát hiện sớm còn hơn phát hiện ở tuần 3 khi đã có pipeline ETL |
| Danh sách bệnh không khớp với 5 bài báo cốt lõi của Thành viên 2 | Thấp–Trung bình | Họp đối chiếu bắt buộc ở Ngày 7, không để đến tuần 2 mới phát hiện lệch hướng |
