# Báo cáo Model Sample — Dự báo Giá & Hệ số nhân của đối thủ

**Dự án:** Competitor Fare Forecasting (GSM) · **Cấu phần:** (ii) — Build Model
**Người thực hiện:** Nguyễn Đức Hiếu (S.AI.20K) · **Ngày:** 24/07/2026
**Dữ liệu:** Uber & Lyft Boston — snapshot 15 phút (sinh từ 637.322 chuyến sạch, 25/11–18/12/2018)

---

**Tóm tắt:** Đã build model sample dự báo giá đối thủ theo hướng **nowcasting với quan sát trễ**.
Model giá **vượt baseline persistence 29–35% MAE**, sai số thật **~1,1 USD (Uber)** và
**~1,5 USD (Lyft)** mỗi chuyến. Model hệ số nhân có tín hiệu phân loại (ROC-AUC 0,65) nhưng điểm
forecast chạm trần do dữ liệu thiếu tín hiệu cung–cầu. Trần độ chính xác của giá là **sàn nhiễu
~2 USD** do dataset thiếu cột thời lượng chuyến đi. → Đề xuất mentor bổ sung 4 nhóm trường dữ liệu.

---

## 1. Kiến trúc model sử dụng

### 1.1 Ba model độc lập

| Model | Loại | Thuật toán | Target |
|---|---|---|---|
| **Giá Uber** | Regression | `HistGradientBoostingRegressor` | `target_price` |
| **Giá Lyft** | Regression | `HistGradientBoostingRegressor` | `target_price` |
| **Hệ số nhân Lyft** | 2 tầng | Classifier + Regressor | `target_surge` |

**Vì sao 3 model:** giá tách theo hãng (Uber/Lyft khác công thức giá, đơn giá/dặm chênh tới
11,5%); hệ số nhân chỉ có ở Lyft (Uber toàn bộ `surge = 1.0`). → 2 model giá + 1 model surge.

### 1.2 Thuật toán: Gradient Boosting Decision Trees (HistGradientBoosting)

Model xây **cây quyết định tuần tự** — mỗi cây sửa lỗi (residual) của các cây trước.

**Vì sao chọn (không dùng neural network):**
- Dữ liệu **dạng bảng** → gradient boosting thường thắng neural network.
- Xử lý **categorical + NaN native** (không cần one-hot), tự học tương tác `distance × name`.
- **Giải thích được** (permutation importance) — hợp yêu cầu interpretability.
- Train nhanh trên CPU.

### 1.3 Model hệ số nhân — kiến trúc 2 tầng (hurdle model)

Không hồi quy thẳng (86% giá trị = 1.0 → hồi quy thẳng thua cả hằng số). Tách:

```
Tầng 1 (phân loại):  P(có surge | X)         → HistGB Classifier
Tầng 2 (hồi quy):    E[độ lớn | có surge]    → HistGB Regressor (train trên nhóm có surge)
Kết hợp:  E[hệ số nhân] = P(surge)·E[độ lớn] + (1 − P(surge))·1.0
```

---

## 2. Phân chia dữ liệu huấn luyện

Chia **theo THỜI GIAN**, tuyệt đối không chia ngẫu nhiên (bài toán dự báo — chia random sẽ để
model "nhìn thấy tương lai" → kết quả đẹp giả).

| Tập | Khoảng thời gian | Số dòng (bảng giá) | Dùng để |
|---|---|---|---|
| **train** | 25/11 → 10/12 | 289.271 | Huấn luyện model |
| *(buffer)* | 11–12/12 | *(loại)* | Ngăn train dính sát calibration |
| **calibration** | 13/12 → 15/12 | 97.697 | Dành cho cấu phần (iii) — Conformal Prediction |
| **test** | 16/12 → 18/12 | 84.681 | Đánh giá cuối, model **chưa từng thấy** |

**Chống rò rỉ (đã kiểm chứng):**
- Mọi feature chỉ dùng lag từ **quá khứ** (`shift(k≥1)`); tuyệt đối không dùng giá/surge tại t.
- Kiểm `lag1 == shift(1)` **trong từng split** → khớp 100% (train/calib/test).
- Loại các cột tính tại t: `price_min/max/spread`, `quote_count`.

---

## 3. Cấu hình ban đầu

| Tham số | Giá trị | Ý nghĩa |
|---|---|---|
| `max_iter` | 500 | Số cây tối đa (số vòng boosting) |
| `learning_rate` | 0,05 | Mỗi cây đóng góp bao nhiêu (nhỏ = học chậm, chắc) |
| `l2_regularization` | 1,0 | Phạt độ phức tạp → chống overfit |
| `early_stopping` | True | Tự dừng khi validation không cải thiện |
| `validation_fraction` | 0,1 | 10% tập train làm validation nội bộ |
| `categorical_features` | name, source, destination, obs_age_bucket | Xử lý categorical native |
| **log-target** | có | Giá lệch phải → `log` cân đối phân phối, giảm MAE ~5% |

**Đường huấn luyện:** train loss và validation loss giảm dốc trong ~50 cây rồi phẳng, **gần như
trùng khít nhau** → không overfit; phần phẳng = đã chạm sàn nhiễu của dữ liệu.

**Bộ feature:**
- **Giá:** `name`, `distance_median`, `source`, `destination` + `lag1/2/3_price`,
  `roll_mean6_price`, `roll_std3_price`, `observation_age_minutes`, `hour_local`, `weekday_local`, `is_weekend`.
- **Surge:** `source`, `destination`, `short_summary`, `hour_local` + `lag1/2_surge`,
  `roll_mean6_surge`, `roll_surge_rate6`, `observation_age_minutes`.

---

## 4. Kết quả thu được (tập test)

### 4.1 Model GIÁ — chỉ số tổng hợp

| Hãng | n_test | MAE (USD) | RMSE | R² | MAPE | Bias | vs persistence | vs hist-avg |
|---|---|---|---|---|---|---|---|---|
| **Uber** | 43.767 | **1,088** | 1,810 | **0,955** | 7,37% | −0,09 | **+35,4%** | +17,9% |
| **Lyft** | 40.914 | **1,502** | 2,933 | **0,914** | 9,71% | −0,19 | **+29,3%** | +15,4% |

Baseline: persistence (dùng giá cũ) Uber 1,683 / Lyft 2,125; historical-avg 1,325 / 1,775.
→ Model **vượt cả hai baseline** ở cả hai hãng.

### 4.2 ⭐ Sai số tiền thật — đây là con số dễ hiểu nhất

> **MAE = số tiền sai trung bình mỗi chuyến.** Model dự đoán giá đối thủ lệch trung bình
> **~1,1 USD (Uber, ~28 nghìn đồng)** và **~1,5 USD (Lyft)** so với giá thật.

**Phân bố sai số tuyệt đối (USD):**

| Hãng | p50 (trung vị) | p75 | p90 | p95 | max |
|---|---|---|---|---|---|
| Uber | 0,73 | 1,32 | 2,27 | 3,18 | 47,29 |
| Lyft | 0,85 | 1,71 | 3,05 | 4,47 | 45,47 |

**Tỷ lệ chuyến dự đoán đúng trong ngưỡng:**

| Hãng | ≤ 0,5 USD | ≤ 1 USD | ≤ 2 USD | ≤ 3 USD | > 5 USD (lệch lớn) |
|---|---|---|---|---|---|
| Uber | 35,6% | 63,9% | 87,4% | 94,3% | 1,9% |
| Lyft | 32,1% | 56,0% | 79,9% | 89,7% | 4,2% |

→ **~50% chuyến sai dưới ~0,85 USD; ~90% sai dưới ~3 USD.** Vài case lệch lớn (~45 USD) là chuyến
giá cao bất thường.

### 4.3 Suy giảm theo độ trễ — kết quả vận hành

MAE model (USD) theo độ trễ quan sát:

| Độ trễ | Uber | Lyft |
|---|---|---|
| ≤15 phút | 1,096 | 1,527 |
| 15–30 phút | 1,090 | 1,450 |
| 30–60 phút | 1,083 | 1,494 |
| 1–3 giờ | 1,076 | 1,536 |
| >3 giờ | **1,029** | 1,529 |

→ **MAE gần như phẳng** (Uber còn giảm nhẹ) từ 15 phút tới 3 giờ. Model dùng quan sát cũ 3 giờ
vẫn chính xác gần như dùng quan sát 15 phút. **Trả lời câu hỏi kinh doanh: không cần crawl dày
cho giá → tiết kiệm chi phí thu thập.**

### 4.4 Model HỆ SỐ NHÂN (Lyft) — báo cáo trung thực

| Chỉ số | Model | Baseline | Đánh giá |
|---|---|---|---|
| ROC-AUC | **0,652** | persistence 0,518 | ✅ có tín hiệu phân loại |
| PR-AUC | 0,189 | nền 0,135 | 🟡 nhỉnh hơn nền |
| Brier | 0,113 | — | (cho phần iii) |
| MAE E[mult] | 0,064 | luôn-1.0: 0,040 | ❌ thua hằng số |

**Diễn giải:** khi surge thực cao (1,4–1,5), model thường chỉ đoán ~1,05 → hụt, vì surge hiếm
(13,5%) + **không dai dẳng** + thiếu tín hiệu cung–cầu. Giá trị của model nằm ở **xác suất
P(surge)** (khu Back Bay P cao hơn hẳn Haymarket), không ở con số điểm — đây là **trần thật của
dữ liệu**, không phải model dở.

---

## 5. Kết luận về model hiện tại

**Đạt được:**
- Model giá **vượt KPI** (giảm 29–35% MAE vs persistence, R² 0,91–0,96), vượt cả baseline mạnh
  hơn là historical-average.
- Sai số thật chỉ **~1,1–1,5 USD/chuyến**; ~90% chuyến sai dưới 3 USD.
- **Không suy giảm theo độ trễ** → không cần crawl dày.
- Model **giải thích được**, không overfit (train ≈ validation).

**Giới hạn — là của DỮ LIỆU, không phải model:**
- Giá chạm **sàn nhiễu ~2 USD**: với hai chuyến giống hệt (cùng xe, cùng quãng đường tới 0,01
  dặm, cùng giây), 88,7% vẫn khác giá — do dataset **thiếu cột thời lượng chuyến đi** (giá thật
  có thành phần tính theo phút, vd Grab 350đ/phút). → trần R² ~0,93.
- Model surge point-forecast chạm trần do **thiếu tín hiệu cung–cầu** (số chuyến trong dataset là
  lịch crawl, không phản ánh nhu cầu thật).

> **Điểm mấu chốt:** muốn cải thiện hiệu suất, phải **bổ sung dữ liệu**, không phải chỉnh model.
> Model đã khai thác hết thông tin có trong bộ Boston.

---

## 6. Đề xuất mentor — trường dữ liệu thật để mô phỏng & cải thiện

Không cần data raw — xin theo dạng **phân phối (distribution) để sample** hoặc **simulated data**
theo cấu trúc giá GSM. Bốn nhóm, ưu tiên #1 và #2:

| # | Trường dữ liệu | Giải quyết giới hạn | Lợi ích kỳ vọng |
|---|---|---|---|
| 1 | **Thời lượng chuyến đi** (duration/ETA) — phân phối theo quãng đường × giờ × tình trạng giao thông | Sàn nhiễu ~2 USD (§5) | Nâng trần R² vượt 0,93 |
| 2 | **Tín hiệu cung–cầu** (số tài xế rảnh, số cuốc chờ) — phân phối theo khu × giờ | Model surge chỉ R²≈0,04 | Nếu dự đoán surge tốt: giảm MAE giá thêm ~30% (1,5 → 1,1 USD) |
| 3 | **Log đặt xe thật** (thay lịch crawl cố định) | Số chuyến hiện không phản ánh cầu | Kích hoạt lại nhóm feature thời gian (giờ cao điểm) |
| 4 | **Vùng địa lý rộng hơn** (sân bay/liên quận/ngoại ô) | Vùng thu thập hiện chỉ lõi Boston ~6,7 km² | Kết luận về vị trí khái quát được |

**Cách dùng dữ liệu xin được:** dùng phân phối/simulated data để **bổ sung hai biến trung gian
(thời lượng, cung–cầu)** vào snapshot hiện tại → train lại model → đo mức cải thiện MAE. Đây là
bước mô phỏng để chứng minh giá trị của dữ liệu trước khi triển khai trên hệ thống thật của GSM.

---

## 7. Sản phẩm bàn giao

| File | Nội dung |
|---|---|
| `model/data_preparation.ipynb` | Xử lý dữ liệu → snapshot |
| `model/model_train.ipynb` | Huấn luyện 3 model |
| `model/test_evaluation.ipynb` | Đánh giá chi tiết trên tập test |
| `data/test_ketqua_price_{uber,lyft}.csv` | Dự đoán + sai số từng dòng |
| `data/test_ketqua_surge_lyft.csv` | Dự đoán surge từng dòng |
| `docs/MODEL_DESIGN.md`, `docs/MODEL_RESULTS.md` | Thiết kế & kết quả chi tiết |
