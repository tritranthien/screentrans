# ScreenTranslator - Hướng dẫn sử dụng (Portable)

Đây là phiên bản Portable của ScreenTranslator. Bạn chỉ cần tải về và chạy ngay, không cần cài đặt thêm bất kỳ phần mềm nào khác.

## Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11 (64-bit)
- **RAM**: Tối thiểu 4GB (khuyến nghị 8GB)

## Cài đặt và Chạy

1. Tải file nén `.zip` về máy.
2. Giải nén toàn bộ thư mục ra (ví dụ: ra Desktop).
3. Mở thư mục `ScreenTranslator`.
4. Tìm và chạy file **`ScreenTranslator.exe`**.

**Lưu ý**: 
- Không được tách file `.exe` ra khỏi thư mục. Ứng dụng cần các file đi kèm trong thư mục để hoạt động.
- Lần chạy đầu tiên có thể mất vài giây để khởi tạo.

## Sử dụng

### Giao diện chính

Sau khi chạy, bạn sẽ thấy:
- **Nút nổi** (Floating button) ở góc dưới bên phải màn hình
- **Biểu tượng** trong System Tray (khay hệ thống)

### Cách dịch văn bản

**Phương pháp 1**: Click vào nút nổi
1. Click vào nút tròn ở góc màn hình
2. Kéo chọn vùng văn bản cần dịch
3. Kết quả dịch sẽ hiển thị ngay trên màn hình

**Phương pháp 2**: Sử dụng System Tray
1. Click chuột phải vào biểu tượng trong System Tray
2. Chọn "📸 Capture Region"
3. Kéo chọn vùng văn bản cần dịch

### Cài đặt

Click chuột phải vào biểu tượng System Tray → **⚙️ Settings**

#### Translation Engine

**Google Translate (Miễn phí)**:
- Không cần API key
- Dịch nhanh, chất lượng tốt

**Gemini AI (Chất lượng cao)**:
1. Chọn "Gemini AI (Chất lượng cao)"
2. Click "Lấy API Key" để mở trang đăng ký
3. Tạo API key miễn phí tại: https://makersuite.google.com/app/apikey
4. Copy và paste API key vào ô "API Key"

#### Ngôn ngữ

- **Ngôn ngữ nguồn**: Mã ngôn ngữ gốc (ví dụ: `en`, `ja`, `ko`, `zh`)
- **Ngôn ngữ đích**: Mã ngôn ngữ đích (ví dụ: `vi`, `en`)

**Lưu ý**: Thay đổi cài đặt sẽ được áp dụng ngay lập tức!

## Xử lý sự cố

### "Không nhận dạng được văn bản"
- Đảm bảo thư mục `Tesseract-OCR` nằm cùng cấp với file `ScreenTranslator.exe`.
- Đảm bảo vùng chọn có chứa văn bản rõ ràng.

### "Gemini API không hoạt động"
- Kiểm tra API key có đúng không.
- Đảm bảo có kết nối internet.

### Ứng dụng chạy chậm
- Lần chạy đầu tiên sẽ chậm hơn.
- Đảm bảo máy có đủ RAM.

## Gỡ cài đặt

Chỉ cần xóa thư mục `ScreenTranslator` là xong.

## Liên hệ & Hỗ trợ

- **GitHub**: https://github.com/tritranthien/screentrans
