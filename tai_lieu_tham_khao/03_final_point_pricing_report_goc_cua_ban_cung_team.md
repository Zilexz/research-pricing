# Báo cáo đóng nghiên cứu point-pricing TP.HCM (synthetic)

Version: `2.6.0`
Phạm vi: dữ liệu synthetic TP.HCM, forecast `target_shown_price`, competitor observations.
> Price (`target_shown_price`) và Multiplier là hai đại lượng khác nhau. Target
> vận hành của report này vẫn là Price; kết quả Multiplier từ relation study
> chỉ dùng để giải thích cấu trúc dữ liệu và định hướng surge work sau đó,
> không phải metric song song để chọn point-price model.

---

## 1. Vấn đề đặt ra

Dự đoán `target_shown_price` tại request time, chỉ dùng thông tin biết đến
thời điểm đó (as-of). Đây là báo cáo đóng dòng nghiên cứu P5–P12, quyết định
có tiếp tục tối ưu point-price trên cùng data contract hay không.

## 2. Dữ liệu

Dataset mô phỏng tình huống giá đối thủ không được quan sát tại đúng thời điểm
request. Mỗi forecasting example kết hợp thông tin chuyến đi hiện tại với
competitor quote gần nhất trước cutoff.

### 2.1. Phạm vi và độ phủ

| Thành phần | Quy mô/giá trị | Ý nghĩa |
| --- | ---: | --- |
| Forecasting rows, 4 lags | 6,897,051 | inventory đầy đủ cho lag 5/10/15/30 phút |
| Primary lag-15 rows | 1,724,255 | phạm vi chính của point-price research |
| Thời gian | 3 tháng | đủ out-of-time comparison ngắn hạn, chưa đủ policy drift dài hạn |
| Khu vực đón | 3 | Crescent Mall, SC Vivo City, EcoGreen Sài Gòn |
| Dịch vụ | 2 synthetic services | kiểm tra được service effect nhưng chưa đại diện product portfolio thực |

Số `6.90M` không tương đương `6.90M` target độc lập: một
`target_request_id` có thể xuất hiện ở bốn lag. Vì vậy độ đa dạng thực nghiệm
được quyết định nhiều hơn bởi ba tháng, ba khu vực và hai dịch vụ hơn là tổng
số dòng.

### 2.2. Profile của hai target

| Target | Phân phối | Hàm ý mô hình |
| --- | --- | --- |
| Price | median `114,000 VND`; P05–P95 `60,000–206,000 VND`; bước giá chính `1,000 VND` | scale rộng, error tăng theo distance; phải báo cả MAE aggregate và slice theo trip scale |
| Multiplier | median `1.17`; P05–P95 `0.85–1.44`; min–max `0.85–1.80`; 96 giá trị | là target continuous có nhiều regime, không phải nhãn surge nhị phân |
| Multiplier = 1 | `1.06%` observations | không phù hợp bê nguyên hurdle “surge so với 1” từ Boston/Lyft |

Price và Multiplier liên quan nhưng không thay thế nhau: Price còn chứa base
fare, route/service tariff và các fee/state không được biểu diễn đầy đủ bởi
Multiplier.

### 2.3. Prediction-time information contract

Relation study tổ chức trường đầu vào thành bảy information blocks:

1. **fare structure/route:** distance, duration, service và zone;
2. **delayed price history:** latest/history price statistics trước cutoff;
3. **delayed multiplier history:** latest/history multiplier trước cutoff;
4. **lagged market state:** demand, supply, quote count và imbalance đã lag;
5. **calendar/time:** hour, day-of-week và weekend;
6. **weather:** trạng thái thời tiết đã quan sát;
7. **freshness/availability:** age, missingness và độ tin cậy của observation.

Chỉ các trường biết được tại request/cutoff mới được phép dùng. Relation study
loại target/evaluation fields, target-time competitor observation, technical
IDs/raw timestamps không có prediction meaning và duplicate encodings. Với
model riêng lag 15, `requested_lag_minutes` không được dùng làm feature.

### 2.4. Những phép phân tích đã thực hiện

| Lớp phân tích | Đã tính | Câu hỏi trả lời |
| --- | --- | --- |
| Target/data profile | quantile, granularity, category coverage và lag inventory | target có scale và regime nào? |
| Raw association | Pearson/Spearman cho numeric; η² cho categorical | trường nào liên hệ tuyến tính, đơn điệu hoặc khác biệt theo level? |
| Mutual information | MI theo từng target | có quan hệ phi tuyến bị correlation đơn giản bỏ sót không? |
| Out-of-time permutation | individual và group permutation trên validation sau train | model thực sự dựa vào field/information block nào để forecast? |
| Adjusted effect | thay numeric P10→P90 hoặc category level, giữ các trường khác cố định | prediction thay đổi bao nhiêu khi riêng một trường thay đổi? |
| Stability | lặp theo 4 lag, 3 tháng và 3 pickup hex | quan hệ có giữ hướng ngoài một aggregate sample không? |
| Baseline screen | Price và Multiplier ở lag 5/10/15/30 | delayed state còn hữu ích đến horizon nào? |

`consensus_weight_pct` là consensus ranking từ raw association, MI,
permutation và adjusted-effect range; nó không phải coefficient trong công
thức giá. Group weight được tính riêng bằng cách permute đồng thời cả
information block để giảm hiện tượng các feature tương quan che nhau.

Relation study dùng fixed hash sampling với seed `42`: `173,530` train rows
cho relation fit, `97,119` validation rows cho out-of-time importance/effect
và `138,896` rows cho stability across lags. Target profile vẫn được tính trên
toàn bộ `1,724,255` lag-15 rows.

### 2.5. Signal theo nhóm: Price và Multiplier

| Information block | Price weight | Multiplier weight | Kết luận |
| --- | ---: | ---: | --- |
| Fare structure/route | 76.75% | 0.56% | chi phối Price nhưng gần như không quyết định Multiplier |
| Delayed multiplier history | 10.99% | 61.27% | nguồn state mạnh nhất cho Multiplier và truyền ảnh hưởng sang Price |
| Lagged market state | 5.72% | 29.93% | demand–supply/imbalance chủ yếu điều khiển Multiplier |
| Delayed price history | 5.47% | 0.01% | có Price context nhưng gần như không thêm Multiplier state sau điều chỉnh |
| Calendar/time | 0.90% | 6.48% | time regime quan trọng với Multiplier hơn Price |
| Weather | 0.16% | 1.58% | signal phụ trong simulator hiện tại |
| Freshness/availability | 0.01% | 0.17% | ít direct signal, chủ yếu phù hợp reliability/slice diagnostics |

**Key finding:** Price có hai khối signal: trip/base-fare structure và pricing
state. Multiplier gần như tách khỏi distance/duration, chủ yếu được xác định
bởi delayed multiplier và lagged demand–supply imbalance.

### 2.6. Tác động của các trường chính

Bảng dưới dùng **adjusted high–low effect**: giữ các trường khác cố định trong
relation HGB rồi thay một trường numeric từ P10 lên P90; với categorical là
chênh lệch lớn nhất giữa các level.

| Trường | Adjusted effect lên Price | Adjusted effect lên Multiplier | Ý nghĩa dữ liệu |
| --- | ---: | ---: | --- |
| `quote_distance` | +39,117 VND | ≈0.0000 | quyết định quy mô base fare, gần như không đổi multiplier |
| `quote_duration` | +35,241 VND | +0.0003 | phản ánh trip scale/base fare hơn là surge state |
| `latest_observed_multiplier` | +21,242 VND | +0.2892 | delayed pricing state mạnh nhất, tác động tới cả hai target |
| `pricing_market_imbalance_5m_lag` | +13,838 VND | +0.1496 | market state đi qua multiplier rồi phản ánh vào price |
| `history_60m_price_mean` | +10,443 VND | ≈0.0000 | delayed base-price context, gần như không thêm multiplier state sau điều chỉnh |
| `target_hour` | chênh tối đa 6,609 VND | chênh tối đa 0.0491 | time regime ảnh hưởng cả hai target, không đơn điệu theo giờ |
| `weather_main` | chênh tối đa 1,201 VND | chênh tối đa 0.0137 | signal phụ so với trip structure và market state |

Raw association không đủ để chọn feature. Ví dụ các price-history extrema và
latest price có raw Spearman khá cao với Price (`~0.54–0.64`) nhưng
out-of-time permutation/adjusted effect gần 0 sau khi các trường thay thế đã có
mặt. Tương tự, `history_60m_price_mean` có raw correlation với Multiplier
(`0.588`) nhưng delayed-price group chỉ chiếm `0.01%` Multiplier weight và
adjusted effect xấp xỉ 0. Đây là predictive redundancy/confounding, không phải
mâu thuẫn dữ liệu.

### 2.7. Độ ổn định theo lag, tháng và khu vực

| Target/signal | Theo lag 5/10/15/30 | Theo 3 tháng | Theo 3 pickup hex | Nhận xét |
| --- | --- | --- | --- | --- |
| Price–distance, Spearman | `0.663` ổn định | `0.662–0.669` | `0.549–0.678` | hướng rất ổn định; strength thay đổi theo địa bàn |
| Price–duration, Spearman | `0.677` ổn định | `0.676–0.683` | `0.565–0.713` | driver cấu trúc bền nhất cùng distance |
| Price–market imbalance, Spearman | `0.451` ổn định | `0.444–0.461` | `0.370–0.390` | market effect giữ hướng nhưng yếu hơn trip scale |
| Multiplier–latest multiplier, Spearman | giảm `0.986 → 0.876` khi lag `5 → 30` | `0.947–0.949` | `0.919–0.944` | delayed state rất mạnh nhưng mất freshness theo horizon |
| Multiplier–imbalance, Spearman | `0.848` ổn định | `0.837–0.859` | `0.804–0.895` | market imbalance là signal bền qua lag và khu vực |
| Multiplier–hour, η² | `0.489` ổn định | `0.482–0.502` | `0.453–0.644` | time regime tồn tại nhưng mức mạnh phụ thuộc khu vực |

Stability check xác nhận hướng chính không đến từ một tháng duy nhất. Tuy
nhiên spatial strength thay đổi đáng kể và delayed multiplier suy giảm theo
lag, nên model nhiều horizon phải dùng lag/context rõ ràng hoặc tách model theo
horizon.

### 2.8. Giới hạn diễn giải

- Đây là synthetic evidence mô tả simulator, không chứng minh hành vi thị
  trường hay quan hệ nhân quả tại TP.HCM thật.
- Ba tháng, ba khu vực và hai dịch vụ không đủ để đánh giá policy drift,
  coverage địa lý hoặc product changes dài hạn.
- Adjusted effect vẫn phụ thuộc relation model; permutation đo model reliance,
  không tự động quyết định giữ/bỏ feature.
- Stress scenarios không được dùng cho relation ranking hoặc tuning.

Evidence đầy đủ nằm trong
`docs/tphcm_synthetic_relation_study_v1.0.0/` và các CSV/workbook tái lập ở
`artifacts/tphcm_synthetic_relation/v1.0.0/`.

## 3. Chia dữ liệu

| Split | Rows | Tỷ trọng | Nội dung |
| --- | ---: | ---: | --- |
| Train | 1,160,442 | 67.30% | mỗi tháng tạo 3 expanding folds + purge gap để chọn model |
| Outer validation | 193,746 | 11.24% | xác nhận candidate đã lock từ train |
| Calibration | 153,977 | 8.93% | dành riêng cho uncertainty task (iii), không fit/so sánh point model |
| Nominal test | 216,090 | 12.53% | descriptive baseline screen; sau đó learned-model comparison mở một lần khi contract đã khóa |

Mỗi tháng là một forecasting fold độc lập: 20 ngày train, sau đó validation,
calibration và test theo thời gian. History được reset ở monthly boundary;
model của tháng sau không được dùng để chấm tháng trước.

### 3.1. Split dùng cho từng câu hỏi

| Mục đích | Fit/ước lượng | Evaluation | Vai trò của test |
| --- | --- | --- | --- |
| Relation study Price/Multiplier | raw association/MI trên train lag 15; HGB fit trong train từng tháng | permutation và adjusted effect trên sampled outer validation cùng tháng | exploratory hypothesis evidence, không phải independent model-selection proof |
| Stability analysis | fixed-hash sample qua 4 lags, 3 tháng và 3 hex | so hướng/strength giữa slices | không dùng |
| Feature/model selection | 3 expanding chronological folds mỗi tháng, có purge gap | outer validation mở sau khi khóa candidate | không dùng để tuning |
| Descriptive baseline screen | rule/lookup fit từ train | nominal test ở 4 lags | đặt sanity baselines, không tune learned model |
| Final point-model comparison | fit lại `train + validation` theo từng tháng | nominal test chung 216,090 rows | mở một lần, kết quả ở mục 6 |
| Uncertainty task (iii) | point model đã cố định | calibration split riêng | ngoài phạm vi report point-model này |

## 4. Baseline

Relation study đã screen baseline riêng cho hai target ở cả bốn lag:

| Lag | Best Price baseline | Price MAE | Best Multiplier baseline | Multiplier MAE |
| ---: | --- | ---: | --- | ---: |
| 5 phút | History 60m price mean | 25,056 VND | Latest observed multiplier | 0.0188 |
| 10 phút | History 60m price mean | 25,333 VND | Latest observed multiplier | 0.0290 |
| 15 phút | History 60m price mean | 25,615 VND | Latest observed multiplier | 0.0383 |
| 30 phút | History 60m price mean | 26,441 VND | Pricing average multiplier 5m lag | 0.0572 |

Tại lag 15, chốt **History 60m price mean** làm Price baseline chính; nó mạnh
hơn route×service median (`28,143 VND`), distance-scaled persistence
(`29,585 VND`) và latest-price persistence (`33,707 VND`). Multiplier dùng
latest observed multiplier làm strong baseline (`0.0383`).

**Key finding:** baseline error tăng theo observation lag. Với Multiplier,
latest observation thắng ở 5–15 phút nhưng bị market-average baseline vượt ở
30 phút; freshness của delayed state quan trọng và baseline/model gate phải
được đọc theo từng horizon.

Baseline table là descriptive test evidence, không phải feature/model-selection
evidence. Sau khi đọc bảng này, learned-model candidates vẫn phải được chọn và
khóa bằng train/outer-validation protocol riêng.

## 5. Feature engineering và feature selection

Relation study inventory `33` prediction-time features. P5 không lấy bảng
importance làm feature list cuối; nó chuyển các findings thành một chuỗi
experiment có retrain, chronological folds và gate đăng ký trước.

### 5.1. Từ relation findings tới feature contract

| Stage | Câu hỏi/thử nghiệm | Kết quả | Ý nghĩa |
| --- | --- | --- | --- |
| Relation prioritization | 7 information blocks; raw association, MI, permutation, adjusted effect | trip structure, delayed multiplier và market state là ba nguồn signal chính | tạo hypothesis và thứ tự thử, chưa quyết định giữ/bỏ |
| Stage 1 — source screening | Core 24 features; Core+Weather; Core+Freshness; Full 33 | Core thắng history baseline `28.87%`, 3/3 tháng; Full chỉ hơn Core `2.85 VND` (`0.0158%`), CI cắt 0 | weather/freshness không có incremental evidence đủ mạnh trong direct HGB |
| Stage 2 — group ablation + forward addition | refit các data groups theo cả drop và add path | chọn `CORE_MINUS_PRICE_HISTORY`, 15 features; validation MAE `18,067.24 VND` | delayed price có association nhưng bị trip/multiplier/market fields thay thế trong learner này |
| Stage 3A — engineered batches | FE-A route speed; FE-B distance scaling; FE-C history dynamics; FE-D market gaps; FE-E cyclic time; FE-F reliability | 6 batches, 62/62 checks PASS; không batch nào đạt retain gate `0.1%` | không có engineered block đơn lẻ tạo bước nhảy |
| Stage 3C — interaction recovery | 22 pair/bridge candidates trên 9 train-only folds | `STOP_NO_TRAIN_CANDIDATE`; không candidate đạt `0.1%` | bounded cross-batch synergy cũng không giải thích plateau |
| Stage 4 — sequential pruning | drop-column refit, mỗi vòng bỏ tối đa một feature rồi đánh giá lại | 7 rounds, `15 → 8` features; validation `18,067.24 → 18,062.43 VND`; CI `[-1.64, 10.32]` | simplification/non-inferiority win, không phải material accuracy gain |
| Stage 5 — HGB tuning | 33 deterministic specifications trên 9 purged folds | khóa `S5_HPT_004`; validation MAE `18,035.28 VND`, hơn default `0.1503%` | tuning có gain thật nhưng vẫn nhỏ so với noise floor |

Relation permutation và adjusted effect đo model reliance/association trên một
model đã fit. Feature-contract decision dùng group ablation, batch ablation và
drop-column **có retrain**, để các feature còn lại có cơ hội thay thế signal.
Do đó các con số relation ở mục 2 không được đọc như selection threshold.

### 5.2. Impact của từng feature được giữ lại

Để quyết định feature contract, mỗi feature được bỏ riêng khỏi HGB 15-feature
base và đánh giá lại trên 9 chronological folds. Bảng dưới báo cáo mức MAE tăng
khi bỏ feature; số càng lớn thì feature càng khó được thay thế bởi các feature
còn lại.

| Feature bị bỏ | MAE tăng | MAE tăng tương đối | Kết luận |
| --- | ---: | ---: | --- |
| `quote_distance` | 1,742.94 VND | 9.792% | driver mạnh nhất |
| `quote_duration` | 1,670.19 VND | 9.383% | driver mạnh thứ hai |
| `service_id` | 103.23 VND | 0.580% | giữ khác biệt fare theo service |
| `latest_observed_multiplier` | 73.64 VND | 0.414% | cung cấp delayed pricing state |
| `target_hour` | 43.93 VND | 0.247% | giữ time-of-day pattern |
| `pricing_market_imbalance_5m_lag` | 35.91 VND | 0.202% | market signal nhỏ nhưng còn độc lập |
| `pickup_zone_id` | 27.26 VND | 0.153% | giữ khác biệt theo khu vực đón |
| `target_day_of_week` | 10.00 VND | 0.056% | impact nhỏ nhất nhưng chưa đủ bằng chứng để bỏ |

8 feature giữ lại: `quote_distance`, `quote_duration`,
`latest_observed_multiplier`, `pricing_market_imbalance_5m_lag`,
`service_id`, `pickup_zone_id`, `target_hour`, `target_day_of_week`.

7 feature còn lại được loại tuần tự vì không mang thêm signal độc lập khi 8
feature trên đã có mặt. Sau pruning, outer-validation MAE thay đổi từ
`18,067.24` xuống `18,062.43 VND` (`+4.80 VND`, chỉ `0.0266%`). Vì vậy lợi
ích chính của feature engineering là giảm contract từ 15 xuống 8 biến mà không
làm giảm accuracy đáng kể; nó không tạo ra bước nhảy về MAE.

## 6. Model: P5 → P12

Tất cả candidate dưới đây được fit lại trên `train + validation` theo từng
tháng và đánh giá trên đúng cùng nominal test gồm `216,090` observations. Test
không được dùng để đổi feature, hyperparameter, threshold hoặc candidate.

| Model | Hướng tiếp cận | Test MAE (VND) | Test RMSE (VND) | Test WAPE | ΔMAE vs P6 (VND) |
| --- | --- | ---: | ---: | ---: | ---: |
| P5 | Tuned HGB (32 candidates, 9 folds) | 18,045.07 | 24,540.95 | 14.672% | +42.47 |
| **P6** | **CatBoost, 700 trees/depth 6/lr 0.05, MAE loss** | **18,002.60** | **24,461.46** | **14.638%** | **0.00** |
| EBM-GAM | GAM base | 18,746.46 | 25,001.91 | 15.243% | +743.86 |
| **P7** | **Residual CatBoost** | **17,998.21** | **24,337.58** | **14.634%** | **−4.40** |
| P9 | Full 33-feature CatBoost | 18,011.37 | 24,484.30 | 14.645% | +8.76 |
| P9 | Multi-lag CatBoost | 18,011.93 | 24,485.72 | 14.646% | +9.33 |
| P10 | Causal meta-residual | 18,000.11 | 24,440.33 | 14.636% | −2.49 |
| P11 | Retrieval advantage gate | 18,002.38 | 24,461.67 | 14.638% | −0.22 |
| P12 | Latent-state CatBoost | 18,000.98 | 24,425.10 | 14.637% | −1.62 |
| P12 | Public rate-card transfer | 24,893.36 | 33,286.95 | 20.241% | +6,890.75 |

P7 có MAE thấp nhất về số học, nhưng chỉ thấp hơn P6 `4.40 VND` (`0.024%`);
đây không phải mức cải thiện có ý nghĩa vận hành. Bỏ candidate rate-card,
các learned tree model chỉ nằm trong dải `17,998–18,045 VND`, cho thấy kết
luận model plateau vẫn giữ nguyên khi mọi model được đặt lên cùng một tập test.
Vì test đã được dùng cho bảng cuối này, kết quả không được dùng để mở thêm vòng
tuning hoặc tái chọn model.

## 7. Kết quả chính

P6 test MAE `18,002.60 VND` tương đương khoảng `15.8%` của median fare; WAPE
là `14.638%`. P90 absolute error đạt `38,640 VND`, bằng khoảng `34%` median
fare. Nghĩa là model đã tốt hơn các baseline đơn giản nhưng tail error vẫn lớn
đối với một hệ thống cần dùng prediction để ra quyết định giá.

| Evidence | Kết quả | Ý nghĩa |
| --- | ---: | --- |
| P7 test MAE | 17,998.21 VND | thấp nhất về số học, chỉ hơn P6 4.40 VND |
| P6 test MAE | 18,002.60 VND | gần như trùng outer-validation 18,001.97 VND |
| P6 WAPE | 14.638% | aggregate error vẫn lớn so với tổng fare value |
| P6 P90 absolute error | 38,640 VND | 10% prediction có lỗi ít nhất xấp xỉ mức này |

## 8. Bottleneck

Bằng chứng: residual HGB/CatBoost tương quan `~0.99`; biết trước true
multiplier chỉ giảm MAE `~217 VND`; base-fare error lớn hơn multiplier error
`~7.39×`; P12 residual tương quan P6 tới `0.99753`. → Bottleneck là **thiếu
thông tin hidden base-pricing state** (rate-card version, fee/surcharge,
promotion, operational state), không phải thiếu model tốt hơn.

## 9. Kết luận

1. Giữ P6 làm incumbent benchmark đã chọn trước khi mở test, không claim
   production-ready; không promote P7 từ chênh lệch test `4.40 VND`.
2. Dừng mở lineage point-price mới trên cùng data contract.
3. Next: chuyển sang multiplier/surge và acceptance-rate modeling.
4. Chỉ mở lại point-price nếu có information block mới giải quyết hidden
   base-pricing state.
