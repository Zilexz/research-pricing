# Dựng lại Snapshot ở bucket 15 phút

**Ngày:** 23/07/2026 · **Script:** `model/data_preparation.py` · **Mục đích:** nền cho cấu phần (ii)

---

## 1. Vì sao phải làm

Bài toán cấu phần (ii): *dự đoán giá đối thủ hiện tại từ quan sát cách đây **5–18 phút**.*
Snapshot cũ gộp theo **giờ** → độ trễ nhỏ nhất phân biệt được là 1 giờ → **không nghiên cứu
được độ trễ 5–18 phút**, mà đó chính là lõi bài toán.

**Lưu ý bản chất:** đây **không phải sinh thêm dữ liệu**. Số báo giá vẫn y nguyên (~18 phút/lần).
Chỉ **chia lưới thời gian mịn hơn** (60 phút → 15 phút) để giữ lại chi tiết mà cách gộp theo
giờ đã làm mất — nhờ đó mới tính được độ trễ.

```
Gộp theo GIỜ (mất chi tiết):        Gộp theo 15 PHÚT (giữ chi tiết):
  14:03  12,5$ ┐                       14:03 → [14:00] 12,5$
  14:11  12,5$ ├→ [14:00] TB 12,6$     14:28 → [14:30] 13,0$
  14:28  13,0$ │                       14:52 → [14:45] 12,5$
  14:52  12,5$ ┘                       (đo được: 15 phút sau giá đổi 0,5$)
```

---

## 2. Các bước đã làm

### Bước 1 — Tham số hoá bucket

Thêm cấu hình `BUCKETS = {"15min": "15min", "60min": "h"}`. Chạy một lần ra **cả hai** bản:
15 phút (bản chính cho mục ii) và 60 phút (giữ làm đối chứng).

### Bước 2 — Refine `observation_age_bucket`

Đổi ngưỡng độ trễ từ `[<=1h, 1-3h, 3-6h, >6h]` (quá thô) sang
**`[<=15p, 15-30p, 30-60p, 1-3h, >3h]`** để phục vụ phân tích suy giảm theo độ trễ τ.

### Bước 3 — Giữ nguyên mọi thứ khác

- Hai độ phân giải: `price` cấp cuốc (route × service), `surge` cấp thị trường (route, bỏ Shared)
- Tách hãng Uber/Lyft
- Lag 1/2/3, rolling mean/std, `observation_age`, split theo thời gian
- Target surge dùng **mean** (giữ cường độ), `target_is_surge` suy trực tiếp từ đó

### Bước 4 — Chạy & kiểm chứng

```
python model/data_preparation.py     # ~150s, ra 4 file
```

---

## 3. Kết quả — 4 file trong `data/`

| File | Snapshot | Series | Ghi chú |
|---|---|---|---|
| `snapshot_price_15min.parquet` | **471.649** | 864 | ⭐ bản chính cho model giá |
| `snapshot_surge_15min.parquet` | **66.445** | 72 | ⭐ bản chính cho model surge |
| `snapshot_price_60min.parquet` | 245.596 | 864 | đối chứng |
| `snapshot_surge_60min.parquet` | 23.293 | 72 | đối chứng |

**So với bản cũ theo giờ: nhiều gấp 1,9× (price) và 2,9× (surge) số snapshot.**

### Độ trễ giữa 2 snapshot (bản 15 phút)

| | Price | Surge |
|---|---|---|
| Median | — | **15 phút** |
| p90 | — | 30 phút |
| Phân bố (surge) | | `<=15p`: 47.779 · `15-30p`: 12.756 · `30-60p`: 5.015 · `1-3h`: 678 · `>3h`: 145 |

→ **72% snapshot có độ trễ ≤ 15 phút** — đúng dải cần nghiên cứu cho bài toán.

### Split theo thời gian (không đổi)

| Split | Khoảng | Surge 15p |
|---|---|---|
| train | 25/11 – 10/12 | 39.761 |
| calibration | 13 – 15/12 | 14.330 |
| test | 16 – 18/12 | 12.354 |

---

## 4. Kiểm chứng chất lượng

### ✅ Không rò rỉ dữ liệu tương lai

| Kiểm tra | Price 15p | Surge 15p |
|---|---|---|
| `lag1 == shift(1)` (đúng cấu trúc thời gian) | 603 lệch | 18 lệch |
| train < calibration < test | ✅ | ✅ |

**603/18 dòng "lệch" đã xác minh là vô hại:** tất cả nằm ở **calibration**, là dòng đầu mỗi
series sau khoảng trống ngày 11–12/12 (đã bị loại khỏi split). Lag của chúng trỏ về quan sát
cuối của **train** — quá khứ hợp lệ, chỉ khác split. Đã chứng minh trước đó: `shift(1)` trên
dữ liệu sắp theo thời gian **về cấu trúc không thể** lấy từ tương lai.

### ✅ Bucket mịn cho target surge trung thực hơn

| Cách đo tỷ lệ surge | Giá trị |
|---|---|
| Per-cuốc (Lyft, bỏ Shared) | 8,2% |
| **Bucket 15 phút** | **14,4%** |
| Bucket 60 phút | 33,7% *(bị thổi phồng — gộp cả giờ nên chỉ cần 1 cuốc surge là mean > 1)* |

Bucket càng mịn thì `target_is_surge = (mean surge > 1)` càng ít bị thổi phồng, càng gần
tỷ lệ per-cuốc thật. Bản 15 phút đáng tin hơn bản 60 phút.

---

## 5. Đánh đổi đã cân nhắc

| Bucket | % ô có dữ liệu | Đánh giá |
|---|---|---|
| 10 phút | 18% | quá rỗng, model khó học |
| **15 phút** | **25%** | ✅ điểm cân bằng đã chọn |
| 60 phút | 53% | đặc nhưng mất chi tiết độ trễ |

15 phút đủ mịn để nghiên cứu độ trễ 5–15 phút, chưa quá rỗng. Ô rỗng **để nguyên, không bịa
số** — model xử lý bằng lag, và khoảng cách tới ô có dữ liệu gần nhất chính là `observation_age`.

---

## 6. Việc tiếp theo (mục ii)

Các file `*_15min.parquet` giờ là đầu vào chuẩn cho:

1. Baseline persistence + historical-average (cả 2 target)
2. Model giá (Uber + Lyft) — CatBoost/LGBM
3. Model surge 2 tầng (Lyft)
4. ⭐ **Phân tích suy giảm theo độ trễ τ** — dùng `observation_age_bucket`, deliverable đắt giá nhất
