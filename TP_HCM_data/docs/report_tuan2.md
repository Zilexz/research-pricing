# Báo cáo Tuần 2 — Phân tích & Build Model trên bộ dữ liệu TP.HCM

**Dự án:** Competitor Fare Forecasting (GSM) · **Người thực hiện:** Nguyễn Đức Hiếu (S.AI.20K) · **Ngày:** 30/07/2026
**Dữ liệu:** `synthetic_quote_context_sandbox` (TP.HCM, synthetic) — 6.897.051 dòng × 70 cột, 3 tháng (01–03/2026), 3 khu vực

---

**Motivation.** Tuần 1 trên bộ Boston kết luận **giờ và thời tiết gần như không ảnh hưởng giá**
(η < 0,01). Mentor xác nhận kết luận này hợp lý với thực tế Mỹ — đường thoáng, giờ cao điểm dân tự
lái ô tô riêng, ít mưa — nhưng **dự đoán bộ dữ liệu Việt Nam sẽ khác**: giờ cao điểm và trời mưa sẽ
ảnh hưởng giá nhiều. Tuần 2 kiểm chứng chính xác giả thuyết này trên bộ TP.HCM.

**Kết quả cốt lõi.** **Mentor dự đoán đúng.** Giờ ảnh hưởng lên giá cuối ở TP.HCM **mạnh gấp 74 lần**
Boston (η 0,296 vs 0,004); mưa làm giá tăng **+7,3%** (Boston: **0,0%**). Trong cùng dải quãng đường,
giá TP.HCM dao động **49,3%** theo giờ, còn Boston **phẳng tuyệt đối** (16,50 USD ở mọi giờ).

**Contribution.**
1. Chỉ ra **cơ chế** tác động: giờ/mưa **không** đổi giá cơ bản mà đổi **hệ số nhân** qua chuỗi
   *cầu → mất cân bằng cung-cầu → surge → giá cuối*, kiểm chứng từng mắt xích.
2. Sửa một **lỗi diễn giải** dễ mắc: phân tích trên giá cơ bản (đã bỏ surge) cho η ≈ 0,03, nếu lấy
   con số này kết luận "giờ không ảnh hưởng giá" thì **bỏ mất toàn bộ kênh tác động chính**.
3. Build **3 model** (giá cơ bản, hệ số nhân, giá trực tiếp) × **3 thuật toán**, chốt kiến trúc
   **Hybrid** (giá cơ bản × hệ số nhân) — thắng dự đoán trực tiếp.
4. Thử **8 hướng cải thiện độc lập**, tất cả đều dừng ở cùng một mức → xác định được **sàn nhiễu**
   của bộ dữ liệu, thay vì đoán.

---

## 0. Bối cảnh & phạm vi tuần 2

| Mục | Nội dung | Trạng thái tuần 2 |
|---|---|---|
| **i** | Study relation — key feature ↔ giá & hệ số nhân | ✅ Hoàn thành trên bộ TP.HCM |
| **ii** | Build model dự đoán giá + hệ số nhân từ quan sát trễ | ✅ Hoàn thành, đã chốt kiến trúc |
| iii | Uncertainty quantification — khoảng dự đoán | ⏳ Chưa bắt đầu |

**So với tuần 1:** bộ TP.HCM có **2 nhóm trường mà Boston thiếu** — đây là lý do kết quả khác hẳn:

| Nhóm trường mới | Cột | Vai trò |
|---|---|---|
| **Thời lượng chuyến** | `quote_duration` (ETA, giây) | Đo được tắc đường → giải thích phần giá theo phút |
| **Cung–cầu thời gian thực** | `pricing_demand_index_5m_lag`, `pricing_supply_index_5m_lag`, `pricing_market_imbalance_5m_lag` | Mắt xích trung gian để giờ/thời tiết tác động lên surge |

Tuần 1 đã kết luận đây chính là 2 nguyên nhân khiến model Boston chạm trần. Tuần 2 xác nhận: **có
2 nhóm trường này, kết quả thay đổi hoàn toàn.**

---

## 1. Tổng quan bộ dữ liệu TP.HCM

### 1.1 Cấu trúc

| Thuộc tính | Giá trị |
|---|---|
| Số dòng | 6.897.051 (mẫu phân tích 15% ≈ 1.034.550) |
| Số cột | 70 |
| Thời gian | 01/01/2026 – 30/03/2026 (3 tháng) |
| Khu vực | 3 hex: Crescent Mall, SC VivoCity, EcoGreen Sài Gòn |
| Dịch vụ | 2 loại: Synthetic Standard Car, Synthetic Premium Car |
| Giá | 32.000 – 959.000 VND (median **114.000**) |
| Hệ số nhân | 0,85 – 1,80 |
| **Tỷ lệ chuyến có surge** | **81,7%** (Boston: 3,3%) |
| Tỷ lệ có mưa | 45,3% (Boston: 21,7%) |
| Thiếu dữ liệu thời tiết | 1,71% (đã có cờ `weather_missing`) |

### 1.2 Bài toán — nowcasting với quan sát trễ

Mỗi dòng = **1 lần báo giá** (khách chọn điểm đón/đến, app tính giá). Model phải dự đoán giá **hiện
tại** của đối thủ, chỉ được dùng thông tin **cũ hơn τ phút** (τ ∈ {5, 10, 15, 30}):

| Loại thông tin | Cột | Được dùng? |
|---|---|---|
| Giá/hệ số nhân **hiện tại** của đối thủ | `target_shown_price`, `target_shown_multiplier` | ❌ Đây là đáp án cần dự đoán |
| Giá đối thủ quan sát **gần nhất** (cùng tuyến + loại xe) | `latest_observed_price`, `latest_observed_multiplier` | ✅ |
| Lịch sử giá 60 phút | `history_60m_price_mean/std/slope` | ✅ |
| Thuộc tính chuyến hiện tại | `quote_distance`, `quote_duration` | ✅ (biết khi khách yêu cầu) |
| Cung–cầu (trễ 5 phút) | `pricing_*_5m_lag` | ✅ |

Đã kiểm tra chống rò rỉ: `observation_cutoff_timestamp ≤ target_timestamp` (đúng 100%),
`actual_observation_age_minutes ≥ 0` (đúng 100%). Độ trễ thực tế trung bình 16,3 phút.

### 1.3 Chia dữ liệu — theo thời gian, theo từng tháng

| Tập | Vai trò | Khoảng thời gian trong mỗi tháng |
|---|---|---|
| train | Huấn luyện | ~20 ngày đầu tháng |
| validation | Tinh chỉnh siêu tham số | ngày 21–24 |
| calibration | Dành cho khoảng dự đoán (mục iii) | ngày 24–27 |
| test | Đánh giá cuối | 3–4 ngày cuối tháng |

> ⚠️ **Bắt buộc train riêng từng tháng** (theo tài liệu dataset): lịch sử giá đối thủ **reset theo
> tháng**, gộp nhiều tháng sẽ gây rò rỉ. Mọi model đều lặp theo `evaluation_month`, cho ra 3 fold
> độc lập rồi tổng hợp.

---

## 2. Phân tích key feature ↔ giá & hệ số nhân

### 2.1 ⚠️ Yêu cầu phương pháp: phải tách 3 đối tượng, không được gộp

**Giá khách trả = giá cơ bản × hệ số nhân.** Đây không phải chi tiết kỹ thuật — nó quyết định
kết luận đúng hay sai:

| Đối tượng | Định nghĩa | Do gì quyết định |
|---|---|---|
| **Giá cơ bản** | `target_shown_price ÷ target_shown_multiplier` | Quãng đường + thời gian đi (~92%) |
| **Hệ số nhân** | `target_shown_multiplier` | Cung–cầu (corr 0,80) |
| **Giá cuối** | `target_shown_price` | = giá cơ bản × hệ số nhân |

Nếu chỉ đo trên **giá cơ bản**, giờ/thời tiết cho η ≈ 0,03 → dễ kết luận sai *"không ảnh hưởng"*.
Thực tế giờ/thời tiết tác động **qua kênh hệ số nhân**, và vì giá cuối = giá cơ bản × hệ số nhân
nên chúng **vẫn ảnh hưởng mạnh đến giá khách trả**.

**Thước đo dùng:** η (correlation ratio, thang 0→1) — cho biết bao nhiêu phần biến thiên của giá
được giải thích bởi biến phân nhóm. Dùng được cho biến phân loại (giờ, loại thời tiết), khác Pearson
chỉ đo quan hệ tuyến tính.

### 2.2 ⭐ Bảng cốt lõi — Boston vs TP.HCM trên cùng thước đo

| Yếu tố | Bộ | → Giá cơ bản | → Hệ số nhân | → **Giá cuối** |
|---|---|---|---|---|
| **Giờ trong ngày** | TP.HCM | 0,0326 | **0,7022** | **0,2960** |
| | Boston | 0,0038 | 0,0101 | 0,0040 |
| | *HCM mạnh hơn* | — | **69,5×** | **74,0×** |
| **Loại thời tiết** | TP.HCM | 0,0426 | **0,1533** | 0,0973 |
| | Boston | 0,0033 | 0,0064 | 0,0036 |
| | *HCM mạnh hơn* | — | **24,0×** | **27,0×** |
| **Có mưa / không** | TP.HCM | 0,0422 | **0,1524** | 0,0972 |
| | Boston | 0,0000 | 0,0043 | 0,0010 |
| | *HCM mạnh hơn* | — | **35,4×** | **97,2×** |

**Đọc bảng:** ở cả 2 bộ, giờ/thời tiết đều **không ảnh hưởng giá cơ bản** (η 0,003–0,043 — giá cơ
bản do quãng đường/thời gian quyết định). Khác biệt nằm ở **kênh hệ số nhân**: TP.HCM η = 0,70 với
giờ, Boston chỉ 0,01.

### 2.3 🕐 Thời gian

**Cách phân tích.** Cố định dải quãng đường **4–6 km** (395.062 chuyến) để loại ảnh hưởng của độ
dài chuyến, rồi xem giá median / tỷ lệ surge / hệ số nhân theo từng giờ (đã quy đổi giờ Việt Nam,
UTC+7 — dữ liệu gốc là UTC, giữ nguyên sẽ đọc lệch 7 tiếng).

**Kết luận ảnh hưởng.**

- **→ Giá cuối:** ảnh hưởng **mạnh** (η = 0,296). Cùng quãng đường 4–6 km, giá median dao động từ
  **73.000 VND (2h sáng)** đến **109.000 VND (18h)** — chênh **49,3%**. Boston cùng phép đo:
  **0,0%** (16,50 USD ở mọi giờ).
- **→ Hệ số nhân:** ảnh hưởng **cực mạnh** (η = 0,702) — tỷ lệ chuyến có surge từ **0,1% (3h sáng)**
  lên **98,3% (8h sáng)**.
- **→ Giá cơ bản:** gần như **không ảnh hưởng** (η = 0,033) — đúng như kỳ vọng, vì giá cơ bản chỉ
  phụ thuộc quãng đường/thời gian đi.

**Pattern giờ cao điểm khớp thực tế Việt Nam:**

| Khung giờ | Tỷ lệ surge | Hệ số nhân TB | Diễn giải |
|---|---|---|---|
| 2–4h | 0,1–2,6% | 0,86–0,88 | Đêm, không có nhu cầu |
| **6–9h** | **92,5–98,3%** | 1,17–1,23 | **Giờ đi làm sáng** |
| 10–16h | 90–97% | 1,17–1,20 | Ban ngày, nền cao |
| **17–19h** | **94,3–96,8%** | **1,23–1,28** ⭐ | **Giờ tan làm — hệ số cao nhất** |
| 20–23h | 92–94% | 1,15–1,24 | Tối |

**Vì sao TP.HCM khác Boston?** Vì bộ TP.HCM **có tín hiệu cung–cầu**, và cầu dao động rất mạnh theo
giờ: η(giờ → chỉ số cầu) = **0,7144**. Boston không có cột cung–cầu, và chỉ **3,3%** chuyến có surge
→ cơ chế điều chỉnh giá theo cung–cầu gần như không hoạt động → giá phẳng tuyệt đối theo giờ.

### 2.4 🌦️ Thời tiết

**Cách phân tích.** So giá/surge giữa 4 loại thời tiết; gộp nhóm "có mưa" (`Rain` + `Drizzle` +
`Thunderstorm`) vs "không mưa"; kiểm soát quãng đường 4–6 km khi so trực tiếp.

**Phân bố thời tiết** (khác hẳn Boston vốn thiếu ngày mưa):

| Loại | Số chuyến | Giá median | Tỷ lệ surge | Hệ số nhân TB | Tốc độ (km/h) |
|---|---|---|---|---|---|
| **Rain** | 468.851 (45,3%) | **119k** | 82,8% | **1,194** | **15,57** ⬇ |
| Clouds | 316.381 | 111k | 83,1% | 1,144 | 17,27 |
| Clear | 230.933 | 110k | 78,0% | 1,139 | 17,37 |
| Mist | 18.385 | 112k | 75,1% | 1,125 | 17,08 |

**Kết luận ảnh hưởng** (cùng dải quãng đường 4–6 km):

| | Không mưa | Có mưa | Thay đổi |
|---|---|---|---|
| Giá cuối | 96.000 VND | 103.000 VND | **+7,29%** |
| Giá cơ bản | 85.710 VND | 88.140 VND | +2,82% |
| Hệ số nhân | 1,1274 | 1,1804 | **+4,70%** |
| Chỉ số cầu | 120,3 | 132,4 | **+10,1%** |
| Tốc độ | 17,18 km/h | 15,53 km/h | **−9,6%** (tắc hơn) |

Boston cùng phép đo: giá cuối **+0,00%**, hệ số nhân **−0,1%** — không ảnh hưởng.

**Vì sao mưa ảnh hưởng ở TP.HCM mà không ở Boston?** Mưa tác động qua **2 đường**, cả 2 đều cần
trường dữ liệu mà Boston thiếu:
1. **Mưa → cầu tăng** (+10,1%) → mất cân bằng cung–cầu → surge tăng (+4,70%). Cần cột cung–cầu.
2. **Mưa → tắc đường** (tốc độ −9,6%) → thời gian đi dài hơn → phần cước theo phút tăng → giá cơ
   bản tăng (+2,82%). Cần cột `quote_duration`.

Tuần 1 đã dự đoán chính xác 2 mắt xích này khi giải thích vì sao Boston đo được η ≈ 0.

### 2.5 🚦 Tắc đường

**Cách phân tích.** Đo tắc đường bằng `speed_kmh` (quãng đường ÷ thời gian) và `dur_per_km`
(phút/km); kiểm soát quãng đường khi đo tương quan với giá.

**Kết luận ảnh hưởng.**

- **→ Giá:** **rất mạnh** — corr(thời lượng, giá) = **0,697**; sau khi kiểm soát quãng đường vẫn
  còn **0,484**. Nghĩa là: **cùng một quãng đường, chuyến tắc hơn thì đắt hơn thật sự** (do thành
  phần cước tính theo phút). Đây chính là mắt xích Boston thiếu, gây "sàn nhiễu ~2 USD" ở tuần 1.
- **→ Hệ số nhân:** ảnh hưởng vừa (η = 0,195) — tỷ lệ surge tăng đều theo mức tắc:

| Mức tắc | Tỷ lệ surge | Hệ số nhân TB |
|---|---|---|
| Thông | 74,8% | 1,117 |
| Hơi thông | 79,1% | 1,144 |
| Trung bình | 81,9% | 1,164 |
| Hơi tắc | 84,7% | 1,186 |
| **Tắc nặng** | **87,8%** | **1,215** |

**Lưu ý:** tắc đường trong bộ này **ít biến thiên theo giờ** (tốc độ median 15,8 km/h giờ 6 → 17,8
km/h giờ 1, chỉ chênh 12%) — nó tạo khác biệt *giữa các chuyến* nhiều hơn là *theo giờ*.

### 2.6 📍 Vị trí

| Khu đón | Số chuyến | Giá median | Tỷ lệ surge | Hệ số nhân | Quãng đường TB | Tốc độ |
|---|---|---|---|---|---|---|
| Crescent Mall | 349.202 | 98k | 74% | 1,10 | 5,63 km | 17,83 km/h |
| **EcoGreen Sài Gòn** | 333.210 | **127k** | **88%** | **1,23** | 6,50 km | **14,71** ⬇ |
| SC Vivo City | 352.138 | 123k | 82% | 1,17 | **7,25 km** | 17,21 km/h |

**Kết luận ảnh hưởng.** η(khu → giá) = 0,292; η(khu → hệ số nhân) = 0,299 — cả hai đều rõ hơn
Boston (0 với giá, 0,15 với surge). Sau khi kiểm soát quãng đường, chênh giá giữa các khu còn
**17,6%** — tức phần lớn chênh lệch thô là do **cơ cấu quãng đường** khác nhau (SC VivoCity chuyến
dài nhất 7,25 km), nhưng vẫn còn premium thật.

EcoGreen là khu **tắc nhất** (14,71 km/h) và **surge cao nhất** (88%) — nhất quán với chuỗi
*tắc đường → thị trường căng → surge cao*.

⚠️ Chỉ 3 khu nên kết luận về vị trí còn hạn chế (Boston có 12 khu).

### 2.7 Chuỗi nhân quả — kiểm chứng từng mắt xích

Giả thuyết: **giờ/mưa → cầu tăng → mất cân bằng cung–cầu → surge tăng → giá cuối tăng.**
Bộ TP.HCM có sẵn chỉ số cung–cầu nên kiểm chứng được từng bước (Boston không có):

| Mắt xích | Phép đo | Giá trị |
|---|---|---|
| **1a.** Giờ → cầu | η(giờ, demand_index) | **0,7144** ✅ |
| **1b.** Giờ → cung | η(giờ, supply_index) | 0,2240 |
| **1c.** Giờ → mất cân bằng | η(giờ, market_imbalance) | **0,6119** ✅ |
| **1d.** Mưa → cầu | η(có_mưa, demand_index) | 0,0998 |
| **1e.** Mưa → mất cân bằng | η(có_mưa, market_imbalance) | 0,1662 |
| **2.** Mất cân bằng → hệ số nhân | corr(imbalance, multiplier) | **0,7978** ✅ |
| **3.** Hệ số nhân → giá cuối | corr(multiplier, price) | **0,4760** ✅ |

Bổ sung: corr(chỉ số **cầu**, hệ số nhân) = **+0,689**; corr(chỉ số **cung**, hệ số nhân) = **−0,276**
— đúng chiều kinh tế học (cầu tăng đẩy surge lên, cung tăng kéo surge xuống).

→ **Toàn bộ chuỗi được xác nhận.** Giờ là yếu tố mạnh nhất khởi động chuỗi (η 0,71 lên cầu), mưa
yếu hơn nhưng cùng cơ chế.

---

## 3. Tổng hợp: feature nào quyết định giá, feature nào quyết định hệ số nhân

### 3.1 Xếp hạng đầy đủ (η, mẫu 1.034.550 dòng)

| Yếu tố | → GIÁ | → HỆ SỐ NHÂN | Ghi chú |
|---|---|---|---|
| **Thời lượng chuyến (tắc đường)** | **0,665** ⭐ | 0,205 | Cột mới, Boston không có |
| Phút/km (tắc đường) | 0,665 | 0,205 | Cùng thông tin, dạng khác |
| **Quãng đường** | **0,654** ⭐ | 0,092 | Trục giá cơ sở |
| **Giờ (VN)** | 0,296 | **0,702** ⭐ | Mạnh nhất với surge |
| Khu đón | 0,292 | 0,299 | Chỉ 3 khu |
| Tốc độ | 0,167 | 0,198 | |
| Thời tiết | 0,097 | 0,153 | Boston ≈ 0 |
| Thứ trong tuần | 0,089 | 0,225 | |
| Cuối tuần | 0,077 | 0,190 | Cuối tuần surge 84% vs 80,7% |
| Loại dịch vụ | 0,029 | 0,012 | Chỉ 2 loại |

### 3.2 Chốt lại — hai nhóm yếu tố khác nhau

> **Giá cơ bản** ← *thuộc tính chuyến đi*: quãng đường + thời lượng (tắc đường) chiếm ~92% (xác nhận
> bằng permutation importance ở mục 4.4).
>
> **Hệ số nhân** ← *bối cảnh thị trường*: cung–cầu (corr 0,80) + giờ (η 0,70).
>
> → **Phải tách 2 model, 2 bộ feature** — nhất quán với kết luận tuần 1 trên bộ Boston.

### 3.3 So sánh tổng thể Boston vs TP.HCM

| Tiêu chí | Boston (tuần 1) | TP.HCM (tuần 2) |
|---|---|---|
| Tắc đường → giá | ❌ Không đo được (thiếu cột thời lượng) | ✅ corr 0,70; kiểm soát quãng đường còn 0,48 |
| Cung–cầu → surge | ❌ Không có tín hiệu | ✅ imbalance corr **0,80** |
| Giờ → surge | Yếu (1,36×) | ✅ **Cực mạnh** (η 0,70; 0,1% → 98,3%) |
| Giờ → giá cuối | η 0,004 (giá phẳng 0,0%) | ✅ η 0,296 (giá dao động **49,3%**) |
| Thời tiết → giá | ≈ 0 (thiếu ngày mưa) | ✅ Mưa đắt hơn **+7,3%** |
| Vị trí | η_surge 0,15; giá ≈ 0 sau kiểm soát | η_giá 0,29; η_surge 0,30 |
| Tỷ lệ surge | 3,3% (hiếm) | 81,7% (phổ biến) |

---

## 4. Build model (cấu phần ii)

### 4.1 Kiến trúc — 3 model, chốt Hybrid

| Model | Target | Bộ feature | Vai trò |
|---|---|---|---|
| **A. Giá cơ bản** | `base_price` = giá ÷ hệ số nhân (log) | Quãng đường, thời lượng, dịch vụ, tuyến, lịch sử giá, giá cơ bản quan sát gần nhất | Lõi Hybrid |
| **B. Hệ số nhân** | `target_shown_multiplier` | Cung–cầu (imbalance/demand/supply/quote_count), hệ số nhân quan sát gần nhất, giờ | Lõi Hybrid |
| **C. Giá trực tiếp** | `target_shown_price` (log) | Như A nhưng dùng `latest_observed_price` (có surge) | Baseline đối chiếu |

**Kiến trúc chốt — Hybrid:**
```
giá cuối dự đoán = model_A(giá cơ bản) × model_B(hệ số nhân)
```

**So sánh 2 hướng** (trên giá cuối, cùng tập test, HistGB):

| Hướng | MAE | R² | MAPE | Bias TB |
|---|---|---|---|---|
| **Hybrid (giá cơ bản × hệ số nhân)** | **18.048 VND** | **0,730** | **14,74%** | −2,3k |
| Hướng 1 (đoán thẳng giá cuối) | 18.834 VND | 0,700 | 15,36% | −2,9k |

→ **Hybrid thắng ở cả 4 chỉ số.** Lý do: mỗi model học đúng phần việc của nó — giá cơ bản theo
quãng đường/thời lượng, hệ số nhân theo cung–cầu; không bị nhiễu lẫn nhau.

> ⚠️ **Lưu ý về trade-off của Hybrid:** thắng về trung bình nhưng **rủi ro hơn ở từng chuyến lẻ** —
> khi cả 2 model cùng lệch một chiều, sai số bị **nhân lên** thay vì cộng. Ví dụ thực tế từ 15 test
> case: có chuyến Hướng 1 sai 0,4% trong khi Hybrid sai 18,2%. Cần nêu rõ khi báo cáo, không chỉ
> báo MAE trung bình.

### 4.2 Thuật toán — 3 thuật toán cho kết quả gần như giống hệt nhau

Tất cả là **gradient boosting cây quyết định** (họ thuật toán tốt nhất cho dữ liệu dạng bảng, xử lý
categorical/NaN native, giải thích được, train nhanh CPU).

**Kết quả trên giá cơ bản** (toàn bộ 864.360 dòng test, 3 tháng):

| Thuật toán | MAE (VND) | R² | MAPE |
|---|---|---|---|
| **HistGradientBoosting** (sklearn) | **15.032** | 0,6563 | 14,6% |
| LightGBM | 15.038 | 0,6562 | 14,6% |
| XGBoost | 15.045 | 0,6556 | 14,6% |

→ Chênh lệch **13 VND (0,09%)** giữa thuật toán tốt nhất và kém nhất — nằm hoàn toàn trong nhiễu
ngẫu nhiên. **Chọn HistGB** làm mặc định (không cần thư viện ngoài sklearn, dễ maintain).

### 4.3 Kết quả model

**Model giá cơ bản** (lõi Hybrid):

| Chỉ số | Giá trị |
|---|---|
| MAE | 15.032 VND |
| RMSE | 20.095 VND |
| R² | 0,656 |
| MAPE | 14,6% |

**Model hệ số nhân:**

| Chỉ số | Giá trị | Baseline persistence |
|---|---|---|
| MAE | **0,0233** | 0,0371 |
| R² | 0,9606 | — |
| **ROC-AUC** (phân biệt có surge) | **0,9979** | — |

**Model giá cuối (Hybrid) vs baseline:**

| | MAE | Cải thiện |
|---|---|---|
| **Hybrid** | **18.048 VND** | — |
| Baseline persistence (dùng thẳng giá quan sát gần nhất) | 33.683 VND | **+44,1%** ✅ |

→ Model **vượt baseline persistence 44,1%** — mốc bắt buộc phải vượt để chứng minh có giá trị.

### 4.4 Feature nào model thực sự dùng (permutation importance, giá cơ bản)

| Feature | Importance | Tỷ trọng |
|---|---|---|
| **quote_distance** | 0,684 | **68%** |
| **quote_duration** | 0,233 | **23%** |
| service_name | 0,0122 | 1,2% |
| pickup_location_name | 0,00198 | 0,2% |
| history_60m_price_mean | 0,000623 | ~0% |
| gio_vn | 0,000591 | ~0% |
| *(9 feature còn lại)* | < 0,0001 | ~0% |

→ **Quãng đường + thời lượng = 92%.** Điều này **không mâu thuẫn** với mục 2 (giờ ảnh hưởng mạnh):
đây là model **giá cơ bản** (đã bỏ surge), còn giờ ảnh hưởng qua **hệ số nhân** — đúng như phân tích
chuỗi nhân quả ở 2.7.

**Đối chiếu chéo bằng GAM** (Generalized Additive Model, theo đề xuất mentor):

| Model | MAE | R² | MAPE |
|---|---|---|---|
| GAM | 15.099 | **0,6599** | 14,78% |
| HistGB | 15.032 | 0,6563 | 14,6% |

GAM đạt **R² nhỉnh hơn** GBM, MAE chỉ chênh 67 VND — xác nhận quan hệ feature → giá cơ bản chủ yếu
là **cộng dồn đơn giản**, không cần tương tác phức tạp. GAM còn cho **p-value** kiểm định ý nghĩa
thống kê: `weather_main` (p = 0,203), `history_60m_price_slope` (p = 0,475),
`actual_observation_age_minutes` (p = 0,334) — **không có ý nghĩa** với giá cơ bản, khớp permutation
importance ≈ 0.

---

## 5. Trần độ chính xác — 8 hướng cải thiện đều dừng ở cùng một mức

Model giá cơ bản dừng ở **MAE ~15.000 VND / MAPE ~14,6%**. Để xác định đây là **sàn nhiễu của dữ
liệu** hay **model chưa tối ưu**, đã thử 8 hướng độc lập:

| # | Hướng thử | Cách làm | Kết quả |
|---|---|---|---|
| 1 | **Đổi thuật toán** | HistGB / LightGBM / XGBoost | Chênh 13 VND |
| 2 | **Đổi hàm mất mát** | `absolute_error` thay `squared_error` (tối ưu thẳng MAE) | Chênh 26 VND |
| 3 | **Thêm feature tắc đường** | `dur_per_km`, `speed_kmh` tường minh | Chênh 19 VND |
| 4 | **Đổi target sang đơn giá/km** | Đoán `giá/km` rồi × quãng đường | Chênh 22 VND |
| 5 | **Thêm feature quan sát gần nhất** | Tốc độ + đơn giá/km của chuyến quan sát gần nhất | Importance ≈ 0 |
| 6 | **Chuẩn hóa theo tuyến** | Z-score trong từng tuyến (18 tuyến), đo lại giờ/thứ/tháng | η ≈ 0 sau chuẩn hóa |
| 7 | **Ném hết 49 feature + trọng số** | Toàn bộ cột khả dụng, `feature_weights` ưu tiên feature quan trọng | Chênh 6 VND (full 6,9M dòng) |
| 8 | **Fine-tune siêu tham số** | Optuna, 9 tham số × 40 trial × 3 tháng, dùng tập validation | Chênh **+2 VND** |

**Kết luận:** 8 hướng độc lập, dùng cả toàn bộ dữ liệu (6,9M dòng), đều dừng ở cùng một mức
→ **MAE ~15.000 VND (MAPE ~14,6%) là sàn nhiễu thật của bộ dữ liệu**, không phải model/feature/tham
số chưa tối ưu.

**Bằng chứng bổ sung:** dùng chỉ 2 feature (quãng đường + thời lượng), model tuyến tính và model cây
cho R² **giống nhau** (0,662 vs 0,661) — độ lệch chuẩn phần dư còn lại **19.920 VND** trên giá cơ
bản median 99.281 VND ≈ **20% nhiễu per-quote** mà không feature nào giải thích được.

**Thử nghiệm ngoài GBM:** Neural Network 1 thân 2 đầu ra (multi-task, có cổng trọng số feature học
được) — giá MAE 18.156 vs GBM 18.048; hệ số nhân MAE 0,0260 vs GBM 0,0233 → **thua GBM ở cả 2 target**.
Nguyên nhân: 2 bài toán dùng feature gần như tách biệt, ít lợi ích khi học chung representation.

---

## 6. Điểm cần lưu ý trung thực về dữ liệu synthetic

### 6.1 Hệ số nhân đạt ROC-AUC 0,998 — con số này bị thổi phồng

Model hệ số nhân đạt độ chính xác gần tuyệt đối, nhưng **không nên diễn giải là "model rất giỏi"**:

Bộ dữ liệu **cho sẵn** `pricing_market_imbalance_5m_lag` — chính là kết quả trung gian của công thức
sinh surge (theo tài liệu XanhSM: `m_market = f(ℓ_t, q_t)` với `ℓ_t = cầu − cung`). Model chỉ cần
**học lại một hàm toán học đã biết**, không phải học hành vi thị trường thật.

**Trong production thật:** thường **không có sẵn** chỉ số cung–cầu chính xác thời gian thực, hoặc nó
nhiễu/trễ/không đầy đủ. Khi đó model phải **suy luận cung–cầu gián tiếp** từ giờ, thời tiết, sự kiện,
lịch sử giá → ROC-AUC sẽ **thấp hơn nhiều** so với 0,998.

### 6.2 Quan hệ giờ/mưa → giá mạnh vì được sinh theo công thức

η(giờ → hệ số nhân) = 0,70 chứng minh **cơ chế đã được cài đặt trong dữ liệu** — không phải bằng
chứng về hành vi thị trường thật ở TP.HCM. Kết luận đúng: *"bộ dữ liệu synthetic TP.HCM có mô hình
hóa đầy đủ cơ chế giờ cao điểm/thời tiết → cung-cầu → surge, khác bộ Boston vốn thiếu các mắt xích
này"*.

Tuy nhiên, chiều tác động và độ lớn **khớp với quan sát thực tế của mentor** trên hệ thống production
(giờ cao điểm sáng và trời mưa làm cầu tăng cao, thuật toán tự tăng giá mạnh mà khách vẫn chấp nhận)
→ cơ chế mô hình hóa là **hợp lý**, dù con số cụ thể không thể lấy làm ước lượng cho production.

---

## 7. Kết luận & hướng phát triển

### 7.1 Trả lời trực tiếp câu hỏi của mentor

> **Mentor dự đoán đúng.** Trên bộ dữ liệu Việt Nam, giờ cao điểm và trời mưa **ảnh hưởng giá rõ rệt**
> — mạnh gấp **74 lần** (giờ) và **97 lần** (mưa) so với Boston. Cơ chế: giờ/mưa làm **cầu tăng** →
> mất cân bằng cung–cầu → **hệ số nhân tăng** → giá cuối tăng. Boston không thể hiện điều này vì chỉ
> **3,3%** chuyến có surge (TP.HCM: **81,7%**) và thiếu cả cột thời lượng lẫn tín hiệu cung–cầu —
> đúng như 2 nhược điểm dataset đã nêu ở tuần 1.

### 7.2 Tình trạng 3 cấu phần

| Cấu phần | Trạng thái |
|---|---|
| **i. Study relation** | ✅ Hoàn thành — xác nhận cả 5 nhóm yếu tố (giờ, thời tiết, tắc đường, vị trí, cung–cầu), kiểm chứng chuỗi nhân quả |
| **ii. Build model** | ✅ Hoàn thành — chốt kiến trúc Hybrid, vượt baseline 44,1%, xác định sàn nhiễu qua 8 hướng thử |
| **iii. Uncertainty** | ⏳ Chưa bắt đầu — dữ liệu **đã có sẵn tập `calibration`** (615.908 dòng) dành riêng cho việc này |

### 7.3 Hướng phát triển tiếp — ưu tiên theo thứ tự

**1. Uncertainty Quantification (cấu phần iii) — ưu tiên cao nhất.**
Đã chứng minh MAE ~15k là sàn nhiễu không thể giảm → **đưa ra khoảng dự đoán có giá trị hơn** việc
cố ép một con số điểm chính xác hơn. Ví dụ: *"giá ~114k, khoảng tin cậy 90%: [95k – 135k]"*.
- **Conformal Prediction** — dùng tập `calibration` có sẵn, cho bảo đảm phủ theo lý thuyết
- **Quantile Regression** (LightGBM `objective="quantile"`) — dự đoán trực tiếp P5/P50/P95
- Nên làm **cả 2 để so sánh** độ rộng khoảng và tỷ lệ phủ thực tế

**2. Acceptance rate model — theo yêu cầu mới của mentor.**
Đã kiểm tra: **cả 2 bộ dữ liệu đều không có nhãn accept/reject** (rà soát toàn bộ 87 cột HCM + 57 cột
Boston). Mentor xác nhận team production cũng không có, chỉ dùng outcome cuốc + demographic. Mentor
đã **đơn giản hóa yêu cầu** thành: 2 model xu hướng (khả năng chấp nhận **tăng/giảm** khi biết giá
đối thủ / thời tiết). Cần làm rõ đây là **mô phỏng dựa trên giả định elasticity từ literature**,
không phải model học từ hành vi khách hàng thật.

**3. Cải thiện tính ổn định của Hybrid.**
Hybrid thắng về MAE trung bình nhưng phương sai case-by-case cao hơn (do nhân 2 nguồn sai số). Có thể
thử: chọn động giữa Hybrid và Hướng 1 tùy độ tin cậy của từng dự đoán.

**4. Không nên tiếp tục các hướng đã loại trừ.**
8 hướng ở mục 5 đã được kiểm chứng đầy đủ (đổi thuật toán, đổi loss, thêm feature, đổi target, chuẩn
hóa, ném hết feature, fine-tune, NN) — tiếp tục sẽ tốn thời gian mà không có dư địa cải thiện.

### 7.4 Đề xuất trao đổi với mentor

1. **Xác nhận hướng làm acceptance rate model** — mô phỏng dựa trên literature có được chấp nhận
   trong báo cáo, hay cần nguồn dữ liệu khác có nhãn thật?
2. **Về ROC-AUC 0,998 của hệ số nhân** — có nên bổ sung thí nghiệm "bỏ cột cung–cầu, buộc model suy
   luận từ giờ/thời tiết" để có ước lượng gần production hơn?
3. **Về GAM** — kết quả ngang GBM và dễ giải thích hơn (vẽ được đường cong + p-value từng feature).
   Có nên dùng GAM cho phần trình bày/báo cáo, giữ GBM cho production?

---

## Phụ lục A — Danh mục notebook phân tích

| File | Nội dung |
|---|---|
| `00_TONG_HOP_SO_SANH.ipynb` | ⭐ Tổng hợp Boston vs TP.HCM, tách 3 đối tượng, kiểm chứng chuỗi nhân quả |
| `overview_data.ipynb`, `tong_quan_data_moi.ipynb` | Tổng quan 70 cột, profiling từng cột, dữ liệu mẫu |
| `01_location.ipynb` | Vị trí/khu vực ↔ giá & hệ số nhân |
| `02_time.ipynb` | Giờ/thứ ↔ giá & hệ số nhân (giờ VN, UTC+7) |
| `03_weather.ipynb` | Thời tiết ↔ giá & hệ số nhân |
| `04_traffic.ipynb` | Tắc đường (ETA, tốc độ) ↔ giá & hệ số nhân |
| `05_kmpertime.ipynb` | Tốc độ + đơn giá/km — kiểm chứng thực nghiệm feature mới |
| `05b_kmpertime_gia_coban.ipynb` | Như trên nhưng tách riêng giá cơ bản |
| `06_tuyen_chuanhoa.ipynb` | Chuẩn hóa theo 18 tuyến, đo lại giờ/thứ/tháng |
| `key_feature_analysis_hcm.ipynb` | Xếp hạng đầy đủ 10 yếu tố + bảng so sánh Boston |
| `FS_model_gia.ipynb`, `FS_model_gia_coban.ipynb`, `FS_model_heso.ipynb` | Feature selection 5 phương pháp/model |

## Phụ lục B — Thông số kỹ thuật model

**Siêu tham số HistGradientBoosting** (đã xác nhận qua Optuna là gần tối ưu):
```python
HistGradientBoostingRegressor(
    max_iter=500, learning_rate=0.05, l2_regularization=1.0,
    early_stopping=True, validation_fraction=0.1, n_iter_no_change=20,
    categorical_features=CAT, random_state=42)
```

**Bộ feature model giá cơ bản (B_NUM):** `quote_distance`, `quote_duration`, `gio_vn`,
`latest_observed_base`, `history_60m_price_mean`, `history_60m_price_std`,
`history_60m_price_slope_per_minute`, `latest_observed_quote_distance`,
`latest_observed_quote_duration`, `actual_observation_age_minutes`
+ categorical: `service_name`, `pickup_location_name`, `dropoff_location_name`, `weather_main`

**Bộ feature model hệ số nhân (M_NUM):** `pricing_market_imbalance_5m_lag`,
`pricing_demand_index_5m_lag`, `pricing_supply_index_5m_lag`, `pricing_quote_count_5m_lag`,
`latest_observed_multiplier`, `gio_vn`, `actual_observation_age_minutes` + cùng bộ categorical

**Target:** giá cơ bản dùng log-transform (phân phối lệch phải); hệ số nhân không log (dải hẹp ~1).
