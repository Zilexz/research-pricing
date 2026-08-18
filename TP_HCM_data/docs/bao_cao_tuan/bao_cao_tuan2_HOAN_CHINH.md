# Báo cáo Tuần 2 (bản hoàn chỉnh) — Phân tích quan hệ Feature & Build Model trên bộ TP.HCM

**Dự án:** Competitor Fare Forecasting (GSM) · **Ngày:** 31/07/2026
**Dữ liệu:** `synthetic_quote_context_sandbox` (TP.HCM, synthetic) — 6.897.051 dòng × 70 cột, 3 tháng (01–03/2026), 3 khu vực, 2 dịch vụ

**Phân công thực hiện:**

| Phần | Nội dung | Người thực hiện |
|---|---|---|
| **Mục 1** | Phân tích quan hệ key feature ↔ giá cơ bản / hệ số nhân / giá cuối | Nguyễn Đức Hiếu |
| **Mục 2** | Build model — hướng **Hybrid** (giá cơ bản × hệ số nhân) | Nguyễn Đức Hiếu |
| **Mục 3** | Build model — hướng **point-price trực tiếp** (lineage P5→P12, CatBoost) | Thành viên phụ trách nhánh point-price |
| **Mục 4–6** | Đối chiếu 2 hướng, tổng hợp giới hạn & kết luận chung | Cả nhóm |

---

**Motivation.** Tuần 1 trên bộ Boston kết luận **giờ và thời tiết gần như không ảnh hưởng giá**
(η < 0,01). Mentor xác nhận kết luận này hợp lý với thực tế Mỹ nhưng **dự đoán bộ dữ liệu Việt Nam
sẽ khác**: giờ cao điểm và trời mưa sẽ ảnh hưởng giá nhiều. Tuần 2 kiểm chứng giả thuyết này trên
bộ TP.HCM, đồng thời xây dựng model dự đoán giá theo **hai hướng kiến trúc độc lập** để đối chiếu.

**Kết quả cốt lõi.**
1. **Mentor dự đoán đúng.** Giờ ảnh hưởng lên giá cuối ở TP.HCM **mạnh gấp 74 lần** Boston
   (η 0,296 vs 0,004); mưa làm giá tăng **+7,3%** (Boston: **0,0%**).
2. **Chỉ ra cơ chế:** giờ/mưa **không** đổi giá cơ bản mà đổi **hệ số nhân**, qua chuỗi
   *cầu → mất cân bằng cung–cầu → surge → giá cuối*, kiểm chứng từng mắt xích.
3. **Hai hướng model độc lập hội tụ về cùng một mức sai số** (~18.000 VNĐ MAE trên giá cuối) dù
   khác hẳn nhau về kiến trúc, thuật toán, feature contract và giao thức chia dữ liệu.
4. **Xác định được bottleneck chung:** nút thắt nằm ở phần **giá cơ bản** — cụ thể là thiếu thông
   tin trạng thái định giá ẩn (hidden base-pricing state), không phải thiếu model tốt hơn.
5. **(Bổ sung theo góp ý mentor)** Trực quan hóa uncertainty theo thời gian cho thấy model giá chỉ
   tái tạo được **70,3%** độ dao động thật, trong khi model hệ số nhân đạt **97,1%** — bất đối xứng
   **7,1×**, khớp với con số 7,39× đo độc lập bằng phương pháp khác ở hướng B.

---

## 0. Bối cảnh & phạm vi tuần 2

| Cấu phần đề bài | Nội dung | Trạng thái |
|---|---|---|
| **i** | Study relation — key feature ↔ giá & hệ số nhân | ✅ Hoàn thành (mục 1) |
| **ii** | Build model dự đoán giá + hệ số nhân từ quan sát trễ | ✅ Hoàn thành 2 hướng (mục 2, 3) |
| iii | Uncertainty quantification — khoảng dự đoán | ⏳ Chưa bắt đầu |

**So với tuần 1:** bộ TP.HCM có **2 nhóm trường mà Boston thiếu** — đây là lý do kết quả khác hẳn:

| Nhóm trường mới | Cột | Vai trò |
|---|---|---|
| **Thời lượng chuyến** | `quote_duration` (ETA, giây) | Đo được tắc đường → giải thích phần giá theo phút |
| **Cung–cầu thời gian thực** | `pricing_demand_index_5m_lag`, `pricing_supply_index_5m_lag`, `pricing_market_imbalance_5m_lag` | Mắt xích trung gian để giờ/thời tiết tác động lên surge |

### 0.1. Bài toán — nowcasting với quan sát trễ

Mỗi dòng = **1 lần báo giá**. Model phải dự đoán giá **hiện tại** của đối thủ, chỉ được dùng thông
tin **cũ hơn τ phút** (τ ∈ {5, 10, 15, 30}):

| Loại thông tin | Cột | Được dùng? |
|---|---|---|
| Giá/hệ số nhân **hiện tại** của đối thủ | `target_shown_price`, `target_shown_multiplier` | ❌ Đây là đáp án cần dự đoán |
| Giá đối thủ quan sát **gần nhất** (cùng tuyến + loại xe) | `latest_observed_price`, `latest_observed_multiplier` | ✅ |
| Lịch sử giá 60 phút | `history_60m_price_mean/std/slope` | ✅ |
| Thuộc tính chuyến hiện tại | `quote_distance`, `quote_duration` | ✅ (biết khi khách yêu cầu) |
| Cung–cầu (trễ 5 phút) | `pricing_*_5m_lag` | ✅ |

Đã kiểm tra chống rò rỉ: `observation_cutoff_timestamp ≤ target_timestamp` (đúng 100%),
`actual_observation_age_minutes ≥ 0` (đúng 100%). Độ trễ thực tế trung bình 16,3 phút.

> ⚠️ **Bắt buộc train riêng từng tháng** (theo tài liệu dataset): lịch sử giá đối thủ **reset theo
> tháng**, gộp nhiều tháng sẽ gây rò rỉ. Cả 2 hướng model đều tuân thủ ràng buộc này.

---

## 1. Phân tích mối quan hệ Key Feature ↔ Giá & Hệ số nhân

### 1.1. Khung sườn — mọi phân tích đều xoay quanh công thức này

```
Giá cuối (khách trả) = Giá cơ bản × Hệ số nhân (surge)
```

Đây không phải chi tiết kỹ thuật — nó quyết định cách đọc **đúng hay sai** mọi kết luận về feature.
Phải luôn phân biệt rõ 3 đối tượng khi nói "yếu tố X ảnh hưởng giá":

- Ảnh hưởng đến **giá cuối** (con số khách nhìn thấy)
- Ảnh hưởng đến **giá cơ bản** (phần do quãng đường/thời gian quyết định, trước khi nhân surge)
- Ảnh hưởng đến **hệ số nhân** (phần điều chỉnh theo cung–cầu)

Một yếu tố hoàn toàn có thể **không ảnh hưởng giá cơ bản** nhưng **ảnh hưởng cực mạnh hệ số nhân**
— và vì giá cuối là **tích** của 2 cái, nó vẫn ảnh hưởng mạnh đến giá cuối. Nhầm giữa 3 đối tượng
này là nguồn gốc phổ biến nhất của kết luận sai.

### 1.2. Bảng tổng hợp — yếu tố nào ảnh hưởng cái gì

| Yếu tố | → Giá cơ bản | → Hệ số nhân | Ghi chú |
|---|---|---|---|
| **Quãng đường** | 🔴 Rất mạnh | Yếu | Trục giá cơ sở, chiếm phần lớn importance |
| **Thời lượng đi / tắc đường** | 🔴 Mạnh — nhưng **tự nó ngẫu nhiên**, không dự đoán trước được | Vừa | Là ETA thật, có sẵn tại thời điểm báo giá |
| **Cung–cầu (demand/supply/imbalance)** | ~0 | 🔴 **Rất mạnh** | Nguồn chính của surge |
| **Giờ trong ngày** | Rất yếu | 🔴 **Cực mạnh** | Tác động **qua** cung–cầu, không trực tiếp lên giá cơ bản |
| **Vị trí/khu vực** | Yếu (sau kiểm soát quãng đường) | Vừa | Chỉ 3 khu, kết luận còn hạn chế |
| **Thời tiết** | Yếu | Yếu-vừa | Tác động qua tắc đường + cầu, yếu hơn giờ nhiều |
| **Thứ / cuối tuần** | Rất yếu | Yếu-vừa | |
| **Giá/hệ số quan sát gần nhất** | Yếu | 🔴 **Rất mạnh** | Vì hệ số nhân dai dẳng theo thời gian |

🔴 = yếu tố quan trọng nhất trong nhóm của nó.

### 1.3. Phát hiện cốt lõi — sự bất đối xứng giữa 2 thành phần của giá

{{IMG:O1_r2_giaithich.png|Hình O1 — Bộ dữ liệu hiện có giải thích được chỉ ~19% chênh lệch giá cơ bản, nhưng tới ~96,6% chênh lệch hệ số nhân.}}

| | Giá cơ bản | Hệ số nhân |
|---|---|---|
| Dữ liệu giải thích được | **~19%** | **~96,6%** |
| Bản chất | Có **nhiễu ngẫu nhiên per-quote** thật sự | Gần như **giá trị thị trường dùng chung** |
| Vì sao | Yếu tố chính (thời lượng/tắc đường) tự nó ngẫu nhiên | Sinh trực tiếp từ công thức cung–cầu có sẵn trong dữ liệu |

→ **"Nút thắt cổ chai" của độ chính xác dự đoán giá nằm hoàn toàn ở giá cơ bản, không phải hệ số
nhân.** Model hệ số nhân có thể gần như hoàn hảo, nhưng giá cuối vẫn bị giới hạn bởi phần nhiễu
không giải thích được trong giá cơ bản.

### 1.4. Chuỗi nhân quả đầy đủ

```
Giờ trong ngày / Mưa
        │
        ▼
Cầu tăng vọt giờ cao điểm  →  Mất cân bằng cung–cầu (demand − supply)
        │
        ▼
HỆ SỐ NHÂN tăng                          Thời lượng đi (tắc đường)
        │                                  │  ⚠️ CHỈ ~3,5% dự đoán được từ
        │                                  │  giờ/thời tiết — phần lớn NGẪU
        ▼                                  │  NHIÊN theo từng chuyến cụ thể
   GIÁ CUỐI = Giá cơ bản  ×  Hệ số nhân ◄──┘
        │
        ▼
   ~65% chênh lệch giá cuối (cùng tuyến/xe/km) VẪN KHÔNG GIẢI THÍCH ĐƯỢC
   → SÀN NHIỄU của dữ liệu, không phải thiếu feature
```

{{IMG:O2_phanra_phuongsai.png|Hình O2 — Phân rã phương sai log(giá cuối), cùng dải quãng đường: giá cơ bản đóng góp ~61%, hệ số nhân ~31%, phần chồng lấn (2·Cov) ~8%. Phương pháp: `Var[log Price] = Var[log Base] + Var[log Multiplier] + 2·Cov(...)`.}}

---

### 1.5. Key feature → GIÁ CƠ BẢN

**Giá cơ bản** = `target_shown_price ÷ target_shown_multiplier` — phần giá **trước khi nhân surge**,
phản ánh đúng cước phí theo quãng đường/thời gian/dịch vụ.

#### 1.5.1. Quãng đường & Thời lượng đi — 2 yếu tố áp đảo (~92% importance)

{{IMG:B1_B2_distance_duration_vs_baseprice.png|Hình B1-B2 — Giá cơ bản tăng đơn điệu, rõ ràng theo cả quãng đường và thời lượng đi. Đây là 2 yếu tố mạnh nhất, chiếm phần lớn khả năng giải thích của giá cơ bản.}}

- **Quãng đường (`quote_distance`):** tương quan Pearson với giá cơ bản **r ≈ 0,76** — mạnh nhất
  trong toàn bộ feature. Quan hệ tăng dần, **lồi (chậm dần)** — đúng cấu trúc cước "phí mở cửa +
  phí/km". Chiếm **~68% permutation importance** trong model dự đoán giá cơ bản.
- **Thời lượng đi (ETA, `quote_duration`):** tương quan **r ≈ 0,70** — gần bằng quãng đường. Cùng
  quãng đường, chuyến tắc hơn (thời lượng dài hơn) thì đắt hơn **thật sự**, do có thành phần cước
  tính theo phút di chuyển. Chiếm **~23% permutation importance**.
- Hai feature này tương quan với nhau **r ≈ 0,64** (hợp lý — đường dài thường mất nhiều thời gian
  hơn), nên tổng importance 68%+23%=91-92% không hoàn toàn "cộng dồn độc lập", nhưng cả hai đều
  đóng vai trò nhân quả thực sự (không chỉ là hiện tượng thống kê giả).
- **Ước lượng bằng hồi quy tuyến tính đơn giản** (chỉ 2 biến này):

  ```
  Giá cơ bản ≈ 21.645 VNĐ  +  8.361 VNĐ × (quãng đường, km)  +  1.108 VNĐ × (thời lượng, phút)
  ```

  Riêng công thức 2-biến này đã đạt **R² ≈ 0,66** trên toàn bộ dữ liệu — **gần như bằng đúng** mức
  trần R² của model đầy đủ tính năng dùng để dự đoán giá cơ bản. Đây là bằng chứng định lượng rõ
  ràng nhất: quãng đường + thời lượng gần như là toàn bộ tín hiệu hữu ích hiện có; các feature còn
  lại (giờ, thời tiết, vị trí, lịch sử giá...) gộp lại chỉ đóng góp thêm một phần rất nhỏ.

#### 1.5.2. Khai thác cột giờ để suy ra tắc đường — thời lượng đi trung bình theo khung giờ

Mục 1.5.1 cho thấy thời lượng đi là 1 trong 2 driver chính của giá cơ bản. Câu hỏi tiếp theo: bản
thân thời lượng đi bị chi phối bởi điều gì? Cột giờ trong ngày (`gio_vn`) có thể dùng để suy ra
mức độ tắc đường trung bình, tách biệt với chuyện dự đoán riêng lẻ từng chuyến.

Phương pháp: gộp toàn bộ chuyến đi theo **6 khung giờ sinh hoạt** (Đêm khuya, Sáng sớm, Cao điểm
sáng, Giữa ngày, Cao điểm chiều, Tối), tính thời lượng đi trung bình và tốc độ trung bình
(= quãng đường ÷ thời lượng) trong từng khung. Quãng đường trung bình gần như không đổi giữa các
khung (~6,5-6,6 km) — nên chênh lệch thời lượng/tốc độ phản ánh đúng mức độ tắc đường, không phải
do khác nhau về cự ly.

{{IMG:T1_thoiluong_tocdo_theo_gio.png|Hình T1 — Thời lượng đi và tốc độ trung bình theo từng giờ trong ngày (24 giờ). Giờ cao điểm sáng (6-9h) có tốc độ thấp nhất, thời lượng đi dài nhất — đúng quy luật tắc đường thực tế.}}

{{IMG:T2_6khunggio.png|Hình T2 — Gộp theo 6 khung giờ sinh hoạt: Cao điểm sáng và Giữa ngày có thời lượng đi TB cao nhất (~25-25,5 phút) và tốc độ TB thấp nhất (~17 km/h).}}

| Khung giờ | Quãng đường TB | Thời lượng đi TB | Tốc độ TB |
|---|---:|---:|---:|
| Đêm khuya (0-5h) | 6,55 km | 22,8 phút | 18,7 km/h |
| Sáng sớm (5-7h) | 6,55 km | 24,6 phút | 17,5 km/h |
| Cao điểm sáng (7-9h) | 6,54 km | 25,5 phút | 16,9 km/h |
| Giữa ngày (9-16h) | 6,56 km | 25,0 phút | 17,2 km/h |
| Cao điểm chiều (16-19h) | 6,57 km | 24,7 phút | 17,5 km/h |
| Tối (19-24h) | 6,56 km | 24,8 phút | 17,4 km/h |

Giờ **tắc nhất** trong ngày: **6h sáng** (tốc độ TB chỉ 16,7 km/h, thời lượng đi TB 25,8 phút).
Giờ **thông thoáng nhất**: **1h sáng** (18,8 km/h, 22,6 phút). Chênh lệch tốc độ giữa 2 giờ này:
**~12,3%**; chênh lệch thời lượng: **~14,2%**.

**Lưu ý quan trọng — không mâu thuẫn với mục 1.5.3/1.5.4:** quy luật tắc đường theo giờ là **có
thật** và đúng chiều (cao điểm chậm hơn), nhưng khi hồi quy `thời lượng đi ~ giờ + thứ + thời tiết`,
mô hình chỉ giải thích được **R² ≈ 3,5%** tổng phương sai của thời lượng đi. Nói cách khác: biết
giờ trong ngày giúp đoán *xu hướng trung bình* của tắc đường (biên độ ~12-14%), nhưng **không đủ
để đoán chính xác thời lượng của một chuyến cụ thể** — phần lớn biến thiên thời lượng vẫn là nhiễu
ngẫu nhiên riêng từng chuyến (tình trạng giao thông tức thời, lựa chọn tuyến của tài xế...). Đây
chính là lý do mục 1.5.4 xác nhận thời lượng đi "tự nó ngẫu nhiên" dù có quy luật theo giờ ở tầng
vĩ mô.

#### 1.5.3. Giờ & Thời tiết — gần như KHÔNG ảnh hưởng trực tiếp (khi đã kiểm soát quãng đường)

{{IMG:B3_B4_hour_weather_vs_baseprice.png|Hình B3-B4 — Cùng dải quãng đường 4-6km, giá cơ bản gần như phẳng theo giờ và theo thời tiết. Biên độ chỉ vài %, quá nhỏ để có ý nghĩa thực tế so với biên độ ~32% của thời lượng đi.}}

Đây là điểm dễ hiểu nhầm nhất: giờ/thời tiết **có** ảnh hưởng đến giá **cuối** (qua kênh hệ số
nhân — xem mục 1.7), và cũng ảnh hưởng **gián tiếp** đến giá cơ bản thông qua thời lượng đi (mục
1.5.2), nhưng **không** có một khoản phụ phí "theo giờ" hay "theo thời tiết" nào được cộng thẳng
vào giá cơ bản.

#### 1.5.4. ⭐ Phát hiện quan trọng nhất — nhiễu ngẫu nhiên THẬT SỰ, không phải do thiếu kiểm soát

Câu hỏi: liệu phần dao động còn lại của giá cơ bản có phải do dải quãng đường "chưa đủ hẹp"? Kiểm
tra bằng cách thu hẹp dần dải quãng đường (cùng 1 tuyến, cùng 1 loại xe) xuống tới mức cực đoan:

{{IMG:B5_cv_khong_giam.png|Hình B5 — Hệ số biến thiên (CV) của giá cơ bản giữ nguyên ~20% dù thu hẹp dải quãng đường từ 2.000 mét xuống còn 2 MÉT. Chứng minh đây là nhiễu ngẫu nhiên thật sự gắn với từng lần báo giá, không phải do đo lường/kiểm soát chưa đủ chặt.}}

**Kết luận:** cùng tuyến, cùng xe, quãng đường giống hệt nhau tới từng mét — giá cơ bản vẫn dao
động ~20%. Đây là bằng chứng mạnh nhất cho sàn nhiễu.

#### 1.5.5. Permutation importance — xác nhận bằng model thực tế

{{IMG:B6_permutation_baseprice.png|Hình B6 — Trong phạm vi cùng tuyến+xe+quãng đường, thời lượng đi gần như là feature DUY NHẤT model thực sự dùng để dự đoán giá cơ bản. Giờ, thứ, thời tiết, lịch sử giá... đều có importance gần 0.}}

---

### 1.6. Key feature → HỆ SỐ NHÂN

**Hệ số nhân** (`target_shown_multiplier`) — phần điều chỉnh giá theo cung–cầu, dao động 0,85–1,80.

#### 1.6.1. Cung–cầu — driver mạnh nhất

{{IMG:M1_M2_imbalance_lastmult.png|Hình M1-M2 — Hệ số nhân tăng gần như tuyến tính theo market imbalance (cầu − cung) và theo hệ số nhân quan sát gần nhất. Đây là 2 driver mạnh nhất.}}

- **Market imbalance:** cầu tăng, cung giảm → mất cân bằng tăng → hệ số nhân tăng — đúng cơ chế
  kinh tế học cung–cầu.
- **Hệ số nhân quan sát gần nhất:** tương quan rất mạnh (~0,95) — vì hệ số nhân **dai dẳng theo
  thời gian**, ít thay đổi đột ngột trong khoảng vài phút.

#### 1.6.2. Giờ trong ngày — ảnh hưởng cực mạnh (khác hẳn giá cơ bản)

{{IMG:M3_M4_hour_weather_vs_multiplier.png|Hình M3-M4 — Hệ số nhân dao động rất mạnh theo giờ (đỉnh giờ đi làm sáng 6-9h và tan làm 17-19h), biên độ ~50%. Thời tiết ảnh hưởng yếu hơn nhiều nhưng vẫn có xu hướng rõ (mưa → hệ số nhân cao hơn).}}

Giờ tác động lên hệ số nhân **qua kênh cung–cầu**: giờ cao điểm → cầu tăng vọt → mất cân bằng tăng
→ hệ số nhân tăng. Đây là chuỗi nhân quả đã kiểm chứng ở mục 1.4.

#### 1.6.3. ⭐ Phát hiện quan trọng nhất — hệ số nhân gần như là "giá trị thị trường dùng chung"

Kiểm tra: trong **cùng 1 khu vực + cùng 1 khung 5 phút**, hệ số nhân có còn dao động nhiều không?

{{IMG:M5_hang_so_thi_truong.png|Hình M5 — Độ lệch chuẩn hệ số nhân trong cùng khu vực + cùng khung 5 phút chỉ còn ~20% so với toàn bộ dữ liệu. Xác nhận: hệ số nhân là giá trị dùng CHUNG cho cả thị trường tại thời điểm đó, không phải nhiễu riêng từng khách.}}

**Kết luận:** khác hẳn giá cơ bản (vẫn dao động ~20% dù kiểm soát chặt tới 2 mét), hệ số nhân **gần
như là hằng số** trong phạm vi khu vực + khung thời gian ngắn — đây là lý do dữ liệu giải thích
được tới 96,6% chênh lệch của nó.

#### 1.6.4. Kết luận về hệ số nhân

> **Hệ số nhân được quyết định bởi cung–cầu (mạnh nhất) và giờ trong ngày (qua kênh cung–cầu)** —
> cả 2 đều đo lường được tốt trong dữ liệu. Vì bản chất là giá trị cấp thị trường (không phải nhiễu
> per-quote), dữ liệu hiện có giải thích được tới **~96,6%** chênh lệch của nó — gần như tất định.
> ⚠️ Lưu ý: con số này bị ảnh hưởng bởi việc dữ liệu synthetic cung cấp sẵn chỉ số cung–cầu gần với
> công thức sinh surge — trong production thật (không có sẵn chỉ số này), độ chính xác sẽ thấp hơn.

---

### 1.7. Key feature → GIÁ CUỐI CÙNG

**Giá cuối** (`target_shown_price`) = Giá cơ bản × Hệ số nhân — con số khách hàng thực sự nhìn thấy
và trả tiền.

#### 1.7.1. Giá cuối "thừa hưởng" đặc điểm của cả 2 thành phần

{{IMG:F1_amplitude_gia_cuoi.png|Hình F1 — Cùng dải quãng đường, biên độ dao động của giá cuối theo giờ bám rất sát hình dạng của hệ số nhân (đỉnh giờ cao điểm), trong khi giá cơ bản gần như phẳng. Chứng minh trực tiếp: biến động giá cuối theo giờ chủ yếu đến từ hệ số nhân.}}

#### 1.7.2. So sánh Boston vs TP.HCM — xác nhận đúng giả thuyết mentor

{{IMG:F2_boston_vs_hcm.png|Hình F2 — TP.HCM bị ảnh hưởng bởi giờ và thời tiết mạnh hơn Boston 70-97 lần (đo trên cùng phương pháp, cùng dải quãng đường).}}

Boston (dữ liệu thật, tỷ lệ surge chỉ 3,3%) gần như không thể hiện ảnh hưởng giờ/thời tiết lên giá
(giá phẳng tuyệt đối theo giờ). TP.HCM (synthetic, tỷ lệ surge 81,7%) thể hiện rất rõ — vì dữ liệu
mô phỏng đầy đủ cơ chế giờ → cầu → surge → giá mà Boston thiếu (thiếu cột thời lượng và tín hiệu
cung–cầu).

#### 1.7.3. Ví dụ cụ thể — cùng điều kiện, giá cuối vẫn dao động rất mạnh

{{IMG:F3_phanbo_cungdieukien.png|Hình F3 — Cùng tuyến, cùng loại xe, cùng quãng đường (5,4-5,6km): phân bố giá cuối trải rộng hơn nhiều so với phân bố giá cơ bản — phần mở rộng thêm này chủ yếu do hệ số nhân đóng góp.}}

#### 1.7.4. Tổng hợp — bảng phân rã đóng góp

| Nguồn đóng góp vào chênh lệch giá cuối (cùng dải quãng đường) | Tỷ trọng |
|---|---:|
| Giá cơ bản (quãng đường + thời lượng, phần lớn là nhiễu ~81%) | ~61% |
| Hệ số nhân (cung–cầu + giờ, gần tất định ~96,6%) | ~31% |
| Phần chồng lấn (2·Cov — chuyến giá cao thường rơi vào giờ surge cao) | ~8% |
| **Không giải thích được (nhiễu tổng hợp)** | **~65%** |

#### 1.7.5. Kết luận về giá cuối

> **Giá cuối chịu tác động của cả 2 kênh — trực tiếp qua giá cơ bản (quãng đường/thời lượng) và
> qua hệ số nhân (cung–cầu/giờ) — nhưng 2 kênh này có "chất lượng dữ liệu" hoàn toàn khác nhau.**
> Hệ số nhân gần như tất định (96,6%), còn giá cơ bản có nhiễu per-quote thật sự (~81%). Vì vậy
> dù model hệ số nhân có tốt đến đâu, **độ chính xác của giá cuối vẫn bị giới hạn bởi nhiễu trong
> giá cơ bản** — đây là bottleneck chính, đã xác nhận bằng nhiều phương pháp độc lập (phân rã
> phương sai, permutation importance, kiểm định thu hẹp quãng đường tới 2 mét).

---

## 2. Build model — Hướng A: Kiến trúc Hybrid (giá cơ bản × hệ số nhân)

**Ý tưởng xuất phát từ mục 1:** giá cơ bản và hệ số nhân do **2 nhóm yếu tố hoàn toàn khác nhau**
quyết định (thuộc tính chuyến đi vs bối cảnh thị trường). Nếu ép 1 model học cả 2 cùng lúc, nó phải
trộn 2 nguồn tín hiệu tách biệt vào chung một hàm — nên tách thành 2 model chuyên biệt rồi nhân lại.

### 2.1. Kiến trúc — 3 model, chốt Hybrid

| Model | Target | Bộ feature | Vai trò |
|---|---|---|---|
| **A. Giá cơ bản** | `base_price` = giá ÷ hệ số nhân (log) | Quãng đường, thời lượng, dịch vụ, tuyến, lịch sử giá, giá cơ bản quan sát gần nhất | Lõi Hybrid |
| **B. Hệ số nhân** | `target_shown_multiplier` | Cung–cầu (imbalance/demand/supply/quote_count), hệ số nhân quan sát gần nhất, giờ | Lõi Hybrid |
| **C. Giá trực tiếp** | `target_shown_price` (log) | Như A nhưng dùng `latest_observed_price` (còn surge) | Baseline đối chiếu nội bộ |

**Kiến trúc chốt — Hybrid:**
```
giá cuối dự đoán = model_A(giá cơ bản) × model_B(hệ số nhân)
```

**So sánh 2 hướng** (trên giá cuối, cùng tập test, cùng thuật toán HistGB):

| Hướng | MAE | R² | MAPE | Bias TB |
|---|---|---|---|---|
| **Hybrid (giá cơ bản × hệ số nhân)** | **18.048 VNĐ** | **0,730** | **14,74%** | −2,3k |
| Dự đoán thẳng giá cuối | 18.834 VNĐ | 0,700 | 15,36% | −2,9k |

→ **Hybrid thắng ở cả 4 chỉ số.** Lý do: mỗi model học đúng phần việc của nó — giá cơ bản theo
quãng đường/thời lượng, hệ số nhân theo cung–cầu; không bị nhiễu lẫn nhau.

> ⚠️ **Trade-off của Hybrid:** thắng về trung bình nhưng **rủi ro hơn ở từng chuyến lẻ** — khi cả 2
> model cùng lệch một chiều, sai số bị **nhân lên** thay vì cộng. Ví dụ thực tế từ 15 test case: có
> chuyến hướng trực tiếp sai 0,4% trong khi Hybrid sai 18,2%. Cần nêu rõ khi báo cáo, không chỉ báo
> MAE trung bình.

### 2.2. Thuật toán — 3 thuật toán cho kết quả gần như giống hệt nhau

Tất cả là **gradient boosting cây quyết định** (họ thuật toán tốt nhất cho dữ liệu dạng bảng, xử lý
categorical/NaN native, giải thích được, train nhanh trên CPU).

**Kết quả trên giá cơ bản** (toàn bộ 864.360 dòng test, 3 tháng):

| Thuật toán | MAE (VNĐ) | R² | MAPE |
|---|---:|---:|---:|
| **HistGradientBoosting** (sklearn) | **15.032** | 0,6563 | 14,6% |
| LightGBM | 15.038 | 0,6562 | 14,6% |
| XGBoost | 15.045 | 0,6556 | 14,6% |

→ Chênh lệch **13 VNĐ (0,09%)** giữa thuật toán tốt nhất và kém nhất — nằm hoàn toàn trong nhiễu
ngẫu nhiên. **Chọn HistGB** làm mặc định (không cần thư viện ngoài sklearn, dễ maintain).

### 2.3. Kết quả model

**Model A — giá cơ bản** (lõi Hybrid):

| Chỉ số | Giá trị |
|---|---:|
| MAE | 15.032 VNĐ |
| RMSE | 20.095 VNĐ |
| R² | 0,656 |
| MAPE | 14,6% |

**Model B — hệ số nhân:**

| Chỉ số | Giá trị | Baseline persistence |
|---|---:|---:|
| MAE | **0,0233** | 0,0371 |
| R² | 0,9606 | — |
| **ROC-AUC** (phân biệt có surge) | **0,9979** | — |

**Model ghép (Hybrid) → giá cuối, so với baseline:**

| | MAE | Cải thiện |
|---|---:|---:|
| **Hybrid** | **18.048 VNĐ** | — |
| Baseline persistence (dùng thẳng giá quan sát gần nhất) | 33.683 VNĐ | **+44,1%** ✅ |

→ Model **vượt baseline persistence 44,1%** — mốc bắt buộc phải vượt để chứng minh có giá trị.

### 2.4. Feature nào model thực sự dùng (permutation importance, giá cơ bản)

| Feature | Importance | Tỷ trọng |
|---|---:|---:|
| **quote_distance** | 0,684 | **68%** |
| **quote_duration** | 0,233 | **23%** |
| service_name | 0,0122 | 1,2% |
| pickup_location_name | 0,00198 | 0,2% |
| history_60m_price_mean | 0,000623 | ~0% |
| gio_vn | 0,000591 | ~0% |
| *(9 feature còn lại)* | < 0,0001 | ~0% |

→ **Quãng đường + thời lượng = 92%.** Điều này **không mâu thuẫn** với mục 1 (giờ ảnh hưởng mạnh):
đây là model **giá cơ bản** (đã bỏ surge), còn giờ ảnh hưởng qua **hệ số nhân**.

**Đối chiếu chéo bằng GAM** (Generalized Additive Model, theo đề xuất mentor):

| Model | MAE | R² | MAPE |
|---|---:|---:|---:|
| GAM | 15.099 | **0,6599** | 14,78% |
| HistGB | 15.032 | 0,6563 | 14,6% |

GAM đạt **R² nhỉnh hơn** GBM, MAE chỉ chênh 67 VNĐ — xác nhận quan hệ feature → giá cơ bản chủ yếu
là **cộng dồn đơn giản**, không cần tương tác phức tạp. GAM còn cho **p-value** kiểm định ý nghĩa
thống kê: `weather_main` (p = 0,203), `history_60m_price_slope` (p = 0,475),
`actual_observation_age_minutes` (p = 0,334) — **không có ý nghĩa** với giá cơ bản, khớp permutation
importance ≈ 0.

### 2.5. Trần độ chính xác — 8 hướng cải thiện đều dừng ở cùng một mức

Model giá cơ bản dừng ở **MAE ~15.000 VNĐ / MAPE ~14,6%**. Để xác định đây là **sàn nhiễu của dữ
liệu** hay **model chưa tối ưu**, đã thử 8 hướng độc lập:

| # | Hướng thử | Cách làm | Kết quả |
|---|---|---|---|
| 1 | **Đổi thuật toán** | HistGB / LightGBM / XGBoost | Chênh 13 VNĐ |
| 2 | **Đổi hàm mất mát** | `absolute_error` thay `squared_error` (tối ưu thẳng MAE) | Chênh 26 VNĐ |
| 3 | **Thêm feature tắc đường** | `dur_per_km`, `speed_kmh` tường minh | Chênh 19 VNĐ |
| 4 | **Đổi target sang đơn giá/km** | Đoán `giá/km` rồi × quãng đường | Chênh 22 VNĐ |
| 5 | **Thêm feature quan sát gần nhất** | Tốc độ + đơn giá/km của chuyến quan sát gần nhất | Importance ≈ 0 |
| 6 | **Chuẩn hóa theo tuyến** | Z-score trong từng tuyến (18 tuyến), đo lại giờ/thứ/tháng | η ≈ 0 sau chuẩn hóa |
| 7 | **Ném hết 49 feature + trọng số** | Toàn bộ cột khả dụng, `feature_weights` ưu tiên feature quan trọng | Chênh 6 VNĐ (full 6,9M dòng) |
| 8 | **Fine-tune siêu tham số** | Optuna, 9 tham số × 40 trial × 3 tháng, dùng tập validation | Chênh **+2 VNĐ** (kém hơn) |

**Kết luận:** 8 hướng độc lập, dùng cả toàn bộ dữ liệu (6,9M dòng), đều dừng ở cùng một mức
→ **MAE ~15.000 VNĐ (MAPE ~14,6%) là sàn nhiễu thật của bộ dữ liệu**, không phải model/feature/tham
số chưa tối ưu.

**Bằng chứng bổ sung:** dùng chỉ 2 feature (quãng đường + thời lượng), model tuyến tính và model cây
cho R² **giống nhau** (0,662 vs 0,661) — độ lệch chuẩn phần dư còn lại **19.920 VNĐ** trên giá cơ
bản median 99.281 VNĐ ≈ **20% nhiễu per-quote** mà không feature nào giải thích được.

**Thử nghiệm ngoài GBM:** Neural Network 1 thân 2 đầu ra (multi-task, có cổng trọng số feature học
được) — giá MAE 18.156 vs GBM 18.048; hệ số nhân MAE 0,0260 vs GBM 0,0233 → **thua GBM ở cả 2
target**. Nguyên nhân: 2 bài toán dùng feature gần như tách biệt, ít lợi ích khi học chung
representation.

---

## 3. Build model — Hướng B: Point-price trực tiếp, lineage P5 → P12

> **Phạm vi hướng B.** Dự đoán thẳng `target_shown_price` tại request time, chỉ dùng thông tin biết
> đến thời điểm đó (as-of). Multiplier **không** được dùng làm metric song song để chọn model — kết
> quả Multiplier từ relation study chỉ dùng để giải thích cấu trúc dữ liệu và định hướng surge work
> sau đó. Đây là báo cáo đóng dòng nghiên cứu P5–P12, quyết định có tiếp tục tối ưu point-price
> trên cùng data contract hay không.

### 3.1. Phạm vi dữ liệu và độ phủ

| Thành phần | Quy mô/giá trị | Ý nghĩa |
|---|---:|---|
| Forecasting rows, 4 lags | 6.897.051 | inventory đầy đủ cho lag 5/10/15/30 phút |
| Primary lag-15 rows | 1.724.255 | phạm vi chính của point-price research |
| Thời gian | 3 tháng | đủ out-of-time comparison ngắn hạn, chưa đủ policy drift dài hạn |
| Khu vực đón | 3 | Crescent Mall, SC Vivo City, EcoGreen Sài Gòn |
| Dịch vụ | 2 synthetic services | kiểm tra được service effect nhưng chưa đại diện product portfolio thực |

Số `6,90M` không tương đương `6,90M` target độc lập: một `target_request_id` có thể xuất hiện ở bốn
lag. Vì vậy độ đa dạng thực nghiệm được quyết định nhiều hơn bởi ba tháng, ba khu vực và hai dịch vụ
hơn là tổng số dòng.

**Profile của hai target:**

| Target | Phân phối | Hàm ý mô hình |
|---|---|---|
| Price | median `114.000 VNĐ`; P05–P95 `60.000–206.000 VNĐ`; bước giá chính `1.000 VNĐ` | scale rộng, error tăng theo distance; phải báo cả MAE aggregate và slice theo trip scale |
| Multiplier | median `1,17`; P05–P95 `0,85–1,44`; min–max `0,85–1,80`; 96 giá trị | là target continuous có nhiều regime, không phải nhãn surge nhị phân |
| Multiplier = 1 | `1,06%` observations | không phù hợp bê nguyên hurdle "surge so với 1" từ Boston/Lyft |

Price và Multiplier liên quan nhưng không thay thế nhau: Price còn chứa base fare, route/service
tariff và các fee/state không được biểu diễn đầy đủ bởi Multiplier.

### 3.2. Prediction-time information contract

Relation study tổ chức trường đầu vào thành **bảy information blocks**:

1. **fare structure/route:** distance, duration, service và zone;
2. **delayed price history:** latest/history price statistics trước cutoff;
3. **delayed multiplier history:** latest/history multiplier trước cutoff;
4. **lagged market state:** demand, supply, quote count và imbalance đã lag;
5. **calendar/time:** hour, day-of-week và weekend;
6. **weather:** trạng thái thời tiết đã quan sát;
7. **freshness/availability:** age, missingness và độ tin cậy của observation.

Chỉ các trường biết được tại request/cutoff mới được phép dùng. Relation study loại target/evaluation
fields, target-time competitor observation, technical IDs/raw timestamps không có prediction meaning
và duplicate encodings. Với model riêng lag 15, `requested_lag_minutes` không được dùng làm feature.

**Những phép phân tích đã thực hiện:**

| Lớp phân tích | Đã tính | Câu hỏi trả lời |
|---|---|---|
| Target/data profile | quantile, granularity, category coverage và lag inventory | target có scale và regime nào? |
| Raw association | Pearson/Spearman cho numeric; η² cho categorical | trường nào liên hệ tuyến tính, đơn điệu hoặc khác biệt theo level? |
| Mutual information | MI theo từng target | có quan hệ phi tuyến bị correlation đơn giản bỏ sót không? |
| Out-of-time permutation | individual và group permutation trên validation sau train | model thực sự dựa vào field/information block nào để forecast? |
| Adjusted effect | thay numeric P10→P90 hoặc category level, giữ các trường khác cố định | prediction thay đổi bao nhiêu khi riêng một trường thay đổi? |
| Stability | lặp theo 4 lag, 3 tháng và 3 pickup hex | quan hệ có giữ hướng ngoài một aggregate sample không? |
| Baseline screen | Price và Multiplier ở lag 5/10/15/30 | delayed state còn hữu ích đến horizon nào? |

`consensus_weight_pct` là consensus ranking từ raw association, MI, permutation và adjusted-effect
range; nó **không phải** coefficient trong công thức giá. Group weight được tính riêng bằng cách
permute đồng thời cả information block để giảm hiện tượng các feature tương quan che nhau.

Relation study dùng fixed hash sampling với seed `42`: `173.530` train rows cho relation fit,
`97.119` validation rows cho out-of-time importance/effect và `138.896` rows cho stability across
lags. Target profile vẫn được tính trên toàn bộ `1.724.255` lag-15 rows.

### 3.3. Signal theo nhóm: Price và Multiplier

| Information block | Price weight | Multiplier weight | Kết luận |
|---|---:|---:|---|
| Fare structure/route | 76,75% | 0,56% | chi phối Price nhưng gần như không quyết định Multiplier |
| Delayed multiplier history | 10,99% | 61,27% | nguồn state mạnh nhất cho Multiplier và truyền ảnh hưởng sang Price |
| Lagged market state | 5,72% | 29,93% | demand–supply/imbalance chủ yếu điều khiển Multiplier |
| Delayed price history | 5,47% | 0,01% | có Price context nhưng gần như không thêm Multiplier state sau điều chỉnh |
| Calendar/time | 0,90% | 6,48% | time regime quan trọng với Multiplier hơn Price |
| Weather | 0,16% | 1,58% | signal phụ trong simulator hiện tại |
| Freshness/availability | 0,01% | 0,17% | ít direct signal, chủ yếu phù hợp reliability/slice diagnostics |

**Key finding:** Price có hai khối signal — trip/base-fare structure và pricing state. Multiplier
gần như tách khỏi distance/duration, chủ yếu được xác định bởi delayed multiplier và lagged
demand–supply imbalance.

> 📌 **Đối chiếu với mục 1:** kết luận này **trùng khớp hoàn toàn** với phân tích ở mục 1 dù dùng
> phương pháp hoàn toàn khác (mục 1 dùng η/R²/phân rã phương sai; mục 3 dùng consensus weight từ
> 4 phương pháp). Xem đối chiếu chi tiết ở mục 4.1.

### 3.4. Tác động của các trường chính

Bảng dưới dùng **adjusted high–low effect**: giữ các trường khác cố định trong relation HGB rồi thay
một trường numeric từ P10 lên P90; với categorical là chênh lệch lớn nhất giữa các level.

| Trường | Adjusted effect lên Price | Adjusted effect lên Multiplier | Ý nghĩa dữ liệu |
|---|---:|---:|---|
| `quote_distance` | +39.117 VNĐ | ≈0,0000 | quyết định quy mô base fare, gần như không đổi multiplier |
| `quote_duration` | +35.241 VNĐ | +0,0003 | phản ánh trip scale/base fare hơn là surge state |
| `latest_observed_multiplier` | +21.242 VNĐ | +0,2892 | delayed pricing state mạnh nhất, tác động tới cả hai target |
| `pricing_market_imbalance_5m_lag` | +13.838 VNĐ | +0,1496 | market state đi qua multiplier rồi phản ánh vào price |
| `history_60m_price_mean` | +10.443 VNĐ | ≈0,0000 | delayed base-price context, gần như không thêm multiplier state |
| `target_hour` | chênh tối đa 6.609 VNĐ | chênh tối đa 0,0491 | time regime ảnh hưởng cả hai target, không đơn điệu theo giờ |
| `weather_main` | chênh tối đa 1.201 VNĐ | chênh tối đa 0,0137 | signal phụ so với trip structure và market state |

Raw association **không đủ** để chọn feature. Ví dụ các price-history extrema và latest price có raw
Spearman khá cao với Price (`~0,54–0,64`) nhưng out-of-time permutation/adjusted effect gần 0 sau
khi các trường thay thế đã có mặt. Tương tự, `history_60m_price_mean` có raw correlation với
Multiplier (`0,588`) nhưng delayed-price group chỉ chiếm `0,01%` Multiplier weight và adjusted effect
xấp xỉ 0. Đây là **predictive redundancy/confounding**, không phải mâu thuẫn dữ liệu.

### 3.5. Độ ổn định theo lag, tháng và khu vực

| Target/signal | Theo lag 5/10/15/30 | Theo 3 tháng | Theo 3 pickup hex | Nhận xét |
|---|---|---|---|---|
| Price–distance, Spearman | `0,663` ổn định | `0,662–0,669` | `0,549–0,678` | hướng rất ổn định; strength thay đổi theo địa bàn |
| Price–duration, Spearman | `0,677` ổn định | `0,676–0,683` | `0,565–0,713` | driver cấu trúc bền nhất cùng distance |
| Price–market imbalance, Spearman | `0,451` ổn định | `0,444–0,461` | `0,370–0,390` | market effect giữ hướng nhưng yếu hơn trip scale |
| Multiplier–latest multiplier, Spearman | giảm `0,986 → 0,876` khi lag `5 → 30` | `0,947–0,949` | `0,919–0,944` | delayed state rất mạnh nhưng mất freshness theo horizon |
| Multiplier–imbalance, Spearman | `0,848` ổn định | `0,837–0,859` | `0,804–0,895` | market imbalance là signal bền qua lag và khu vực |
| Multiplier–hour, η² | `0,489` ổn định | `0,482–0,502` | `0,453–0,644` | time regime tồn tại nhưng mức mạnh phụ thuộc khu vực |

Stability check xác nhận hướng chính **không đến từ một tháng duy nhất**. Tuy nhiên spatial strength
thay đổi đáng kể và delayed multiplier suy giảm theo lag, nên model nhiều horizon phải dùng
lag/context rõ ràng hoặc tách model theo horizon.

**Giới hạn diễn giải:**

- Đây là synthetic evidence mô tả simulator, **không** chứng minh hành vi thị trường hay quan hệ
  nhân quả tại TP.HCM thật.
- Ba tháng, ba khu vực và hai dịch vụ không đủ để đánh giá policy drift, coverage địa lý hoặc
  product changes dài hạn.
- Adjusted effect vẫn phụ thuộc relation model; permutation đo model reliance, không tự động quyết
  định giữ/bỏ feature.
- Stress scenarios không được dùng cho relation ranking hoặc tuning.

### 3.6. Chia dữ liệu

| Split | Rows | Tỷ trọng | Nội dung |
|---|---:|---:|---|
| Train | 1.160.442 | 67,30% | mỗi tháng tạo 3 expanding folds + purge gap để chọn model |
| Outer validation | 193.746 | 11,24% | xác nhận candidate đã lock từ train |
| Calibration | 153.977 | 8,93% | dành riêng cho uncertainty task (iii), không fit/so sánh point model |
| Nominal test | 216.090 | 12,53% | descriptive baseline screen; sau đó learned-model comparison mở **một lần** khi contract đã khóa |

Mỗi tháng là một forecasting fold độc lập: 20 ngày train, sau đó validation, calibration và test theo
thời gian. History được reset ở monthly boundary; model của tháng sau không được dùng để chấm tháng
trước.

**Split dùng cho từng câu hỏi:**

| Mục đích | Fit/ước lượng | Evaluation | Vai trò của test |
|---|---|---|---|
| Relation study Price/Multiplier | raw association/MI trên train lag 15; HGB fit trong train từng tháng | permutation và adjusted effect trên sampled outer validation cùng tháng | exploratory hypothesis evidence, không phải independent model-selection proof |
| Stability analysis | fixed-hash sample qua 4 lags, 3 tháng và 3 hex | so hướng/strength giữa slices | không dùng |
| Feature/model selection | 3 expanding chronological folds mỗi tháng, có purge gap | outer validation mở sau khi khóa candidate | không dùng để tuning |
| Descriptive baseline screen | rule/lookup fit từ train | nominal test ở 4 lags | đặt sanity baselines, không tune learned model |
| Final point-model comparison | fit lại `train + validation` theo từng tháng | nominal test chung 216.090 rows | mở một lần, kết quả ở mục 3.9 |
| Uncertainty task (iii) | point model đã cố định | calibration split riêng | ngoài phạm vi report point-model này |

### 3.7. Baseline

Relation study đã screen baseline riêng cho hai target ở cả bốn lag:

| Lag | Best Price baseline | Price MAE | Best Multiplier baseline | Multiplier MAE |
|---:|---|---:|---|---:|
| 5 phút | History 60m price mean | 25.056 VNĐ | Latest observed multiplier | 0,0188 |
| 10 phút | History 60m price mean | 25.333 VNĐ | Latest observed multiplier | 0,0290 |
| 15 phút | History 60m price mean | 25.615 VNĐ | Latest observed multiplier | 0,0383 |
| 30 phút | History 60m price mean | 26.441 VNĐ | Pricing average multiplier 5m lag | 0,0572 |

Tại lag 15, chốt **History 60m price mean** làm Price baseline chính; nó mạnh hơn route×service
median (`28.143 VNĐ`), distance-scaled persistence (`29.585 VNĐ`) và latest-price persistence
(`33.707 VNĐ`). Multiplier dùng latest observed multiplier làm strong baseline (`0,0383`).

**Key finding:** baseline error **tăng theo observation lag**. Với Multiplier, latest observation
thắng ở 5–15 phút nhưng bị market-average baseline vượt ở 30 phút; freshness của delayed state quan
trọng và baseline/model gate phải được đọc theo từng horizon.

Baseline table là descriptive test evidence, **không phải** feature/model-selection evidence. Sau khi
đọc bảng này, learned-model candidates vẫn phải được chọn và khóa bằng train/outer-validation
protocol riêng.

### 3.8. Feature engineering và feature selection

Relation study inventory `33` prediction-time features. P5 **không** lấy bảng importance làm feature
list cuối; nó chuyển các findings thành một chuỗi experiment có retrain, chronological folds và gate
đăng ký trước.

| Stage | Câu hỏi/thử nghiệm | Kết quả | Ý nghĩa |
|---|---|---|---|
| Relation prioritization | 7 information blocks; raw association, MI, permutation, adjusted effect | trip structure, delayed multiplier và market state là ba nguồn signal chính | tạo hypothesis và thứ tự thử, chưa quyết định giữ/bỏ |
| Stage 1 — source screening | Core 24 features; Core+Weather; Core+Freshness; Full 33 | Core thắng history baseline `28,87%`, 3/3 tháng; Full chỉ hơn Core `2,85 VNĐ` (`0,0158%`), CI cắt 0 | weather/freshness không có incremental evidence đủ mạnh trong direct HGB |
| Stage 2 — group ablation + forward addition | refit các data groups theo cả drop và add path | chọn `CORE_MINUS_PRICE_HISTORY`, 15 features; validation MAE `18.067,24 VNĐ` | delayed price có association nhưng bị trip/multiplier/market fields thay thế trong learner này |
| Stage 3A — engineered batches | FE-A route speed; FE-B distance scaling; FE-C history dynamics; FE-D market gaps; FE-E cyclic time; FE-F reliability | 6 batches, 62/62 checks PASS; **không batch nào** đạt retain gate `0,1%` | không có engineered block đơn lẻ tạo bước nhảy |
| Stage 3C — interaction recovery | 22 pair/bridge candidates trên 9 train-only folds | `STOP_NO_TRAIN_CANDIDATE`; không candidate đạt `0,1%` | bounded cross-batch synergy cũng không giải thích plateau |
| Stage 4 — sequential pruning | drop-column refit, mỗi vòng bỏ tối đa một feature rồi đánh giá lại | 7 rounds, `15 → 8` features; validation `18.067,24 → 18.062,43 VNĐ`; CI `[-1,64, 10,32]` | simplification/non-inferiority win, không phải material accuracy gain |
| Stage 5 — HGB tuning | 33 deterministic specifications trên 9 purged folds | khóa `S5_HPT_004`; validation MAE `18.035,28 VNĐ`, hơn default `0,1503%` | tuning có gain thật nhưng vẫn nhỏ so với noise floor |

**Impact của từng feature được giữ lại** — mỗi feature được bỏ riêng khỏi HGB 15-feature base và
đánh giá lại trên 9 chronological folds. Số càng lớn thì feature càng khó được thay thế:

| Feature bị bỏ | MAE tăng | MAE tăng tương đối | Kết luận |
|---|---:|---:|---|
| `quote_distance` | 1.742,94 VNĐ | 9,792% | driver mạnh nhất |
| `quote_duration` | 1.670,19 VNĐ | 9,383% | driver mạnh thứ hai |
| `service_id` | 103,23 VNĐ | 0,580% | giữ khác biệt fare theo service |
| `latest_observed_multiplier` | 73,64 VNĐ | 0,414% | cung cấp delayed pricing state |
| `target_hour` | 43,93 VNĐ | 0,247% | giữ time-of-day pattern |
| `pricing_market_imbalance_5m_lag` | 35,91 VNĐ | 0,202% | market signal nhỏ nhưng còn độc lập |
| `pickup_zone_id` | 27,26 VNĐ | 0,153% | giữ khác biệt theo khu vực đón |
| `target_day_of_week` | 10,00 VNĐ | 0,056% | impact nhỏ nhất nhưng chưa đủ bằng chứng để bỏ |

**8 feature giữ lại:** `quote_distance`, `quote_duration`, `latest_observed_multiplier`,
`pricing_market_imbalance_5m_lag`, `service_id`, `pickup_zone_id`, `target_hour`,
`target_day_of_week`.

7 feature còn lại được loại tuần tự vì không mang thêm signal độc lập khi 8 feature trên đã có mặt.
Sau pruning, outer-validation MAE thay đổi từ `18.067,24` xuống `18.062,43 VNĐ` (`+4,80 VNĐ`, chỉ
`0,0266%`). Vì vậy lợi ích chính của feature engineering là **giảm contract từ 15 xuống 8 biến mà
không làm giảm accuracy đáng kể**; nó không tạo ra bước nhảy về MAE.

### 3.9. Model: P5 → P12

Tất cả candidate dưới đây được fit lại trên `train + validation` theo từng tháng và đánh giá trên
đúng cùng nominal test gồm `216.090` observations. Test không được dùng để đổi feature,
hyperparameter, threshold hoặc candidate.

| Model | Hướng tiếp cận | Test MAE (VNĐ) | Test RMSE (VNĐ) | Test WAPE | ΔMAE vs P6 (VNĐ) |
|---|---|---:|---:|---:|---:|
| P5 | Tuned HGB (32 candidates, 9 folds) | 18.045,07 | 24.540,95 | 14,672% | +42,47 |
| **P6** | **CatBoost, 700 trees/depth 6/lr 0,05, MAE loss** | **18.002,60** | **24.461,46** | **14,638%** | **0,00** |
| EBM-GAM | GAM base | 18.746,46 | 25.001,91 | 15,243% | +743,86 |
| **P7** | **Residual CatBoost** | **17.998,21** | **24.337,58** | **14,634%** | **−4,40** |
| P9 | Full 33-feature CatBoost | 18.011,37 | 24.484,30 | 14,645% | +8,76 |
| P9 | Multi-lag CatBoost | 18.011,93 | 24.485,72 | 14,646% | +9,33 |
| P10 | Causal meta-residual | 18.000,11 | 24.440,33 | 14,636% | −2,49 |
| P11 | Retrieval advantage gate | 18.002,38 | 24.461,67 | 14,638% | −0,22 |
| P12 | Latent-state CatBoost | 18.000,98 | 24.425,10 | 14,637% | −1,62 |
| P12 | Public rate-card transfer | 24.893,36 | 33.286,95 | 20,241% | +6.890,75 |

P7 có MAE thấp nhất về số học, nhưng chỉ thấp hơn P6 `4,40 VNĐ` (`0,024%`); đây **không phải** mức
cải thiện có ý nghĩa vận hành. Bỏ candidate rate-card, các learned tree model chỉ nằm trong dải
`17.998–18.045 VNĐ`, cho thấy kết luận **model plateau** vẫn giữ nguyên khi mọi model được đặt lên
cùng một tập test. Vì test đã được dùng cho bảng cuối này, kết quả không được dùng để mở thêm vòng
tuning hoặc tái chọn model.

### 3.10. Kết quả chính của hướng B

P6 test MAE `18.002,60 VNĐ` tương đương khoảng `15,8%` của median fare; WAPE là `14,638%`. P90
absolute error đạt `38.640 VNĐ`, bằng khoảng `34%` median fare. Nghĩa là model đã tốt hơn các
baseline đơn giản nhưng **tail error vẫn lớn** đối với một hệ thống cần dùng prediction để ra quyết
định giá.

| Evidence | Kết quả | Ý nghĩa |
|---|---:|---|
| P7 test MAE | 17.998,21 VNĐ | thấp nhất về số học, chỉ hơn P6 4,40 VNĐ |
| P6 test MAE | 18.002,60 VNĐ | gần như trùng outer-validation 18.001,97 VNĐ |
| P6 WAPE | 14,638% | aggregate error vẫn lớn so với tổng fare value |
| P6 P90 absolute error | 38.640 VNĐ | 10% prediction có lỗi ít nhất xấp xỉ mức này |

**Kết luận hướng B:**

1. Giữ **P6** làm incumbent benchmark đã chọn trước khi mở test, **không** claim production-ready;
   không promote P7 từ chênh lệch test `4,40 VNĐ`.
2. Dừng mở lineage point-price mới trên cùng data contract.
3. Next: chuyển sang multiplier/surge và acceptance-rate modeling.
4. Chỉ mở lại point-price nếu có information block mới giải quyết hidden base-pricing state.

---

## 4. Đối chiếu 2 hướng model — điều gì trùng khớp, điều gì khác biệt

### 4.1. Hai relation study độc lập, hai bộ phương pháp khác nhau, cùng một kết luận

Mục 1 và mục 3.3–3.4 được thực hiện **hoàn toàn độc lập**, dùng phương pháp khác hẳn nhau:

| | Mục 1 (hướng A) | Mục 3 (hướng B) |
|---|---|---|
| Thước đo chính | η (correlation ratio), R², phân rã phương sai | consensus weight từ 4 nguồn (raw assoc, MI, permutation, adjusted effect) |
| Đối tượng tách | giá cơ bản / hệ số nhân / giá cuối | Price / Multiplier (không tách base fare) |
| Cách đo tác động | biên độ dao động khi kiểm soát quãng đường | adjusted P10→P90 effect, giữ trường khác cố định |
| Kiểm định bổ trợ | thu hẹp dải quãng đường tới 2 mét | stability qua 4 lag × 3 tháng × 3 hex |

**Kết luận trùng khớp:**

| Kết luận | Bằng chứng hướng A | Bằng chứng hướng B |
|---|---|---|
| Quãng đường + thời lượng chi phối phần giá cơ sở | ~92% permutation importance; r = 0,76 / 0,70 | fare structure block = **76,75%** Price weight; drop-column +1.743 / +1.670 VNĐ |
| Hệ số nhân tách rời hẳn quãng đường/thời lượng | η(quãng đường → hệ số nhân) ≈ 0,09 | adjusted effect của `quote_distance` lên Multiplier ≈ **0,0000** |
| Cung–cầu là driver chính của hệ số nhân | corr(imbalance, multiplier) = **0,80** | lagged market state = **29,93%** Multiplier weight; Spearman `0,848` ổn định |
| Hệ số nhân quan sát gần nhất rất mạnh | corr ≈ 0,95 | delayed multiplier block = **61,27%** Multiplier weight |
| Giờ ảnh hưởng Multiplier mạnh hơn Price nhiều | η 0,702 vs 0,296 | calendar block: 6,48% (Mult) vs 0,90% (Price) |
| Thời tiết chỉ là signal phụ | η 0,153 (hệ số nhân) | weather block 1,58% (Mult), 0,16% (Price) |

→ **Hai phương pháp độc lập cho cùng một bức tranh.** Đây là bằng chứng chéo mạnh: kết luận không
phải là artifact của một cách đo cụ thể.

### 4.2. Kết quả model — hai kiến trúc hội tụ về cùng một mức sai số

| | Hướng A (Hybrid) | Hướng B (point-price P6) |
|---|---|---|
| Kiến trúc | 2 model tách: giá cơ bản × hệ số nhân | 1 model dự đoán thẳng giá cuối |
| Thuật toán chốt | HistGradientBoosting | CatBoost (700 trees, depth 6, lr 0,05, MAE loss) |
| Số feature | 14 (model A) + 11 (model B) | 8 (sau sequential pruning) |
| Giao thức chọn model | train/validation theo tháng | 3 expanding folds + purge gap, test mở 1 lần |
| **MAE trên giá cuối** | **18.048 VNĐ** | **18.002,60 VNĐ** |
| MAPE / WAPE | 14,74% (MAPE) | 14,638% (WAPE) |
| R² | 0,730 | — (không báo cáo) |

> ⚠️ **Lưu ý khi đọc so sánh này:** 2 con số MAE **không nằm trên cùng một tập test** — hướng A dùng
> tập test riêng (3-4 ngày cuối mỗi tháng, 864.360 dòng), hướng B dùng nominal test đã khóa
> (216.090 dòng). Vì vậy **không được kết luận "model nào tốt hơn"** từ chênh lệch 45 VNĐ này.

**Nhưng có một bằng chứng cho thấy 2 tập test có độ khó tương đương:** cả 2 hướng đều tính độc lập
baseline *latest-price persistence* và ra con số gần như trùng khớp:

| Baseline persistence (dùng thẳng giá quan sát gần nhất) | Giá trị |
|---|---:|
| Hướng A tính được | 33.683 VNĐ |
| Hướng B tính được | 33.707 VNĐ |
| **Chênh lệch** | **24 VNĐ (0,07%)** |

→ Hai tập test có cùng độ khó ở mức baseline. Điều này khiến việc **cả 2 kiến trúc đều dừng ở
~18.000 VNĐ** trở thành một quan sát có ý nghĩa thật, không phải trùng hợp do chia dữ liệu.

### 4.3. Ý nghĩa của sự hội tụ

Hai hướng khác nhau ở **gần như mọi lựa chọn thiết kế** — kiến trúc (tách 2 model vs 1 model), thuật
toán (HistGB vs CatBoost), feature contract (25 biến vs 8 biến), cách xử lý target (log-transform vs
raw), giao thức đánh giá — nhưng vẫn cho ra cùng một mức sai số.

Cộng với:
- Hướng A: 8 hướng cải thiện độc lập đều dừng ở cùng mức (mục 2.5)
- Hướng B: 10 candidate model trong dải `17.998–18.045 VNĐ`, không stage feature engineering nào
  đạt gate `0,1%` (mục 3.8, 3.9)

→ Tổng cộng **~20 thử nghiệm độc lập** từ 2 người, 2 hướng tiếp cận, đều hội tụ. Đây là bằng chứng
thực nghiệm đủ vững để kết luận: **~18.000 VNĐ MAE là sàn nhiễu của bộ dữ liệu ở data contract hiện
tại**, không phải giới hạn của kiến trúc hay thuật toán.

### 4.4. Điểm khác biệt còn lại giữa 2 hướng

| Khía cạnh | Nhận xét |
|---|---|
| **Khả năng diễn giải** | Hướng A tách được sai số thành "sai ở giá cơ bản" vs "sai ở hệ số nhân" — hữu ích cho chẩn đoán. Hướng B cho 1 con số duy nhất. |
| **Rủi ro từng chuyến** | Hướng A có phương sai case-by-case cao hơn (nhân 2 nguồn sai số). Hướng B ổn định hơn ở tail. |
| **Độ chặt của giao thức** | Hướng B chặt hơn (purge gap, test mở 1 lần, gate đăng ký trước). Nên dùng giao thức này làm chuẩn chung cho các thử nghiệm sau. |
| **Sẵn sàng cho surge work** | Hướng A đã có sẵn model hệ số nhân riêng (MAE 0,0233, ROC-AUC 0,998) — dùng lại được ngay cho cấu phần surge. |

---

## 5. Trực quan hóa so sánh model & đánh giá uncertainty

> 📌 **Mục này bổ sung theo góp ý của mentor sau báo cáo tuần 2:** *"nếu mà được thì 2 em có thêm
> plot khi mà so sánh các model nhé. Kiểu plot price over time hay multiplier over time anh nghĩ là
> sẽ informative hơn, với có cả vùng standard deviation nữa, để mình đánh giá được mức độ
> uncertainty."*
>
> Toàn bộ biểu đồ dưới đây dựng trên **tập test 864.360 dòng** (3 tháng, 11 ngày test), dùng đúng bộ
> dự đoán đã tạo ra các con số ở mục 2 — đã đối chiếu khớp: giá cơ bản MAE 15.031,56 · hệ số nhân
> MAE 0,0233 · Hybrid MAE 18.047,97 · trực tiếp MAE 18.834,01 · persistence MAE 33.683,22.

### 5.1. Giá & hệ số nhân theo giờ — kèm vùng ±1 độ lệch chuẩn

{{IMG:U1_gia_heso_theo_gio_std.png|Hình U1 — Giá cuối (trái) và hệ số nhân (phải) theo giờ trong ngày, dải quãng đường 4-6km. Đường liền = giá trị thực tế trung bình, đường đứt = model dự đoán, vùng mờ = ±1 độ lệch chuẩn. Model bám sát đường trung bình ở cả 2 target, nhưng vùng ±1std của giá cuối HẸP HƠN RÕ RỆT so với thực tế, trong khi vùng ±1std của hệ số nhân gần như trùng khít.}}

**Đọc biểu đồ — 2 tầng thông tin:**

| | Giá cuối | Hệ số nhân |
|---|---|---|
| Biên độ dao động theo giờ (thực tế) | 74,1k → 121,6k VNĐ (**+64,2%**) | 0,856 → 1,358 (**+58,6%**) |
| Model có bám đúng đường trung bình? | ✅ Có, sát | ✅ Có, gần như trùng khít |
| Độ lệch chuẩn TB — thực tế | 25.161 VNĐ | 0,1148 |
| Độ lệch chuẩn TB — model dự đoán | 15.545 VNĐ | 0,1102 |
| **Model hẹp hơn thực tế** | **−38,2%** ⚠️ | **−3,9%** ✅ |

→ **Đây là phát hiện mới mà chỉ nhìn qua MAE không thấy được.** Cả 2 model đều dự đoán đúng *xu
hướng trung bình*, nhưng model giá **không tái tạo được độ dao động thật** — nó dự đoán quá "an
toàn", co về gần giá trị trung bình có điều kiện. Ngược lại, model hệ số nhân tái tạo được gần như
trọn vẹn độ dao động thật (chỉ hẹp hơn 3,9%).

Đây chính là **biểu hiện trực quan của sàn nhiễu** đã kết luận ở mục 1.3 và 2.5: phần dao động
per-quote của giá cơ bản không tương quan với bất kỳ feature nào, nên model tối ưu theo MAE/MSE
buộc phải bỏ qua nó và dự đoán về mức trung bình.

### 5.2. Diễn biến theo thời gian thực

{{IMG:U2_chuoi_thoigian_std.png|Hình U2 — Giá cuối (trên) và hệ số nhân (dưới) theo thời gian thực trong cửa sổ test tháng 01/2026, gộp theo từng giờ, dải 4-6km. Chu kỳ ngày-đêm lặp lại rất rõ. Model (đường đứt) bám sát thực tế (đường liền) qua mọi chu kỳ, kể cả các đỉnh giờ cao điểm.}}

Biểu đồ theo thời gian thực xác nhận thêm 3 điểm mà biểu đồ gộp theo giờ không thể hiện được:

1. **Model bám đúng qua mọi chu kỳ ngày** — không chỉ đúng "trung bình cộng dồn". Các đỉnh giá
   (~140k) và đáy (~72k) đều được dự đoán đúng thời điểm.
2. **Hệ số nhân gần như trùng khít hoàn toàn** — đường xanh lá và đường đen chồng lên nhau ở hầu hết
   thời điểm, kể cả tại các đỉnh nhọn 1,55.
3. **Sai lệch lớn nhất rơi vào các đỉnh nhọn của giá** — tại đỉnh, model có xu hướng dự đoán thấp
   hơn thực tế (đường đứt xanh nằm dưới đường đen). Nhất quán với bias trung bình −2.298 VNĐ ở mục 5.3.

### 5.3. So sánh model — sai số theo giờ & phân bố sai số

{{IMG:U3_sosanh_model_saiso.png|Hình U3 — Trái: MAE theo từng giờ trong ngày của 3 phương án (Hybrid, dự đoán trực tiếp, baseline persistence). Phải: phân bố sai số của Hybrid vs dự đoán trực tiếp — bề rộng phân bố chính là mức độ uncertainty.}}

| Chỉ số | Hybrid | Dự đoán trực tiếp | Baseline persistence |
|---|---:|---:|---:|
| MAE tổng | **18.048 VNĐ** | 18.834 VNĐ | 33.683 VNĐ |
| MAE thấp nhất (giờ 3h) | **12.655 VNĐ** | 12.9k VNĐ | 23,6k VNĐ |
| MAE cao nhất (giờ 18h) | **21.186 VNĐ** | 22,7k VNĐ | 38,4k VNĐ |
| Độ lệch chuẩn sai số | **24.426 VNĐ** | 25.476 VNĐ | — |
| Bias trung bình | **−2.298 VNĐ** | −2.939 VNĐ | — |

**Nhận xét:**

- **Hybrid thắng dự đoán trực tiếp ở 24/24 giờ** — không phải chỉ thắng trung bình. Khoảng cách nới
  rộng nhất vào giờ cao điểm chiều (17-19h): 21,2k vs 22,7k.
- **Uncertainty thay đổi rất mạnh theo giờ** — MAE giờ tắc nhất (18h) cao gấp **1,67 lần** giờ thấp
  nhất (3h). Đây là thông tin quan trọng cho cấu phần (iii): khoảng dự đoán **không nên có độ rộng
  cố định**, mà phải nới ra vào giờ cao điểm.
- **Cả 2 model đều lệch âm** (đoán thấp hơn thực tế ~2,3-2,9k VNĐ) — phân bố sai số hơi lệch phải.
  Nguyên nhân: target giá cơ bản dùng log-transform, khi đổi ngược `exp()` sinh lệch hệ thống nhẹ.
  Có thể sửa bằng hiệu chỉnh Duan smearing khi làm cấu phần (iii).
- Baseline persistence sai gấp đôi ở gần như mọi giờ — xác nhận model có giá trị thật.

### 5.4. Bất đối xứng uncertainty — giá cơ bản vs hệ số nhân

{{IMG:U4_uncertainty_batdoixung.png|Hình U4 — Trái: độ lệch chuẩn của sai số chia cho giá trị trung bình (uncertainty tương đối) theo giờ, so sánh giá cơ bản vs hệ số nhân. Phải: model có tái tạo được độ dao động thật không — so độ lệch chuẩn của giá trị thực tế vs giá trị model dự đoán.}}

| | Giá cơ bản | Hệ số nhân | Tỷ lệ |
|---|---:|---:|---:|
| Uncertainty tương đối TB (std sai số / giá trị TB) | **18,66%** | **2,63%** | **7,1×** |
| Độ lệch chuẩn thực tế | 28.740 VNĐ (giá cuối) | 0,1808 | — |
| Độ lệch chuẩn model dự đoán | 20.207 VNĐ | 0,1756 | — |
| **Tỷ lệ tái tạo được độ dao động** | **0,703** ⚠️ | **0,971** ✅ | — |

> ⭐ **Bằng chứng chéo rất mạnh.** Tỷ lệ uncertainty giá cơ bản / hệ số nhân đo được ở đây là
> **7,1×**. Hoàn toàn độc lập, hướng B (mục 6.2, mục d) tính tỷ lệ base-fare error /
> multiplier error bằng phương pháp khác và ra **7,39×**. Hai phép đo khác nhau, hai người làm, hai
> bộ công cụ — chênh nhau chưa tới 4%. Đây là xác nhận định lượng mạnh nhất cho kết luận "bottleneck
> nằm ở giá cơ bản, không phải hệ số nhân".

Panel phải trả lời trực tiếp câu hỏi *"model có tái tạo được uncertainty thật không?"*:

- **Hệ số nhân: có** — model dự đoán độ lệch chuẩn 17,6 so với thực tế 18,1 (đạt 97,1%). Model này
  gần như đã "hiểu" trọn vẹn cơ chế sinh hệ số nhân.
- **Giá cuối: không** — model chỉ tái tạo 70,3% độ dao động thật (20,2 so với 28,7). Gần **30% độ
  dao động thật bị model bỏ qua** vì không giải thích được từ feature hiện có.

→ Đây là lý do **Uncertainty Quantification là bước tiếp theo bắt buộc**, không phải tùy chọn: model
điểm hiện tại *có hệ thống* báo thiếu mức độ dao động thật, nên nếu dùng thẳng con số điểm để ra
quyết định giá sẽ đánh giá thấp rủi ro.

### 5.5. Xác nhận thêm — quan hệ giá gần tuyến tính, model đơn giản xấp xỉ được

Mentor cho biết study trước của team cũng đi đến kết luận *"price model thật ra khá là linear và có
thể approximate được bằng các model đơn giản"*. Kết quả của nhóm **độc lập xác nhận điều này** bằng
3 bằng chứng riêng biệt:

| Bằng chứng | Kết quả | Nguồn |
|---|---|---|
| Hồi quy tuyến tính chỉ 2 biến (quãng đường + thời lượng) | R² ≈ **0,66** | mục 1.5.1 |
| GAM (cộng dồn, không tương tác) vs HistGB | GAM R² **0,6599** ≥ GBM 0,6563 | mục 2.4 |
| Model tuyến tính vs model cây, cùng 2 feature | R² **0,662 vs 0,661** — gần như bằng nhau | mục 2.5 |

→ Cả 3 đều chỉ ra: **phần tín hiệu học được của giá cơ bản gần như hoàn toàn là quan hệ cộng dồn
đơn giản**; các model phức tạp (GBM, CatBoost, Neural Network) không khai thác thêm được tương tác
phi tuyến nào có ý nghĩa. Điều này nhất quán với việc lineage P5→P12 ở mục 3 dừng ở cùng một mức MAE
dù thử qua 10 kiến trúc khác nhau.

---

## 6. Giới hạn hiện tại — Bottleneck nằm ở dự đoán GIÁ CƠ BẢN

### 6.1. Hai "trần" đã đạt được — nhưng khác nhau hoàn toàn về bản chất

| Thành phần | Trần đã đạt | Bằng chứng |
|---|---|---|
| **Hệ số nhân** | R² ≈ **96,6%** (gần tất định) | Std trong cùng khu vực + khung 5 phút chỉ còn ~20% so với toàn bộ dữ liệu (mục 1.6.3) |
| **Giá cơ bản** | R² ≈ **0,66**, MAE ≈ **15.032 VNĐ** (MAPE ≈ 14,6%) | Không cải thiện được sau 8 hướng thử độc lập (mục 2.5) |

→ Model hệ số nhân gần như đã tối ưu hết mức. **Toàn bộ dư địa cải thiện độ chính xác giá cuối nằm
ở giá cơ bản** — đây là giới hạn/nút thắt hiện tại của cả hệ thống dự đoán giá.

### 6.2. Vì sao đây là giới hạn "cứng", không phải do model/feature chưa tối ưu

**(a) Phân biệt rõ 3 khái niệm hay bị nhầm — importance, R², MAE.**
Permutation importance (~68% quãng đường + ~23% thời lượng ≈ 92%) chỉ là **xếp hạng tương đối** giữa
các feature đang có, KHÔNG phải phần trăm phương sai giải thích được. Bằng chứng: một hồi quy tuyến
tính đơn giản chỉ dùng đúng 2 feature quan trọng nhất này (mục 1.5.1) đã đạt R² ≈ 0,66 — gần bằng
đúng model đầy đủ tính năng. Nói cách khác: **biết chính xác quãng đường + thời lượng, mô hình tốt
nhất có thể vẫn chỉ giải thích được ~66% biến thiên giá cơ bản**, phần còn lại (~34%, tương đương
MAE ~15.032 VNĐ) là nhiễu mà không feature nào trong dữ liệu hiện tại giải thích thêm được.

**(b) Kiểm định trực tiếp ở mức mét (mục 1.5.4).** Cố định tuyến + xe + quãng đường giống hệt nhau
tới từng mét, giá cơ bản vẫn dao động CV ~20%. Đây là bằng chứng mạnh nhất rằng phần nhiễu này gắn
với từng lần báo giá cụ thể (per-quote), không phải do thiếu kiểm soát biến số.

**(c) ~20 thử nghiệm độc lập từ 2 hướng đều hội tụ** (mục 2.5, 3.8, 3.9, 4.3).

**(d) Bằng chứng định lượng trực tiếp từ hướng B** — chỉ ra bottleneck nằm ở base fare chứ không
phải multiplier:

| Bằng chứng | Giá trị | Diễn giải |
|---|---:|---|
| Tương quan residual giữa HGB và CatBoost | ~**0,99** | các model khác nhau cùng sai ở **đúng những dòng giống nhau** |
| Tương quan residual P12 vs P6 | **0,99753** | kể cả latent-state model cũng không chạm được phần sai số này |
| Giảm MAE nếu **biết trước true multiplier** | chỉ ~**217 VNĐ** | multiplier gần như không còn dư địa |
| Tỷ lệ base-fare error / multiplier error | ~**7,39×** | sai số tập trung áp đảo ở phần base fare |

→ Ngay cả khi có một model hệ số nhân **hoàn hảo tuyệt đối**, MAE tổng chỉ giảm ~217 VNĐ trên
~18.000 VNĐ (~1,2%). Đây là bằng chứng định lượng trực tiếp nhất cho kết luận ở mục 1.3.

### 6.3. Nguyên nhân gốc rễ & dữ liệu cần bổ sung để phá vỡ giới hạn

Phần nhiễu còn lại (per-quote, không tương quan với bất kỳ feature quan sát được) nhiều khả năng đến
từ một **trạng thái ẩn ở tầng định giá** (*hidden base-pricing state*) không có mặt trong dữ liệu
hiện tại:

- **Phiên bản bảng giá / rate-card** hiệu lực tại đúng thời điểm báo giá (có thể thay đổi nhiều
  lần/ngày)
- **Fee / surcharge** đặc thù (phụ phí cầu đường, sân bay, đêm khuya...)
- **Khuyến mãi, mã giảm giá** áp dụng cho từng khách/chuyến
- **Operational state** phía vận hành không được log lại ở mức quote

Bằng chứng gián tiếp ủng hộ giả thuyết này: candidate **P12 Public rate-card transfer** (thử áp bảng
giá công bố công khai) cho MAE `24.893,36 VNĐ` — **kém hơn hẳn** model học từ dữ liệu, chứng tỏ bảng
giá thực tế được dùng **khác** bảng giá công bố, và sự khác biệt đó chính là phần thông tin đang
thiếu.

> **Kết luận chung về giới hạn:** hướng đi hiệu quả nhất tiếp theo **không phải** tiếp tục thử thêm
> thuật toán/kiến trúc model. Cả 2 hướng đã độc lập chứng minh dư địa đó đã cạn. Việc cần làm là
> (i) xác nhận với mentor/nguồn dữ liệu xem có thể bổ sung các trường trạng thái ẩn nói trên hay
> không, và (ii) chuyển hướng sang Uncertainty Quantification — lượng hóa khoảng dự đoán thay vì
> tiếp tục cố ép về 1 con số điểm chính xác hơn.

---

## 7. Kết luận chung & hướng phát triển

### 7.1. Trả lời trực tiếp câu hỏi của mentor

> **Mentor dự đoán đúng.** Trên bộ dữ liệu Việt Nam, giờ cao điểm và trời mưa **ảnh hưởng giá rõ
> rệt** — mạnh gấp **74 lần** (giờ) và **97 lần** (mưa) so với Boston. Cơ chế: giờ/mưa làm **cầu
> tăng** → mất cân bằng cung–cầu → **hệ số nhân tăng** → giá cuối tăng. Boston không thể hiện điều
> này vì chỉ **3,3%** chuyến có surge (TP.HCM: **81,7%**) và thiếu cả cột thời lượng lẫn tín hiệu
> cung–cầu — đúng như 2 nhược điểm dataset đã nêu ở tuần 1.

### 7.2. Tình trạng 3 cấu phần

| Cấu phần | Trạng thái |
|---|---|
| **i. Study relation** | ✅ Hoàn thành — 2 relation study độc lập, phương pháp khác nhau, kết luận trùng khớp (mục 4.1) |
| **ii. Build model** | ✅ Hoàn thành — 2 kiến trúc độc lập (Hybrid & point-price), cùng hội tụ ~18.000 VNĐ MAE, xác định được sàn nhiễu |
| **iii. Uncertainty** | ⏳ Chưa bắt đầu — dữ liệu **đã có sẵn tập `calibration`** dành riêng cho việc này |

### 7.3. Hướng phát triển tiếp — ưu tiên theo thứ tự

**1. Uncertainty Quantification (cấu phần iii) — ưu tiên cao nhất.**
Cả 2 hướng đã độc lập chứng minh MAE ~18k là sàn nhiễu không thể giảm ở data contract hiện tại →
**đưa ra khoảng dự đoán có giá trị hơn** việc cố ép một con số điểm chính xác hơn. Ví dụ:
*"giá ~114k, khoảng tin cậy 90%: [95k – 135k]"*.
- **Conformal Prediction** — dùng tập `calibration` có sẵn, cho bảo đảm phủ theo lý thuyết
- **Quantile Regression** (LightGBM `objective="quantile"`) — dự đoán trực tiếp P5/P50/P95
- Nên làm **cả 2 để so sánh** độ rộng khoảng và tỷ lệ phủ thực tế

> 🔎 **Mục 5 vừa bổ sung 3 ràng buộc thiết kế cụ thể cho bước này:**
> (a) model điểm hiện tại chỉ tái tạo **70,3%** độ dao động thật của giá (mục 5.4) → khoảng dự đoán
> phải được hiệu chỉnh mở rộng, không thể suy ra từ phương sai dự đoán của model;
> (b) uncertainty **thay đổi 1,67 lần** giữa giờ thấp nhất và cao nhất (mục 5.3) → phải dùng khoảng
> **thay đổi theo giờ**, không dùng độ rộng cố định;
> (c) cả 2 model đều lệch âm ~2,3-2,9k VNĐ do log-transform → cần hiệu chỉnh bias (Duan smearing)
> trước khi hiệu chỉnh khoảng.

**2. Multiplier / surge modeling.**
Model hệ số nhân từ hướng A đã sẵn sàng (MAE 0,0233, R² 0,961, ROC-AUC 0,998) — dùng lại được ngay.
Cần bổ sung thí nghiệm "bỏ cột cung–cầu, buộc model suy luận từ giờ/thời tiết" để có ước lượng gần
production hơn (xem cảnh báo ở mục 7.4).

**3. Acceptance rate model — theo yêu cầu mới của mentor.**
Đã kiểm tra: **cả 2 bộ dữ liệu đều không có nhãn accept/reject** (rà soát toàn bộ 87 cột HCM + 57
cột Boston). Mentor xác nhận team production cũng không có, chỉ dùng outcome cuốc + demographic.
Mentor đã **đơn giản hóa yêu cầu** thành: 2 model xu hướng (khả năng chấp nhận tăng/giảm khi biết
giá đối thủ / thời tiết). Cần làm rõ đây là **mô phỏng dựa trên giả định elasticity từ literature**,
không phải model học từ hành vi khách hàng thật.

**4. Không nên tiếp tục các hướng đã loại trừ.**
~20 thử nghiệm ở mục 2.5, 3.8, 3.9 đã kiểm chứng đầy đủ. Chỉ mở lại point-price nếu có
**information block mới** giải quyết hidden base-pricing state.

### 7.4. Điểm cần lưu ý trung thực về dữ liệu synthetic

**(a) Hệ số nhân đạt ROC-AUC 0,998 — con số này bị thổi phồng.**
Bộ dữ liệu **cho sẵn** `pricing_market_imbalance_5m_lag` — chính là kết quả trung gian của công thức
sinh surge (theo tài liệu XanhSM: `m_market = f(ℓ_t, q_t)` với `ℓ_t = cầu − cung`). Model chỉ cần
**học lại một hàm toán học đã biết**, không phải học hành vi thị trường thật. Trong production thật,
thường **không có sẵn** chỉ số cung–cầu chính xác thời gian thực → độ chính xác sẽ **thấp hơn nhiều**.

**(b) Quan hệ giờ/mưa → giá mạnh vì được sinh theo công thức.**
η(giờ → hệ số nhân) = 0,70 chứng minh **cơ chế đã được cài đặt trong dữ liệu** — không phải bằng
chứng về hành vi thị trường thật ở TP.HCM. Kết luận đúng phải phát biểu là: *"bộ dữ liệu synthetic
TP.HCM có mô hình hóa đầy đủ cơ chế giờ cao điểm/thời tiết → cung-cầu → surge, khác bộ Boston vốn
thiếu các mắt xích này"*.

Tuy nhiên, chiều tác động và độ lớn **khớp với quan sát thực tế của mentor** trên hệ thống production
→ cơ chế mô hình hóa là **hợp lý**, dù con số cụ thể không thể lấy làm ước lượng cho production.

**(c) Phạm vi hạn chế.** Ba tháng, ba khu vực và hai dịch vụ không đủ để đánh giá policy drift,
coverage địa lý hoặc product changes dài hạn. Chỉ 3 khu vực nên mọi kết luận về vị trí còn hạn chế
(Boston có 12 khu).

### 7.5. Đề xuất trao đổi với mentor

1. **Hidden base-pricing state** — có thể bổ sung các trường rate-card version / fee / promotion vào
   dataset không? Đây là điều kiện duy nhất để phá vỡ trần MAE ~18k hiện tại.
2. **Xác nhận hướng làm acceptance rate model** — mô phỏng dựa trên literature có được chấp nhận
   trong báo cáo, hay cần nguồn dữ liệu khác có nhãn thật?
3. **Về ROC-AUC 0,998 của hệ số nhân** — có nên bổ sung thí nghiệm "bỏ cột cung–cầu, buộc model suy
   luận từ giờ/thời tiết" để có ước lượng gần production hơn?
4. **Về GAM** — kết quả ngang GBM và dễ giải thích hơn (vẽ được đường cong + p-value từng feature).
   Có nên dùng GAM cho phần trình bày/báo cáo, giữ GBM cho production?

---

## Phụ lục A — Nguồn phân tích (hướng A)

Toàn bộ số liệu/biểu đồ mục 1 và 2 tổng hợp từ 19 notebook trong `TP_HCM_data/analysis/` và
`TP_HCM_data/model/`, xem bản đồ chi tiết tại `analysis/00_DOC_TRUOC_TONG_HOP.md`.

| Chủ đề | Notebook |
|---|---|
| So sánh Boston vs TP.HCM | `00_TONG_HOP_SO_SANH.ipynb` |
| Vị trí, giờ, thời tiết, tắc đường (riêng lẻ) | `01`–`04` |
| Kiểm chứng feature engineering (tốc độ, giá/km, chuẩn hóa tuyến) | `05`, `05b`, `06` |
| Biên độ dao động, phân rã phương sai, sàn nhiễu | `07`–`11` |
| Trực quan hóa tổng hợp theo giờ/thời tiết | `12` |
| Feature selection cho model | `15_chon_feature_gia_cuoi.ipynb`, `16_chon_feature_gia_co_ban.ipynb`, `17_chon_feature_he_so_nhan.ipynb` |
| Train Model A / B / baseline / GAM | `model/train/01`–`04` |
| Đánh giá & ghép Hybrid | `model/evaluation/01`–`05` |
| 8 hướng cải thiện đã thử | `model/_archive/thu_nghiem/` |
| Biểu đồ uncertainty mục 5 (U1–U4) | `model/evaluation/06_plot_uncertainty.ipynb` |

> ⚠️ **Lưu ý kỹ thuật khi tái lập mục 5:** các file `model/<ThuatToan>/*.joblib` hiện tại **không
> tái tạo được** các con số trong báo cáo (đã kiểm chứng: nạp lại model và dự đoán trên chính bộ
> feature đã lưu cho hệ số nhân ra MAE 0,1351 / R² 0,034 thay vì 0,0233 / 0,961). Nhiều khả năng
> các file joblib đã bị ghi đè bởi một lần chạy thử nghiệm sau đó. **Các file `.parquet` dự đoán
> mới là artifact đúng** — đã đối chiếu khớp từng con số với báo cáo. Cần chạy lại
> `train/01`–`03` để đồng bộ lại joblib trước khi dùng chúng cho việc gì khác.

## Phụ lục B — Thông số kỹ thuật model (hướng A)

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

## Phụ lục C — Nguồn evidence (hướng B)

Evidence đầy đủ của lineage P5–P12 nằm trong `docs/tphcm_synthetic_relation_study_v1.0.0/` và các
CSV/workbook tái lập ở `artifacts/tphcm_synthetic_relation/v1.0.0/`. Report gốc:
`03_final_point_pricing_report_goc_cua_ban_cung_team.md` (version `2.6.0`).
