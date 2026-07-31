# Pipeline Dự đoán Giá & Hệ số nhân của Đối thủ

**Dự án:** Competitor Fare Forecasting (XanhSM / GreenSM)
**Cập nhật:** 22/07/2026 — phiên bản đã tối ưu dựa trên kết quả phân tích thực nghiệm

---

## Bài toán

> Cho biết giá đối thủ quan sát được ở **các mốc trước** + ngữ cảnh chuyến đi,
> dự đoán **giá** và **hệ số nhân** đối thủ đang áp dụng **ngay bây giờ**, kèm **khoảng tin cậy**.

Cụm *"các mốc trước"* là trọng tâm: hệ thống chỉ thu thập được giá đối thủ ở những thời
điểm rời rạc, nên khi cần báo giá thì dữ liệu đã cũ vài phút đến vài chục phút.

---

## Sơ đồ tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│  BƯỚC 0 — Làm sạch dữ liệu                                      │
│  693.071 dòng thô  →  637.322 dòng sạch                         │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  BƯỚC 1 — Tách theo HÃNG                                        │
│  Uber (330.070)   │   Lyft (307.252)                            │
│  Mỗi hãng một model riêng — công thức giá khác nhau             │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  BƯỚC 2 — Gộp thành SNAPSHOT theo 2 độ phân giải                │
│                                                                  │
│   price  →  series = tuyến × dịch vụ, gộp theo giờ              │
│   surge  →  series = tuyến,           gộp theo giờ (bỏ Shared)  │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  BƯỚC 3 — Feature Engineering                                   │
│  Ngữ cảnh · Lag · Rolling · Độ trễ quan sát                     │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  BƯỚC 4 — Chia dữ liệu THEO THỜI GIAN                           │
│  train → calibration → test  (không bao giờ chia ngẫu nhiên)    │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
        ┌────────────────────┴────────────────────┐
        ▼                                         ▼
┌───────────────────┐                   ┌───────────────────┐
│ PART I            │                   │ PART II           │
│ Phân tích         │──── feature ─────▶│ Model             │
│ EDA · Correlation │                   │ CatBoost/LGBM/XGB │
│ Importance · SHAP │                   │ → price, surge    │
└───────────────────┘                   └─────────┬─────────┘
                                                  ▼
                                        ┌───────────────────┐
                                        │ PART III          │
                                        │ Conformal         │
                                        │ Prediction        │
                                        │ → khoảng tin cậy  │
                                        └─────────┬─────────┘
                                                  ▼
                                        ┌───────────────────┐
                                        │ ĐÁNH GIÁ          │
                                        │ vs baseline       │
                                        │ suy giảm độ trễ   │
                                        └───────────────────┘
```

---

## BƯỚC 0 — Làm sạch dữ liệu

**Đầu vào:** `rideshare_kaggle.csv` (693.071 dòng, 57 cột)
**Đầu ra:** `dataset_clean.parquet` (637.322 dòng, 63 cột)
**Notebook:** `analysis/00_clean_full_dataset.ipynb`

| Việc | Tác dụng |
|---|---|
| Bỏ 55.749 dòng thiếu giá (toàn bộ loại `Taxi`) | `price` là biến mục tiêu — dòng không có giá thì vô dụng |
| **Bỏ 654 bản ghi trùng lặp** (giống mọi cột trừ `id`) | Tránh đếm trùng, tránh cùng một quan sát rơi vào cả train lẫn test |
| Bỏ cột `visibility.1` (trùng 100%) và `timezone` (1 giá trị) | Giảm nhiễu, tránh chia phiếu importance |
| Sửa `timestamp` lỗi định dạng khoa học | Tránh mất dòng khi ép kiểu |
| Đổi UTC → giờ Boston (UTC−5) | Phân tích giờ cao điểm phải theo giờ địa phương |
| Tạo 8 cột dẫn xuất | `hour_local`, `weekday_local`, `is_weekend`, `price_per_mile`, `is_surge`… |

> ⚠️ **Không** dùng `timestamp + tuyến + dịch vụ` làm khoá chống trùng — `timestamp` bị làm
> tròn nên nhiều chuyến **khác nhau thật** (quãng đường khác) lại trùng khoá, xoá nhầm ~12.000 dòng hợp lệ.

---

## BƯỚC 1 — Tách theo hãng

**Tác dụng:** mỗi hãng có **công thức giá riêng**, gộp chung sẽ làm model học sai.

Bằng chứng:

| Dải quãng đường | Uber rẻ hơn Lyft |
|---|---|
| < 1 dặm | −2,5% |
| 2–3 dặm | −10,0% |
| 3–4 dặm | −11,5% |

Khoảng cách **giãn ra** theo quãng đường → **đơn giá/dặm khác nhau**, không phải lệch một
hằng số. Thêm nữa danh mục dịch vụ **không trùng nhau chút nào** (Uber: UberX, Black, WAV… ·
Lyft: Lyft, Lux, Shared…).

> Trong bài toán thật, đây tương ứng với việc train **model riêng cho Grab và cho Be**.

---

## BƯỚC 2 — Gộp thành snapshot theo 2 độ phân giải

Đây là bước dễ làm sai nhất. **Hai target có độ phân giải khác nhau.**

### `price` — cấp từng chuyến

```
series_id = source × destination × name
snapshot  = gộp theo từng giờ
```

Mỗi loại dịch vụ có giá riêng → phải giữ `name` trong định nghĩa chuỗi.

### `surge` — cấp thị trường

```
series_id = source × destination        (KHÔNG có name)
snapshot  = gộp theo từng giờ
loại bỏ   = dịch vụ Shared
```

**Tác dụng:** tránh đếm trùng. Bằng chứng surge là đại lượng cấp thị trường:

- 5 dịch vụ Lyft có **đúng cùng số cuốc surge** (4.195 mỗi loại)
- Trong cùng (thời điểm × tuyến), surge giống hệt nhau ở **98,5%** trường hợp
- `Shared` **không bao giờ** surge (0/51.233 cuốc)

Nếu để nguyên từng cuốc: 256.037 dòng nhưng chỉ chứa **120.067 quan sát độc lập** —
tức mỗi quan sát bị lặp **2,1 lần**, làm độ tin cậy bị thổi phồng.

> 🔗 Điều này khớp với tài liệu nghiên cứu của mentor: *"hệ số nhân thị trường được dùng
> chung cho mọi báo giá trong bucket"*.

---

## BƯỚC 3 — Feature Engineering

### Nhóm A — Ngữ cảnh chuyến đi ⭐ quan trọng nhất

| Feature | Tác dụng | Bằng chứng |
|---|---|---|
| **`name`** | Bậc giá của hạng xe | Giải thích **70–76%** phổ giá |
| **`distance`** | Độ dài chuyến | Cùng `name` cho **R² 0,90–0,95** |
| `source` | Khu vực đón | 14–17% phổ giá · **η 0,15 với surge** (mạnh nhất) |
| `destination` | Khu vực đến | 12–16% phổ giá |

> ❌ **Không dùng `cab_type`** — đã nằm trong `name` (UberX ⇒ Uber), đóng góp **0,0%**.

### Nhóm B — Thời gian

| Feature | Tác dụng |
|---|---|
| `hour_local` | Giờ cao điểm — **mã hoá phân loại**, không dùng số nguyên 0–23 |
| `weekday_local`, `is_weekend` | Chu kỳ tuần |

> ⚠️ Quan hệ giờ ↔ surge **không đơn điệu** (cao 8h → thấp 11h → cao 17h) nên Pearson ≈ 0
> dù thực tế có tín hiệu. Phải mã hoá phân loại hoặc chu kỳ sin/cos.

### Nhóm C — Lag & Rolling ⭐ lõi của bài toán

| Feature | Tác dụng |
|---|---|
| `lag1/2/3_price` | Giá đối thủ ở các mốc trước |
| `lag1_surge` | Hệ số nhân ở mốc trước |
| `rolling_mean_3/6` | Mức giá nền gần đây, lọc nhiễu |
| `rolling_std_3` | Độ biến động — thị trường đang ổn định hay xáo trộn |
| `price_delta_1_2` | Xu hướng: giá đang tăng hay giảm |
| **`observation_age_minutes`** | **Dữ liệu đang cũ bao nhiêu phút** |

**Vì sao nhóm này quyết định:** `history_price_mean_last6` có importance **0,742** — cao gấp
2,8 lần `name` (0,266). Hệ số nhân **không dự đoán được** từ ngữ cảnh (R² 0,04) nhưng
**quan sát được** từ giá gần đây.

> 💡 Ý tưởng mượn từ Tầng 1 của tài liệu mentor: tách thành **mức độ** (giá đang cao/thấp
> bất thường) và **chuyển động** (đang tăng hay giảm), rồi làm mượt bằng trung vị → trung
> bình mũ → clip.

### Nhóm D — Thời tiết ⚠️ mức độ ưu tiên thấp

Giữ `short_summary`, `temperature`, `precipIntensity` để **theo dõi**, nhưng kỳ vọng thấp:

- Chỉ giải thích **~5%** phổ giá, η = 0,010 với surge
- `Drizzle` chỉ xuất hiện **2 ngày**, `Rain`/`Foggy` **3 ngày** trong 18 ngày → **lẫn với
  hiệu ứng ngày**, kết luận không đáng tin

> 🔄 Trên dữ liệu GreenSM (khí hậu Việt Nam, mùa mưa rõ rệt) **phải đánh giá lại**.

### ❌ Các feature KHÔNG dùng

| Feature | Lý do loại |
|---|---|
| `holiday` | **Không có ngày lễ nào** trong 25/11–18/12/2018 → hằng số |
| `latitude`, `longitude` | **Bị lệch hàng** so với `source`; 1 toạ độ sai lệch 15 km |
| `moonPhase` | Đúng **1 giá trị/ngày** → mã số ngày trá hình (r = 0,845 với số thứ tự ngày) |
| `pressure`, `ozone` | Proxy ngày (r > 0,5), không khái quát sang dữ liệu khác |
| `cab_type` | Trùng với `name` |
| `apparentTemperature`, `windGust` | Trùng \|r\| > 0,93 với `temperature`, `windSpeed` |
| `price_per_mile` | Bị quãng đường làm nhiễu nặng (r = −0,92); max 1.375 USD/dặm |
| `distance × service` | Model cây **tự học** tương tác (+0,0002). *Chỉ cần cho model tuyến tính (+0,021).* |
| `route` ghép tay | `source` + `destination` riêng là đủ; ghép chỉ +0,0001 mà tăng cardinality |

### 🚨 Quy tắc chống rò rỉ

Tại mốc thời gian **t**, chỉ được dùng:

- ✅ Ngữ cảnh biết trước: `name`, `distance`, `source`, `destination`, thời gian, thời tiết
- ✅ Lag từ mốc **t−1 trở về trước**
- ❌ **Tuyệt đối không** dùng giá/surge **tại mốc t** làm feature
- ❌ Không dùng các thống kê cùng mốc: `price_min/max/spread`, `quote_count` tại t

---

## BƯỚC 4 — Chia dữ liệu theo thời gian

```
train        →  calibration  →  test
(quá khứ)       (giữa)          (tương lai)
```

**Tác dụng:** đây là bài toán **dự báo**. Chia ngẫu nhiên sẽ để model "nhìn thấy tương lai"
→ kết quả đẹp giả tạo, sập khi chạy thật.

Tập **calibration** riêng là **bắt buộc** cho Conformal Prediction ở Part III — không được
dùng chung với train.

---

## PART I — Phân tích & chọn feature

**Đã hoàn thành.** 7 notebook trong `analysis/key_feature_analysis/`.

| Phương pháp | Bắt được gì | Điểm mù |
|---|---|---|
| Pearson / Spearman | Quan hệ tuyến tính / đơn điệu | Mù với quan hệ răng cưa (như giờ) |
| Mutual Information | Quan hệ phi tuyến | Không cho biết chiều |
| Correlation ratio (η) | Sức mạnh biến phân loại | Bị thổi phồng nếu nhiều nhóm |
| Permutation importance | Cái model **thực sự** dùng | Bị chia phiếu khi feature trùng lặp |
| SHAP | Đóng góp từng dòng, có chiều | Chậm; sai lệch khi feature tương quan |
| Hồi quy có kiểm soát | **Hiệu ứng thuần** tính bằng % | Giả định dạng hàm |

> **Không tin một chỉ số đơn lẻ.** `moonPhase` đứng cao ở *cả* MI *lẫn* permutation nhưng
> vẫn là rác — chỉ lộ ra khi kiểm tra "proxy ngày".

**Kết quả xếp hạng:**

| Yếu tố | % phổ giá | η với surge |
|---|---|---|
| Loại xe | **70–76%** | — |
| Khu vực | 14–17% | **0,152** |
| Giờ | ~5% | 0,011 |
| Thời tiết | ~5% | 0,010 |

---

## PART II — Model

### Bộ feature đề xuất

```
Model GIÁ   : name, distance, source, destination
              + lag1/2/3_price, rolling_mean_6, rolling_std_3, observation_age

Model SURGE : source, destination, hour_local, short_summary
              + lag1_surge, rolling_surge_rate, observation_age
              (train trên bảng CẤP THỊ TRƯỜNG, đã bỏ Shared)
```

### Model

CatBoost / LightGBM / XGBoost — đều là gradient boosting, phù hợp dữ liệu bảng và tự học
tương tác. CatBoost xử lý biến phân loại tốt nhất, đỡ phải one-hot.

### Chỉ số đánh giá

| Target | Dùng | ❌ Không dùng |
|---|---|---|
| `price` | MAE, RMSE, R², MAPE | — |
| `surge` | **ROC-AUC, PR-AUC** | **Accuracy** |

> ⚠️ Surge chỉ chiếm ~8,6% → đoán "không surge" cho tất cả đã đạt accuracy **0,914**.
> Model đạt 0,933 nghe có vẻ tốt nhưng thực chất **chỉ hơn 0,002**. Phải đọc ROC-AUC.

### Baseline bắt buộc so sánh

| Baseline | Cách đoán | Ý nghĩa |
|---|---|---|
| **Persistence** | Lấy y hệt giá quan sát gần nhất | Phương án **không cần AI**. Không thắng nó thì dự án vô nghĩa |
| Hằng số | Luôn đoán surge = 1.0 | Ngưỡng tầm thường cho multiplier |

---

## PART III — Conformal Prediction

**Tác dụng:** biến dự đoán điểm thành **khoảng có bảo đảm thống kê**.

```
Giá đối thủ: 18,4 USD  →  khoảng 80%: [17,2 · 20,6]
```

**Vì sao chọn Conformal:**

- Không giả định phân phối sai số
- Gắn được vào **bất kỳ** model nào (CatBoost, LGBM…)
- **Có bảo đảm toán học** về độ phủ, miễn là dữ liệu trao đổi được

**Cách làm:**

1. Train model trên tập **train**
2. Tính phần dư trên tập **calibration** (chưa từng thấy)
3. Lấy phân vị 80% của trị tuyệt đối phần dư → nửa độ rộng khoảng
4. Áp lên tập **test**

**Chỉ số đánh giá:**

| Chỉ số | Yêu cầu |
|---|---|
| **Coverage** | Khoảng 80% phải phủ đúng **~80%** giá trị thật (75–85% là đạt) |
| **Độ rộng khoảng** | Càng hẹp càng tốt — nhưng phải đạt coverage trước |

> Khoảng [0, 100] luôn phủ 100% nhưng vô dụng. Phải đọc **cả hai** chỉ số.

**Vì sao khoảng tin cậy quan trọng về kinh doanh:** hai tình huống cùng dự đoán 18,50 nhưng
khác nhau hoàn toàn — `[18,2 · 18,8]` → định giá sát; `[12,0 · 25,0]` → phải để biên an toàn.

---

## BƯỚC CUỐI — Đánh giá

### 1. So với baseline

Luôn báo cáo kèm baseline: *"MAE = 1,38 so với baseline 1,94 (cải thiện 29%)"* — không bao
giờ báo cáo con số trần trụi.

### 2. ⭐ Phân tích suy giảm theo độ trễ

```
Quan sát cũ  5 phút  →  MAE = ?
Quan sát cũ 15 phút  →  MAE = ?
Quan sát cũ 30 phút  →  MAE = ?
Quan sát cũ  1 giờ   →  MAE = ?
```

**Tác dụng:** trả lời câu hỏi tiền bạc — **"bao lâu phải thu thập giá đối thủ một lần?"**
Nếu 1 tiếng vẫn chính xác thì tiết kiệm được rất nhiều chi phí crawl. Đây có thể là kết quả
giá trị nhất của cả PoC.

---

## Giới hạn đã biết của dữ liệu

| Hạn chế | Bằng chứng | Hệ quả |
|---|---|---|
| **Uber không có surge** | 330.070 dòng đều = 1.0 | Model surge chỉ train được trên Lyft |
| **Sàn nhiễu ~2 USD** | Cùng loại xe, cùng quãng đường **chính xác 0,01 dặm**, cùng **một giây** → 90,7% vẫn khác giá | Trần của mọi model: R² ≈ 0,90–0,95 |
| **Thiếu biến thời lượng** | Đã loại trừ surge/tắc đường/thời tiết bằng phép thử cùng-thời-điểm | Nghi phạm chính của sàn nhiễu |
| **Không có tín hiệu cung–cầu** | Số báo giá mỗi (khu × giờ) có CV = 0,09 → là lịch crawl, không phải nhu cầu | Trần của model surge |
| **12 khu đều là trung tâm** | Trải trên 2,9 × 4,2 km; cặp gần nhất cách 0,31 km | Chưa kiểm chứng được vùng ngoại ô |
| **Chỉ 18 ngày mùa đông** | 25/11–18/12/2018, thiếu 6 ngày | Thời tiết lẫn với hiệu ứng ngày |

---

## Tiến độ

| Phần | Trạng thái | % |
|---|---|---|
| Bước 0 — Làm sạch | ✅ Xong | 100% |
| Bước 1 — Tách hãng | ✅ Xong | 100% |
| Bước 2 — Snapshot | ⏳ Có bản cũ (60k), cần dựng lại trên 637k | 50% |
| Bước 3 — Feature Engineering | ⏳ Đã chốt danh sách, chờ bảng snapshot | 50% |
| Bước 4 — Chia theo thời gian | ✅ Đã định nghĩa | 100% |
| **Part I — Phân tích** | ✅ 7 notebook | 90% |
| **Part II — Model** | ⏳ Price R² 0,93 · Surge AUC 0,65 | 50% |
| **Part III — Conformal** | ⬜ Chưa bắt đầu | 0% |
| Phân tích độ trễ | ⬜ Chưa bắt đầu | 0% |

**Tổng thể: ~50%**
