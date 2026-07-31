# Phân tích Key Feature — Pricing Research (XanhSM)

Phân tích **quãng đường · thời gian · thời tiết · địa điểm** ảnh hưởng thế nào đến
**giá** và **hệ số nhân** (price multiplier).

## Thứ tự chạy

| File | Nội dung | Thời gian |
|---|---|---|
| `00_tong_quan.ipynb` | Nạp dữ liệu, nêu 2 cạm bẫy phải tránh | ~1s |
| `01_location.ipynb` | 📍 Khu vực → 12 chân dung khu, heatmap, premium thật | ~5s |
| `02_time.ipynb` | 🕐 Giờ / thứ / cuối tuần, xác định giờ cao điểm | ~2s |
| `03_weather.ipynb` | 🌦️ Nhóm thời tiết, mức mưa, nhiệt độ | ~6s |
| `04_distance_baseprice.ipynb` | 📏 Giải mã công thức giá cơ sở | ~19s |
| `05_tong_hop.ipynb` | ⚖️ So sức mạnh + hồi quy kiểm soát | ~11s |

Mỗi notebook chạy **độc lập** — mở lên bấm **Run All** là xong.

## Dữ liệu

Đọc từ `../../data/dataset_clean.parquet` (637.322 chuyến đã làm sạch).
Chưa có file này thì chạy `../00_clean_full_dataset.ipynb` trước.

## `_common.py`

Module dùng chung, mỗi notebook nạp bằng:

```python
import sys; sys.path.insert(0, ".")
from _common import *
setup(); df, dfL = load()
```

| Thành phần | Công dụng |
|---|---|
| `load()` | Trả về `df` (cả 2 hãng), `dfU` (Uber), `dfL` (Lyft) |
| `so_sanh_hang(df, cột)` | Bảng so sánh Uber vs Lyft theo nhóm, kèm chênh lệch % |
| `MAU_HANG` | Màu cố định cho mỗi hãng (Uber xanh, Lyft cam) |
| `setup()` | Cấu hình pandas + matplotlib |
| `eta(groups, y)` | Correlation ratio — sức mạnh giải thích (0–1) |
| `binned(s)` | Chia bin biến số để so sánh công bằng với biến phân loại |
| `base_price_model(df)` | Học giá cơ sở từ chuyến không surge |
| `BLUE, ORANGE, GREEN, RED, PURPLE, MUT` | Bảng màu thống nhất |

## ⚠️ Bốn nguyên tắc bắt buộc

**0. Tách riêng Uber (`dfU`) và Lyft (`dfL`).**
Hai hãng có **công thức giá khác nhau**, không phải chỉ lệch một hằng số:

| Dải quãng đường | Uber rẻ hơn Lyft |
|---|---|
| <1 dặm | −2,5% |
| 2–3 dặm | −10,0% |
| 3–4 dặm | −11,5% |

Khoảng cách **giãn ra** theo quãng đường → đơn giá/dặm khác nhau. Thêm nữa danh mục
dịch vụ **không trùng nhau chút nào** (Uber: UberX, Black, WAV… · Lyft: Lyft, Lux, Shared…).
Chỉ dùng `df` khi cần **so sánh** 2 hãng.

**1. Không so sánh giá thô giữa các khu/giờ.**
Giá bị `quãng đường × loại dịch vụ` chi phối. Tương quan giữa giá TB của khu và
quãng đường TB là **r = 0,986** — chênh lệch giá gần như hoàn toàn do độ dài chuyến.

**2. Hệ số nhân chỉ phân tích trên Lyft (`dfL`).**
Uber có `surge_multiplier = 1.0` ở **toàn bộ** 330.070 dòng (API không trả về trường này).
Gộp vào sẽ pha loãng mọi kết quả bằng số 0 giả.

**3. Số chuyến KHÔNG phải nhu cầu.**
Số báo giá mỗi (khu × giờ) có CV chỉ **0,093** — đó là lịch crawl. Tương quan với
tỷ lệ surge chỉ **0,026**. Muốn đo áp lực cầu, dùng **tỷ lệ surge**.

## Cạm bẫy khác đã gặp

- **`price_per_mile` bị nhiễu nặng** — phí mở cửa chia cho ít dặm khiến khu có chuyến ngắn
  *trông như* đắt (r = −0,92 với quãng đường TB). Phải so trong cùng dải quãng đường.
- **`moonPhase`, `pressure`, `ozone`** là **mã số ngày trá hình** (1 giá trị/ngày) —
  xếp hạng cao nhưng vô dụng, không khái quát được sang dữ liệu khác.
- **Giờ là biến không đơn điệu** (cao ở 8h, thấp 12h, cao lại 17h) → Pearson ≈ 0.
  Phải mã hoá dạng phân loại.
- **Accuracy là chỉ số sai** cho surge (93% là 1.0) → dùng **ROC-AUC**.
