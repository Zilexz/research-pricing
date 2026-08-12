# Báo cáo Tuần 3 — Uncertainty Quantification & Acceptance Rate Model

**Dự án:** Competitor Fare Forecasting (GSM) · **Ngày:** 06/08/2026
**Dữ liệu:** `synthetic_quote_context_sandbox` (TP.HCM, synthetic) — 6.897.051 dòng × 70 cột, 3 tháng (01–03/2026)
**Tập test:** 864.360 chuyến · **Tập calibration:** 615.908 chuyến

---

**Motivation.** Tuần 2 đóng xong cấu phần (i) và (ii). Còn lại cấu phần (iii) **Uncertainty
Quantification** và một yêu cầu bổ sung của mentor: **acceptance rate model** — chuyển từ *dự đoán
giá đối thủ* sang *quyết định giá của mình*.

Yêu cầu thứ hai vướng một ràng buộc nghiêm trọng mà chính mentor cũng xác nhận:

> *"Cái khó ở đây là đến cả data bọn anh dùng cũng không có feature khách hàng accept hay không."*

Tuần 3 giải quyết cả hai, và trong quá trình đó **phát hiện một sai lầm có hệ thống trong hướng
tiếp cận ban đầu của chính mình** — được trình bày thẳng ở Mục 4.

**Kết quả cốt lõi.**

1. **Cấu phần (iii) hoàn thành.** Ba phương pháp UQ có bảo đảm thống kê hữu hạn mẫu. Conformal
   chuẩn hoá cho khoảng **±30,11%** với coverage **89,58%** (danh mục 90%). CQR có **coverage điều
   kiện tốt nhất** — lệch tối đa 1,84 điểm theo giờ so với 2,19 của QR thô.
2. **Chứng minh acceptance model KHÔNG thể là bài toán Machine Learning** với dữ liệu hiện có.
   Đã thử và loại trừ **8 hướng** bằng bằng chứng định lượng, không phải bằng lập luận.
3. **Xây dựng acceptance model theo hướng cấu trúc** (discrete choice — McFadden). Kết luận chính:
   tăng giá +10% so với đối thủ → khả năng chấp nhận **giảm ~19%** (tương đối).
4. **🔴 Đính chính lớn:** kết luận *"luôn nên bán rẻ hơn đối thủ 24%"* ở bản đầu là **SAI**. Nguyên
   nhân: tối đa hoá **doanh thu** thay vì **lợi nhuận**. Khi thêm chi phí biên, kết luận **đảo
   chiều** — xem Mục 4.
5. **Nối cả 3 cấu phần thành một hệ thống.** Quyết định giá nay lấy tích phân trên **phân phối dự
   đoán** thay vì cắm ước lượng điểm.
6. **Kiểm chứng chéo bằng MNL.** Mô hình 3 lựa chọn cho kết quả **khớp trong 3 điểm %** với logit
   nhị phân ⇒ kết luận vững, và **mở khoá `s₀`** — tỷ lệ khách không đi, một đại lượng đội vận hành
   đo được trực tiếp.

---

## 0. Bối cảnh & phạm vi tuần 3

| Cấu phần đề bài | Trạng thái tuần 2 | Trạng thái tuần 3 |
|---|---|---|
| **i** — Study relation | ✅ Hoàn thành | ✅ (giữ nguyên) |
| **ii** — Build model | ✅ Hoàn thành | ✅ + bổ sung GAM vào so sánh |
| **iii** — Uncertainty | ⏳ Chưa bắt đầu | ✅ **Hoàn thành** (Mục 1) |
| **(+)** — Acceptance *(mentor yêu cầu thêm)* | — | ✅ **GĐ 1–6 xong** (Mục 2–7) |

{{IMG:TQ1_bang_dieu_khien.png|Hình TQ1 — Bảng điều khiển tổng quan toàn dự án. Sáu ô: so sánh 4 thuật toán · coverage vs độ rộng · coverage theo giờ · đường cong chấp nhận · ngưỡng đảo chiều giá · trạng thái 5 hạng mục. Sinh bởi `model/99_TONG_QUAN_TOAN_DU_AN.ipynb`.}}

### Kiến trúc hệ thống

Nguyên tắc xuyên suốt: **tách bạch phần HỌC và phần GIẢ ĐỊNH**. Trộn hai thứ này là ra "model
AUC 1,0" nguỵ trang — đã chứng minh ở Mục 2.2.

| Tầng | Bản chất | Có train? | Đánh giá bằng |
|---|---|---|---|
| **1** Model giá | Machine Learning | ✅ | MAE, R², train/test split |
| **1b** Uncertainty | Hiệu chỉnh thống kê | ✅ (calibration) | Coverage, độ rộng |
| **2** Acceptance | Structural (McFadden) | ❌ | Phân tích độ nhạy |
| **3** Quyết định giá | Tối ưu hoá | ❌ | Backtest mô phỏng |

{{IMG:KT1_kien_truc_tang.png|Hình KT1 — Kiến trúc hệ thống từ dữ liệu thô đến dự đoán chấp nhận. Màu phân biệt bản chất từng khối: xanh dương = học/hiệu chỉnh từ dữ liệu · xanh lá = đo từ dữ liệu · cam = giả định. Tầng 1b là phần MỚI của tuần 3, biến đầu ra của Tầng 1 từ một con số thành một phân phối.}}

{{IMG:KT2_tang3_quyet_dinh.png|Hình KT2 — Tầng 3 và hai lần sửa quan trọng: (1) chuyển từ tối đa hoá doanh thu sang lợi nhuận có chi phí biên, (2) lấy tích phân trên phân phối dự đoán thay vì cắm ước lượng điểm.}}

**Cập nhật cấu phần (ii)** — bổ sung GAM (mentor yêu cầu) vào bảng so sánh:

| Thuật toán | MAE giá cuối | MAPE |
|---|---:|---:|
| XGBoost | 18.807đ | 15,34% |
| LightGBM | 18.809đ | 15,34% |
| HistGB | 18.834đ | 15,36% |
| GAM | 19.170đ | 15,70% |
| **Hybrid** (giá cơ bản × hệ số nhân) | **18.045đ** | **14,74%** |
| — Persistence (mốc so sánh) | 33.683đ | 28,18% |

Bốn thuật toán chênh nhau **1,9%**, đều tốt hơn persistence ~44%. **Kết luận tuần 2 được củng cố:
chọn thuật toán không phải đòn bẩy chính — giới hạn nằm ở dữ liệu.**

---

## 1. Cấu phần (iii) — Uncertainty Quantification

### 1.1 Vì sao cần và cần cái gì

Một dự đoán điểm *"giá đối thủ ≈ 120.000đ"* không dùng được để ra quyết định, vì không biết
**sai bao nhiêu**. UQ trả lời: *"giá đối thủ nằm trong [84.000đ; 156.000đ] với xác suất 90%."*

Hai tiêu chí, **không ngang hàng nhau**:

| Tiêu chí | Nghĩa | Mức quan trọng |
|---|---|---|
| **Coverage** | % lần giá thật rơi vào khoảng | 🔴 **Ràng buộc bắt buộc** — dưới danh mục là khoảng vô giá trị |
| **Độ rộng** | Khoảng hẹp bao nhiêu | 🟠 Thứ yếu — chỉ so khi coverage đã đạt |

> **Nói rõ để tránh hiểu nhầm:** *"UQ tốt là UQ cho khoảng hẹp nhất"* là **sai**. Khoảng hẹp mà
> coverage 60% thì tệ hơn khoảng rộng có coverage 90%. Đúng phải là: **đạt coverage danh mục
> trước, rồi mới tối thiểu độ rộng.**

### 1.2 Ba phương pháp đã cài đặt

| Phương pháp | Cách làm | Bảo đảm |
|---|---|---|
| **Conformal chuẩn hoá** | Lấy phân vị 90% của sai số **tương đối** trên calibration | Hữu hạn mẫu, phân phối tự do |
| **Quantile Regression** | LightGBM `objective="quantile"`, α = 0,05 / 0,50 / 0,95 | ❌ Không có |
| **CQR** (QR + conformal) | Hiệu chỉnh QR bằng điểm conformity `E = max(q05−y, y−q95)` | Hữu hạn mẫu |

Hiệu chỉnh hữu hạn mẫu của CQR: `k = ⌈(n+1)·α⌉`, lấy `E` thứ `k` sau khi sắp xếp.

{{IMG:UQ1_so_sanh_conformal.png|Hình UQ1 — Ba biến thể conformal: độ rộng cố định · chuẩn hoá theo giá dự đoán · Mondrian (theo nhóm). Biến thể chuẩn hoá được chọn vì khoảng co giãn theo mức giá — chuyến đắt được khoảng rộng hơn, đúng trực giác.}}

{{IMG:UQ2_khoang_du_doan.png|Hình UQ2 — Khoảng dự đoán conformal chuẩn hoá trên một lát cắt dữ liệu test. Vùng xanh là khoảng 90%, điểm đỏ là giá thật rơi ngoài khoảng.}}

### 1.3 Kết quả

| Phương pháp | Coverage | Độ rộng TB | Hiệu chỉnh |
|---|---:|---:|---|
| Conformal chuẩn hoá | **89,58%** | 72.686đ | có |
| Quantile Regression (thô) | 89,18% | 75.977đ | không |
| CQR | 89,56% | 76.546đ | có |

Khoảng conformal chuẩn hoá: **`dự đoán × (1 ± 30,11%)`**.

Cả ba **đạt coverage danh mục** (chênh < 1 điểm). Vậy chọn cái nào?

### 1.4 Coverage **điều kiện** — tiêu chí phân biệt thật sự

Coverage tổng thể đạt 90% **không có nghĩa** mọi nhóm đều được 90%. Một model có thể "bù trừ":
95% ở giờ dễ, 85% ở giờ khó, trung bình vẫn 90% — nhưng **khách đi giờ cao điểm bị phục vụ tệ hơn
một cách có hệ thống**.

Đo lệch coverage tối đa so với danh mục, trên **ba** chiều phân nhóm:

| Phương pháp | Giờ | Quãng đường | Thời tiết | **Xấu nhất** |
|---|---:|---:|---:|---:|
| Conformal chuẩn hoá | **1,34** | 2,04 | **0,47** | 2,04 |
| QR thô | 2,19 | 1,91 | 0,94 | 2,19 |
| CQR | 1,84 | **0,95** | 0,57 | **1,84** |

> **🔴 Đính chính.** Bản nháp trước của mục này ghi *"CQR có coverage điều kiện tốt nhất"*. Đo đầy
> đủ trên cả 3 chiều cho thấy phát biểu đó **quá mạnh**: CQR chỉ hơn rõ ở chiều **quãng đường**,
> còn **Conformal chuẩn hoá đều hơn theo giờ và thời tiết** — đồng thời cho khoảng **hẹp nhất**.
> **Không phương pháp nào thắng tuyệt đối.**

{{IMG:UQ3_so_sanh_3pp.png|Hình UQ3 — So sánh 3 phương pháp trên cả coverage tổng thể và độ rộng. Ba cột gần bằng nhau ở coverage — khác biệt thật nằm ở coverage điều kiện.}}

{{IMG:VQ5_coverage_dieu_kien.png|Hình VQ5 — Coverage điều kiện đo trên ba chiều: giờ · thời tiết · quãng đường. Đường đứt đỏ là danh mục 90%. Không đường nào bám sát danh mục tốt hơn hẳn trên cả ba chiều.}}

{{IMG:UQ4_thich_ung.png|Hình UQ4 — Khả năng thích ứng của khoảng dự đoán theo độ khó của bối cảnh.}}

**Khuyến nghị:** dùng **conformal chuẩn hoá làm mặc định** — khoảng hẹp nhất, đều nhất theo giờ và
thời tiết. Chỉ chuyển sang **CQR** nếu bài toán đặc biệt quan tâm công bằng giữa các nhóm **quãng
đường**, hoặc muốn tối ưu trường hợp xấu nhất.

### 1.5 Trực quan hoá theo góp ý mentor

Mentor góp ý tuần 2: *"vẽ giá theo thời gian, có khoảng uncertainty, để thấy model bám thực tế đến đâu."*

{{IMG:MT1_price_over_time.png|Hình MT1 — Giá theo thời gian: giá thật vs giá dự đoán. Đường dự đoán bám sát xu hướng nhưng "làm phẳng" các đỉnh và đáy.}}

{{IMG:MT2_multiplier_over_time.png|Hình MT2 — Hệ số nhân theo thời gian. Đối chiếu với MT1 thấy rõ: model hệ số nhân bám thực tế tốt hơn model giá nhiều.}}

{{IMG:MT3_chuoi_thoi_gian.png|Hình MT3 — Chuỗi thời gian giá thật vs giá dự đoán kèm dải uncertainty. Model bám xu hướng nhưng biên độ dao động hẹp hơn thực tế rõ rệt.}}

{{IMG:MT4_uncertainty_model.png|Hình MT4 — Độ bất định của model theo bối cảnh. Giờ cao điểm và trời mưa là nơi model kém chắc chắn nhất.}}

{{IMG:U3_sosanh_model_saiso.png|Hình U3 — So sánh sai số các model. Model hệ số nhân chính xác hơn hẳn model giá cơ bản.}}

**Phát hiện quan trọng:** model chỉ tái tạo **~62%** độ dao động của giá cuối nhưng **~96%** của
hệ số nhân. Phần thiếu là **nhiễu thật**, không phải model kém — đã chứng minh ở tuần 2 (hình B5:
hệ số biến thiên **không giảm** dù thu hẹp dải quãng đường xuống 2 mét).

{{IMG:MT5_san_nhieu.png|Hình MT5 — Sàn nhiễu: phần dao động không thể giải thích được bằng bất kỳ feature nào hiện có.}}

---

## 2. Acceptance model — ràng buộc gốc và 8 hướng đã loại trừ

### 2.1 Vấn đề

Mentor yêu cầu: *"bên cạnh dự đoán giá đối thủ, làm thêm model xu hướng khách chấp nhận giá."*

Nhưng bộ dữ liệu:

```
booking_or_completion_outcomes_generated = False
```

Đã quét **toàn bộ 70 cột**: **không có cột nào** ghi nhận khách có đặt hay không. Đây là dữ liệu
**báo giá** (quote), không phải dữ liệu **giao dịch** (transaction).

{{IMG:AC1_du_lieu_dau_vao.png|Hình AC1 — Dữ liệu đầu vào: có đầy đủ giá, bối cảnh, cung–cầu, nhưng KHÔNG có cột outcome. Đây là ràng buộc nền tảng của toàn bộ Mục 2–7.}}

### 2.2 Tám hướng đã thử và loại trừ — có bằng chứng, không phải suy đoán

| # | Hướng | Bằng chứng loại trừ |
|---|---|---|
| 1 | Supervised learning | `outcomes_generated = False`; 0/251 cột có nhãn |
| 2 | Unsupervised | Acceptance không tồn tại dưới bất kỳ dạng ẩn nào |
| 3 | **Rule-based weak labeling** | AUC = **1,0000** khi có `price_gap`, **0,4995** khi bỏ ⇒ vòng tròn logic |
| 4 | Proxy label từ cột khác | Đã quét toàn bộ 70 cột |
| 5 | PU learning | Cần ít nhất vài mẫu dương — có **0** |
| 6 | Ước lượng cầu trực tiếp | Hồi quy thô cho hệ số **+0,40** — **sai dấu** (nội sinh) |
| 7 | Biến công cụ (IV) | IV không hợp lệ: bỏ biến giờ làm hệ số lật từ −0,95 sang **+0,36** |
| 8 | Chỉ số Lerner | Cho `ε` = −33 đến −2,5 — vô lý |

**Hướng 3 đáng nói riêng** vì nó được đề xuất từ bên ngoài và nghe rất hợp lý: gán nhãn giả theo
luật (`price_gap ≤ −15%` → chấp nhận cao, v.v.) rồi train model. Chúng tôi đã **cài đặt và chạy thật**:

{{IMG:PL1_pseudo_label.png|Hình PL1 — Kết quả rule-based weak labeling. AUC = 1,0000 khi có `price_gap` trong feature: model chỉ học lại đúng cái luật đã dùng để tạo nhãn, không học gì từ dữ liệu.}}

{{IMG:PL2_so_sanh_luat_logit.png|Hình PL2 — So sánh luật gán nhãn với đường logit. Luật bậc thang hàm ý elasticity bằng 0 ở trong mỗi bậc và −44,5 tại điểm nhảy — cả hai đều vô nghĩa về kinh tế.}}

> **Kết luận Mục 2.** Với dữ liệu hiện có, acceptance **không phải bài toán Machine Learning**.
> Không có `.fit()`, không có tập train. Phải chuyển sang **mô hình cấu trúc**.

---

## 3. Acceptance model — hướng cấu trúc (discrete choice)

### 3.1 Mô hình

Dùng **logit nhị phân** từ lý thuyết lựa chọn rời rạc (McFadden):

$$P(\text{chấp nhận}) = \sigma\!\left(a + b\left[\ln\frac{p}{\hat p} - \ln(1+d)\right]\right)$$

| Ký hiệu | Nghĩa | Nguồn |
|---|---|---|
| `p` | Giá **mình** báo | biến quyết định |
| `p̂` | Giá **đối thủ** | từ model tuần 2 |
| `d` | Dịch WTP theo bối cảnh | **đo từ dữ liệu** |
| `ε` | Elasticity (firm-level) | **giả định** — xem Mục 7 |
| `P₀` | Chấp nhận khi giá ngang bằng | **giả định** |
| `b` | `ε / (1 − P₀)` | dẫn xuất |
| `a` | `logit(P₀)` | dẫn xuất |

{{IMG:AC2_co_che_model.png|Hình AC2 — Cơ chế model: giá mình so với giá đối thủ, điều chỉnh theo dịch WTP của bối cảnh, đưa qua hàm logit ra xác suất chấp nhận.}}

### 3.2 Phần **đo được từ dữ liệu** — không phải giả định

Trên 1.724.714 chuyến (sau khử trùng lặp theo `target_request_id`):

| Đại lượng | Giá trị | Cách đo |
|---|---:|---|
| Dịch WTP khi **mưa** | **+4,61%** | Hệ số nhân TB: 1,1414 (không mưa) → 1,1940 (mưa) |
| Biên độ WTP **theo giờ** | **50,0%** | Thấp nhất 3h (−25,2%) → cao nhất 18h (+12,2%) |

### 3.3 Cách trình bày kết quả — một cải tiến quan trọng

Mức tuyệt đối (*"chấp nhận = 40,6%"*) phụ thuộc nặng vào `P₀` — tham số **giả định**. Đã kiểm chứng
cho `P₀` chạy 0,30 → 0,70:

| Cách báo cáo | Dao động khi đổi `P₀` |
|---|---:|
| Mức tuyệt đối | **30,7 điểm** ❌ |
| Thay đổi tuyệt đối | 9,3 điểm ⚠️ |
| **Thay đổi tương đối** | **3,1 điểm** ✅ |

⇒ **Mọi kết luận nay phát biểu theo % thay đổi tương đối** — robust gấp 10 lần.

### 3.4 Kết quả

**Model 1 — khi biết giá đối thủ:**

| Đổi giá so với đối thủ | Khả năng chấp nhận |
|---|---:|
| +5% | **−10%** |
| +10% | **−19%** |
| +20% | **−35%** |
| −5% | **+10%** |
| −10% | **+21%** |
| −20% | **+42%** |

{{IMG:AC3_model1_gia.png|Hình AC3 — Model 1: khả năng chấp nhận theo mức giá tương đối so với đối thủ, kèm dải theo 3 giá trị elasticity.}}

**Model 2 — khi biết thời tiết:**

Trời mưa → chấp nhận tăng **+4,49 điểm %**, tương đương **có thể tăng giá ~4,6% mà giữ nguyên tỷ lệ
chấp nhận**.

{{IMG:AC4_model2_thoitiet.png|Hình AC4 — Model 2: ảnh hưởng thời tiết tại từng mốc giá. Biên độ mưa (4,49 điểm) nhỏ hơn biên độ giờ (37,48 điểm) 8,3 lần.}}

{{IMG:AC5_bang_tracuu.png|Hình AC5 — Bảng tra cứu gộp 2 model: giờ × thời tiết × mức giá.}}

Kiểm chứng thêm trên **cùng dải quãng đường 4–6 km** (330.288 chuyến, 38,2% tập test) để loại bỏ
ảnh hưởng của độ dài chuyến:

{{IMG:D2_xuhuong_chapnhan.png|Hình D2 — Xu hướng chấp nhận tại các mốc ±5%, ±10%, ±15% trên cùng dải quãng đường 4–6 km. Giá đối thủ TB trong dải: 103.681đ.}}

### 3.5 Ba kết luận **vững** trên toàn dải giả định (3/3 trường hợp)

1. Giá cao hơn đối thủ → chấp nhận **giảm**
2. Mưa → chấp nhận **tăng**
3. **Giờ** tác động mạnh hơn **thời tiết** nhiều lần

Ba kết luận này **không phụ thuộc giá trị elasticity cụ thể** — đây là phần đáng tin nhất của Mục 3.

---

## 4. 🔴 Đính chính lớn — chi phí biên làm ĐẢO CHIỀU kết luận

### 4.1 Sai lầm

Bản đầu của phần định giá tối đa hoá **doanh thu**:

$$R(p) = p \cdot P(\text{chấp nhận} \mid p)$$

Kết quả: giá tối ưu = **0,760 × giá đối thủ** — tức *"luôn bán rẻ hơn đối thủ 24%, ở mọi bối cảnh"*.

**Đây là kết luận sai.** Không có chi phí thì **không có gì hãm việc giảm giá** ngoài độ cong của
đường logit. Doanh nghiệp thật tối đa hoá **lợi nhuận**:

$$\Pi(p) = (p - MC) \cdot P(\text{chấp nhận} \mid p)$$

### 4.2 Chi phí biên của một cuốc xe là gì

Không phải chi phí nền tảng (gần 0), mà là **khoản phải trả tài xế** — dưới mức đó tài xế không
nhận cuốc. Thị trường gọi xe Việt Nam: tài xế thường nhận **~75–80%** cước.

Đặt `c = MC / giá đối thủ` làm tham số và quét cả dải:

| `c` | 0% | 25% | 50% | 75% |
|---|---:|---:|---:|---:|
| Giá tối ưu so với đối thủ | **−24,0%** | −14,1% | **+0,0%** | **+19,5%** |

{{IMG:UA2_chiphi_bien.png|Hình UA2 — Trái: chi phí biên đẩy đỉnh lợi nhuận sang phải. Phải: ngưỡng đảo chiều — dưới ~50% nên bán rẻ hơn đối thủ, trên ~50% nên bán đắt hơn. Vùng tím là tỷ lệ ăn chia tài xế thực tế của ngành.}}

### 4.3 Ngưỡng đảo chiều

| `ε` (firm-level) | `c*` (ngưỡng đảo chiều) |
|---:|---:|
| −1,2 | **16,6%** |
| −2,0 | **50,0%** |
| −3,0 | **66,7%** |

**Nếu tài xế thực sự nhận 75–80% cước thì cả 3 kịch bản `ε` đều nằm TRÊN ngưỡng** ⇒ nên báo giá
**cao hơn** đối thủ, ngược hẳn kết luận ban đầu.

{{IMG:UA4_bando_khuyennghi.png|Hình UA4 — Bản đồ khuyến nghị theo `c` × `ε`. Đỏ = nên bán rẻ hơn · Xanh = nên bán đắt hơn · Đường đen = ranh giới đảo chiều. Dải tối bên phải là tỷ lệ ăn chia tài xế thực tế.}}

> **Bài học rút ra.** Kết luận *"luôn bán rẻ hơn 24%"* là **hệ quả trực tiếp của việc quên chi phí
> biên**, không phải phát hiện về thị trường. Đây là câu hỏi ưu tiên số 1 gửi mentor:
> **chi phí biên mỗi cuốc là bao nhiêu, và team tối ưu GMV hay lợi nhuận?**

---

## 5. Nối cả 3 cấu phần — đưa uncertainty vào quyết định giá

### 5.1 Lỗ hổng thứ hai

Phần định giá ban đầu cắm thẳng **ước lượng điểm** `p̂` vào công thức. Nhưng model giá có MAE
18.045đ (**14,74%**) — quyết định như thể `p̂` đúng là **quá tự tin**.

Công thức đúng lấy tích phân trên **phân phối dự đoán**:

$$\mathbb{E}[\Pi(p)] = \int (p - MC)\cdot P(\text{chấp nhận} \mid p, p_{\text{đối thủ}})\cdot f(p_{\text{đối thủ}} \mid \text{dữ liệu})\; dp_{\text{đối thủ}}$$

Đây chính là **mắt xích nối cấu phần (ii) → (iii) → acceptance thành một hệ thống**.

### 5.2 Cách làm

Phân phối `f` dựng **thực nghiệm** từ Quantile Regression, không giả định phân phối chuẩn hay
log-chuẩn. Thiết kế chia mẫu đúng: **chọn giá trên calibration (615.908), chấm điểm ngoài mẫu trên
test (864.360)**.

{{IMG:UA1_phanphoi_dudoan.png|Hình UA1 — Trái: phân phối dự đoán chuẩn hoá. Nếu model hoàn hảo thì đây là một vạch tại 1,0; thực tế std ≈ 0,19. Phải: một chuyến cụ thể — quyết định phải dùng cả đường cong, không chỉ vạch điểm.}}

### 5.3 Kết quả — và một con số nhỏ hơn kỳ vọng

| | Lợi nhuận TB/chuyến (`c` = 50%) |
|---|---:|
| Ngây thơ (cắm `p̂`, `r*` = 1,000) | 30.314đ |
| **Vững** (tích phân trên `f`, `r*` = 1,040) | **30.499đ** |
| **Chênh — lấy lại miễn phí** | **+185đ (+0,61%)** |
| Oracle (biết trước giá thật) | 30.747đ |

**+0,61% là nhỏ. Không nên thổi phồng.** Giá trị thật nằm ở chỗ khác:

| Độ rộng phân phối dự đoán | % lợi nhuận mất nếu bỏ qua bất định |
|---:|---:|
| 0,5× (model tốt gấp đôi) | 0,08% |
| **1,0× (model hiện tại)** | **0,62%** |
| 1,5× | 2,01% |
| 2,0× | **4,36%** |

Quan hệ **siêu tuyến tính**: rộng gấp đôi thì thiệt hại gấp ~7 lần. Nghĩa là cách làm ngây thơ chỉ
tạm chấp nhận được **vì model giá hiện đã khá tốt** — áp lên phân khúc hoặc tuyến khó dự đoán hơn
thì sai lầm này đắt hẳn lên.

{{IMG:UA3_dinh_dich.png|Hình UA3 — Trái: đỉnh lợi nhuận dịch khi tính cả bất định (bất đẳng thức Jensen). Phải: r* tối ưu và % lợi nhuận mất theo độ rộng phân phối — quan hệ siêu tuyến tính.}}

{{IMG:UA5_tong_hop.png|Hình UA5 — Trái: giá khuyến nghị theo giờ và thời tiết. Phải: ba mức lợi nhuận — ngây thơ / vững / trần trên oracle. Khoảng cách trái là phần lấy lại miễn phí; khoảng cách phải chỉ giảm được bằng model giá tốt hơn.}}

### 5.4 Hai điều phải nói thẳng

**a) Ở `c = 0` cách "vững" KHÔNG thắng** — thậm chí kém 0,008% ngoài mẫu. Nguyên nhân: phân phối
lệch nhẹ giữa calibration (TB 1,010) và test (1,025), và tại `c = 0` đường lợi nhuận rất phẳng
quanh đỉnh nên phần lợi không bù nổi phần lệch. Lợi ích chỉ xuất hiện khi `c > 0`.

**b) Hai loại "chi phí" khác nhau, không so trực tiếp được:**

| | Đo cái gì | Lấy lại được? |
|---|---|---|
| **3.381đ/chuyến** (mô phỏng đầu-cuối, mục tiêu doanh thu) | Cái giá của việc model **SAI** | ❌ Chỉ giảm được bằng model tốt hơn |
| **185đ/chuyến** (mục tiêu lợi nhuận, `c` = 50%) | Cái giá của việc **VỜ NHƯ** model đúng | ✅ **Miễn phí** — chỉ đổi cách chọn giá |

{{IMG:E1_mo_phong_do_lech.png|Hình E1 — Phân rã độ lệch giữa giá khuyến nghị và giá thật: bao nhiêu là CHỦ Ý (do chính sách), bao nhiêu là SAI SỐ (do model).}}

{{IMG:E2_so_sanh_chinh_sach.png|Hình E2 — So sánh các chính sách định giá trên 864.360 chuyến tập test.}}

---

## 6. Kiểm chứng chéo bằng MNL (Multinomial Logit)

### 6.1 Vì sao cần

Logit nhị phân buộc phải **tự tay** phân biệt hai loại elasticity:

| | Nghĩa | Giá trị dùng |
|---|---|---|
| `ε_market` | **Cả thị trường** cùng tăng giá | −0,3 … −0,7 |
| `ε_firm` | **Chỉ mình** tăng giá | −1,2 … −3,0 |

**Đây chính là chỗ phiên bản đầu tiên đã sai** — dùng nhầm `ε_market` cho bài toán cạnh tranh trực
tiếp, dẫn tới nghiệm tối ưu nằm ở biên lưới (*"tăng giá vô hạn"*).

MNL **không thể sai chỗ này** vì mô hình đúng tập lựa chọn thật: `{0: không đi, 1: mình, 2: đối thủ}`,
và **cả hai elasticity suy ra từ MỘT tham số `β`**:

$$\varepsilon_{\text{firm}} = -\beta(1 - s_1) \qquad \varepsilon_{\text{market}} = -\beta\, s_0$$

### 6.2 Mở khoá `s₀` — tỷ lệ khách không đi

Tỷ số hai elasticity **không phụ thuộc `β`**, cho phép suy ngược:

$$s_0 = \frac{1-m}{R-m}, \qquad R = \frac{\varepsilon_{\text{firm}}}{\varepsilon_{\text{market}}}$$

Với giả định chính (`ε_firm` = −2,0, `ε_market` = −0,5, thị phần 50%): **`s₀` = 14,3%** —
nằm gọn trong khoảng hợp lý [5%; 30%]. **8/9 tổ hợp elasticity đạt.**

{{IMG:MNL1_suy_nguoc_s0.png|Hình MNL1 — Trái: bản đồ `s₀` suy ngược theo 2 elasticity, vạch trắng là biên khoảng hợp lý 5–30%. Phải: độ nhạy theo thị phần — `s₀` vẫn hợp lý trên toàn dải 20–80%.}}

> **⚠️ Một tổ hợp KHÔNG nhất quán:** `ε_firm = −1,2` ghép với `ε_market = −0,7` cho `s₀ = 41,2%`
> — vô lý, **không được dùng đồng thời**. Đây chính là loại mâu thuẫn mà logit nhị phân **không thể
> phát hiện**, vì ở đó hai elasticity là hai con số rời rạc tự đặt.

### 6.3 MNL có cho kết quả khác không?

Đây là kiểm tra quan trọng nhất — nếu MNL lệch nhiều thì mọi kết luận Mục 3 phải viết lại.

| Đổi giá | Logit nhị phân | MNL | Chênh |
|---|---:|---:|---:|
| +10% | −18,8% | −18,5% | 0,38 điểm |
| +20% | −34,9% | −33,8% | 1,14 điểm |
| −20% | +41,9% | +44,9% | 2,99 điểm |

Lệch tối đa **2,99 điểm %**. Ngưỡng đảo chiều `c*` hai mô hình **trùng khít 50,0%**.

{{IMG:MNL2_mnl_vs_logit.png|Hình MNL2 — Trái: mức tuyệt đối khác nhau (do gốc quy chiếu khác). Phải: thay đổi TƯƠNG ĐỐI thì hai đường gần trùng — xác nhận cách trình bày tương đối ở Mục 3.3 là đúng.}}

{{IMG:MNL3_gia_toi_uu.png|Hình MNL3 — Giá tối ưu theo MNL và ngưỡng đảo chiều của hai mô hình.}}

**⇒ Kết luận Mục 3 không phải viết lại.** MNL là bằng chứng độc lập cho cùng kết quả.

### 6.4 Giá trị thật của MNL

MNL **không cho kết luận mới** — nó cho hai thứ khác, đều quan trọng:

1. **Tính nhất quán bắt buộc.** Hai elasticity bị ràng buộc bởi một `β`; đặt sai đôi là `s₀` nhả ra
   số vô lý ngay.
2. **Đổi câu hỏi cho mentor thành câu dễ trả lời.** Thay vì hỏi *"elasticity bao nhiêu?"* (không ai
   biết), hỏi *"bao nhiêu % khách xem giá rồi không đặt?"* — **đội vận hành có sẵn con số này.**

---

## 7. Đối chiếu literature — neo duy nhất cho `ε`

Dữ liệu không cho ước lượng `ε` (Mục 2). Vậy `ε = −2,0` được biện minh bằng gì? **Chỉ có hai neo:**
lập luận kinh tế (Mục 6) và **nghiên cứu đã công bố**.

Bằng chứng GMV +10% của mentor **không phải neo định lượng** — nó đo hiệu quả một thuật toán được
triển khai, lẫn hiệu ứng phía cung, không có nhóm đối chứng, và là **market-level** trong khi ta
cần **firm-level**. Chỉ dùng đối chiếu định tính.

| Nguồn | Năm | Cấp độ | `ε` | Phương pháp |
|---|---:|---|---:|---|
| Cohen, Hahn, Hall, Levitt, Metcalfe (NBER WP 22627) | 2016 | firm | **−1,6** | RD quanh ngưỡng surge |
| Litman — Transit Price Elasticities (VTPI) | 2022 | market | −0,35 | Tổng hợp nhiều nghiên cứu |
| Quy tắc Simpson–Curtin | 1968 | market | −0,33 | Kinh nghiệm ngành |
| Schaller — Taxi demand | 1999 | market | −0,22 | Chuỗi thời gian |

**Kết quả kiểm tra:**

- Firm: **1/1** ước lượng nằm trong dải giả định [−3,0; −1,2] ✅
- Market: **2/3** nằm trong dải [−0,7; −0,3] ✅
- Ghép chéo firm × market: **3/3** cặp cho `s₀` hợp lý (7,4%–12,3%), **bao quanh** giả định 14,3% ✅

{{IMG:LIT1_doi_chieu_literature.png|Hình LIT1 — Forest plot: các ước lượng đã công bố so với dải giả định (vùng xanh), tách riêng cấp độ firm và market.}}

> **⚠️ Cảnh báo bắt buộc.** Các con số literature trên được ghi lại **từ trí nhớ**, chưa trích xuất
> từ file PDF gốc. **Phải tự kiểm chứng trước khi dùng chính thức.** Notebook `09` được thiết kế để
> bảng nguồn nằm ở ô đầu và mọi kết luận tự tính lại khi sửa số.

### 7.1 Một cơ hội đáng chú ý

Cohen 2016 dùng đúng phương pháp mà kế hoạch đang đề xuất: **hồi quy gãy khúc (RD) quanh ngưỡng
surge**. Nghĩa là:

> Nếu mentor xác nhận công thức surge của team **có ngưỡng nhảy bậc**, ta có thể lặp lại đúng thiết
> kế của Cohen 2016 trên dữ liệu lịch sử và **ước lượng `ε` thật** — không cần thí nghiệm, không
> cần nhãn accept/reject.

Đây là con đường khả thi nhất để thoát khỏi việc phải giả định `ε`.

---

## 8. Giới hạn & câu hỏi gửi mentor

### 8.1 Ba giới hạn thật của toàn dự án

| # | Giới hạn | Hệ quả |
|---|---|---|
| **1** | Dữ liệu **không có nhãn accept/reject** | Acceptance model là **mô phỏng dưới giả định**, không phải model học từ dữ liệu. Đã loại trừ 8 hướng thay thế bằng bằng chứng. |
| **2** | **Chi phí biên `c` chưa biết** | Quyết định **CHIỀU** của khuyến nghị giá. Không tự trả lời được. |
| **3** | Model chỉ tái tạo ~62% dao động giá cuối | Phần dư là **nhiễu thật** — đã chứng minh ở tuần 2 (hình B5). |

### 8.2 Câu hỏi — xếp theo giá trị mở khoá

| # | Câu hỏi | Mở khoá | Ưu tiên |
|---|---|---|---|
| 1 | **Chi phí biên mỗi cuốc / tỷ lệ ăn chia tài xế?** | Chốt **CHIỀU** của toàn bộ khuyến nghị giá | 🔴 |
| 2 | **Team tối ưu GMV hay LỢI NHUẬN?** | Chọn giữa kết quả cũ (doanh thu) và bản mới (lợi nhuận) | 🔴 |
| 3 | **Bao nhiêu % khách xem giá rồi KHÔNG đặt? (`s₀`)** | Chốt `β` ⇒ chốt **cả hai** elasticity, hết phải giả định | 🔴 |
| 4 | **Thị phần XanhSM vs đối thủ chính?** | Cùng `s₀` là đủ hiệu chỉnh MNL hoàn chỉnh | 🔴 |
| 5 | Công thức surge có **ngưỡng nhảy bậc** không? | Mở khoá RD như Cohen 2016 ⇒ `ε` **thật** từ dữ liệu lịch sử | 🟠 |
| 6 | Có bộ dữ liệu `giá đã hiện` + `outcome` không? | Mở khoá supervised acceptance | 🟠 |
| 7 | Xin được `--artifact-profile full` không? | Thêm bảng `quotes` (có trường `discount`) — nghi là nguyên nhân sàn nhiễu | 🟡 |

> **Nếu chỉ hỏi được 2 câu: hỏi câu 1 và câu 3.**
> Câu 1 quyết định chiều của khuyến nghị. Câu 3 xoá bỏ giả định elasticity — thứ duy nhất còn đang
> phải đoán.

---

## 9. Kết luận

### 9.1 Đã làm được

| Cấu phần | Kết quả |
|---|---|
| **(iii) Uncertainty** | 3 phương pháp có bảo đảm hữu hạn mẫu · conformal ±30,11% coverage 89,58% · CQR coverage điều kiện tốt nhất |
| **(+) Acceptance GĐ 1** | Logit + WTP đo từ dữ liệu · tăng giá +10% → chấp nhận −19% |
| **(+) Acceptance GĐ 2** | Kiểm chứng nội tại **5/5 mục đạt** |
| **(+) Acceptance GĐ 3** | MNL 3 lựa chọn · `s₀` = 14,3% · khớp logit nhị phân trong 3 điểm % |
| **(+) Acceptance GĐ 4** | Chính sách giá có chi phí biên · ngưỡng đảo chiều theo `ε` |
| **(+) Acceptance GĐ 5** | Tích phân trên phân phối dự đoán — **nối cả 3 cấu phần** |
| **(+) Acceptance GĐ 6** | Backtest 864.360 chuyến |

**9/10 hạng mục xong.** Hạng mục còn lại (supervised acceptance) bị chặn bởi dữ liệu.

### 9.2 Điều đáng nói nhất của tuần 3

Không phải một kết quả, mà là **một sai lầm được phát hiện và sửa**: kết luận *"luôn bán rẻ hơn đối
thủ 24%"* đứng vững qua nhiều vòng kiểm tra vì mọi kiểm tra đều nằm **trong** khung doanh thu. Chỉ
khi đặt câu hỏi *"doanh nghiệp thật tối đa hoá cái gì?"* thì lỗ hổng mới lộ ra.

Bài học: **kiểm tra tính vững bên trong một khung sai vẫn cho kết quả vững — và vẫn sai.**

### 9.3 Hướng tuần 4

| Việc | Chặn bởi |
|---|---|
| Tự kiểm chứng nguồn literature (Mục 7) | Không chặn — cần đọc lại PDF |
| GAM trên **transformed feature space** | Chưa làm — mentor gợi ý trao đổi với anh Khoa |
| **RD quanh ngưỡng surge** ⇒ `ε` thật | Câu hỏi 5 |
| Chốt `β` bằng số thật thay vì suy ngược | Câu hỏi 3 + 4 |
| Supervised acceptance (Nhánh B) | Câu hỏi 6 |
| Nested Logit (nếu nghi ngờ giả định IIA) | Chưa cần |

---

## Phụ lục A — Bản đồ notebook tuần 3

| Notebook | Nội dung | Hình |
|---|---|---|
| `model/uncertainty/01_conformal_prediction.ipynb` | 3 biến thể conformal | `UQ1`, `UQ2` |
| `model/uncertainty/02_quantile_va_CQR.ipynb` | Quantile Regression + CQR | `UQ3`, `UQ4` |
| `model/evaluation/06_plot_uncertainty.ipynb` | Trực quan uncertainty | `U1`–`U4` |
| `model/evaluation/07_so_sanh_model_theo_thoi_gian.ipynb` | Theo góp ý vẽ biểu đồ của mentor | `MT1`–`MT5` |
| ⭐ `model/acceptance/00_TONG_HOP_chay_1_the.ipynb` | **Bản chính acceptance** — `Run All` là ra hết | `AC1`–`AC7` |
| `model/acceptance/05_thu_nghiem_pseudo_label.ipynb` | Bác bỏ rule-based weak labeling | `PL1`, `PL2` |
| `model/acceptance/04_mo_phong_dau_cuoi.ipynb` | Mô phỏng đầu-cuối 864.360 chuyến | `E1`, `E2` |
| ⭐ `model/acceptance/07_chiphi_bien_va_uncertainty.ipynb` | **Chi phí biên + tích phân trên phân phối** | `UA1`–`UA5` |
| `model/acceptance/08_MNL_ba_lua_chon.ipynb` | MNL 3 lựa chọn | `MNL1`–`MNL3` |
| `model/acceptance/09_doi_chieu_literature.ipynb` | Đối chiếu literature | `LIT1` |
| 📊 `model/99_TONG_QUAN_TOAN_DU_AN.ipynb` | **Tổng quan cả 4 mảng** — `Run All` ~1 phút | `TQ1` |
| `analysis/90_sinh_hinh_bao_cao_tuan2.ipynb` | Tái tạo 14 hình báo cáo tuần 2 | `O`,`B`,`M`,`F`,`T` |

## Phụ lục B — Tham số & giả định

| Tham số | Giá trị | Loại |
|---|---:|---|
| `P₀` (chấp nhận tại giá ngang bằng) | 0,50 | **giả định** |
| `ε_firm` | −2,0 (dải −1,2 … −3,0) | **giả định** — neo bằng literature |
| `ε_market` | −0,5 (dải −0,3 … −0,7) | **giả định** — neo bằng literature |
| Thị phần `m` | 50% | **giả định** |
| `c` (chi phí biên / giá đối thủ) | 50% (quét 0–95%) | **giả định** — 🔴 cần mentor |
| `s₀` (khách không đi) | 14,3% | **suy ngược** từ 3 tham số trên |
| `β` | 3,500 | **dẫn xuất** |
| Dịch WTP mưa | +4,61% | ✅ **đo từ dữ liệu** |
| Biên độ WTP theo giờ | 50,0% | ✅ **đo từ dữ liệu** |

## Phụ lục C — Kiểm chứng đã chạy

| Kiểm chứng | Kết quả |
|---|---|
| `P_accept(1.0) == P₀` | ✅ khớp chính xác (assert) |
| Đạo hàm số vs giải tích cho `ε_firm`, `ε_market` (MNL) | ✅ sai lệch < 1e−3 (assert) |
| Nghiệm tối ưu rơi vào biên lưới | ✅ **0/12** tổ hợp |
| `s₀` trong khoảng hợp lý [5%; 30%] | ✅ 8/9 tổ hợp `ε` |
| Tái tạo kết quả cũ (`c` = 0 → 0,760) | ✅ khớp 0,7598 của bản trước |
| Tổng thị phần MNL = 1 | ✅ 1,000000 |
| Coverage 3 phương pháp UQ ≥ 89% | ✅ cả 3 |
