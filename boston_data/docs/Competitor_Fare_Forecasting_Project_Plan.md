# Competitor Fare Forecasting with Calibrated Uncertainty — Working Plan (Hiếu)

> Bản kế hoạch làm việc của Hiếu, **đồng bộ với** `Workplan_CompFare_XanhSM.md` (bản chính thức
> của mentor: 6 tuần / 3 sprint, mỗi sprint 2 tuần). File này bám sát bản mentor nhưng bổ sung
> **trạng thái tiến độ** và các quyết định kỹ thuật đã chốt sau tuần 1.
>
> Cập nhật: 23/07/2026 · Phân công: Hiếu → cấu phần (ii), EDA "What determines price?"

---

## 1. Bài toán

GreenSM chỉ quan sát được giá đối thủ (Grab/Be) với **độ trễ**. Cần ước lượng **giá + hệ số nhân
hiện tại** của đối thủ từ quan sát bị trễ, kèm **prediction interval đã hiệu chuẩn** để pricing
engine biết khi nào tin được tín hiệu.

**Ba cấu phần:**
- **(i)** Phân tích yếu tố quyết định `price` và `price multiplier`
- **(ii)** Model dự báo `price` + `multiplier` từ delayed observations ← *trọng tâm của Hiếu*
- **(iii)** Uncertainty quantification → prediction interval (vd 80% PI: [17,20 · 20,60])

---

## 2. ⚙️ Data Contract — CHỐT sau tuần 1

Đây là phần mentor yêu cầu chốt đầu tiên. Quyết định dựa trên số đo thực tế:

| Hạng mục | Quyết định | Căn cứ |
|---|---|---|
| **Đơn vị dự báo** | `route × service` = source × destination × name | Series tự nhiên; 864 series |
| **Target** | `price` (cấp cuốc) **và** `multiplier` (cấp thị trường, bỏ Shared) | Multiplier dùng chung mọi service trong 1 (thời điểm × tuyến) |
| **Độ trễ τ** | quan sát median cách nhau **18 phút** (33% ≤ 10 phút) | Đo trên gap trong series |
| **Bucket snapshot** | **15 phút** (không dùng 10 phút) | 10 phút → 82% ô rỗng; 15 phút → 25% đầy |
| **Tách hãng** | Uber và Lyft train **riêng** | Công thức giá khác; đơn giá/dặm chênh tới 11% |
| **Chống rò rỉ** | Split theo **thời gian**; lag chỉ dùng quá khứ | Đã kiểm chứng permutation |

> ⚠️ **Việc cần làm ngay:** snapshot hiện tại đang ở bucket **theo giờ** (`snapshot_price/surge.parquet`)
> → phải **dựng lại ở bucket 15 phút** để nghiên cứu được độ trễ 5–15 phút. Đây là nút thắt của
> cả cấu phần (ii).

---

## 3. Kế hoạch 6 tuần (bám bản mentor) + trạng thái

Ký hiệu: ✅ xong · 🟡 một phần · ⬜ chưa · ❌ cần làm lại

### Sprint 1 — Tuần 1: cấu phần (i) + khoá đầu vào

| Việc | Trạng thái |
|---|---|
| Chốt data contract (τ, đơn vị, target) | 🟡 đã đo, **chờ mentor review** |
| Đo phân bố gap → chốt τ (median 18 phút) | ✅ |
| Rebuild snapshot bucket 15 phút, giữ `observation_age` | ❌ **đang là theo giờ, cần làm lại** |
| **EDA (i) — driver của giá** | ✅ **vượt yêu cầu** (7 notebook + permutation test) |
| EDA (i) — biến động giá (Chiến) | ⬜ phần Chiến |
| Xin mentor distribution / simulated data | ⬜ **cần gửi** |

**Punchline tuần 1 (đã có):** *Giá do loại xe + quãng đường quyết định gần như tất định (R² 0,93);
thời tiết/giờ không tác động trực tiếp mà qua **hai đường gián tiếp** — (1) cung–cầu → hệ số nhân
(Tầng 1 tài liệu mentor) và (2) tắc đường → thời lượng → đơn giá/phút (công thức niêm yết Grab
350đ/phút). Bộ Boston thiếu **cả hai** mắt xích (không có tín hiệu cung–cầu, không có cột thời
lượng) nên hai đường này không quan sát được — đó là lý do đo ra ~0 và cũng là lý do có sàn nhiễu.*

### Sprint 1 — Tuần 2: khởi động (ii)

| Việc | Trạng thái |
|---|---|
| Baseline persistence + historical-average | ✅ persistence (MAE 1,94) · 🟡 historical-avg |
| Feature engineering v1: lag, rolling, route, weather, obs_age | 🟡 có trên bản theo giờ, dựng lại theo 15 phút |
| Train gradient boosting cho **cả 2 target** | 🟡 price ✅ (R² 0,93) · multiplier 🟡 (AUC 0,65) |
| Chốt time-split, metric, tập lát cắt | ✅ |
| Kiểm tra leakage (permutation) | ✅ |
| Chốt KPI từ số thực, gửi mentor | ⬜ |

**Punchline dự kiến:** *Model đầu tiên thắng baseline persistence 29% MAE trên split không leakage.*

### Sprint 2 — Tuần 3: hoàn thiện point forecast (ii)

- So sánh CatBoost / LGBM / XGBoost trên cùng test set · thử ensemble
- **Ablation**: bỏ weather / lịch sử giá / route → đo đóng góp
- **Phân tích sai số theo độ trễ τ** ← câu hỏi kinh doanh cốt lõi, chưa làm
- Chốt model cho (iii)

### Sprint 2 — Tuần 4: khởi động uncertainty (iii)

- Quantile regression (pinball 10/50/90) · Split conformal · Ensemble interval
- Calibration set tách theo thời gian
- Đo coverage / width / pinball / CRPS · reliability diagram

### Sprint 3 — Tuần 5: interval nới đúng chỗ

- Adaptive/Mondrian conformal (hiệu chuẩn theo nhóm: cao điểm, thời tiết, service, obs_age)
- Conditional coverage · stress test · decision rule + đo tác động · decision latency

### Sprint 3 — Tuần 6: bàn giao

- Tổng hợp trade-off · go/no-go · integration proposal · limitations & transfer
- Đóng gói handoff để mentor test trên GreenSM

---

## 4. Tiêu chí hoàn thành (KPI, theo mentor)

| KPI | Ngưỡng | Hiện tại |
|---|---|---|
| Cải thiện MAE vs persistence | **≥ 20%** | ✅ **29%** (price) |
| Coverage 80%/90% PI sai lệch | **≤ 3 điểm %** | ⬜ chưa (cấu phần iii) |
| Interval nới đúng chỗ theo lát cắt | có | ⬜ |
| Decision rule có ngưỡng cụ thể | có | ⬜ |
| Weekly report có punchline = sprint goal | mỗi tuần | ✅ tuần 1 |

---

## 5. Kết luận đánh giá hướng đi

**Hướng tiếp cận ĐÚNG và khớp mục tiêu bài toán.** Cấu phần (i) làm vượt yêu cầu. Ba việc cần
xử lý ngay để không phải làm lại về sau:

1. **Dựng lại snapshot ở bucket 15 phút** — nút thắt của toàn bộ cấu phần (ii) và (iii).
2. **Gửi mentor xin data**: phân phối cung–cầu theo (giờ × khu) — mắt xích trung gian đang thiếu
   giữa key-feature và hệ số nhân.
3. **Chốt data contract với mentor** trước khi sang tuần 2.

---

## 6. Giới hạn đã biết (theo mentor, không nằm ngoài scope)

- Dataset chỉ **23 ngày** → không claim seasonality dài hạn.
- Uber không có surge → model multiplier chỉ dùng Lyft.
- 12 khu đều lõi đô thị Boston (~20–30 km²) → không mở rộng cho ngoại ô / sân bay.
- Thiếu biến thời lượng chuyến đi và tín hiệu cung–cầu → sàn nhiễu ~2 USD, trần R² ≈ 0,93.
- Eval trên public data; test trên GreenSM do mentor thực hiện, **ngoài scope cam kết**.
