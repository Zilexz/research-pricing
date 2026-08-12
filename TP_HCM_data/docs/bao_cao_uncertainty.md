# Uncertainty Quantification — báo cáo tổng hợp

> Cấu phần **(iii)** của đề bài: *lượng hoá độ bất định của dự đoán giá đối thủ.*
>
> Tổng hợp từ 6 notebook trong `model/uncertainty/`. Mọi con số tính lại trực tiếp từ
> `uq_pred_*.parquet` và `qr_pred_da_muc_*.parquet`, ngày 10/08/2026.

---

## Tóm tắt trong một trang

Model giá cho MAE **18.048đ** (MAPE 14,74%, R² 0,730) — nhưng một con số điểm không đủ để ra
quyết định định giá. Cấu phần này biến `p̂` thành **một khoảng kèm bảo đảm**.

**Đã triển khai 3 phương pháp × 3 mức tin cậy**, tất cả đều có bảo đảm hữu hạn mẫu trừ QR thô.
Ở mức 90%:

| Phương pháp | Coverage | Độ rộng TB | Lệch tối đa giữa band |
|---|---:|---:|---:|
| **Conformal chuẩn hoá** | 89,55% | **72.630đ** | 7,28 điểm ❌ |
| QR thô | 89,09% | 75.783đ | 2,75 điểm |
| **CQR** | 89,54% | 76.449đ | **1,39 điểm** ✅ |

**Phát hiện quan trọng nhất:** coverage tổng thể 89,55% nhìn thì đạt danh mục, nhưng **che mất**
chuyện band giá >300k chỉ đạt **82,72%**. Nhóm khách đắt tiền nhất bị phục vụ tệ nhất.

**Khuyến nghị:** giữ Conformal chuẩn hoá nhưng hiệu chỉnh **riêng theo `band giá × cao điểm`**
(Mondrian). Lệch tối đa xuống **0,83 điểm**, chỉ tốn **+0,46%** độ rộng, không cần train lại model.

**Về việc thu hẹp khoảng:** đã thử 5 cách hiệu chỉnh × 7 cách chia nhóm, tốt nhất chỉ được
**0,43%**. Đường "giảm uncertainty" đã cạn — muốn khoảng hẹp hơn thì **phải cải thiện model điểm**
(quan hệ 1:1). Xem mục 6b.

---

## 1. Bài toán

Dự đoán 100.000đ mà giá thật có thể rơi bất kỳ đâu trong 70.000–130.000đ là chuyện rất khác so
với 95.000–105.000đ. Quyết định định giá cần biết **biên độ sai**, không chỉ điểm giữa.

Yêu cầu đặt ra cho khoảng dự đoán:

| # | Yêu cầu | Vì sao |
|---|---|---|
| 1 | **Có bảo đảm** — nói 90% thì phải đạt ~90% | Không có bảo đảm thì con số vô nghĩa |
| 2 | **Càng hẹp càng tốt** | Khoảng rộng thì đúng nhưng vô dụng |
| 3 | **Đều giữa các nhóm** | Coverage tổng thể đẹp mà một nhóm hụt 7 điểm là đang giấu vấn đề |

Yêu cầu 3 hay bị bỏ qua nhất, và cũng là chỗ phát hiện được vấn đề lớn nhất.

## 2. Thiết kế dữ liệu

| Tập | Số chuyến | Dùng làm gì |
|---|---:|---|
| `train` | 4.641.799 | Train model giá |
| **`calibration`** | **615.908** | **Hiệu chỉnh khoảng — không train** |
| `test` | 864.360 | Đánh giá cuối |
| `validation` | 774.984 | Early stopping |

Tách riêng `calibration` là **điều kiện bắt buộc** để conformal có bảo đảm hữu hạn mẫu. Nếu hiệu
chỉnh trên chính tập đã train thì sai số bị đánh giá thấp và khoảng sẽ hẹp giả tạo.

Sinh bởi `model/train/07_sinh_du_lieu_UQ.ipynb`.

## 3. Ba phương pháp

### 3.1 Conformal chuẩn hoá

Trên calibration, đo sai số **tương đối** từng chuyến:

```
e_i = |p̂_i − y_i| / p̂_i
q   = phân vị α của {e_i}
khoảng = [p̂ × (1 − q),  p̂ × (1 + q)]
```

**Vì sao chia cho `p̂`:** nếu dùng sai số tuyệt đối thì mọi chuyến nhận cùng một khoảng tính bằng
đồng — vô lý, vì chuyến 300k sai 30k là bình thường còn chuyến 50k sai 30k là thảm hoạ.

**Bảo đảm:** hữu hạn mẫu, phân phối tự do. Không cần giả định sai số phân phối chuẩn, không cần
model tốt. Điều kiện duy nhất là chuyến calibration và chuyến mới **hoán đổi được**.

Kết quả: `q = ±30,09%` ở mức 90%.

### 3.2 Quantile Regression

Train model riêng cho từng phân vị bằng **pinball loss**:

```
L_α(y, q̂) = α·(y − q̂)      nếu y ≥ q̂
            (1−α)·(q̂ − y)   nếu y < q̂
```

Với `α = 0,95`, dự đoán thấp bị phạt nặng gấp 19 lần dự đoán cao → model tự đẩy đầu ra lên sát
phân vị 95%. Khoảng 90% là `[q05, q95]`.

`model/train/06_train_quantile_da_muc.ipynb` train **7 phân vị × 3 tháng = 21 model**
(0,05 · 0,10 · 0,15 · 0,50 · 0,85 · 0,90 · 0,95).

**Không có bảo đảm nào.** Coverage đạt được là kết quả model học tốt, không phải tính chất toán
học — nên nó hụt danh mục ~1 điểm ở cả ba mức.

### 3.3 CQR — ghép hai thứ lại

Lấy khoảng của QR rồi hiệu chỉnh bằng cơ chế conformal. Trên calibration:

```
E_i = max( q̂_lo(x_i) − y_i ,  y_i − q̂_hi(x_i) )
Q   = phần tử thứ ⌈(n+1)·α⌉ của {E_i} đã sắp xếp
khoảng = [q̂_lo(x) − Q,  q̂_hi(x) + Q]
```

`E` âm nghĩa là khoảng thừa, dương nghĩa là thiếu. Nếu QR vốn bao thừa thì `Q` âm và CQR **thu
hẹp** khoảng — không phải lúc nào cũng nới ra.

**Vì sao vừa thích ứng vừa có bảo đảm:** hình dạng khoảng vẫn do QR quyết định (chuyến khó thì
rộng, chuyến dễ thì hẹp); CQR chỉ dịch đều hai đầu một lượng `Q` chung.

Ở đây `Q = +333đ` tại mức 90% — chỉ **0,4%** độ rộng. QR vốn đã gần đạt, CQR chỉ chỉnh một chút.
Nhưng chính "một chút" đó biến QR từ **không bảo đảm** thành **có bảo đảm**.

### 3.4 Khác biệt cốt lõi

| | Conformal | QR | CQR |
|---|---|---|---|
| Khoảng đến từ | Sai số lịch sử của model điểm | Model học thẳng hai đầu | QR + hiệu chỉnh |
| Mỗi chuyến | Cùng tỷ lệ `±q` | **Riêng** | **Riêng** |
| Đối xứng quanh `p̂` | ✅ luôn | ❌ không cần | ❌ không cần |
| Bảo đảm hữu hạn mẫu | ✅ | ❌ | ✅ |
| Cần train thêm | Không | 21 model | 21 model |

---

## 4. Kết quả tổng thể

Ba phương pháp × ba mức tin cậy, đo trên 864.360 chuyến test:

| Phương pháp | Mức | Coverage | Lệch | Độ rộng TB | Trượt trên | Trượt dưới |
|---|---:|---:|---:|---:|---:|---:|
| Conformal | 70% | 69,73% | −0,27 | 45.320đ | 17,63% | 12,64% |
| Conformal | 80% | 79,60% | −0,40 | 56.118đ | 13,00% | 7,40% |
| **Conformal** | **90%** | **89,55%** | −0,45 | **72.630đ** | 7,83% | 2,62% |
| QR thô | 70% | 68,88% | −1,12 | 47.406đ | 16,25% | 14,88% |
| QR thô | 80% | 78,89% | −1,11 | 58.772đ | 11,11% | 10,01% |
| QR thô | 90% | 89,09% | −0,91 | 75.783đ | 5,79% | 5,12% |
| CQR | 70% | 69,26% | −0,74 | 47.684đ | 16,10% | 14,64% |
| CQR | 80% | 79,44% | −0,56 | 59.284đ | 10,90% | 9,66% |
| **CQR** | **90%** | **89,54%** | −0,46 | 76.449đ | 5,65% | 4,81% |

Đọc bảng này thì Conformal thắng: coverage tương đương CQR, khoảng **hẹp hơn 5,0%**.

**Đó chính là kết luận của tuần 3 — và nó sai.** Lý do ở mục 5.

### Cái giá của mức tin cậy

| Mức | Độ rộng | So với 90% | Tỷ lệ trượt |
|---|---:|---:|---:|
| 70% | 45.320đ | −37,6% | 30,3% |
| 80% | 56.118đ | −22,7% | 20,4% |
| 90% | 72.630đ | — | 10,5% |

Hạ từ 90% xuống 80% làm khoảng hẹp đi gần một phần tư, đổi lại cứ 5 chuyến thì 1 chuyến nằm
ngoài khoảng thay vì 1/10.

---

## 5. Coverage điều kiện — chỗ vấn đề thật

> *"Các em đưa ra các % uncertainty nhưng trong report thường average out. Như vậy nó làm mất đi
> độ insight."* — feedback tuần 3 của mentor

### 5.1 Phân rã theo band giá — Conformal, mức 90%

| Band giá dự đoán | Số chuyến | Coverage | Độ rộng trung vị | Trượt trên | Trượt dưới |
|---|---:|---:|---:|---:|---:|
| <50k | 10.821 | **92,40%** | 26.756đ | 7,07% | 0,53% |
| 50–100k | 264.201 | 90,31% | 50.904đ | 7,26% | 2,43% |
| 100–150k | 409.883 | 89,15% | 72.505đ | 8,09% | 2,76% |
| 150–200k | 149.324 | 89,27% | 100.346đ | 8,03% | 2,69% |
| 200–300k | 28.875 | 89,09% | 130.627đ | 8,44% | 2,47% |
| **>300k** | **1.256** | **82,72%** ⚠️ | 196.603đ | 11,78% | 5,49% |

Lệch **7,28 điểm** giữa hai đầu. Đã kiểm bằng sai số lấy mẫu: band >300k có `±1,96·SE = 2,09
điểm`, lệch 7,28 điểm ⇒ **thật**, không phải nhiễu do mẫu ít.

### 5.2 Gốc vấn đề: một tỷ lệ cho tất cả

Độ rộng **tuyệt đối** chênh 7,3 lần giữa band thấp và cao. Nhưng độ rộng **tương đối** thì
**60,2% ở cả 6 band, không lệch một số lẻ nào** — vì Conformal áp một `q` duy nhất.

Sai số tương đối thật của band >300k lớn hơn thế:

| Band | `q` thật cần | `q` được cấp | Thiếu |
|---|---:|---:|---:|
| <50k | ±27,69% | ±30,09% | thừa 2,40 |
| 50–100k | ±29,62% | ±30,09% | thừa 0,47 |
| 100–150k | ±30,45% | ±30,09% | thiếu 0,36 |
| 150–200k | ±30,16% | ±30,09% | ≈ đủ |
| 200–300k | ±30,64% | ±30,09% | thiếu 0,55 |
| **>300k** | **±41,01%** | ±30,09% | **thiếu 10,92** |

Bốn band giữa gần như không sao. Toàn bộ vấn đề nằm ở hai đầu, đặc biệt band đắt nhất.

### 5.3 Đây là lỗi của phương pháp, không phải của dữ liệu

Câu hỏi tiếp: cả ba phương pháp có cùng hỏng không? Nếu có thì đổi phương pháp vô ích.

Lệch coverage tối đa giữa các band, đơn vị **điểm %** — càng nhỏ càng đều:

| Phương pháp | Mức 70% | Mức 80% | Mức 90% | Trung bình |
|---|---:|---:|---:|---:|
| Conformal chuẩn hoá | 10,05 | 8,26 | 7,28 | **8,53** |
| QR thô | 3,28 | 3,73 | 2,75 | 3,25 |
| **CQR** | 3,28 | 3,57 | **1,39** | **2,75** |

**Không.** QR và CQR gần như phẳng vì chúng sinh phân vị **riêng cho từng chuyến** nên tự thích
ứng. Chỉ Conformal hỏng, và hỏng vì đúng cái giả định "một tỷ lệ cho tất cả".

**Điều này sửa lại kết luận tuần 3.** Lúc đó chọn Conformal dựa trên coverage tổng thể và độ
rộng — đúng kiểu đánh giá mentor phê bình.

### 5.4 Sai số bất đối xứng

Coverage chỉ nói *"10,5% rơi ra ngoài"*, không nói **rơi về phía nào**. Với định giá thì hai
chiều khác hẳn nhau.

| Phương pháp (90%) | Trượt trên | Trượt dưới | Tỷ lệ |
|---|---:|---:|---:|
| Conformal | 7,83% | 2,62% | **3,0×** |
| QR thô | 5,79% | 5,12% | 1,1× |
| CQR | 5,65% | 4,81% | 1,2× |

Nếu khoảng cân đối thì mỗi phía phải trượt ~5%. Conformal lệch hẳn: **giá thật vượt cận trên
nhiều gấp 3 lần** rơi xuống dưới.

Nguyên nhân: giá có **đuôi lệch phải** — surge chỉ nhân lên, không nhân xuống, và giá có sàn.
Khoảng đối xứng `p̂ × (1 ± q)` về mặt cấu trúc không diễn đạt được dạng lệch này. QR và CQR
không bị vì khoảng của chúng không cần đối xứng.

**Hệ quả vận hành:** nếu dùng cận trên để định giá cạnh tranh, sẽ bị đối thủ vượt giá thường
xuyên hơn con số coverage gợi ý.

---

## 6. Cách sửa — Mondrian conformal

Thay vì một `q` chung, hiệu chỉnh `q` **riêng cho từng band**. Không train lại model, chỉ lưu
thêm 6 con số thay vì 1.

| Band | Coverage trước | Coverage sau |
|---|---:|---:|
| <50k | 92,40% | 90,43% |
| 50–100k | 90,31% | 89,81% |
| 100–150k | 89,15% | 89,54% |
| 150–200k | 89,27% | 89,35% |
| 200–300k | 89,09% | 89,67% |
| **>300k** | **82,72%** | **91,24%** |

| | Trước | Sau |
|---|---:|---:|
| Lệch tối đa | 7,28 điểm | **1,24 điểm** (−83%) |
| Coverage tổng thể | 89,55% | 89,61% |
| Độ rộng TB | 72.630đ | 73.012đ (**+0,53%**) |

### So hai cách sửa

| | Cách | Lệch tối đa | Chi phí |
|---|---|---:|---|
| **A** ⭐ | Conformal + Mondrian | **1,24 điểm** | +0,53% độ rộng, lưu thêm 5 số |
| **B** | Chuyển sang CQR | 1,39 điểm | +5,3% độ rộng, train 21 model |

**Chọn A.** Vừa đều hơn một chút, vừa rẻ hơn 10 lần về độ rộng, và giữ nguyên hạ tầng hiện có.

Cùng kỹ thuật đã thử theo chiều **quãng đường** — kết quả tương tự, nhưng band giá là chiều
tạo khác biệt lớn nhất.

---

## 6b. Thu hẹp khoảng mà vẫn giữ độ tin cậy — **không làm được**

> *"Nên improve model hay giữ model nhưng tìm cách giảm uncertainty?"* — mentor

Đã thử **5 cách hiệu chỉnh × 7 cách chia nhóm**. Kết quả tốt nhất thu hẹp **0,43%**, và cái đó
còn kèm tụt coverage xuống 89,14%.

| Cách | Coverage | Rộng TB | So với gốc |
|---|---:|---:|---:|
| A. Gốc — đối xứng, q chung | 89,55% | 72.630đ | — |
| B. Bất đối xứng (hai phân vị riêng) | 89,79% | 73.729đ | +1,51% |
| C. Mondrian theo band giá | 89,61% | 73.012đ | +0,53% |
| D. Mondrian theo độ trễ | 89,56% | 72.645đ | +0,02% |
| **E. Chuẩn hoá theo độ khó học được** | 89,14% | **72.321đ** | **−0,43%** |
| F. Bất đối xứng + độ khó | 89,34% | 73.301đ | +0,92% |

### Vì sao cạn — bốn bằng chứng

| # | Bằng chứng | Con số |
|---|---|---|
| 1 | Dư địa lý thuyết **có thật** | Biết trước độ khó từng chuyến ⇒ hẹp được **−50,3%** (36.096đ) |
| 2 | Nhưng độ lớn sai số **không dự đoán được** | Tương quan hạng **0,34**; `σ̂` biến thiên 2,3 lần trong khi sai số thật biến thiên **17 lần** |
| 3 | Thêm feature **không giúp** | 22 feature (có `history_60m_price_std` + toàn bộ tín hiệu cung–cầu) cho 0,3395 — **kém hơn** 8 feature (0,3411) |
| 4 | Lý do gốc | Feature áp đảo là **chính giá dự đoán** (importance 0,126 vs 0,033). Ba cái kế tiếp — `quote_duration`, `quote_distance`, `base_pred` — cũng chỉ là biến thể của độ lớn giá. Mà conformal *chuẩn hoá* đã chia cho `p̂` rồi |

**Phần sai số dự đoán được đã bị khai thác hết. Phần còn lại là nhiễu thật.**

### Chia nhóm: không làm hẹp, nhưng làm đều

| Cách chia nhóm | Số nhóm | Rộng | Lệch band tối đa |
|---|---:|---:|---:|
| Không chia (q chung) | 1 | — | 7,28 điểm |
| Band giá | 6 | +0,53% | 1,24 điểm |
| **Band giá × cao điểm** | 12 | +0,46% | **0,83 điểm** ⭐ |
| Band × cao điểm × mưa | 24 | +0,35% | **7,28 điểm** ⚠️ |

⚠️ **Bẫy chia quá mịn:** 24 nhóm tụt về đúng mức không chia. Band >300k chỉ có ~900 chuyến
calibration, chia tiếp cho 4 tổ hợp thì mỗi nhóm dưới ngưỡng 200 mẫu, buộc dùng `q` chung —
đúng nhóm cần nhất lại mất quyền lợi.

**Cấu hình nên dùng: `band giá × cao điểm`** — tốt hơn band đơn thuần, chi phí như nhau.

### Hai đòn bẩy thật sự

| Đòn bẩy | Hiệu quả | Bản chất |
|---|---|---|
| **Cải thiện model điểm** | Quan hệ **1:1** — giảm sai số 10% thì khoảng hẹp 10% | Cải thiện thật |
| Hạ mức tin cậy 90% → 80% | −22,7% độ rộng | **Đánh đổi** — trượt từ 10,4% lên 20,4% |

### Trả lời mentor

**Phải improve model.** Đường giảm uncertainty đã cạn — đo hết rồi, chỉ còn 0,43% và không đáng.

Điều này khớp kết luận tuần 2: 4 thuật toán chênh nhau 1,9%, fine-tune Optuna không cải thiện.
Model đã chạm trần **của bộ dữ liệu này**. Muốn tiến thì cần **dữ liệu mới về chất**, không phải
thêm feature từ nguồn cũ hay thuật toán mới.

Chi tiết: `uncertainty/06_thu_hep_khoang.ipynb`, hình `TH1`–`TH5`.

---

## 7. Phân rã theo thời gian

> *"có những đoạn critical ví dụ như rush hour hay demand surge và đo đạc được mức độ sai số ở
> những thời điểm nhạy cảm một cách trực quan anh nghĩ khá là quan trọng."* — mentor

Mentor nêu ba kịch bản, MAE trung bình có thể bằng nhau nhưng giá trị vận hành khác hẳn:

| Kịch bản | Nghĩa |
|---|---|
| Uncertainty đều 30% | Trung tính |
| 10% cao điểm · 40% giờ thường | **Tốt** — chắc chắn ở chỗ quan trọng |
| 40% cao điểm · 10% giờ thường | **Tệ** — mù ở đúng chỗ cần thấy |

**Model thuộc kịch bản 1.** Độ rộng khoảng 60,2% ở cả hai khung, chênh 0,00%.

| | Số chuyến | MAPE | MAE | Coverage |
|---|---:|---:|---:|---:|
| Cao điểm (7–9h, 17–19h) | 229.820 | 14,74% | 19.703đ | 89,61% |
| Giờ thường | 634.540 | 14,75% | 17.449đ | 89,53% |

Biên độ MAPE qua 24 giờ chỉ **3,8%**. Lệch coverage tối đa theo giờ **1,33 điểm**.

**Chỗ dễ hiểu nhầm:** MAE tuyệt đối chênh **67%** (12.655đ lúc 3h → 21.186đ lúc 18h). Nhưng đó
là vì **giá cao hơn**, không phải model kém đi — sai số tương đối phẳng.

**Đợt demand surge** (bucket 30 phút có hệ số nhân ≥ phân vị 90, tức ≥1,367): 53/528 bucket.
Sai số ở đó **giảm** 1,1% (14,60% vs 14,76%), coverage 88,45%.

→ **Model không fail ở thời điểm nhạy cảm. Nó fail ở band giá cao.**

---

## 8. Kết luận và khuyến nghị

### Chốt cấu hình

```
khoảng dự đoán = p̂ × (1 ± q_band)

q_band:  <50k     ±27,7%
         50–100k  ±29,6%
         100–150k ±30,5%
         150–200k ±30,2%
         200–300k ±30,6%
         >300k    ±41,0%
```

Coverage 89,61% ở danh mục 90%, lệch tối đa giữa band 1,24 điểm, độ rộng TB 73.012đ.

### Ba điều nên nói khi trình bày

1. **Không báo coverage tổng thể một mình.** Luôn kèm phân rã theo band — 89,6% tổng thể che mất
   band >300k chỉ 82,7%.
2. **Vấn đề band giá là lỗi phương pháp, không phải dữ liệu.** Kiểm 9 tổ hợp mới kết luận được.
3. **Khoảng hiện tại rộng ±30%** — đó là độ bất định thật của model, không phải lựa chọn tồi.
   Chia nhóm theo giờ/thời tiết/quãng đường đều không làm hẹp hơn.

### Hạn chế còn lại

| | Hạn chế | Hướng xử lý |
|---|---|---|
| 1 | Khoảng vẫn **đối xứng** nên không bắt được đuôi lệch phải (trượt trên 3× trượt dưới) | Chuyển sang CQR, hoặc Mondrian hai phía riêng |
| 2 | Band >300k chỉ có **1.256 chuyến** test — `q` riêng của nó ước lượng từ mẫu nhỏ | Gộp band hoặc dùng shrinkage |
| 3 | Mốc chia band (50k/100k/150k/200k/300k) do nhóm **tự chọn** | Cần hỏi mentor mốc chuẩn của team |
| 4 | Chưa kiểm coverage theo **độ hiếm của tuyến** | Chỉ có 9 tuyến nên khó tách nhóm hiếm |

---

## Phụ lục — file nào ở đâu

| Notebook | Nội dung | Hình |
|---|---|---|
| `uncertainty/00_TONG_QUAN` | Cơ chế ba phương pháp, trực quan hoá | `VQ1`–`VQ7` |
| `uncertainty/01_conformal_chuan_hoa` | Phương pháp 1 từ đầu đến cuối + Mondrian | `UQ1` `UQ2` · `TC1`–`TC4` · `MD1`–`MD6` · `BG1`–`BG4` |
| `uncertainty/02_quantile_regression` | Phương pháp 2 từ đầu đến cuối | `QR1`–`QR4` |
| `uncertainty/03_CQR` | Phương pháp 3 từ đầu đến cuối | `CQ1`–`CQ4` |
| `uncertainty/04_SO_SANH` | 3 pp × 3 mức, tổng thể + theo band | `UQ3` `UQ4` · `PM1`–`PM4` · `BM1`–`BM3` · `SS1`–`SS5` |
| `uncertainty/06_thu_hep_khoang` | Thử 5 cách × 7 nhóm để thu hẹp khoảng | `TH1`–`TH5` |
| `uncertainty/05_PHAN_RA_theo_thoi_gian` | Sai số ở thời điểm nhạy cảm | `TT1`–`TT4` |
| `train/06_train_quantile_da_muc` | 21 model quantile | — |
| `train/07_sinh_du_lieu_UQ` | Sinh `uq_pred_*` và `qr_pred_*` | — |

Bản cũ (10 notebook trước khi sắp xếp lại) ở `uncertainty/_archive/`.
