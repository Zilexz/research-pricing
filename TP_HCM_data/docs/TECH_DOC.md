# Tài liệu kỹ thuật — Competitor Fare Forecasting (TP.HCM)

**Dự án:** Dự báo giá đối thủ và lượng hoá độ bất định · GSM/XanhSM
**Phạm vi dữ liệu:** 01/01–31/03/2026 · 1.724.714 lần báo giá · synthetic
**Phiên bản:** 1.1 — 15/08/2026 *(bổ sung §15.4 demo)*
**Đối tượng đọc:** mentor và team kỹ thuật

---

## 0.1 Quy ước

**Ký hiệu.** Tài liệu viết bằng tiếng Việt nhưng giữ nguyên thuật ngữ tiếng Anh đã thành
chuẩn ngành (*coverage*, *conformal*, *multiplier*, *elasticity*…) vì dịch ra sẽ khó đối chiếu với
tài liệu tham khảo. Từ điển ở §0.3.

**Số liệu.** Mọi con số trong tài liệu đều tái lập được. Chỗ nào là giả định hoặc trích từ
literature chưa xác minh đều được đánh dấu rõ. Đây là nguyên tắc xuyên suốt: người đọc phải phân
biệt được điều gì đo được và điều gì giả định.

---

## 0.2 Tóm tắt điều hành

### Bài toán

Dự báo `target_shown_price` — mức giá đối thủ sẽ hiển thị cho một yêu cầu chuyến đi — tại thời điểm
chỉ quan sát được giá đối thủ trễ 5–30 phút. Kèm theo là một khoảng tin cậy cho mỗi dự báo.

### Kiến trúc

Hệ thống 3 tầng, trong đó chỉ 2 tầng đầu là machine learning:

```
TẦNG 0  Dữ liệu ─ 1,72tr báo giá · KHÔNG có nhãn accept/reject
   │
   ▼
TẦNG 1  Model giá         [HỌC]   giá = giá cơ bản × hệ số nhân
   │  → p̂ (một con số)
   ▼
TẦNG 1b Uncertainty       [HỌC]   conformal chuẩn hoá + Mondrian
   │  → f(p̂) (một phân phối)
   ▼
TẦNG 2  Acceptance    [GIẢ ĐỊNH]  mô hình cấu trúc McFadden, không train
```

### Kết quả chính

| Hạng mục | Kết quả |
|---|---:|
| MAPE giá cuối (test, lag 5′) | **14,65%** |
| MAE giá cuối (test đầy đủ) | **~18.048đ** |
| Vượt baseline persistence | **47,4%** |
| Khoảng dự báo 90% | **giá dự đoán × (1 ± 30,1%)** |
| Coverage thực tế | **89,8%** |

### Ba kết luận đáng nói nhất

1. **Model đã chạm sàn sai số của bộ dữ liệu.** 98,9% phương sai sai số nằm ở tầng giá cơ bản, mà
   tầng đó có trần lý thuyết 14,98% trong khi model đạt 14,58%. Các chuyến giống hệt nhau về
   mọi thuộc tính quan sát được vẫn có giá cơ bản lệch nhau CV 18,6%. Xem §7.5.

2. Mọi yếu tố thị trường đi qua tầng hệ số nhân — tầng đã gần hoàn hảo. Cung–cầu (+35,1%), giờ
   cao điểm (+11,9%), cuối tuần (+6,3%) đều tác động ≥80% qua hệ số nhân, mà hệ số nhân đã đạt MAPE
   1,42%. ⇒ Thêm feature thị trường không cải thiện được độ chính xác giá cuối. Xem §3.3, §7.5.

3. Model có học được cơ chế nhân quả, nhưng chỉ dùng khi cần. Ở lag 5′ nó chép giá quan sát trễ;
   rút cái nạng đó ra (lag 30′) nó tự bù 94% hiệu ứng mưa. Xem §11.3.

### Giới hạn lớn nhất

Dữ liệu là synthetic (`is_synthetic = True` toàn bộ). Mọi kết luận mô tả hành vi của bộ sinh
dữ liệu, không phải thị trường TP.HCM thật. Ba giới hạn còn lại ở §18.

---

## 0.3 Từ điển thuật ngữ

| Thuật ngữ | Nghĩa trong tài liệu này |
|---|---|
| **Giá cơ bản** (base price) | Phần giá phụ thuộc cấu trúc chuyến, `= giá cuối / hệ số nhân` |
| **Hệ số nhân** (multiplier) | Phần giá phụ thuộc trạng thái thị trường, `target_shown_multiplier` |
| **Hybrid** | Kiến trúc `giá = Model_A(giá cơ bản) × Model_B(hệ số nhân)` |
| **Persistence** | Baseline ngây thơ: dùng thẳng giá quan sát trễ làm dự đoán |
| **Lag** | Độ trễ của giá đối thủ quan sát được: 5, 10, 15, 30 phút |
| **Coverage** | Tỷ lệ giá thật rơi vào khoảng dự báo |
| **Coverage điều kiện** | Coverage tính riêng trong từng nhóm (band giá, quãng đường…) |
| **Conformal** | Phương pháp dựng khoảng có bảo đảm hữu hạn mẫu, không giả định phân phối |
| **Mondrian** | Conformal hiệu chỉnh riêng theo từng nhóm |
| **η²** (eta bình phương) | Tỷ lệ phương sai sai số giải thích được bởi một chiều |
| **Ceteris paribus** | Đổi một yếu tố, giữ nguyên phần còn lại |
| **WTP** | Willingness to pay — mức sẵn lòng chi trả |
| **Elasticity `ε`** | Độ co giãn của cầu theo giá |

---

# PHẦN I — BÀI TOÁN VÀ DỮ LIỆU

## 1. Định nghĩa bài toán

### 1.1 Ba cấu phần đề bài

| # | Cấu phần | Thư mục | Trạng thái |
|---|---|---|---|
| **(i)** | Yếu tố nào ảnh hưởng giá và ảnh hưởng thế nào | `analysis/` | ✅ Xong |
| **(ii)** | Model dự đoán giá đối thủ | `model/train`, `model/evaluation` | ✅ Xong |
| **(iii)** | Lượng hoá độ bất định | `model/uncertainty/` | ✅ Xong |
| **(+)** | Mức độ chấp nhận giá *(mentor bổ sung)* | `model/acceptance/` | ⏸️ Dừng ở v1 |

### 1.2 Hình thức hoá

Tại thời điểm $t$, cho một yêu cầu chuyến đi với đặc trưng $x$ (quãng đường, thời lượng, tuyến,
dịch vụ, thời tiết, giờ), và lịch sử giá đối thủ quan sát được đến $t - \Delta$, dự báo:

$$\hat p = \mathbb{E}[\,p \mid x,\ \mathcal{H}_{t-\Delta}\,], \qquad \Delta \in \{5, 10, 15, 30\}\ \text{phút}$$

trong đó $p$ = `target_shown_price`. Đồng thời dựng khoảng $[\ell, u]$ sao cho
$\mathbb{P}(p \in [\ell, u]) \ge 1 - \alpha$ với $\alpha = 0{,}10$.

**Vì sao có độ trễ.** Dataset mô phỏng tình huống thực tế: giá đối thủ không quan sát được tại đúng
thời điểm cần ra quyết định. Đây là điểm khiến bài toán không tầm thường — nếu quan sát được ngay
thì chỉ cần đọc giá, không cần model.

### 1.3 Đơn vị quan sát — điểm dễ sai nhất

Dataset có hai mức hạt, lẫn lộn hai mức này là lỗi phổ biến nhất:

| Mức | Cột khoá | Số dòng | Dùng khi nào |
|---|---|---:|---|
| **Forecast example** | `forecast_example_id` | 6.897.051 | Train và đánh giá model |
| **Target request** | `target_request_id` | **1.724.714** | Phân tích cấu thành giá |

Mỗi `target_request` xuất hiện 4 lần trong bảng, một lần cho mỗi mức lag. Nghĩa là:

- **Khi train**: giữ nguyên 4 dòng — mỗi dòng là một bài toán dự báo khác nhau (thông tin đầu vào
  khác nhau), hoàn toàn hợp lệ.
- **Khi phân tích giá**: bắt buộc `drop_duplicates("target_request_id")`, nếu không mỗi chuyến
  bị đếm 4 lần và mọi thống kê mô tả đều sai trọng số.

```python
# Phân tích cấu thành giá — PHẢI khử trùng
d = pd.read_parquet(DATA, columns=COLS).drop_duplicates("target_request_id")
```

### 1.4 Tiêu chí thành công và baseline

**Baseline bắt buộc vượt: `persistence`** — dùng thẳng giá quan sát trễ làm dự đoán. Đây là baseline
đúng cho bài toán này (không phải "dự đoán giá trung bình"), vì nó là thứ một hệ thống không có
model sẽ làm.

| | MAE | MAPE |
|---|---:|---:|
| Persistence (test đầy đủ) | 33.683đ | 28,18% |
| **Hybrid** (test đầy đủ) | **18.048đ** | **14,74%** |
| Persistence (test lag 5′) | — | 27,84% |
| **Hybrid** (test lag 5′) | — | **14,65%** |

⚠️ Hai bộ số này khác nhau vì tập test khác nhau — xem §7.1. Khi trích dẫn phải nói rõ tập nào.

---

## 2. Dữ liệu

### 2.1 Nguồn và phạm vi

| | |
|---|---|
| Tên | `synthetic_quote_context_sandbox` (TP.HCM) |
| Nguồn | Mentor cung cấp, 267 file `.csv.gz` chia theo 3 hex |
| Kỳ | 01/01/2026 – 31/03/2026 (90 ngày) |
| Quy mô | 1.724.714 báo giá × 4 lag = 6.897.051 dòng · 72 cột |
| Nền tảng | 1 (`Synthetic Competitor`) |
| Dịch vụ | 2 (`Synthetic Standard Car`, `Synthetic Premium Car`) |
| Khu vực | 3 zone → 9 cặp tuyến |
| Thời tiết | 4 loại (`Clear`, `Clouds`, `Rain`, `Mist`) |

### 2.2 ⚠️ Bản chất synthetic và bốn hệ quả

`is_synthetic = True` cho toàn bộ 6.897.051 dòng. Đây không phải chi tiết kỹ thuật nhỏ — nó điều
kiện hoá mọi kết luận:

| Hệ quả | Chi tiết |
|---|---|
| **1. Kết luận mô tả simulator** | Mọi phát hiện về hành vi giá là phát hiện về **bộ sinh dữ liệu**, không chứng minh được điều gì về thị trường TP.HCM thật |
| **2. Mức nhiễu có thể không thật** | Sàn sai số 14,6% (§7.5) là đặc tính của simulator. Dữ liệu thật có thể sạch hơn hoặc bẩn hơn |
| **3. Thiếu hiện tượng thật** | Ngày lễ không được mô hình hoá (§3.4). Có thể còn hiện tượng khác thiếu mà chưa phát hiện |
| **4. Đa dạng thấp** | 3 khu vực, 2 dịch vụ, 1 nền tảng — không kiểm được tính khái quát |

Đã ghi nhận ở `tai_lieu_tham_khao/03_final_point_pricing_report...`. Phải nêu rõ khi báo cáo.

### 2.3 Từ điển trường — 72 cột theo vai trò

| Nhóm | Số cột | Cột tiêu biểu |
|---|---:|---|
| **Định danh & thời gian** | 6 | `forecast_example_id`, `target_request_id`, `target_timestamp`, `evaluation_month` |
| **Chuyến đi** | 8 | `quote_distance`, `quote_duration`, `service_name`, `pickup/dropoff_zone_id`, toạ độ |
| **Địa điểm** | 5 | `pickup/dropoff_location_name`, `pickup_hex_id_7` |
| **Tín hiệu thị trường** | 5 | `pricing_demand_index_5m_lag`, `pricing_supply_index_5m_lag`, `pricing_market_imbalance_5m_lag`, `pricing_avg_shown_multiplier_5m_lag`, `pricing_quote_count_5m_lag` |
| **Thời tiết** | 20 | `weather_main` *(dùng)* + 19 cột chi tiết *(không dùng)* |
| **Quan sát trễ** | 9 | `latest_observed_price`, `latest_observed_multiplier`, `actual_observation_age_minutes`, `persistence_prediction` |
| **Lịch sử 60 phút** | 7 | `history_60m_price_mean/std/min/max`, `history_60m_price_slope_per_minute`, `history_60m_multiplier_mean`, `history_60m_observation_count` |
| **Nhãn (target)** | 3 | `target_shown_price`, `target_shown_multiplier`, `target_price_per_km` |
| **Phân chia & cờ** | 9 | `split`, `is_synthetic`, `requested_lag_minutes`, `scenario_id` |

Từ điển chi tiết từng trường: `analysis/00a_tu_dien_70_truong.ipynb`.

**Không có trong dữ liệu** (đã rà toàn bộ 72 cột):

- Nhãn `accept` / `reject` · outcome cuốc · `customer_id`
- `public_holiday`
- Chi phí biên, tỷ lệ ăn chia tài xế
- Thị phần

### 2.4 ⚠️ Bốn bẫy dữ liệu đã vấp

Ghi lại để người sau không mất thời gian:

| # | Bẫy | Triệu chứng | Cách đúng |
|---|---|---|---|
| **1** | `quote_duration` tính bằng **giây**, không phải phút | Nhãn hình ra "1125–1130 phút"; tốc độ tính ra 0,3 km/h | `kmh = quote_distance / (quote_duration / 3600)`; ô 5 phút là `// 300` |
| **2** | Mỗi `target_request` lặp 4 lần theo lag | Thống kê mô tả sai trọng số | `drop_duplicates("target_request_id")` khi phân tích giá |
| **3** | `target_is_weekend` là `int8`, không phải `bool` | `unstack()` ném `KeyError: False` | `.astype(bool)` trước khi dùng làm khoá nhóm |
| **4** | Category codes lệch giữa train và test | XGBoost báo lỗi; HistGB/LightGBM **im lặng đoán sai** | Gọi `dat_categories(df)` **một lần trên df đầy đủ** trước khi chia tập |

Bẫy 4 nguy hiểm nhất vì hai trong ba thuật toán không báo lỗi. Đã xử lý bằng `assert` trong
`prep()` — xem §5.3.

Bẫy 1 đã làm sai một con số trong bản thảo (trần 14,84% thay vì 14,98%) — xem Phụ lục C.

### 2.5 Pipeline làm sạch

```
data/synthetic_data/*.csv.gz  (267 file, 459,5 MB)
            │  model/00_chuan_bi_du_lieu.ipynb  (~2,5 phút)
            ▼
data/hcm_train_ready.parquet  (6.897.051 dòng × 72 cột, 368,6 MB)
            │
            ▼  mọi notebook đọc từ đây
```

Notebook chuẩn bị làm: gộp file, ép kiểu (`float32`/`int8` để giảm bộ nhớ), sinh cột dẫn xuất
(`gio_vn`, `thu_vn` theo múi giờ Việt Nam), gán `split`, và cố định danh mục category.

### 2.6 Chia tập theo thời gian

| Tập | Số dòng | Vai trò |
|---|---:|---|
| `train` | 4.641.799 | Huấn luyện |
| `validation` | 774.984 | Early stopping, chọn siêu tham số |
| `calibration` | 615.908 | **Hiệu chỉnh khoảng bất định** — model chưa từng thấy |
| `test` | 864.360 | Đánh giá cuối |

**Chia theo thời gian, không random.** Lý do bắt buộc: dữ liệu có tự tương quan mạnh theo thời gian
(giá 5 phút liên tiếp gần như nhau). Random split sẽ đặt các quan sát gần nhau về thời gian vào cả
train lẫn test → rò rỉ → kết quả đẹp giả.

**Tập `calibration` tách riêng** là điều kiện để conformal prediction có bảo đảm hữu hạn mẫu: hệ số
khoảng phải tính trên dữ liệu model chưa từng thấy. Dùng lại tập train sẽ cho khoảng hẹp giả.

---

## 3. Cấu thành giá — kết quả cấu phần (i)

> Nguồn: `tuan_4/04_CAU_THANH_GIA.ipynb`, `analysis/14_ceteris_paribus.ipynb` · 1.724.714 chuyến độc lập

### 3.1 Cấu trúc hai tầng

$$\text{giá} = \text{giá cơ bản} \times \text{hệ số nhân}$$

Đây chính là cấu trúc *market signal multiplier* mà team mentor mô tả. Giá cơ bản trung bình
103.642đ, hệ số nhân trung bình 1,165 → giá cuối 121.367đ.

Phân biệt hai tầng có ý nghĩa vận hành trực tiếp:

| Tầng | Phản ánh | Cần loại phản ứng nào |
|---|---|---|
| **Giá cơ bản** | Cấu trúc chuyến — dài hơn, lâu hơn, tuyến khác | Bài toán ước lượng thời lượng, quy hoạch tuyến |
| **Hệ số nhân** | Trạng thái thị trường — cung cầu lệch | Bài toán điều phối cung |

### 3.2 Phương pháp — đối chứng ghép cặp

Không chạy được thí nghiệm thật (không ai bật/tắt mưa được), nên dùng đối chứng ghép cặp:

1. Chia dữ liệu thành các ô giống nhau ở mọi yếu tố khống chế
2. Trong từng ô, so hai nhóm khác nhau đúng ở yếu tố đang xét
3. Bình quân các ô theo số chuyến

```python
def ghep_cap(yeu_to, khong_che):
    g = (d.groupby(khong_che + [yeu_to], observed=True)[cot]
           .agg(["mean", "size"]).unstack(yeu_to).dropna())
    n = g[("size", False)] + g[("size", True)]
    w = n / n.sum()
    return float(((g[("mean", True)] / g[("mean", False)] - 1) * w).sum())
```

Mỗi yếu tố có bộ khống chế riêng, chọn để chặn đúng đường nhiễu đặc thù của nó:

| Yếu tố xét | Khống chế | Vì sao |
|---|---|---|
| Trời mưa | quãng đường · giờ · cuối tuần | Mưa hay rơi buổi chiều — không khống chế giờ sẽ tính nhầm hiệu ứng cao điểm thành hiệu ứng mưa |
| Giờ cao điểm | quãng đường · thời tiết · cuối tuần | Cao điểm chỉ có ngày thường |
| Cung–cầu | quãng đường · giờ · thời tiết | Cung–cầu tương quan mạnh với giờ |

**Điểm mấu chốt:** cùng một hàm chạy trên `gia`, `base`, `heso` — nên ba con số so sánh trực tiếp
được và cho biết yếu tố đi vào tầng nào.

### 3.3 Bảng phản ứng giá

| Yếu tố | Giá cuối | Qua giá cơ bản | Qua hệ số nhân | Phần qua HSN |
|---|---:|---:|---:|---:|
| **Cung–cầu** (Q1→Q5) | **+35,08%** | +5,60% | +27,90% | **80%** |
| Đường tắc (cùng quãng đường) | +16,52% | +13,43% | +2,70% | 16% |
| Giờ cao điểm | +11,86% | +0,80% | +11,07% | **93%** |
| Trời mưa | +9,70% | +3,18% | +6,10% | 63% |
| Cuối tuần | +6,30% | +0,24% | +6,38% | **96%** |
| Dịch vụ Premium | −1,29% | −1,02% | −0,25% | — |
| **Ngày lễ** | *không có* | — | — | — |

🖼️ `CG1_xep_hang_yeu_to.png` · `CG2_cau_truc_vs_thi_truong.png`

**Ba điều rút ra:**

1. **Cung–cầu mạnh nhất** — gấp ba lần giờ cao điểm. Xác nhận trực tiếp cách team mentor nghĩ: giá
   là kết quả của thay đổi yếu tố thị trường.

2. **Quy luật tách bạch.** Yếu tố *thị trường* (cung–cầu, giờ, cuối tuần) đi qua hệ số nhân; yếu tố
   *cấu trúc chuyến* (quãng đường, tắc đường) đi qua giá cơ bản.

3. **Mưa là ngoại lệ duy nhất** — nó đi cả hai đường: vừa tăng cầu (hệ số nhân +6,10%), vừa làm
   đường tắc khiến chuyến lâu hơn (giá cơ bản +3,18%). Chuỗi nhân quả khép kín:
   `mưa → tắc đường → thời lượng tăng → giá cơ bản tăng`, song song với `mưa → cầu tăng → hệ số nhân tăng`.

**Quãng đường** không đo bằng ghép cặp nhị phân (nó là biến liên tục và chính là thứ đang được khống
chế ở mọi phép đo khác). Đo riêng: giá cơ bản/km giảm từ 32.534đ (1–2 km) xuống 13.168đ
(17–18 km), tức −60% — có chiết khấu rõ cho chuyến dài.

### 3.4 Ngày lễ — thiếu cả cột lẫn hiện tượng

Mentor nêu `public_holiday` đích danh. Hai vấn đề riêng biệt:

1. **Không có trường** `public_holiday` trong 72 cột.
2. **Hiện tượng cũng không có.** Kỳ dữ liệu chứa Tết Nguyên Đán 17/02/2026 — dịp giá gọi xe tăng
   mạnh nhất năm ở thực tế. Kiểm trực tiếp:

| | Giá TB |
|---|---:|
| Toàn kỳ 90 ngày | 121.178đ (sd theo ngày 4.709đ) |
| Ngày Tết 17/02 | **116.173đ** |
| Xếp hạng ngày Tết | **81/90** (1 = đắt nhất) |

⇒ Bộ sinh dữ liệu không mô hình hoá ngày lễ. Nên câu hỏi cho mentor không phải *"bổ sung cột
được không"* mà là *"dữ liệu thật có hiệu ứng ngày lễ không"*. Thêm cột vào bộ hiện tại sẽ tạo ra
một feature rỗng tín hiệu.

---

# PHẦN II — MODEL

## 4. Kiến trúc

### 4.1 Vì sao hybrid hai tầng

Ba hướng đã cài đặt và so sánh:

| Hướng | Cách làm | MAE (test đầy đủ) |
|---|---|---:|
| **Hybrid** ⭐ | `Model_A(giá cơ bản) × Model_B(hệ số nhân)` | **18.048đ** |
| Trực tiếp | Một model dự đoán thẳng giá cuối | 18.834đ |
| GAM | Generalized Additive Model | 19.170đ |

Hybrid thắng dự đoán trực tiếp ở cả 24/24 giờ trong ngày — không phải thắng nhờ may mắn ở vài
khung giờ.

**Lý do hybrid tốt hơn** không phải "hai model thì mạnh hơn một", mà là hai bài toán con có độ khó
rất khác nhau:

| Nhánh | R² | MAPE | Nhận xét |
|---|---:|---:|---|
| Hệ số nhân | **0,9609** | 1,90% | Gần như đã xong |
| Giá cơ bản | 0,6564 | 14,58% | **Nút thắt** |

Tách ra cho phép mỗi nhánh dùng bộ feature riêng phù hợp với bản chất của nó — hệ số nhân dùng
tín hiệu cung–cầu, giá cơ bản dùng hình học chuyến. Gộp làm một model buộc phải dùng chung feature
set và làm loãng tín hiệu.

Phân tích §3.3 giải thích vì sao cách tách này đúng về mặt cơ chế, không chỉ tiện về mặt kỹ
thuật: hai tầng thật sự chịu tác động của hai nhóm yếu tố khác nhau.

### 4.2 Sơ đồ tầng đầy đủ

Xem §0.2. Nguyên tắc thiết kế chốt:

> **Tách bạch phần HỌC và phần GIẢ ĐỊNH.**

| Tầng | Bản chất | Có train? | Đánh giá bằng |
|---|---|---|---|
| **1** Model giá | Machine learning | ✅ | MAE, R², train/test split |
| **1b** Uncertainty | Hiệu chỉnh thống kê | ✅ (trên calibration) | Coverage, độ rộng |
| **2** Acceptance | Structural (McFadden) | ❌ | Phân tích độ nhạy |

⚠️ Không trộn tầng 1 và tầng 2. Trộn vào sẽ ra "model AUC 1,0" nguỵ trang — bằng chứng ở
`acceptance/05_thu_nghiem_pseudo_label.ipynb`, xem §12.2.

---

## 5. Đặc trưng (feature)

### 5.1 Bộ feature từng model

Định nghĩa tập trung tại `model/_common_train.py`:

```python
CAT = ["service_name", "pickup_location_name", "dropoff_location_name", "weather_main"]

# Nhánh giá cơ bản — dùng latest_observed_base (đã bỏ surge)
B_NUM = ["quote_distance", "quote_duration", "gio_vn", "latest_observed_base",
         "history_60m_price_mean", "history_60m_price_std",
         "history_60m_price_slope_per_minute", "latest_observed_quote_distance",
         "latest_observed_quote_duration", "actual_observation_age_minutes"]

# Nhánh hệ số nhân — nhóm cung–cầu
M_NUM = ["pricing_market_imbalance_5m_lag", "pricing_demand_index_5m_lag",
         "pricing_supply_index_5m_lag", "pricing_quote_count_5m_lag",
         "latest_observed_multiplier", "gio_vn", "actual_observation_age_minutes"]

# Baseline dự đoán trực tiếp — dùng latest_observed_price (đã gồm surge)
D_NUM = ["quote_distance", "quote_duration", "gio_vn", "latest_observed_price",
         "history_60m_price_mean", "history_60m_price_std",
         "history_60m_price_slope_per_minute", "latest_observed_quote_distance",
         "latest_observed_quote_duration", "actual_observation_age_minutes"]
```

**Điểm thiết kế quan trọng:** nhánh giá cơ bản dùng `latest_observed_base` (giá quan sát đã bỏ
surge), nhánh hệ số nhân dùng `latest_observed_multiplier`. Nếu nhánh giá cơ bản dùng
`latest_observed_price` thì surge sẽ bị đếm hai lần khi nhân hai nhánh lại.

**Bốn feature đã loại** nhờ p-value từ GAM (§13.3) — không có ý nghĩa thống kê.

### 5.2 Chống rò rỉ dữ liệu

| Quy tắc | Cài đặt |
|---|---|
| Chỉ dùng thông tin có trước mốc cắt | Mọi feature `*_lag`, `latest_observed_*`, `history_60m_*` đều tính tại `t − Δ` |
| Không dùng cột nhãn hoặc dẫn xuất từ nhãn | `target_shown_*`, `target_price_per_km` chỉ làm target |
| Chia tập theo thời gian | §2.6 |
| Lịch sử giá reset theo tháng | Train riêng từng tháng — gộp lại là rò rỉ |

**Vai trò feature giá quan sát trễ.** `latest_observed_price` / `_base` là feature mạnh nhất, và
điều này có hệ quả sâu hơn vẻ ngoài: model dùng nó như một đường tắt thay vì học cơ chế. Toàn bộ
§11.3 dành cho việc đo hiện tượng này.

### 5.3 Bẫy mã hoá category

```python
def dat_categories(df):
    """PHẢI gọi 1 lần trên df ĐẦY ĐỦ, TRƯỚC khi chia train/test."""
    for c in CAT:
        df[c] = df[c].astype("category")
    return df
```

**Vì sao bắt buộc.** Nếu để `prep()` tự cast trên từng tập con, pandas sinh danh mục riêng theo giá
trị có trong tập con đó → train và test có mã số khác nhau cho cùng một giá trị (ví dụ `Clear`
= 0 ở train nhưng = 1 ở test). Hậu quả:

| Thuật toán | Biểu hiện |
|---|---|
| XGBoost | Báo lỗi `Found a category not in the training set` — dễ phát hiện |
| HistGB, LightGBM | **Không báo lỗi**, đọc sai mã, dự đoán sai âm thầm |

`prep()` có `raise TypeError` nếu phát hiện cột chưa được cast — chốt chặn để không ai quên.

---

## 6. Huấn luyện

### 6.1 Thuật toán và siêu tham số

Ba thuật toán cây được cài đặt song song để đối chứng:

```python
HistGradientBoostingRegressor(max_iter=500, learning_rate=0.05,
    l2_regularization=1.0, early_stopping=True, validation_fraction=0.1,
    n_iter_no_change=20, categorical_features=CAT, random_state=42)

LGBMRegressor(n_estimators=800, learning_rate=0.03, num_leaves=63,
    subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0, random_state=42)

XGBRegressor(n_estimators=800, learning_rate=0.03, max_depth=7,
    subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
    tree_method="hist", enable_categorical=True, random_state=42,
    early_stopping_rounds=20, eval_metric="rmse")
```

**Không tinh chỉnh siêu tham số sâu.** Lý do có bằng chứng: Optuna 40 trial × 3 tháng chỉ cải thiện
**+2 VND**. Ném hết 49 cột vào chỉ được 6 VND. Bốn thuật toán chênh nhau 1,9%. Tất cả đều
chỉ về cùng một kết luận — model đã chạm trần dữ liệu (§7.5), nên đầu tư vào siêu tham số là lãng
phí.

### 6.2 Quy trình và thời gian chạy

| Bước | Notebook | Thời gian |
|---|---|---:|
| Chuẩn bị dữ liệu | `model/00_chuan_bi_du_lieu` | ~2,5 ph |
| Train giá cơ bản · hệ số nhân · trực tiếp | `train/01`–`03` | ~9 ph |
| Train GAM đối chiếu | `train/04` | ~13 ph |
| GAM transformed feature space | `train/05` | — |
| Train 21 model quantile | `train/06` | — |
| Sinh dữ liệu UQ | `train/07` | — |
| **Tổng train** | | **~21 ph** |

### 6.3 Artifact sinh ra

| Thư mục | Dung lượng | Nội dung |
|---|---:|---|
| `QuantileLGBM/` | 67,9 MB | 21 model quantile (7 phân vị × 3 tháng) |
| `XGBoost/` | 63,2 MB | giá cuối · giá cơ bản · hệ số nhân |
| `LightGBM/` | 41,5 MB | như trên |
| `HistGB/` | 28,0 MB | như trên + 2 model riêng cho UQ |
| `GAM/` | 1,1 MB | 3 nhánh GAM + encoder |

⚠️ `.gitignore` loại `*.joblib` và `*.parquet` — không artifact nào có trong git. Xoá là mất
hẳn, chỉ khôi phục bằng cách chạy lại notebook.

---

## 7. Đánh giá

### 7.1 Định nghĩa metric — và hai tập test

```python
MAE  = mean(|y - ŷ|)
RMSE = sqrt(mean((y - ŷ)²))
R²   = 1 - SS_res / SS_tot
MAPE = mean(|y - ŷ| / y) × 100        # chia cho GIÁ THẬT
```

⚠️ Hai quy ước tập test cùng tồn tại trong dự án. Đây là nguồn nhầm lẫn phổ biến khi đối chiếu
số giữa các báo cáo:

| Tập | Số dòng | Dùng ở | MAPE hybrid | MAPE persistence |
|---|---:|---|---:|---:|
| **Test đầy đủ** (4 lag) | 864.360 | Báo cáo tuần 2–3 | 14,74% | 28,18% |
| **Test lag 5′** | 216.090 | Tuần 4, uncertainty | 14,65% | 27,84% |

Cả hai đều đúng. Lag 5′ dễ hơn một chút nên MAPE thấp hơn. Khi trích dẫn phải nói rõ tập nào.

Ngoài ra, cần phân biệt hai mẫu số khi tính sai số tương đối:

| Ký hiệu | Công thức | Dùng khi |
|---|---|---|
| `sai` | `|ŷ − y| / y` | Báo cáo MAPE |
| `res` | `|ŷ − y| / ŷ` | **Dựng khoảng conformal** — vì lúc dự báo chưa biết `y` |

### 7.2 Kết quả tổng

| Model | MAE | MAPE | R² |
|---|---:|---:|---:|
| **Hybrid** | **18.048đ** | **14,74%** | ~0,73 |
| ├─ Giá cơ bản | 15.030đ | 14,58% | 0,6564 |
| └─ Hệ số nhân | 0,0232 | 1,90% | **0,9609** |
| XGBoost trực tiếp | 18.807đ | 15,34% | |
| LightGBM trực tiếp | 18.809đ | 15,34% | |
| HistGB trực tiếp | 18.834đ | 15,36% | |
| GAM | 19.170đ | 15,70% | |
| — Persistence *(baseline)* | 33.683đ | 28,18% | 0,0191 |

Trên tập lag 5′: model vượt persistence 47,4%.

### 7.3 Sai số nằm ở tầng nào

> Nguồn: `tuan_4/00_TONG_HOP.ipynb` · test lag 5′

Vì `giá = cơ bản × hệ số`, lấy log là tách được sai số theo tầng:

$$\log\frac{\hat p}{p} = \log\frac{\hat b}{b} + \log\frac{\hat m}{m}$$

Kiểm tra phép tách: sai lệch tối đa 5,8·10⁻⁸ ⇒ tách chuẩn.

| | Giá cơ bản | Hệ số nhân | Tương tác |
|---|---:|---:|---:|
| **Tỷ trọng phương sai sai số** | **98,9%** | 1,1% | −0,0% |
| MAPE riêng tầng | 14,58% | **1,42%** | — |

Tương quan giữa sai số hai tầng: −0,001 — độc lập.

**Thí nghiệm oracle** — cho một tầng dự đoán hoàn hảo, giữ nguyên tầng kia:

| Kịch bản | MAPE giá cuối | Giảm |
|---|---:|---:|
| Hiện tại | 14,65% | — |
| **Giá cơ bản hoàn hảo** | **1,42%** | **−90%** |
| Hệ số nhân hoàn hảo | 14,58% | **−0%** |

🖼️ `TK1_sai_so_o_tang_nao.png`

⇒ Sửa hệ số nhân về hoàn hảo không cải thiện được gì. Toàn bộ dư địa nằm ở tầng giá cơ bản.

### 7.4 Chẩn đoán — model fail ở đâu

> Nguồn: `evaluation/09_chan_doan_model.ipynb`, `tuan_4/02`

Xếp hạng các chiều bằng η² — tỷ lệ phương sai sai số mà chiều đó giải thích được:

| Chiều | η² | MAPE thấp → cao | Kết luận |
|---|---:|---|---|
| **Quãng đường** | **0,0106** | 9,16% → 17,52% | 🔴 Chỗ hỏng nặng nhất |
| Tuyến | 0,0079 | 10,96% → 15,00% | 🔴 Tương quan 0,894 với quãng đường ⇒ cùng nguyên nhân |
| Band giá | 0,0015 | 13,46% → 18,55% | 🟠 Sửa bằng Mondrian |
| Giờ trong ngày | 0,0001 | 14,48% → 14,85% | 🟢 |
| Thời tiết · cao điểm · cuối tuần | ≤0,0001 | biên độ ≤0,4 điểm | 🟢 Gần như vô can |

**Phát hiện đi ngược trực giác:** giờ cao điểm — thứ mentor nêu ba kịch bản uncertainty quanh nó —
có η² ≈ 0. Chiều thật sự quan trọng là quãng đường, mạnh gấp ~100 lần.

**Nhưng chuyến dài không phải model làm ẩu.** So với persistence theo từng nhóm:

| Quãng đường | MAPE model | MAPE persistence | Model vượt |
|---|---:|---:|---:|
| <2 km | 9,16% | 28,0% | 67,3% |
| 4–6 km | 14,95% | 29,7% | 49,7% |
| 8–10 km | 14,90% | 26,0% | 42,8% |
| **>15 km** | **17,52%** | 52,6% | **66,7%** |
| *Trung bình* | 14,65% | 27,84% | 47,4% |

🖼️ `QD3_fail_o_dau.png`

Nhóm `>15 km` sai nhiều nhất và là nơi model đóng góp nhiều nhất. ⇒ Chuyến dài khó một cách
nội tại, không phải model kém ở đó. Hệ quả lập kế hoạch: đừng đổ công "sửa chuyến dài" trên cùng
bộ feature.

**Không có thiên lệch hệ thống.** Trung bình lệch +1,60% nhưng trung vị +0,01% và tỷ lệ đoán cao
hơn thật 50,02% ⇒ do đuôi phải của phân phối giá, không phải model lệch. Trừ đi một hằng số sẽ
làm hỏng nửa số chuyến đoán thấp.

**Không có nhóm ngoại lai chi phối.** 1% chuyến sai nhất (sai ≥53,1%) chỉ đóng góp 2,7% tổng sai
số tuyệt đối. Không có phím tắt.

### 7.5 Trần thông tin — sàn sai số của bộ dữ liệu

> Đây là kết quả quan trọng nhất của tài liệu. Nguồn: `tuan_4/04` §5, `tuan_4/00`

**Câu hỏi:** giá cơ bản còn dao động bao nhiêu sau khi đã biết mọi thứ quan sát được về chuyến?

**Phương pháp oracle:** gom các chuyến giống hệt nhau ở mọi thuộc tính quan sát được, lấy trung bình
nhóm làm dự đoán. Đó là mức chính xác tốt nhất về lý thuyết mà bất kỳ model nào chỉ dùng các
thuộc tính đó có thể đạt.

| Oracle được biết | MAPE trần | % dữ liệu |
|---|---:|---:|
| Quãng đường (ô 0,5 km) | 16,74% | 100% |
| + thời lượng (ô 5 phút) | 15,22% | 100% |
| + tuyến | 15,19% | 99% |
| + dịch vụ | **14,98%** | 99% |
| **◆ Model hiện tại** | **14,58%** | 100% |

🖼️ `TK1` panel ③ · `CG3_tran_thong_tin_gia_co_ban.png`

**Model đã vượt trần** — nhờ dùng thêm giá cơ bản quan sát trễ, thứ oracle không có.

Và trần này còn được ước lượng lạc quan: trung bình ô tính in-sample nên trần thật cao hơn. Kết
luận vì thế càng chắc.

**Bằng chứng bổ trợ:** các chuyến cùng 5,5–6,0 km và 15–20 phút (n = 83.427) vẫn có giá cơ bản trải
rộng CV 18,7%. Thêm tuyến vào chỉ hạ trần 0,03 điểm (15,22% → 15,19%).

> Kết luận: giá cơ bản có một thành phần nhiễu ngẫu nhiên theo từng báo giá, không có quy luật để
> học. MAPE ~14,6% là sàn của bộ dữ liệu này.

Kết luận này khớp với ba bằng chứng độc lập đã có từ trước:

| Bằng chứng | Nguồn |
|---|---|
| 4 thuật toán chênh nhau 1,9% | §7.2 |
| Thu hẹp quãng đường xuống 2 mét, hệ số biến thiên giá **không giảm** | `B5_cv_khong_giam.png` |
| Optuna 40 trial → +2 VND; ném 49 cột → +6 VND | §6.1 |
| **Transformer 90.792 tham số, đọc thẳng chuỗi 32 báo giá → hoà** | §13.4 |

---

# PHẦN III — UNCERTAINTY (CẤU PHẦN iii)

## 8. Ba phương pháp

Giữ riêng 615.908 chuyến model chưa từng thấy (tập calibration) → đo sai số → lấy phân vị 90%.

| Phương pháp | Coverage | Độ rộng TB | Bảo đảm lý thuyết |
|---|---:|---:|---|
| **Conformal chuẩn hoá** ⭐ | ~89,6% | **~72.700đ** | Hữu hạn mẫu, phân phối tự do |
| Quantile Regression (thô) | 89,18% | 75.977đ | ❌ Không |
| CQR | 89,56% | 76.546đ | Hữu hạn mẫu |

**Conformal chuẩn hoá** làm mặc định — hẹp nhất và có bảo đảm.

**Công thức.** Trên calibration, tính `res = |ŷ − y| / ŷ` cho từng chuyến, lấy phân vị 90%:

$$q = \text{Quantile}_{0{,}90}\big(\{res_i\}_{i \in \text{calib}}\big), \qquad
[\ell, u] = \hat p \cdot (1 \pm q)$$

Kết quả: $q = 30{,}07\%$ → khoảng = giá dự đoán × (1 ± 30%), coverage thực tế 89,81%.

Dùng `res` (chia cho `ŷ`) chứ không phải `sai` (chia cho `y`) vì lúc dự báo chưa biết `y` — xem
§7.1.

## 9. Hiệu chỉnh Mondrian

Conformal toàn cục cho một hệ số `q` chung. Mondrian cho mỗi nhóm một hệ số riêng.

| Cách hiệu chỉnh | Nửa độ rộng | Coverage | Hẹp hơn gốc |
|---|---:|---:|---:|
| Conformal toàn cục | ±30,07% | 89,81% | — |
| Mondrian theo band giá | ±30,11% | 89,84% | +0,11% |
| **Mondrian theo quãng đường** | **±29,96%** | 89,77% | **−0,37%** |
| Mondrian theo giờ | ±30,07% | 89,78% | −0,02% |
| Mondrian theo thời tiết | ±30,07% | 89,80% | −0,01% |

**Mondrian không làm khoảng hẹp hơn.** Nhưng nó làm khoảng đều hơn — và đó mới là lý do dùng:

| Lệch coverage tối đa giữa các nhóm | Toàn cục | Mondrian |
|---|---:|---:|
| Theo band giá | 8,62 điểm | **1,46 điểm** |
| Theo quãng đường | 12,61 điểm | **2,53 điểm** |

🖼️ `QD1_mondrian_lam_deu.png`

Nhóm bị phục vụ tệ nhất dưới hiệu chỉnh toàn cục:

| Nhóm | Coverage toàn cục | Coverage Mondrian |
|---|---:|---:|
| Band `>300k` | 83,79% | **91,13%** |
| Quãng đường `>15 km` | 82,58% | **87,58%** |

Đây là chuyến đắt tiền nhất — nơi sai một khoảng tin cậy tốn nhiều nhất. Chi phí sửa: vài giờ,
không train lại, tốn thêm 0,04% độ rộng.

> Khuyến nghị vận hành: bật Mondrian theo quãng đường.

## 10. Coverage điều kiện và ba kịch bản

Mentor nêu ba model có cùng MAE nhưng phân bổ độ rộng khác nhau. Chạy thật trên tập test:

| Kịch bản | ± cao điểm | Coverage CĐ | ± giờ thường | Coverage GT |
|---|---:|---:|---:|---:|
| A · đều ±30% | 30,0% | 89,9% | 30,0% | 89,7% |
| B · ±10% CĐ / ±40% GT | 10,0% | **42,3%** | 40,0% | 96,3% |
| C · ±40% CĐ / ±10% GT | 40,0% | 96,5% | 10,0% | **42,3%** |
| **Model của mình** | 30,2% | **90,1%** | 30,1% | **89,7%** |

🖼️ `TT5_ba_kich_ban_theo_thoi_gian.png` · `TT6_coverage_ba_kich_ban.png`

**Ba điều rút ra:**

1. **Con số ±30% mentor đưa ra trúng phóc** — chạy thật cho coverage 89,7%.
2. **Model là kịch bản A**, tỷ lệ độ rộng cao điểm / giờ thường = 1,004.
3. **B và C không tồn tại được** trên tập này: khung được cấp ±10% chỉ giữ 42,3% coverage. Muốn hẹp
   ở cao điểm mà vẫn giữ 90% thì sai số ở cao điểm phải nhỏ hơn thật sự — mà §7.4 cho thấy sai
   số cao điểm và giờ thường bằng nhau.

**Cách trình bày quan trọng:** trong hình chuỗi thời gian, chấm đỏ bám coverage cấp chuyến,
không phải phép thử "đường trung bình rơi ngoài dải trung bình". Lý do: ở kịch bản B, đường giá
trung bình vẫn nằm gọn trong dải suốt cao điểm dù coverage thật chỉ 42% — đúng kiểu trung bình hoá
che mất vấn đề.

## 11. Vì sao không thu hẹp được khoảng

### 11.1 Trần lý thuyết

Nếu biết trước độ khó từng chuyến thì chỉ cần ±14,68% thay vì ±30,07% — dư địa −51%.

### 11.2 Nhưng không với tới được

Mọi cách hiệu chỉnh đều dựa trên một ý tưởng: cấp khoảng hẹp cho chuyến dễ, rộng cho chuyến khó. Ý
tưởng đó chỉ chạy được nếu biết trước chuyến nào khó.

| Tương quan hạng (Spearman) với độ lớn sai số | |
|---|---:|
| Quãng đường | +0,0509 |
| Giá dự đoán | +0,0473 |
| Thời lượng | +0,0509 |
| Tốc độ trung bình | +0,0225 |
| **GBM dự đoán độ khó** (4 feature) | **+0,0530** |

🖼️ `QD2_tran_ly_thuyet.png`

Train hẳn một GBM để dự đoán độ lớn sai số → tương quan hạng với sai số thật chỉ 0,053. Đám mây
điểm là một cột dựng đứng: GBM đoán chuyến nào cũng khó ngang nhau (~29–31%) trong khi sai số thật
trải từ 0% tới hơn 60%.

> Khoảng ±30% không phải lỗi hiệu chỉnh. Nó là ảnh phản chiếu trung thực của MAPE 14,65%.
> Muốn khoảng hẹp thì model phải sai ít hơn — mà §7.5 cho thấy model đã chạm sàn.

### 11.2b Khoảng rộng vì thị trường động, hay vì nhiễu?

Một đề xuất tự nhiên chưa bị loại: *"quan sát giá nhanh hơn thì khoảng hẹp lại"*. Kiểm trực tiếp vì
dữ liệu có sẵn bốn mức độ trễ:

| Độ trễ | MAPE model | MAPE persistence | Nửa độ rộng | Coverage |
|---|---:|---:|---:|---:|
| 5′ | 14,65% | 27,84% | ±30,07% | 89,81% |
| 10′ | 14,69% | 28,03% | ±30,05% | 89,66% |
| 15′ | 14,74% | 28,19% | ±30,08% | 89,54% |
| 30′ | 14,91% | 28,67% | ±30,19% | 89,24% |

🖼️ `QD4_bien_dong_vs_khoang.png`

Rút độ trễ 30′ → 5′ chỉ cải thiện MAPE 0,26 điểm; độ rộng gần như không đổi (−0,4%). Để so
sánh, `persistence` — thứ hoàn toàn phụ thuộc độ tươi của giá quan sát — tệ đi 3,0%. Phép đo có
đủ độ nhạy; nó cho thấy model gần như miễn nhiễm với độ trễ.

**Ba nguồn biến động, tách bạch:**

| Nguồn | Độ lớn | Model xử lý được không |
|---|---:|---|
| **Nhịp thị trường** — hệ số nhân theo giờ | biên độ **87,2%** (0,851 → 1,592) | ✅ Có — MAPE **1,42%** ở tầng này |
| **Nhiễu ngang** — giữa các báo giá cùng bối cảnh | CV **18,5%** | ❌ Không feature nào giải thích được |
| **Trôi theo thời gian** — 5′ → 30′ | **0,26 điểm** MAPE | Quá nhỏ để đáng xử lý |

Giá quan sát trong cửa sổ 60 phút dao động CV 24,9% (trung vị 63 báo giá/cửa sổ), nhưng phần lớn
là do các chuyến khác nhau: khống chế quãng đường và thời lượng còn 18,6%, thêm điều kiện cùng
giờ hầu như không giảm nữa (18,5%).

> Thị trường có động và động mạnh — nhưng model đã bắt được nhịp đó. Khoảng ±30% là ảnh
> phản chiếu của nhiễu ngang, không phải cái giá phải trả cho việc quan sát trễ.
> **Cập nhật giá nhanh hơn không phải hướng đi.**

### 11.3 Model có hiểu cơ chế giá không

> Nguồn: `tuan_4/03_CETERIS_PARIBUS_VA_CAUSALITY.ipynb`

Ba câu hỏi phải tách bạch, trộn lẫn là kết luận sai:

| # | Câu hỏi | Đo bằng |
|---|---|---|
| **A** | Trời mưa thì giá **thực tế** đổi bao nhiêu? | Ghép cặp trên dữ liệu thật |
| **B** | Model **dự đoán** giá đổi bao nhiêu? | Cùng phép ghép cặp, chạy trên `hybrid_pred` |
| **C** | Model có **hiểu** rằng *mưa* gây ra thay đổi đó không? | Đổi riêng feature thời tiết (partial dependence) |

Kết quả ở lag 5′:

| | Hiệu ứng mưa |
|---|---:|
| **A** Thực tế | +10,30% |
| **B** Model dự đoán | **+10,34%** |
| **C** Partial dependence | **+0,93%** |
| Persistence *(mù thời tiết hoàn toàn)* | +8,99% |

Ba con số này đều đúng, chúng trả lời ba câu khác nhau. Persistence — một con số không hề biết
trời có mưa hay không — đã tái tạo 87% hiệu ứng. ⇒ Model lấy đáp án qua đường tắt là giá
quan sát trễ, không cần hiểu gì về mưa.

**Phép thử quyết định: rút dần cái nạng ra.**

| Độ trễ | Thực tế | Model | Persistence | Khoảng trống | Model bù được |
|---|---:|---:|---:|---:|---:|
| 5′ | +10,30% | +10,34% | +8,99% | 1,31 điểm | **103%** |
| 10′ | +10,30% | +10,13% | +7,90% | 2,40 điểm | 93% |
| 15′ | +10,30% | +10,10% | +7,14% | 3,16 điểm | 94% |
| **30′** | +10,30% | **+9,97%** | **+4,53%** | **5,77 điểm** | **94%** |

🖼️ `PU1_rut_cai_nang.png`

Ở lag 30′, giá trễ chỉ còn giải thích +4,53% trong +10,30% — cái nạng gãy hơn một nửa. Model vẫn ra
+9,97%, tức tự bù 94% phần thiếu.

> Kết luận: model hiểu cơ chế, nhưng ưu tiên đường tắt khi đường tắt còn dùng được.

Đây là hành vi hợp lý của một model tối ưu MAE, không phải lỗi. Nhưng nó có hệ quả vận hành: ba tình
huống rút nạng ra thì model sai —

1. **Câu what-if** — *"nếu chiều mai mưa thì giá bao nhiêu?"* Chưa có giá quan sát nào để chép.
2. **Horizon xa** — dự báo 30–60 phút tới.
3. **Thị trường mới** — chưa có lịch sử giá đối thủ.

Đúng ba tình huống mentor mô tả bằng cụm *"measure price như là kết quả của một thay đổi của yếu tố
thị trường"*.

**Hệ quả cho việc encode causality:** việc cần làm không phải *dạy* model cơ chế từ đầu, mà buộc
nó dùng cơ chế nó đã có — train ở horizon dài hơn, hoặc phạt sự phụ thuộc vào giá trễ. Rẻ hơn hẳn so
với đổi kiến trúc.

**Cái giá đã đo được:** model bỏ hẳn feature giá quan sát kém 8% MAE (19.660đ vs 18.208đ) nhưng
hiệu ứng cao điểm bật từ +2,4% lên +13,4%, khớp thực tế. Đó là đánh đổi độ chính xác lấy khả
năng trả lời what-if — quyết định thuộc về team, không phải nhóm thực tập.

---

# PHẦN IV — MỞ RỘNG

## 12. Acceptance model (Tầng 2)

> ⏸️ Trạng thái: dừng ở v1 theo chỉ đạo mentor (*"treat nó như một side objective"*). Chờ dữ liệu bổ sung.

### 12.1 Ràng buộc gốc

Dữ liệu không có nhãn accept/reject — `booking_or_completion_outcomes_generated = False`, 0/251
cột chứa outcome. Không có `customer_id` nên cũng không làm được personalized model.

### 12.2 Tám hướng đã thử và loại trừ

Đây là phần có giá trị nhất của nhánh này — mỗi hướng bị loại đều có bằng chứng số, không phải
suy đoán:

| Hướng | Vì sao loại | Bằng chứng |
|---|---|---|
| Supervised từ nhãn thật | Không có nhãn | 0/251 cột |
| Unsupervised | Acceptance không tồn tại dạng ẩn | Quét toàn bộ 72 cột |
| **Rule-based weak labeling** | **Vòng tròn logic** | AUC **1,0000** → bỏ `price_gap` còn **0,4995** |
| Proxy label từ cột khác | Không cột nào phù hợp | Rà hết 72 cột |
| PU learning | Cần ít nhất vài ca dương | Quan sát được **0** ca |
| Ước lượng cầu trực tiếp | Nội sinh | Hồi quy thô cho hệ số **+0,40** — sai dấu |
| Biến công cụ (IV) | IV không hợp lệ | Bỏ biến giờ ⇒ hệ số lật từ −0,95 sang **+0,36** |
| Chỉ số Lerner | Cho `ε` vô lý | −33 đến −2,5 |
| Đảo ngược quy tắc định giá | Surge sinh cơ học | Công thức `m = f(imbalance)` |
| SMM / indirect inference | Mô-men không chứa thông tin | Placebo test: tương quan 0,004 |

Hàng rule-based là bài học đắt nhất: AUC 1,0 trông như thành công lớn, thực chất là model đọc
lại chính cái luật đã dùng để gán nhãn.

### 12.3 Hướng đã chọn — mô hình cấu trúc

Không train. Dùng lý thuyết lựa chọn rời rạc (McFadden):

```python
def P_accept(gia_minh, gia_doithu, eps, P0=0.5, dich_WTP=0.0):
    b = eps / (1 - P0)
    a = np.log(P0 / (1 - P0))
    z = a + b * (np.log(gia_minh / gia_doithu) - np.log1p(dich_WTP))
    return 1 / (1 + np.exp(-z))
```

**Bốn tham số — chỉ 2 là giả định:**

| Tham số | Nguồn | Giá trị | Kiểm chứng được? |
|---|---|---|---|
| `gia_doithu` | 📊 Tầng 1 | `p̂` | ✅ MAE ~18.000đ |
| `dich_WTP` | 📊 Đo từ dữ liệu | mưa +4,61% · giờ ±25% | ✅ Từ hệ số nhân cân bằng |
| `P₀` | ⚠️ Quy ước | 0,5 | ❌ Cần hỏi mentor |
| `ε` | ⚠️ **Giả định** | −2,0 (dải −1,2 → −3,0) | 🟡 Neo bằng literature + MNL |

### 12.4 Cách trình bày — dùng thay đổi tương đối

Phát hiện phương pháp luận đáng ghi: cách báo cáo quyết định độ vững của kết luận.

| Cách báo cáo | Dao động khi `P₀` chạy 0,30 → 0,70 |
|---|---:|
| Mức tuyệt đối | 30,7 điểm ❌ |
| Thay đổi tuyệt đối | 9,3 điểm ⚠️ |
| **Thay đổi tương đối** | **3,1 điểm** ✅ |

### 12.5 Kết quả

| Đổi giá so với đối thủ | Chấp nhận (tương đối) |
|---|---:|
| +5% / **+10%** / +20% | −10% / **−19%** / −35% |
| −5% / −10% / −20% | +10% / +21% / +42% |

Ba kết luận vững trên toàn dải elasticity (3/3):

1. Giá cao hơn đối thủ → chấp nhận giảm
2. Mưa → chấp nhận tăng (+4,49 điểm %, ≈ tăng giá được 4,6% mà không mất khách)
3. **Giờ tác động mạnh hơn thời tiết ~8,3 lần** ⇒ chọn một tín hiệu định giá động thì chọn giờ

### 12.6 Kiểm chứng chéo bằng MNL

MNL 3 lựa chọn `{không đi, mình, đối thủ}` ràng buộc cả hai elasticity vào một `β`:

$$\varepsilon_{\text{firm}} = -\beta(1-s_1), \qquad
\varepsilon_{\text{market}} = -\beta s_0, \qquad
s_0 = \frac{1-m}{R-m}$$

| Kết quả | |
|---|---|
| `s₀` (khách không đi) | **14,3%** — trong khoảng hợp lý [5%; 30%] |
| `β` | 3,500 |
| MNL vs logit nhị phân | Khớp trong **3 điểm %** |

⚠️ Tổ hợp `ε_firm = −1,2` + `ε_market = −0,7` cho `s₀ = 41,2%` — không nhất quán, không được dùng
đồng thời. Đây là loại mâu thuẫn mà logit nhị phân không phát hiện được.

### 12.7 Ngoài phạm vi tài liệu này

Repo còn một tầng quyết định giá đã dựng ở tuần 3 — tối ưu giá nên báo dựa trên phân phối dự
đoán và chi phí biên. Tầng đó không nằm trong tài liệu này vì hai lý do: mentor không yêu cầu,
và chiều của khuyến nghị phụ thuộc hoàn toàn vào chi phí biên — một tham số dự án không có.

Nội dung vẫn còn nguyên trong repo nếu cần tra:

| Nơi | Nội dung |
|---|---|
| `model/acceptance/KIEN_TRUC_CHOT.md` | Hàm mục tiêu, ngưỡng đảo chiều, giá trị của việc tích phân trên phân phối |
| `model/acceptance/07_chiphi_bien_va_uncertainty.ipynb` | Cài đặt và backtest |
| `model/acceptance/bang_tra_cuu_gia.csv` | Bảng giá nên báo theo giờ × thời tiết |

---


---

## 13. GAM và các thử nghiệm kiến trúc khác

### 13.1 GAM — bổ sung theo gợi ý mentor

Đo trên tập test độ trễ 5 phút, 216.090 chuyến, so GAM với HistGB ở từng nhánh:

| Nhánh | GBM | GAM | GAM tệ hơn |
|---|---:|---:|---:|
| Giá cơ bản | 14,58% | 14,78% | **+1,3%** tương đối — gần như ngang |
| **Hệ số nhân** | 1,42% | 1,94% | **+37,0%** tương đối |

**Vì sao chênh lệch lớn thế:** cho cây học lại phần dư của GAM → R² 0,562 ở hệ số nhân vs
**0,018** ở giá cơ bản.

⇒ Giá cơ bản là quan hệ cộng dồn thuần (GAM đủ sức); hệ số nhân có tương tác mà GAM không
bắt được.

### 13.2 Transformed feature space

Theo gợi ý mentor: thêm tensor `te()` cho 3 cặp tương tác mạnh nhất → đóng được 52% khoảng cách
(+30,7% → +14,7%).

### 13.3 Giá trị riêng của GAM

Không phải để thay model, mà để kiểm định thống kê: p-value tìm ra 4 feature không có ý nghĩa
thống kê → bỏ khỏi feature contract.

Đáng chú ý: `weather_main` không ảnh hưởng giá cơ bản nhưng rất mạnh với hệ số nhân — xác nhận
độc lập cho kết luận §3.3 bằng một phương pháp hoàn toàn khác.

### 13.4 Transformer

> Trả lời câu hỏi *"đã test thử neural network transformer chưa?"*

**Test rẻ trước** (LightGBM, 400.000 mẫu train, đánh giá trên 314.368 chuyến test tháng 3):

| Bộ feature | MAE | MAPE |
|---|---:|---:|
| A. Chỉ feature cơ bản (không lịch sử giá) | 19.258đ | 15,34% |
| **B. + nhóm tổng hợp** *(mốc)* | **18.407đ** | 14,81% |
| C. + chuỗi 32 báo giá thô *(bỏ nhóm tổng hợp)* | 18.397đ | 14,81% |
| D. + cả hai | 18.402đ | 14,81% |

**Đọc bảng:**

- Lịch sử giá có giá trị thật — bỏ đi tệ hơn 4,4%
- Nhưng chuỗi thô và nhóm tổng hợp cho kết quả y hệt (−0,1%)
- Nhét cả hai vào không giúp gì (−0,0%)

⇒ Nhóm tổng hợp `mean/std/slope` + giá quan sát gần nhất đã là thống kê đủ cho chuỗi. Transformer
đọc chuỗi sẽ không có gì mới để đọc.

**Kiến trúc đã dựng** (`transformer/kaggle_transformer.ipynb`, ~90.000 tham số):

```
CHUỖI K×7 → Linear → + positional → TransformerEncoder ×2, 4 head → mean pool
                                                                        │
TĨNH (embedding danh mục + 12 feature số) ──────────────────────────────┤
                                                                        ▼
                                                            MLP → 2 đầu ra
                                                    log(giá cơ bản) · hệ số nhân
```

Dự đoán hai đầu ra rồi nhân lại giống kiến trúc Hybrid, train riêng từng tháng (lịch sử giá reset
theo tháng, gộp lại là rò rỉ). Notebook dựng chuỗi bằng `searchsorted` và có `assert` chống rò rỉ:
chỉ lấy báo giá có `ts <= cutoff` — kiểm tra chạy qua, 99,96% mẫu đủ 32 báo giá.

**Kết quả chạy đầy đủ trên Kaggle** (`transformer/pricing-tranfomer.ipynb`, Tesla T4):

| Tháng | MAE | MAPE | R² | n |
|---|---:|---:|---:|---:|
| 1 | 17.846đ | 14,87% | 0,7341 | 315.360 |
| 2 | 17.868đ | 14,76% | 0,7351 | 234.632 |
| 3 | 18.275đ | 14,76% | 0,7287 | 314.368 |
| **Gộp** | **18.008đ** | **14,80%** | **0,7326** | **864.360** |

**So với Hybrid — hoà, không phải thắng:**

| | Hybrid | Transformer | Chênh |
|---|---:|---:|---|
| MAE | 18.048đ | **18.008đ** | −0,22% *(transformer tốt hơn)* |
| MAPE | **14,74%** | 14,80% | +0,06 điểm *(transformer tệ hơn)* |
| Tham số | — | 90.792 | |
| Thời gian train | ~9 ph (CPU) | ~35 ph (GPU T4) | |

⚠️ Notebook tự kết luận *"Transformer THẮNG Hybrid 0,22%"* vì chỉ so MAE. Đọc đủ hai metric thì
đây là hoà: transformer tốt hơn ở sai số tuyệt đối, tệ hơn ở sai số tương đối. MAE ưu ái chuyến
đắt, MAPE ưu ái chuyến rẻ — hai metric đi ngược nhau nghĩa là hai model chỉ khác nhau ở cách phân bổ
sai số, không phải một cái giỏi hơn.

Chênh lệch 0,22% cũng nằm gọn trong dải 1,9% giữa 4 thuật toán cây (§7.2).

**Theo band giá** — điểm yếu giống hệt Hybrid:

| Band | n | MAE | MAPE |
|---|---:|---:|---:|
| <50k | 10.441 | 6.054đ | 13,84% |
| 50–100k | 259.587 | 11.785đ | 14,34% |
| 100–150k | 412.662 | 18.288đ | 15,04% |
| 150–200k | 152.123 | 25.421đ | 15,01% |
| 200–300k | 28.261 | 33.496đ | 14,70% |
| **>300k** | 1.286 | 64.283đ | **18,06%** |

Band `>300k` vẫn tệ nhất (18,06%, so với 18,55% của Hybrid) — cùng một chỗ hỏng, kiến trúc khác
hẳn cũng không sửa được.

**Kết luận:** transformer đọc thẳng chuỗi 32 báo giá không moi thêm được thông tin nào so với
ba con số `mean/std/slope`. Đây đúng là điều test rẻ đã dự đoán. Kết quả này củng cố §7.5: nút
thắt là dữ liệu, không phải sức chứa của model.

> **Không đưa vào pipeline.** Đổi lấy 0,22% MAE (và mất 0,06 điểm MAPE) bằng một model cần GPU, gấp
> 4 lần thời gian train, và phải lưu thêm thống kê chuẩn hoá để phục vụ — không đáng.

### 13.5 Bảng tổng hợp các hướng đã thử

Ghi rõ để sau này không ai phải thử lại:

| Đã thử | Kết quả |
|---|---|
| 4 thuật toán (XGBoost / LightGBM / HistGB / GAM) | Chênh nhau 1,9% |
| Neural network multi-task (MLP) | Thua GBM |
| Optuna 40 trial × 3 tháng | +2 VND |
| Ném hết 49 cột + feature weights | +6 VND |
| Transformer đọc chuỗi (test rẻ) | Không hơn nhóm tổng hợp |
| **Transformer chạy đầy đủ** (90.792 tham số, GPU T4) | **MAE −0,22% · MAPE +0,06 điểm — hoà** |
| 5 cách hiệu chỉnh khoảng × 7 nhóm | Tốt nhất −0,43% |
| GBM dự đoán độ khó từng chuyến | Tương quan hạng 0,053 |

Tất cả đều chỉ về cùng một kết luận: đã chạm trần dữ liệu (§7.5).

---

## 14. Đối chiếu Boston

Bộ dữ liệu Uber/Lyft Boston làm ở tuần 1, trước khi mentor gửi dữ liệu TP.HCM. Giữ lại để đối chiếu
— nhiều kết luận tuần 2–3 có so với Boston (biên độ surge, hệ số co giãn).

| Thư mục | Nội dung |
|---|---|
| `boston_data/analysis/` | 11 notebook EDA |
| `boston_data/model/` | 5 notebook model |
| `boston_data/docs/` | 9 tài liệu |

🖼️ `F2_boston_vs_hcm.png` · `00c_key_feature_hcm_vs_boston.ipynb`

> ⚠️ Hai bộ dữ liệu khác nhau về thị trường, đơn vị tiền tệ và cơ chế surge. Đối chiếu chỉ dùng để
> **kiểm tra tính hợp lý về bậc độ lớn**, không dùng để suy diễn kết luận chéo.

---

# PHẦN V — VẬN HÀNH

## 15. Tái lập

### 15.1 Môi trường

| | |
|---|---|
| Python | 3.11.8 |
| Thư viện chính | pandas, numpy, scikit-learn, lightgbm, xgboost, pygam, matplotlib, scipy |
| Cài đặt | `pip install -r requirements.txt` |
| Chi tiết | `SETUP.md` |

### 15.2 Thứ tự chạy chuẩn

```
1. model/00_chuan_bi_du_lieu          ~2,5 ph   → data/hcm_train_ready.parquet
2. model/train/01–03                  ~9 ph     → HistGB/, LightGBM/, XGBoost/
3. model/train/04–05                  ~13 ph    → GAM/
4. model/train/06                               → QuantileLGBM/
5. model/train/07_sinh_du_lieu_UQ               → evaluation/uq_pred_*.parquet
6. model/evaluation/01–09                       → đánh giá + chẩn đoán
7. model/uncertainty/00–06                      → khoảng bất định
8. model/acceptance/00_TONG_HOP       ~1 ph     → Tầng 2 (độc lập)
9. tuan_4/00–06                                 → tổng hợp tuần 4
```

**Phụ thuộc quan trọng:** bước 8 chỉ cần `hcm_train_ready.parquet`. Các notebook `tuan_4/` cần
`evaluation/uq_pred_{calibration,test}.parquet` từ bước 5.

### 15.3 Dung lượng và thời gian

| Hạng mục | Dung lượng | Sinh lại mất |
|---|---:|---|
| `data/synthetic_data/` | 459,5 MB | **Không sinh lại được** — dữ liệu gốc |
| `data/hcm_train_ready.parquet` | 368,6 MB | ~2,5 ph |
| `evaluation/*.parquet` | ~438 MB | ~25 ph |
| Model `.joblib` | 202 MB | ~21 ph |
| `docs/hinh_anh/` | 17,6 MB | Theo notebook sinh ra |

### 15.4 Demo trình bày

`demo/index.html` — mở bằng cách nháy đúp, không cần cài gì và không cần server. Demo chạy tập test
qua model và mô phỏng từng chuyến trên bản đồ: giá dự đoán, khoảng tin cậy, rồi giá thật khi xe tới
nơi.

Demo đọc `demo/du_lieu/chuyen.json` (900 chuyến đại diện + 327 chuyến >300k, lấy từ tập test) và
`cauhinh.json` (tham số `q` cho 3 mức tin cậy × 6 band, hiệu chỉnh trên tập calibration).
Phải sinh lại hai file này mỗi khi model được train lại, nếu không demo sẽ hiển thị dự đoán cũ.

Kịch bản trình bày 4 bước và danh sách hạn chế cần nói trước nằm ở `demo/README.md` và
`THANH_PHAM_4_TUAN.md`.

## 16. Kiểm thử và biên bản chạy lại

Ngày 10/08/2026 đã chạy lại toàn bộ 59 notebook để kiểm tính tái lập. Kết quả:

| | |
|---|---|
| Notebook chạy lại thành công | 59/59 |
| Hình được vẽ lại | 120/121 |
| Số liệu khớp báo cáo tuần 3 | ✅ (lệch ở hàng thập phân) |
| Artifact không sinh lại được | 7 → **đã vá** |

**Lỗ hổng đã vá:** 7 artifact không có notebook nào sinh ra chúng. Đã bổ sung
`train/07_sinh_du_lieu_UQ.ipynb`, đối chiếu với bản cũ trước khi ghi đè để đảm bảo công thức dựng
lại đúng.

Chi tiết: `BIEN_BAN_CHAY_LAI.md`.

> **Nguyên tắc rút ra:** mọi artifact phải có notebook sinh ra nó. Artifact mồ côi là nợ kỹ thuật —
> khi cần sinh lại thì không ai biết công thức.

## 17. Quy ước repo

| Quy ước | Ví dụ |
|---|---|
| Số thứ tự = thứ tự chạy | `01_train_gia_co_ban` → `02_train_he_so_nhan` |
| `00_` = điểm vào / tổng quan | `00_TONG_QUAN`, `00_chuan_bi_du_lieu` |
| `00_TRINH_BAY_` = bản rút gọn để trình bày | `00_TRINH_BAY_model_gia` |
| `90+` = tiện ích, không thuộc luồng chính | `90_sinh_hinh_bao_cao_tuan2` |
| `_archive/` = bản cũ, không còn dùng | |
| **Tiền tố hình = notebook sinh ra nó** | `CP*` ← `14_ceteris_paribus` |

**Tiền tố hình đã dùng** (không được trùng): `A` `AC` `AT` `B` `BG` `BM` `BT` `CD` `CG` `CP` `CQ`
`CT` `D` `E` `F` `GA` `KT` `LIT` `M` `MD` `MG` `MNL` `MT` `O` `PL` `PM` `PU` `QD` `QR` `SS` `T` `TC`
`TF` `TH` `TK` `TQ` `TT` `U` `UA` `UQ` `V` `VQ`.

Mỗi thư mục notebook có `README.md` liệt kê từng file — sinh tự động từ tiêu đề trong notebook nên
không lệch.

## 18. Rủi ro, giới hạn và việc còn nợ

### 18.1 Ba giới hạn thật

| # | Giới hạn | Hệ quả |
|---|---|---|
| **1** | **Dữ liệu synthetic** | Mọi kết luận mô tả simulator, không phải thị trường thật |
| **2** | Không có nhãn accept/reject | Tầng 2 là **mô phỏng dưới giả định**, không phải model học |
| **3** | Model đã chạm sàn nhiễu dữ liệu | Không cải thiện được độ chính xác bằng dữ liệu hiện có |

⚠️ Số trích từ literature (Cohen 2016) ghi từ trí nhớ, chưa đối chiếu bản gốc.

### 18.2 Cách phát biểu đúng khi báo cáo

| Điểm | Phát biểu đúng |
|---|---|
| Tầng 2 không phải ML | *"Model cấu trúc từ lý thuyết lựa chọn rời rạc, không train"* |
| Kết quả phụ thuộc giả định | *"Dưới giả định ε ∈ [−1,2; −3,0]…"* |
| `P₀` chưa kiểm chứng | *"Con số tuyệt đối phụ thuộc giả định P₀ = 0,5"* |
| Model tĩnh | *"Chưa tính phản ứng của đối thủ"* |
| Dữ liệu synthetic | *"Mô tả hành vi bộ sinh dữ liệu, không phải thị trường TP.HCM"* |

### 18.3 Việc nên làm tiếp, theo thứ tự

| Hướng | Chi phí | Vì sao |
|---|---|---|
| **Bật Mondrian theo quãng đường** | vài giờ | Sửa lệch coverage 12,6 → 2,5 điểm. Không cần thêm thông tin, không train lại |
| **Encode causality** | vừa | Không phải để tăng độ chính xác, mà để **trả lời được what-if** (§11.3) |
| ~~Thêm feature thị trường~~ | — | Đổ vào tầng đã đạt MAPE 1,42%. Giá cuối gần như không đổi |
| ~~Tinh chỉnh siêu tham số~~ | — | Optuna 40 trial → +2 VND |

### 18.4 Câu hỏi chặn tiến độ — gửi mentor

| # | Câu hỏi | Mở khoá | Ưu tiên |
|---|---|---|---|
| **1** | **Dữ liệu thật có mức nhiễu báo giá như bộ synthetic không?** Các chuyến giống hệt nhau vẫn lệch giá cơ bản ~18,6% | Toàn bộ kế hoạch improve model | 🔴 |
| **2** | Team ưu tiên **độ chính xác** hay **khả năng giải thích**? | Hướng đi kỹ thuật (§11.3) | 🔴 |
| **3** | **% khách xem giá rồi không đặt (`s₀`)** + thị phần? | Chốt `β` ⇒ hết phải giả định elasticity | 🔴 |
| **4** | *"Encode causality"* — ràng buộc đơn điệu, feature biến đổi, hay mô hình cấu trúc? | Việc còn nợ duy nhất | 🟠 |
| **5** | Ngày lễ — dữ liệu thật có hiệu ứng này không? | Phần ngày lễ của cấu thành giá | 🟠 |
| **6** | Surge có **ngưỡng nhảy bậc** không? | Mở khoá RD ⇒ `ε` thật từ dữ liệu lịch sử | 🟠 |

> **Nếu chỉ hỏi được 2 câu: hỏi câu 1 và câu 2.**
>
> Câu 1 đứng đầu vì §7.5 cho thấy MAPE 14,65% đã gần sàn của bộ dữ liệu. Nếu dữ liệu thật cũng nhiễu
> như vậy thì mọi nỗ lực improve model là vô ích và team nên chuyển toàn bộ công sức sang khả năng
> giải thích. Nếu dữ liệu thật sạch hơn thì toàn bộ kết luận này cần đo lại.

### 18.5 Điều kiện để nâng cấp kiến trúc

Kiến trúc hiện tại là tối ưu với dữ liệu đang có. Chỉ nâng cấp khi có thêm dữ liệu:

| Nếu có | Thì đổi thành | Lợi ích |
|---|---|---|
| `s₀` + thị phần | MNL hiệu chỉnh bằng số thật | Chốt `β` ⇒ hết giả định elasticity |
| Ngưỡng nhảy bậc surge | Regression Discontinuity | `ε` thật, không cần thí nghiệm |
| `outcome` cuốc | Tầng 2 → supervised thật | `ε` ước lượng thay vì giả định |
| Thí nghiệm giá ngẫu nhiên | Elasticity nhân quả sạch | Chuẩn vàng |
| Nghi ngờ giả định IIA | MNL → Nested Logit | Xử lý thay thế không đối xứng |

---

# PHỤ LỤC

## A. Bản đồ notebook

| Thư mục | Số notebook | Nội dung |
|---|---:|---|
| `analysis/` | 22 | Cấu phần (i) — yếu tố ảnh hưởng giá |
| `model/train/` | 7 | Huấn luyện |
| `model/evaluation/` | 10 | Đánh giá + chẩn đoán |
| `model/uncertainty/` | 7 | Cấu phần (iii) |
| `model/acceptance/` | 11 | Tầng 2–3 |
| `tuan_4/` | 7 | Tổng hợp tuần 4 |
| `transformer/` | 2 | Thử nghiệm |
| `boston_data/` | 16 | Tuần 1, đối chiếu |

**Notebook nên đọc trước nếu tiếp quản:**

| Thứ tự | Notebook | Vì sao |
|---|---|---|
| 1 | `tuan_4/00_TONG_HOP` | Bức tranh toàn cục, tự tính lại mọi số |
| 2 | `model/99_TONG_QUAN_TOAN_DU_AN` | Chạy 1 phút ra hết số chính |
| 3 | `model/evaluation/09_chan_doan_model` | Model sai ở đâu |
| 4 | `model/acceptance/KIEN_TRUC_CHOT.md` | Kiến trúc tầng 2–3 |

## B. Chỉ mục hình theo tiền tố

| Tiền tố | Notebook sinh ra | Chủ đề |
|---|---|---|
| `CD` | `evaluation/09` | Chẩn đoán model |
| `CG` | `tuan_4/04` | Cấu thành giá |
| `CP` | `analysis/14` | Ceteris paribus |
| `CT` | `evaluation/10` | Sai số chi tiết |
| `GA` | `evaluation/08` | GAM |
| `KT` | `model/99` | Kiến trúc tầng |
| `MD` | `uncertainty/01` | Mondrian |
| `PU` | `tuan_4/03` | Phản ứng giá / causality |
| `QD` | `tuan_4/02` | Quyết định improve hay giảm uncertainty |
| `TH` | `uncertainty/06` | Thu hẹp khoảng |
| `TK` | `tuan_4/00` | Tổng kết tuần 4 |
| `TT` | `uncertainty/05`, `tuan_4/01` | Theo thời gian |
| `VQ` | `uncertainty/00` | Trực quan UQ |

## C. Nhật ký đính chính

> Phần này ghi lại các kết luận đã phải sửa. Giá trị của nó: người sau biết chỗ nào từng trơn
> trượt, và người đọc thấy được kết luận nào đã qua kiểm chứng nhiều vòng.

### C.1 "CQR có coverage điều kiện tốt nhất"

| | |
|---|---|
| **Kết luận sai** | CQR tốt nhất về coverage điều kiện |
| **Nguyên nhân** | Chỉ so với QR thô, chưa so với conformal chuẩn hoá và Mondrian |
| **Kết luận đúng** | Không phương pháp nào thắng tuyệt đối trên cả 3 chiều. Mondrian tốt hơn CQR cả về công bằng (0,81 vs 1,09) lẫn độ rộng |
| **Bài học** | So sánh phải đủ bộ đối thủ trước khi tuyên bố "tốt nhất" |

### C.2 "Model bám giá quan sát chứ không hiểu cơ chế"

| | |
|---|---|
| **Kết luận sai** | Phát biểu quá nặng, dựa trên partial dependence ở lag 5′ (+0,93%) |
| **Nguyên nhân** | Chưa tách bạch ba câu hỏi A/B/C (§11.3); chưa thử rút feature giá trễ ra |
| **Kết luận đúng** | Model **hiểu cơ chế**, nhưng ưu tiên đường tắt khi đường tắt còn dùng được. Ở lag 30′ nó tự bù 94% |
| **Bài học** | Một phép đo trả lời đúng một câu. Đổi câu hỏi thì phải đổi phép đo |

### C.3 Đơn vị `quote_duration`

| | |
|---|---|
| **Kết luận sai** | Trần thông tin của giá cơ bản = 14,84%, phủ 72% dữ liệu |
| **Nguyên nhân** | `quote_duration` tính bằng **giây** nhưng bị dùng như phút → ô khống chế thành 5 **giây** thay vì 5 **phút** |
| **Phát hiện nhờ** | Nhãn trên hình in ra "1125–1130 phút" |
| **Kết luận đúng** | Trần = **14,98%**, phủ **99%** dữ liệu. Kết luận không đổi mà còn chắc hơn |
| **Bài học** | Vẽ hình ra và **đọc nhãn** — một con số vô lý trên nhãn lộ ra lỗi mà bảng số giấu kín |

### C.4 GAM so với cây ở §13.1

Bản trước ghi GAM tệ hơn **+0,5%** ở nhánh giá cơ bản và **+30,5%** ở nhánh hệ số nhân.
Tính lại trực tiếp từ `pred_gam.parquet` và `pred_gia_co_ban.parquet` trên tập test độ trễ
5 phút cho **+1,3%** và **+37,0%**. Hai con số cũ không ghi rõ tập đo nên không tái lập
được; bản hiện tại ghi rõ tập và số lượng chuyến.

Kết luận định tính **không đổi**: giá cơ bản là quan hệ cộng dồn thuần nên GAM theo kịp,
còn hệ số nhân có tương tác mà GAM không bắt được.

### C.5 "Phải improve model"

| | |
|---|---|
| **Kết luận chưa đủ** | Đường giảm uncertainty đã cạn ⇒ phải improve model |
| **Bổ sung** | Đường improve model **cũng cạn** trên bộ dữ liệu này (§7.5) |
| **Kết luận đúng** | Ràng buộc thật sự là **dữ liệu**, không phải model |
| **Bài học** | Loại trừ được một đường không có nghĩa đường còn lại đi được |

---

*Tài liệu này tái lập được hoàn toàn. Mọi con số đều có notebook sinh ra. Chỗ nào là giả định đều
được đánh dấu.*
