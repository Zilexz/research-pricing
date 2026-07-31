# Kiến trúc Demo — App mô phỏng đặt xe & dự báo giá đối thủ

**Mục tiêu:** demo local chạy trên bản đồ Boston thật, cho phép chọn điểm đón/đến + cấu hình ngữ
cảnh (giờ, thời tiết, độ trễ) → model dự đoán **giá & hệ số nhân** của đối thủ.

---

## 1. Sơ đồ tổng thể

```
┌──────────────────────────── TRÌNH DUYỆT (Frontend) ────────────────────────────┐
│  index.html  +  Leaflet.js                                                      │
│  • Bản đồ Boston (OpenStreetMap tiles)                                          │
│  • 12 marker khu vực · click chọn đón → đến · vẽ polyline tuyến                 │
│  • Panel cấu hình: hãng, dịch vụ, giờ, thứ, độ trễ, thời tiết                   │
│  • Hiển thị kết quả: giá USD, hệ số nhân, P(surge)                             │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │  HTTP (JSON)
              GET /            GET /api/meta        POST /api/predict
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────────┐
│  server.py  —  http.server (built-in, KHÔNG cần Flask/FastAPI)                  │
│  • Phục vụ index.html                                                           │
│  • /api/meta   → danh sách khu, dịch vụ, thời tiết                             │
│  • /api/predict → nhận cấu hình, dựng feature, gọi model, trả giá             │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │  (in-process, Python)
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌──────────────────┐         ┌──────────────────┐
│ route_lookup  │         │  models.joblib   │         │  meta.json       │
│ surge_lookup  │         │  m_uber, m_lyft  │         │  toạ độ 12 khu   │
│ (bảng tra cứu │         │  clf, reg (surge)│         │  ds dịch vụ/thời │
│  đặc trưng)   │         │                  │         │  tiết            │
└───────────────┘         └──────────────────┘         └──────────────────┘
        ▲                           ▲
        └─────────── sinh bởi ──────┘
                  prepare.py  (chạy 1 lần)
                       ▲
                       │ đọc
              data/snapshot_price_15min.csv
              data/snapshot_surge_15min.csv
```

---

## 2. Ba thành phần

### 2.1 `prepare.py` — Tiền xử lý (chạy 1 lần)

Đọc snapshot đã có → sinh ra mọi thứ app cần:

| Đầu ra | Nội dung |
|---|---|
| `models.joblib` | 3 model đã train: `m_uber`, `m_lyft` (giá), `clf`+`reg` (surge 2 tầng) |
| `route_lookup.json` | 864 dòng (hãng × tuyến × dịch vụ) → quãng đường + giá lag điển hình |
| `surge_lookup.json` | 72 tuyến → lag_surge, roll_surge_rate, thời tiết phổ biến |
| `meta.json` | Toạ độ 12 khu Boston, danh sách dịch vụ, danh sách thời tiết |

> Train lại model tại đây (không load `.joblib` cũ) để **tránh lỗi lệch phiên bản sklearn**.

### 2.2 `server.py` — Backend

Dùng `http.server` của Python chuẩn — **không cần cài web framework**. Load sẵn model + lookup
vào RAM lúc khởi động. Ba route:

| Route | Việc |
|---|---|
| `GET /` | Trả `index.html` |
| `GET /api/meta` | Trả danh sách khu / dịch vụ / thời tiết (để fill dropdown) |
| `POST /api/predict` | Nhận cấu hình → dự đoán → trả JSON giá + surge |

### 2.3 `index.html` — Frontend

Một file HTML thuần + Leaflet (CDN). Không cần build tool. Hiển thị map, marker, panel cấu hình,
kết quả.

---

## 3. Luồng một lần dự đoán (POST /api/predict)

```
1. Người dùng chọn: hãng=Lyft, đón=Back Bay, đến=Fenway, dịch vụ=Lyft, giờ=18, thứ=4, độ trễ=15p
        │
2. server.py tra route_lookup[(Lyft, Back Bay, Fenway, Lyft)]
        → distance_median=1.42, lag1_price=7.0, roll_mean6_price=7.67, ...
        │
3. Dựng 1 dòng feature đầy đủ (14 cột model giá cần):
        name, source, destination, observation_age_bucket,
        distance_median, lag1/2/3_price, roll_mean6/std3, observation_age, hour, weekday, is_weekend
        │
4. Giá = exp( m_lyft.predict(X) )          ← đổi ngược log-target về USD
        │
5. Surge (chỉ Lyft): tra surge_lookup[(Back Bay, Fenway)]
        → clf.predict_proba → P(surge);  reg.predict → độ lớn
        → E[hệ số nhân] = P·độ_lớn + (1−P)·1.0
        │
6. Trả JSON: { gia_du_doan: 7.6, he_so_nhan: 1.117, P_surge: 0.368, quang_duong: 1.42 }
```

**Điểm mấu chốt về feature:** model là **nowcasting** (cần "giá đối thủ quan sát gần đây"). App
không có lịch sử realtime → lấy **giá lag điển hình của tuyến** từ `route_lookup` làm thay. Tức
app trả lời: *"với tuyến & giờ này, model dự đoán giá đối thủ khoảng bao nhiêu."*

---

## 4. Model bên trong (đã train ở prepare.py)

| Model | Loại | Vai trò |
|---|---|---|
| `m_uber`, `m_lyft` | HistGradientBoostingRegressor (log-target) | Dự đoán **giá cuối** (đã gồm surge) |
| `clf` | HistGradientBoostingClassifier | Tầng 1: P(có surge) |
| `reg` | HistGradientBoostingRegressor | Tầng 2: độ lớn khi có surge |

---

## 5. Giới hạn kiến trúc (có chủ ý, đúng với báo cáo)

| Giới hạn | Lý do | Hệ quả trên app |
|---|---|---|
| Không có input **tắc đường** | Dataset thiếu cột thời lượng chuyến đi | App **không** có ô cấu hình tắc đường |
| **Thời tiết** chỉ tác động surge Lyft | Model giá không dùng weather (chỉ ~5%, lẫn hiệu ứng ngày) | Đổi thời tiết chỉ đổi surge |
| Điểm đón/đến = **12 khu Boston** | Đúng độ phân giải model được train | Không chọn toạ độ tự do |
| Lag lấy từ **giá điển hình tuyến** | App không có luồng giá realtime | Kết quả là "giá điển hình", không phải realtime |

> **Nâng cấp khi có data mới của mentor** (duration + cung–cầu): chỉ cần train lại trong
> `prepare.py`, thêm feature vào lookup → app phản ứng được với tắc đường & thời tiết như đời thực,
> không phải sửa kiến trúc.

---

## 6. Công nghệ dùng

| Lớp | Công nghệ | Vì sao |
|---|---|---|
| Bản đồ | Leaflet + OpenStreetMap | Miễn phí, không cần API key |
| Backend | `http.server` (Python chuẩn) | Không cần cài Flask/FastAPI, chạy ngay |
| Model | scikit-learn HistGradientBoosting | Đã có sẵn từ cấu phần (ii) |
| Dữ liệu | CSV snapshot → JSON lookup | Nhẹ, load nhanh lúc khởi động |
```
Phụ thuộc: chỉ cần  pandas · numpy · scikit-learn · joblib  (đã có sẵn cho dự án)
Cần internet để tải: tiles bản đồ + thư viện Leaflet (CDN). Model chạy hoàn toàn local.
```
