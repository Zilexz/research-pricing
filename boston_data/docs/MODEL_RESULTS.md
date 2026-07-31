# Kết quả Model — Cấu phần (ii)

**Ngày:** 23/07/2026 · **Script:** `model/model_train.ipynb` · **Dữ liệu:** snapshot 15 phút
**Test set:** 16–18/12/2018 (time-based split, không leakage)

---

## 1. Model GIÁ — ✅ vượt KPI

| Hãng | MAE | RMSE | R² | MAPE | vs persistence | vs hist-avg |
|---|---|---|---|---|---|---|
| **Uber** | **1,088** | 1,809 | **0,955** | 7,37% | **+35,3%** | +17,8% |
| **Lyft** | **1,504** | 2,935 | **0,914** | 9,73% | **+29,2%** | +15,3% |

**Baseline để so sánh:**

| Hãng | Persistence (lag1) | Historical-avg (roll6) |
|---|---|---|
| Uber | 1,683 | 1,325 |
| Lyft | 2,125 | 1,775 |

> ✅ **Cả hai hãng vượt KPI mentor** (cải thiện ≥ 20% MAE vs persistence). Uber +35%, Lyft +29%.
> Và vượt cả baseline mạnh hơn (historical-avg): Uber +18%, Lyft +15%.

R² Uber (0,955) cao hơn Lyft (0,914) đúng như dự đoán — chênh lệch là **phần surge** mà Lyft có
còn Uber không. R² ~0,93 khớp trần sàn nhiễu đã đo (thiếu biến thời lượng).

---

## 2. ⭐ Suy giảm theo độ trễ — kết quả then chốt cho quyết định vận hành

MAE của model theo `observation_age` (khoảng cách tới quan sát gần nhất):

### Uber
| Độ trễ | n | MAE model | MAE persistence |
|---|---|---|---|
| ≤ 15 phút | 17.660 | 1,095 | 1,686 |
| 15–30 phút | 10.657 | 1,089 | 1,684 |
| 30–60 phút | 9.978 | 1,082 | 1,657 |
| 1–3 giờ | 5.384 | **1,076** | 1,724 |

### Lyft
| Độ trễ | n | MAE model | MAE persistence |
|---|---|---|---|
| ≤ 15 phút | 15.521 | 1,527 | 2,156 |
| 15–30 phút | 9.707 | 1,453 | 2,082 |
| 30–60 phút | 9.630 | 1,495 | 2,096 |
| 1–3 giờ | 5.923 | 1,540 | 2,164 |

### 🎯 Hai kết luận vận hành

**1. Model KHÔNG suy giảm theo độ trễ.** MAE gần như phẳng (Uber ~1,08; Lyft ~1,45–1,54) từ
15 phút tới 3 giờ. Vì giá rất ổn định + model dùng lịch sử giá (không chỉ quan sát cuối).

**2. Model dùng quan sát cũ 3 giờ vẫn chính xác hơn persistence dùng quan sát 15 phút.**
Uber: model@1-3h = **1,076** < persistence@≤15p = 1,686. Đây là bằng chứng mạnh: model
**không phụ thuộc dữ liệu tươi** như cách làm ngây thơ.

> **Trả lời câu hỏi kinh doanh:** với **giá**, không cần crawl dày. Crawl mỗi giờ vẫn cho sai
> số gần như crawl mỗi 15 phút — vì model bù được độ trễ bằng lịch sử giá. Tiết kiệm được nhiều
> chi phí thu thập.

---

## 3. Model HỆ SỐ NHÂN (Lyft) — báo cáo trung thực

| Metric | Model | Baseline | Đánh giá |
|---|---|---|---|
| **ROC-AUC** | **0,653** | persistence 0,518 | ✅ có tín hiệu, thắng persistence |
| PR-AUC | 0,192 | nền 0,135 | 🟡 nhỉnh hơn nền |
| Brier | 0,113 | — | (chuẩn bị cho iii) |
| MAE E[multiplier] | 0,0643 | luôn-1.0 **0,0396** | ❌ **thua hằng số** |
| Accuracy | — | đoán "không" 0,865 | ❌ không dùng metric này |

### Diễn giải trung thực

- **Tầng phân loại CÓ tín hiệu**: ROC-AUC 0,653 > persistence 0,518 > 0,5 (đoán bừa). Model
  phân biệt được phần nào lúc nào dễ surge — chủ yếu nhờ `source`.
- **Nhưng point-forecast hệ số nhân thua hằng số**: MAE E[mult] 0,064 > "luôn 1.0" 0,040.
  Vì surge quá hiếm (13,5%) và không dai dẳng (persistence AUC chỉ 0,52) → dự đoán kỳ vọng
  thêm nhiễu vào 86,5% trường hợp vốn = 1.0.

> **Kết luận:** giá trị của model surge nằm ở **xác suất P(surge)** (feed cho cấu phần iii để
> quyết định độ tin cậy), **không** ở con số điểm. Đây là **trần thật** do thiếu tín hiệu
> cung–cầu, không phải model dở — đúng như phân tích tuần 1.

---

## 4. Đối chiếu yêu cầu bài toán

| # | Yêu cầu | Đạt? |
|---|---|---|
| 1 | Dự đoán cả 2 target | ✅ giá + surge |
| 2 | **Thắng persistence ≥ 20% MAE** | ✅ Uber +35%, Lyft +29% |
| 3 | Split theo thời gian, không leakage | ✅ |
| 4 | Xử lý độ trễ tường minh | ✅ observation_age là feature |
| 5 | **Đo suy giảm theo τ** | ✅ (mục 2) |
| 6 | Train riêng từng hãng | ✅ |
| 7 | Metric đúng (MAE giá, ROC-AUC surge) | ✅ |
| 8 | Báo cáo trần sàn nhiễu | ✅ R² ~0,93 |

---

## 5. Sản phẩm

| File | Nội dung |
|---|---|
| `model/model_price_uber.joblib` | Model giá Uber (R² 0,955) |
| `model/model_price_lyft.joblib` | Model giá Lyft (R² 0,914) |
| `model/model_surge_lyft.joblib` | Model surge 2 tầng (clf + reg) |
| `model/model_results.json` | Toàn bộ metric |
| `model/model_train.ipynb` | Script tái lập |

---

## 6. Punchline (cho weekly report)

> **Model dự báo giá đối thủ vượt baseline persistence 29–35% MAE, và quan trọng hơn: nó
> dùng quan sát cũ 3 giờ vẫn chính xác hơn cách dùng quan sát 15 phút thô — nghĩa là không
> cần crawl dày cho giá. Model hệ số nhân có tín hiệu phân loại (AUC 0,65) nhưng point-forecast
> chạm trần do thiếu dữ liệu cung–cầu; giá trị của nó là xác suất, dành cho lớp uncertainty.**

---

## 7. Việc tiếp theo (Sprint 2)

1. So CatBoost / LightGBM / XGBoost với HistGB hiện tại
2. **Ablation**: bỏ weather / lag / route → đo đóng góp từng nhóm
3. Sai số theo lát cắt (cao điểm, có surge, route hiếm) — cầu nối sang cấu phần (iii)
4. Cải thiện model surge: thêm feature cung–cầu nếu mentor cấp dữ liệu
