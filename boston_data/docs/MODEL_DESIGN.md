# Thiết kế Model — Cấu phần (ii): Dự báo Giá & Hệ số nhân của đối thủ

**Dự án:** Competitor Fare Forecasting · **Cập nhật:** 23/07/2026
**Đầu vào:** `data/snapshot_price_15min.parquet`, `data/snapshot_surge_15min.parquet`

---

## 0. Bản chất bài toán

> Cho biết giá đối thủ **quan sát được cách đây τ phút** (5–18 phút) + ngữ cảnh,
> dự đoán **giá và hệ số nhân đối thủ ĐANG áp dụng NGAY BÂY GIỜ**.

Đây là **nowcasting với quan sát bị trễ**, không phải dự đoán giá thông thường. Độ trễ τ là
lõi bài toán — bỏ τ đi thì không còn gì để đoán.

---

## 1. Xây dựng model gì

**Bốn model độc lập** (2 target × 2 hãng), vì mỗi hãng có công thức giá khác và surge chỉ có ở Lyft:

| Target | Uber | Lyft | Độ phân giải |
|---|---|---|---|
| **Giá** | Model 1 (regression) | Model 2 (regression) | Cấp cuốc (route × service) |
| **Hệ số nhân** | — (Uber luôn = 1.0) | Model 3 (2 tầng) | Cấp thị trường (route, bỏ Shared) |

→ Thực chất **3 model cần train**.

**Vì sao tách:**
- Giá và surge do **hai nhóm yếu tố khác nhau** quyết định (giá ← chuyến đi; surge ← thị trường).
- Uber/Lyft khác công thức giá (đơn giá/dặm chênh tới 11%).
- Surge dùng chung mọi service trong 1 bucket → phải ở cấp thị trường, không cấp cuốc.

---

## 2. Cấu trúc model

### 2.1 Model GIÁ (Model 1, 2) — hồi quy trực tiếp

```
target_price(t)  ←  f( lag_price(t-1,t-2,t-3), rolling_mean6, rolling_std3,
                       observation_age,                     ← độ trễ
                       name, distance_median, source, destination,
                       hour, weekday, is_weekend, thời tiết )
```

Model cây gradient boosting (tự học tương tác, xử lý NaN & categorical). Không cần
`distance × service` thủ công (cây tự học).

> ⚠️ **Chốt về weather cho model GIÁ:** dù snapshot có build 7 cột thời tiết, model giá **KHÔNG
> dùng** chúng (đóng góp ~5%, còn lẫn hiệu ứng ngày — xem báo cáo Study Relation). Weather chỉ
> **giữ để theo dõi** và dùng cho model surge. Không đưa weather vào feature giá trên bộ Boston.
>
> ⚠️ **Rò rỉ đồng thời — cột phải loại tuyệt đối:** `price_min/max/spread`, `quote_count` (tại t)
> vẫn nằm trong parquet snapshot nhưng **cấm dùng làm feature** (tính tại t → nhìn lén hiện tại).
> Chỉ dùng `lag1_quote_count` (từ t−1) nếu cần.

### 2.2 Model HỆ SỐ NHÂN (Model 3) — hai tầng

Không hồi quy thẳng (đã thử, thua cả hằng số 1.0 vì 86% giá trị = 1.0). Tách:

```
Tầng 1 (phân loại):  P(có surge | X)        → HistGB Classifier, đo ROC-AUC
Tầng 2 (hồi quy):    E[độ lớn | có surge]   → HistGB Regressor trên nhóm surge
Kết hợp:  E[multiplier] = P(surge)·E[độ lớn|surge] + (1−P(surge))·1.0
```

Feature: `source` (mạnh nhất, η=0,15), `lag1_surge`, `roll_surge_rate6`, `hour`, thời tiết.

### 2.3 Ghép giá cuối (nếu cần một con số)

```
giá_cuối = giá_dự_báo × (multiplier nếu là Lyft)
```
Nhưng với bài toán dự báo đối thủ, thường **dự báo trực tiếp `target_price`** (đã gồm surge
trong giá quan sát) và **dự báo `multiplier` riêng** để phục vụ pricing engine.

---

## 3. Setup thuật toán

### 3.1 Baseline (bắt buộc so sánh) — số thực đo được, **THEO HÃNG**

Baseline phải tính **riêng từng hãng** (không gộp), vì công thức giá khác nhau. Số đo trên test 15 phút:

| Hãng | Persistence (`lag1`) | Historical-avg (`roll_mean6`) ⭐ | Hằng số surge (luôn 1.0) |
|---|---|---|---|
| **Uber** | 1,683 | **1,325** | — (không có surge) |
| **Lyft** | 2,125 | **1,775** | MAE surge 0,040 |

> ⚠️ **Phát hiện quan trọng:** với giá, **historical-average thắng persistence** ở cả hai hãng
> (Uber 1,325 < 1,683; Lyft 1,775 < 2,125). → mốc thật để model vượt là **historical-avg**, không
> phải persistence. KPI mentor (giảm ≥20% MAE vs persistence) → mục tiêu **Uber ≤ 1,346 · Lyft ≤
> 1,700**; nhưng để có giá trị thật, model phải **vượt cả historical-avg**.
>
> *(Số cũ dạng gộp 1,897 / 1,542 đã thay bằng số theo hãng khớp `MODEL_RESULTS.md`.)*

### 3.2 Model chính

| Thuật toán | Vai trò |
|---|---|
| **HistGradientBoosting** (sklearn) | mặc định — có sẵn, xử lý NaN & categorical native |
| **LightGBM / XGBoost / CatBoost** | so sánh (Sprint 2); CatBoost mạnh với categorical |

**Cấu hình khởi điểm (HistGB):**
```python
HistGradientBoostingRegressor(
    max_iter=500, learning_rate=0.05, l2_regularization=1.0,
    early_stopping=True, validation_fraction=0.1,
    categorical_features=[name, source, destination, short_summary, obs_age_bucket],
    random_state=42)
```
- **Log-target** cho giá (giá lệch phải; đã kiểm chứng giảm MAE ~5%).
- **Early stopping** trên validation nội bộ để tránh overfit.

### 3.3 Chống rò rỉ (đã kiểm chứng)

- Split **theo thời gian**: train ≤ 10/12 · calib 13–15/12 · test 16–18/12.
- Chỉ dùng lag từ **quá khứ**; tuyệt đối không dùng giá/surge tại t.
- Không dùng `target_price_min/max/spread`, `quote_count` tại t (rò rỉ đồng thời).
- Đã kiểm bằng permutation + đối chiếu `lag1 == shift(1)` **trong từng split** (phải kiểm theo split vì 11–12/12 là 2 ngày buffer bị loại; dòng đầu series ở 13/12 có `lag1` trỏ về ngày buffer — vẫn là quá khứ thật, không rò rỉ).

---

## 4. Model cần đáp ứng những gì

### 4.1 Bắt buộc (KPI mentor + bản chất bài toán)

| # | Yêu cầu | Trạng thái |
|---|---|---|
| 1 | Pipeline chạy end-to-end, tái lập được | ✅ data_preparation.py + model_train.ipynb |
| 2 | Dự đoán **cả 2 target** (price + multiplier) | ✅ giá + surge |
| 3 | **Thắng baseline ≥ 20% MAE** (vs persistence) | ✅ Uber +35,3% · Lyft +29,2% |
| 4 | Split **theo thời gian, không leakage** | ✅ |
| 5 | **Xử lý độ trễ tường minh** (`observation_age` là feature) | ✅ có trong snapshot |
| 6 | **Đo suy giảm theo τ** (deliverable đắt giá nhất) | ✅ đã đo (xem MODEL_RESULTS §2) |
| 7 | Train **riêng từng hãng** | ✅ dữ liệu đã tách |
| 8 | Đúng **2 độ phân giải** | ✅ 2 bảng riêng |
| 9 | Metric đúng loại (MAE cho giá, **ROC-AUC** cho surge) | ✅ |
| 10 | Báo cáo kèm **trần sàn nhiễu** (~2 USD, R² ~0,93) | ✅ đã đo |

### 4.2 Nên có

- So sánh CatBoost/LGBM/XGB có kiểm soát · ensemble nếu sai số bổ trợ.
- **Ablation**: bỏ weather / lag / route → đo đóng góp từng nhóm.
- Sai số theo **lát cắt** (cao điểm, surge, route hiếm, τ) — chuẩn bị cho cấu phần (iii).
- Output đọc được dạng nghiệp vụ, sẵn cho conformal bọc lên.

### 4.3 Giới hạn đã biết (báo cáo trung thực, không ép)

- Giá chạm **sàn nhiễu ~2 USD** do thiếu cột thời lượng → R² dừng ~0,90–0,95.
- Surge **không dai dẳng** (lag1 → AUC chỉ 0,52) + thiếu tín hiệu cung–cầu → AUC ~0,65–0,80.
  Đây là trần thật, không phải model dở.

---

## 5. Tiêu chí đánh giá

### 5.1 Model GIÁ (regression)

| Metric | Ý nghĩa | Mục tiêu |
|---|---|---|
| **MAE** | Sai số tuyệt đối TB | ≤ 1,52 (vượt roll-mean), lý tưởng ~1,3–1,4 |
| RMSE | Phạt lỗi lớn | báo cáo kèm |
| MAPE / SMAPE | Sai số tương đối | ~9% (đã đạt trên bộ cũ) |
| R² | % phương sai giải thích | ~0,93 (trần sàn nhiễu) |
| **vs baseline** | Giảm bao nhiêu % so persistence & roll-mean | **≥ 20% vs persistence** |

### 5.2 Model HỆ SỐ NHÂN (imbalanced classification)

| Metric | Ý nghĩa | Ghi chú |
|---|---|---|
| **ROC-AUC** | Phân biệt surge/không | Persistence chỉ 0,52 → dễ vượt |
| **PR-AUC** | Chính xác trên lớp hiếm | So với tỷ lệ nền 13,5% |
| Brier / reliability | Xác suất có hiệu chuẩn không | Chuẩn bị cho (iii) |
| MAE(E[multiplier]) | Sai số kỳ vọng hệ số nhân | So với "luôn 1.0" |
| ❌ **Accuracy** | **KHÔNG dùng** | Đoán "không surge" đã đúng 86,5% |

### 5.3 ⭐ Suy giảm theo độ trễ τ (đặc thù bài toán)

Đo MAE theo `observation_age_bucket`:

| Độ trễ | MAE persistence (đo sẵn) |
|---|---|
| ≤ 15 phút | 1,906 |
| 15–30 phút | 1,873 |
| 30–60 phút | 1,873 |
| 1–3 giờ | 1,954 |

> **Phát hiện sơ bộ:** với **giá**, sai số gần như **phẳng theo độ trễ** (1,87–1,95) — vì giá
> rất ổn định, quan sát 15 phút hay 1 giờ trước gần như nhau. Việc model có giúp giảm sai số
> khi τ lớn hay không sẽ là kết quả then chốt. Với **surge** (không dai dẳng), đường suy giảm
> dự kiến dốc hơn.

Trả lời câu hỏi kinh doanh: **"bao lâu phải crawl giá đối thủ một lần?"**

### 5.4 Theo lát cắt (chuẩn bị cho iii)

Báo cáo MAE/AUC riêng cho: giờ cao điểm · có surge · route hiếm · từng mức τ — để cấu phần
(iii) biết interval cần nới ở đâu.

---

## 6. Thứ tự triển khai

```
1. Baseline persistence + historical-avg (2 target)   ✅ đã có số neo
2. Model giá HistGB (Uber + Lyft) + log-target        ← làm trước, chắc ăn
3. Model surge 2 tầng (Lyft)                          ← khó, báo cáo trung thực
4. ⭐ Phân tích suy giảm theo τ                        ← deliverable đắt giá nhất
5. So CatBoost/LGBM/XGB + ablation                    ← Sprint 2
6. Sai số theo lát cắt                                ← cầu nối sang (iii)
```

---

## 7. Ba cạm bẫy đã biết

1. **Đừng cố nâng R² model giá** — chạm sàn nhiễu 0,93 do thiếu thời lượng.
2. **Đừng dùng accuracy cho surge** — đoán "không" đã đúng 86,5%.
3. **Đừng kỳ vọng surge đoán tốt** — trần AUC ~0,80; báo cáo trung thực mạnh hơn ép số đẹp.

### Điểm cần lưu khi refactor code (robustness)

- **`hour_local`:** nên mã hoá dạng **categorical** hoặc dùng `hour_sin/hour_cos` (đã build sẵn
  trong snapshot) vì giờ không đơn điệu. Với cây thì số nguyên 0–23 vẫn chạy được, nhưng nên
  nhất quán với kết luận analysis.
- **Rolling + `reset_index(drop=True)`** trong `data_preparation.them_lag`: đang đúng vì `g` đã
  sort theo `keys + snapshot`, nhưng cách gán này **mong manh** — nếu đổi thứ tự sort sẽ lệch
  hàng âm thầm. Nên chuyển sang `groupby(...).transform(...)` hoặc gán theo index để an toàn.
- **Kiểm thử chống rò rỉ tự động:** thêm assert `lag1_price == groupby(keys).target_price.shift(1)`
  và kiểm `observation_age_minutes > 0` trên toàn bảng trước khi train.

---

## Phụ lục — Bộ feature chốt

**Model GIÁ:** `name`, `distance_median`, `source`, `destination` + `lag1/2/3_price`,
`roll_mean6_price`, `roll_std3_price`, `observation_age_minutes`, `hour`, `weekday`, `is_weekend`.

**Model SURGE:** `source`, `destination`, `hour`, `short_summary` + `lag1_surge`,
`roll_surge_rate6`, `observation_age_minutes`.

**Loại bỏ:** `cab_type` (trùng name), `moonPhase`/`pressure`/`ozone` (proxy ngày),
`latitude`/`longitude` (lệch hàng), `price_per_mile` (nhiễu quãng đường).
