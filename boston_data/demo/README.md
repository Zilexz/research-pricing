# 🚕 App mô phỏng đặt xe — Dự báo giá đối thủ (Boston)

Demo local: chọn điểm đón/đến trên bản đồ Boston thật → model dự đoán **giá & hệ số nhân** của đối thủ.

## Cách chạy

```bash
# Bước 1 (chạy 1 lần): dựng bảng tra cứu + train model
python demo/prepare.py

# Bước 2: khởi động server
python demo/server.py
```

Rồi mở trình duyệt: **http://localhost:8000**

> Cần internet để tải bản đồ (OpenStreetMap) và thư viện Leaflet. Model + dữ liệu chạy hoàn toàn local.

## Dùng thế nào

1. **Click 2 khu** trên bản đồ (lần 1 = điểm đón, lần 2 = điểm đến), hoặc chọn ở panel bên phải.
2. Cấu hình: hãng đối thủ (Uber/Lyft), dịch vụ, giờ, thứ, độ trễ quan sát, thời tiết.
3. Bấm **Dự đoán giá** → hiện giá USD, hệ số nhân, xác suất surge.

## Cách hoạt động

```
Người dùng chọn (khu đón, khu đến, dịch vụ, giờ...)
   → tra bảng route_lookup: quãng đường + giá quan sát gần đây của tuyến đó
   → dựng đủ feature model cần
   → model .joblib dự đoán giá (exp of log-target) + surge (2 tầng)
   → trả về giao diện
```

## Giới hạn (đúng như báo cáo)

- **Không có ô cấu hình tắc đường** — vì model học từ dataset Boston thiếu cột thời lượng, chưa
  thể phản ứng với tắc đường. Đây là minh hoạ trực quan cho nhược điểm dữ liệu.
- **Thời tiết** chỉ ảnh hưởng tới **surge của Lyft** (Uber không có surge trong dataset).
- Điểm đón/đến giới hạn trong **12 khu lõi Boston** (đúng độ phân giải model được train).
- Khi có data mới của mentor (duration + cung–cầu) → train lại → app sẽ phản ứng được với
  tắc đường/thời tiết như đời thực.

## File

| File | Vai trò |
|---|---|
| `prepare.py` | Dựng lookup + train model (chạy 1 lần) |
| `server.py` | Backend (http.server built-in, không cần Flask) |
| `index.html` | Giao diện bản đồ Leaflet + cấu hình |
| `models.joblib`, `*_lookup.json`, `meta.json` | Sinh bởi prepare.py |
