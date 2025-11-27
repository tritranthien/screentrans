# Tính năng Capture Full Screen

## Mô tả
Tính năng mới cho phép bạn chụp và dịch toàn bộ màn hình chỉ với một cú nhấp chuột hoặc phím tắt.

## Cách sử dụng

### 1. Sử dụng System Tray Menu
- Click phải vào biểu tượng Screen Translator trên system tray
- Chọn **🖥️ Capture Full Screen**
- Ứng dụng sẽ tự động chụp toàn màn hình và dịch tất cả văn bản tìm thấy

### 2. Sử dụng Phím tắt (Hotkey)
- Nhấn **Ctrl+Shift+J** (mặc định) để chụp toàn màn hình
- Bạn có thể tùy chỉnh phím tắt trong file `config.json`

### 3. So sánh với Capture Region
| Tính năng | Capture Region | Capture Full Screen |
|-----------|---------------|---------------------|
| Phím tắt mặc định | Ctrl+J | Ctrl+Shift+J |
| Vùng chụp | Vùng bạn chọn | Toàn màn hình |
| Sử dụng khi | Dịch một phần nhỏ | Dịch toàn bộ màn hình |

## Cấu hình

Trong file `config.json`, bạn có thể tùy chỉnh:

```json
{
  "hotkey": "Ctrl+J",              // Phím tắt cho Capture Region
  "fullscreen_hotkey": "Ctrl+Shift+J"  // Phím tắt cho Capture Full Screen
}
```

### Các phím tắt hợp lệ:
- `Ctrl+J`, `Ctrl+Shift+J`, `Ctrl+Alt+J`
- `Shift+F1`, `Ctrl+F2`, `Alt+F3`
- `Win+J`, `Win+Shift+J`

## Lưu ý
- Tính năng Capture Full Screen rất hữu ích khi bạn muốn dịch toàn bộ nội dung trên màn hình
- Với màn hình lớn, quá trình OCR có thể mất nhiều thời gian hơn
- Kết quả sẽ hiển thị trong overlay window như bình thường
