# Dữ liệu trước & sau xử lý — Tác dụng từng bước

**Script:** `model/data_preparation.ipynb` · **Input:** `dataset_clean.parquet` · **Output:** `snapshot_*.csv`

Tài liệu này ghi lại dữ liệu **thay đổi thế nào** qua bước xử lý và **vì sao** cần mỗi bước.

---

## 1. Tổng quan trước → sau

| | **TRƯỚC** (`dataset_clean.parquet`) | **SAU** (`snapshot_price_15min.csv`) |
|---|---|---|
| Đơn vị 1 dòng | 1 **báo giá lẻ** (quote) | 1 **snapshot** (series × mốc 15 phút) |
| Số dòng | 637.322 | 471.649 |
| Số cột | 63 | 36 |
| Bản chất | Danh sách quote rời rạc | **Chuỗi thời gian** có lag/rolling/độ trễ |
| Chia tập | Chưa có | train / calibration / test (theo thời gian) |

> **Gộp:** 637.322 quote → **471.649 snapshot** giá. Nhiều quote trong cùng (series × 15 phút)
> được gộp thành 1 dòng → giảm trùng lặp, biến dữ liệu điểm rời thành chuỗi thời gian.

**Hai bảng đầu ra (2 độ phân giải khác nhau):**

| File | Đơn vị (series) | Số dòng | Số series | Ghi chú |
|---|---|---|---|---|
| `snapshot_price_15min.csv` | source × destination × **name** | 471.649 | 864 | cấp cuốc, tách từng hãng |
| `snapshot_surge_15min.csv` | source × destination | 66.445 | 72 | cấp thị trường, chỉ Lyft, bỏ Shared |
| `*_60min.csv` | (như trên, bucket 1 giờ) | — | — | đối chứng |

---

## 2. Các bước xử lý & tác dụng

### Bước 1 — Gộp snapshot theo 2 độ phân giải

**Làm gì:** gộp các quote về mốc thời gian tròn (15 phút), theo từng series.
- **Giá:** series = `source × destination × name`, target = **median** giá trong bucket.
- **Surge:** series = `source × destination` (bỏ `name`), target = **mean** của `surge_multiplier`.

**Tác dụng:**
- Biến dữ liệu **điểm rời** thành **chuỗi thời gian** — điều kiện bắt buộc để tạo lag/rolling.
- **Median cho giá** → chống lệch bởi vài quote bất thường.
- **Mean cho surge** (không median): trong 1 bucket nếu chỉ vài quote có surge thì median vẫn
  = 1.0 → mất tín hiệu; mean giữ được cường độ.
- Surge để ở **cấp thị trường** (bỏ `name`) vì surge dùng chung mọi dịch vụ trong 1 bucket →
  nếu để cấp cuốc sẽ **đếm trùng**.

### Bước 2 — Feature thời gian

**Làm gì:** từ mốc `snapshot` suy ra `hour_local`, `weekday_local`, `is_weekend`, `hour_sin`, `hour_cos`.

**Tác dụng:** cho model biết ngữ cảnh giờ/thứ. `hour_sin/cos` mã hoá **chu kỳ** (giờ không đơn
điệu — 23h gần 0h) mà số nguyên 0–23 không thể hiện được.

### Bước 3 — Lag / Rolling / Độ trễ ⭐ quan trọng nhất

**Làm gì:** với mỗi series (sắp theo thời gian), sinh **21 cột mới**:

| Cột mới | Ý nghĩa |
|---|---|
| `lag1/2/3_price` | Giá ở 1/2/3 mốc **trước** |
| `delta_price_1_2` | Xu hướng (đang tăng/giảm) |
| `roll_mean3/6_price` | Mức giá nền gần đây (lọc nhiễu) |
| `roll_std3_price` | Độ biến động thị trường |
| `observation_age_minutes` | **Dữ liệu đang cũ bao nhiêu phút** (= độ trễ τ) |
| `observation_age_bucket` | Nhóm độ trễ (≤15p … >3h) |
| `target_price`, `price_min/max/spread`, `quote_count`, … | Thống kê bucket |

**Tác dụng:**
- Lag/rolling cung cấp **"giá đối thủ quan sát gần đây"** — chính là đầu vào của bài toán
  nowcasting.
- `observation_age` là **feature định danh** của bài toán quan sát trễ.
- 🔒 **Chống rò rỉ:** mọi feature chỉ dùng `shift(k≥1)` → không nhìn thấy giá trị tại mốc hiện
  tại. (`lag1_price` thiếu 0,2% — là dòng đầu mỗi series, đúng như mong đợi.)

### Bước 4 — Gán split theo thời gian

**Làm gì:** gán mỗi dòng vào `train` (≤10/12) · `calibration` (13–15/12) · `test` (≥16/12);
11–12/12 là **buffer** bị loại.

**Tác dụng:**
- Đây là bài toán **dự báo** → chia theo thời gian, **không chia ngẫu nhiên** (chia random sẽ
  để model "nhìn thấy tương lai" → kết quả đẹp giả).
- Buffer 11–12/12 để train không dính sát calibration.
- `calibration` riêng dành cho **Conformal Prediction** (cấu phần iii).

**Kết quả chia (bảng giá 15 phút):** train 289.271 · calibration 97.697 · test 84.681.

---

## 3. Số liệu kiểm chứng (đo từ file thật)

| Chỉ số | Giá trị |
|---|---|
| Quote gốc (Uber + Lyft) | 637.322 |
| Snapshot giá sau gộp | 471.649 (864 series) |
| Snapshot surge sau gộp | 66.445 (72 series) |
| Tỷ lệ surge (mean>1) | 14,45% |
| Độ trễ quan sát (median) | 30 phút |
| `lag1_price` thiếu (dòng đầu series) | 0,2% |
| Cột mới sinh ra | 21 |

---

## 4. Các cột đã LOẠI khi xử lý (không đưa vào model)

| Cột | Lý do loại |
|---|---|
| `moonPhase`, `pressure`, `ozone` | Proxy ngày (1 giá trị/ngày) |
| `latitude`, `longitude` | Lệch hàng so với `source` |
| `price_per_mile` | Bị quãng đường làm nhiễu |
| `apparentTemperature`, `windGust`… | Trùng với `temperature`, `windSpeed` |
| `cab_type` (trong feature) | Đã nằm trong `name` |

> ⚠️ **Cột có trong file nhưng CẤM dùng làm feature** (rò rỉ đồng thời — tính tại t):
> `target_price`, `price_min/max/spread`, `quote_count`. Chỉ được dùng `lag1_quote_count` (từ t−1).

---

**Bước tiếp theo:** mở `model/model_train.ipynb` để huấn luyện.
