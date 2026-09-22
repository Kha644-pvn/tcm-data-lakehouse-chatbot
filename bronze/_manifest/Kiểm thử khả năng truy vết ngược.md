Kiểm thử khả năng truy vết ngược bằng cách chọn ngẫu nhiên 1 file trong manifest để trả lời 3 câu hỏi sau:
1. File này lấy từ nguồn nào, có giấy phép gì?
2. File thuộc dataset nhóm A hay B?
3. Nếu website gốc bị gỡ thì còn cách nào xác minh nội dung từng dùng là gì?

Ví dụ:

1. File này có nguồn gốc từ đâu, có giấy phép gì?
Trả lời:  
+ file name:  SRC-03_CayThuocNam_2003.pdf
+ source_id:  SRC
+ source_url:  https://yhoccotruyenqd.vn/download/Y-hoc-co-truyen/Phong-va-chua-benh-bang-cay-thuoc-nam.html 
+ license_status: Public

2. File này thuộc datáet nhóm nào?
+ dataset_group: yhct-corpus

3. Nếu website gốc bị gỡ thì còn cách nào xác minh nội dung từng dùng là gì?
Có thể xác minh bản dữ liệu đã sử dụng nếu bản sao Bronze vẫn được lưu giữ. Manifest cung cấp storage_path và SHA-256 để xác định và kiểm tra bản sao đó. Còn chỉ nhìn Manifest + Source Registry mà không còn file Bronze thì không thể khôi phục nội dung của file.