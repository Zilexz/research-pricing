# Báo cáo tổng hợp: Quan hệ Key Feature ↔ Giá & Hệ số nhân — TP.HCM (synthetic)

---

## 1. Tổng quan mối quan hệ các feature

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

## 2. Phân tích mối quan hệ của các key feature đến GIÁ CƠ BẢN

**Giá cơ bản** = `target_shown_price ÷ target_shown_multiplier` — phần giá **trước khi nhân surge**,
phản ánh đúng cước phí theo quãng đường/thời gian/dịch vụ.

### 2.1. Quãng đường & Thời lượng đi — 2 yếu tố áp đảo (~92% importance)

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
  trần R² của model production đầy đủ tính năng dùng để dự đoán giá cơ bản. Đây là bằng chứng định lượng rõ
  ràng nhất: quãng đường + thời lượng gần như là toàn bộ tín hiệu hữu ích hiện có; các feature còn
  lại (giờ, thời tiết, vị trí, lịch sử giá...) gộp lại chỉ đóng góp thêm một phần rất nhỏ.

### 2.2. Khai thác cột giờ để suy ra tắc đường — thời lượng đi trung bình theo khung giờ

Mục 2.1 cho thấy thời lượng đi là 1 trong 2 driver chính của giá cơ bản. Câu hỏi tiếp theo: bản
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

**Lưu ý quan trọng — không mâu thuẫn với mục 2.3/2.4:** quy luật tắc đường theo giờ là **có thật**
và đúng chiều (cao điểm chậm hơn), nhưng khi hồi quy `thời lượng đi ~ giờ + thứ + thời tiết`, mô
hình chỉ giải thích được **R² ≈ 3,5%** tổng phương sai của thời lượng đi. Nói cách khác: biết giờ
trong ngày giúp đoán *xu hướng trung bình* của tắc đường (biên độ ~12-14%), nhưng **không đủ để
đoán chính xác thời lượng của một chuyến cụ thể** — phần lớn biến thiên thời lượng vẫn là nhiễu
ngẫu nhiên riêng từng chuyến (tình trạng giao thông tức thời, lựa chọn tuyến của tài xế...). Đây
chính là lý do mục 2.4 xác nhận thời lượng đi "tự nó ngẫu nhiên" dù có quy luật theo giờ ở tầng vĩ mô.

### 2.3. Giờ & Thời tiết — gần như KHÔNG ảnh hưởng trực tiếp (khi đã kiểm soát quãng đường)

{{IMG:B3_B4_hour_weather_vs_baseprice.png|Hình B3-B4 — Cùng dải quãng đường 4-6km, giá cơ bản gần như phẳng theo giờ và theo thời tiết. Biên độ chỉ vài %, quá nhỏ để có ý nghĩa thực tế so với biên độ ~32% của thời lượng đi.}}

Đây là điểm dễ hiểu nhầm nhất: giờ/thời tiết **có** ảnh hưởng đến giá **cuối** (qua kênh hệ số
nhân — xem mục 4), và cũng ảnh hưởng **gián tiếp** đến giá cơ bản thông qua thời lượng đi (mục
2.2), nhưng **không** có một khoản phụ phí "theo giờ" hay "theo thời tiết" nào được cộng thẳng vào
giá cơ bản.

### 2.4. ⭐ Phát hiện quan trọng nhất — nhiễu ngẫu nhiên THẬT SỰ, không phải do thiếu kiểm soát

Câu hỏi: liệu phần dao động còn lại của giá cơ bản có phải do dải quãng đường "chưa đủ hẹp"? Kiểm
tra bằng cách thu hẹp dần dải quãng đường (cùng 1 tuyến, cùng 1 loại xe) xuống tới mức cực đoan:

{{IMG:B5_cv_khong_giam.png|Hình B5 — Hệ số biến thiên (CV) của giá cơ bản giữ nguyên ~20% dù thu hẹp dải quãng đường từ 2.000 mét xuống còn 2 MÉT. Chứng minh đây là nhiễu ngẫu nhiên thật sự gắn với từng lần báo giá, không phải do đo lường/kiểm soát chưa đủ chặt.}}

**Kết luận:** cùng tuyến, cùng xe, quãng đường giống hệt nhau tới từng mét — giá cơ bản vẫn dao
động ~20%. Đây là bằng chứng mạnh nhất cho sàn nhiễu.

### 2.5. Permutation importance — xác nhận bằng model thực tế

{{IMG:B6_permutation_baseprice.png|Hình B6 — Trong phạm vi cùng tuyến+xe+quãng đường, thời lượng đi gần như là feature DUY NHẤT model thực sự dùng để dự đoán giá cơ bản. Giờ, thứ, thời tiết, lịch sử giá... đều có importance gần 0.}}

---

## 3. Phân tích mối quan hệ của các key feature đến HỆ SỐ NHÂN

**Hệ số nhân** (`target_shown_multiplier`) — phần điều chỉnh giá theo cung–cầu, dao động 0,85–1,80.

### 3.1. Cung–cầu — driver mạnh nhất

{{IMG:M1_M2_imbalance_lastmult.png|Hình M1-M2 — Hệ số nhân tăng gần như tuyến tính theo market imbalance (cầu − cung) và theo hệ số nhân quan sát gần nhất. Đây là 2 driver mạnh nhất.}}

- **Market imbalance:** cầu tăng, cung giảm → mất cân bằng tăng → hệ số nhân tăng — đúng cơ chế
  kinh tế học cung–cầu.
- **Hệ số nhân quan sát gần nhất:** tương quan rất mạnh (~0,95) — vì hệ số nhân **dai dẳng theo
  thời gian**, ít thay đổi đột ngột trong khoảng vài phút.

### 3.2. Giờ trong ngày — ảnh hưởng cực mạnh (khác hẳn giá cơ bản)

{{IMG:M3_M4_hour_weather_vs_multiplier.png|Hình M3-M4 — Hệ số nhân dao động rất mạnh theo giờ (đỉnh giờ đi làm sáng 6-9h và tan làm 17-19h), biên độ ~50%. Thời tiết ảnh hưởng yếu hơn nhiều nhưng vẫn có xu hướng rõ (mưa → hệ số nhân cao hơn).}}

Giờ tác động lên hệ số nhân **qua kênh cung–cầu**: giờ cao điểm → cầu tăng vọt → mất cân bằng tăng
→ hệ số nhân tăng. Đây là chuỗi nhân quả đã kiểm chứng ở phần 1.4.

### 3.3. ⭐ Phát hiện quan trọng nhất — hệ số nhân gần như là "giá trị thị trường dùng chung"

Kiểm tra: trong **cùng 1 khu vực + cùng 1 khung 5 phút**, hệ số nhân có còn dao động nhiều không?

{{IMG:M5_hang_so_thi_truong.png|Hình M5 — Độ lệch chuẩn hệ số nhân trong cùng khu vực + cùng khung 5 phút chỉ còn ~20% so với toàn bộ dữ liệu. Xác nhận: hệ số nhân là giá trị dùng CHUNG cho cả thị trường tại thời điểm đó, không phải nhiễu riêng từng khách.}}

**Kết luận:** khác hẳn giá cơ bản (vẫn dao động ~20% dù kiểm soát chặt tới 2 mét), hệ số nhân **gần
như là hằng số** trong phạm vi khu vực + khung thời gian ngắn — đây là lý do dữ liệu giải thích
được tới 96,6% chênh lệch của nó.

### 3.4. Kết luận phần 3

> **Hệ số nhân được quyết định bởi cung–cầu (mạnh nhất) và giờ trong ngày (qua kênh cung–cầu)** —
> cả 2 đều đo lường được tốt trong dữ liệu. Vì bản chất là giá trị cấp thị trường (không phải nhiễu
> per-quote), dữ liệu hiện có giải thích được tới **~96,6%** chênh lệch của nó — gần như tất định.
> ⚠️ Lưu ý: con số này bị ảnh hưởng bởi việc dữ liệu synthetic cung cấp sẵn chỉ số cung–cầu gần với
> công thức sinh surge — trong production thật (không có sẵn chỉ số này), độ chính xác sẽ thấp hơn.

---

## 4. Phân tích mối quan hệ của các key feature đến GIÁ CUỐI CÙNG

**Giá cuối** (`target_shown_price`) = Giá cơ bản × Hệ số nhân — con số khách hàng thực sự nhìn thấy
và trả tiền.

### 4.1. Giá cuối "thừa hưởng" đặc điểm của cả 2 thành phần

{{IMG:F1_amplitude_gia_cuoi.png|Hình F1 — Cùng dải quãng đường, biên độ dao động của giá cuối theo giờ bám rất sát hình dạng của hệ số nhân (đỉnh giờ cao điểm), trong khi giá cơ bản gần như phẳng. Chứng minh trực tiếp: biến động giá cuối theo giờ chủ yếu đến từ hệ số nhân.}}

### 4.2. So sánh Boston vs TP.HCM — xác nhận đúng giả thuyết mentor

{{IMG:F2_boston_vs_hcm.png|Hình F2 — TP.HCM bị ảnh hưởng bởi giờ và thời tiết mạnh hơn Boston 70-97 lần (đo trên cùng phương pháp, cùng dải quãng đường).}}

Boston (dữ liệu thật, tỷ lệ surge chỉ 3,3%) gần như không thể hiện ảnh hưởng giờ/thời tiết lên giá
(giá phẳng tuyệt đối theo giờ). TP.HCM (synthetic, tỷ lệ surge 81,7%) thể hiện rất rõ — vì dữ liệu
mô phỏng đầy đủ cơ chế giờ → cầu → surge → giá mà Boston thiếu (thiếu cột thời lượng và tín hiệu
cung–cầu).

### 4.3. Ví dụ cụ thể — cùng điều kiện, giá cuối vẫn dao động rất mạnh

{{IMG:F3_phanbo_cungdieukien.png|Hình F3 — Cùng tuyến, cùng loại xe, cùng quãng đường (5,4-5,6km): phân bố giá cuối trải rộng hơn nhiều so với phân bố giá cơ bản — phần mở rộng thêm này chủ yếu do hệ số nhân đóng góp.}}

### 4.4. Tổng hợp — bảng phân rã đóng góp

| Nguồn đóng góp vào chênh lệch giá cuối (cùng dải quãng đường) | Tỷ trọng |
|---|---:|
| Giá cơ bản (quãng đường + thời lượng, phần lớn là nhiễu ~81%) | ~61% |
| Hệ số nhân (cung–cầu + giờ, gần tất định ~96,6%) | ~31% |
| Phần chồng lấn (2·Cov — chuyến giá cao thường rơi vào giờ surge cao) | ~8% |
| **Không giải thích được (nhiễu tổng hợp)** | **~65%** |

### 4.5. Kết luận phần 4

> **Giá cuối chịu tác động của cả 2 kênh — trực tiếp qua giá cơ bản (quãng đường/thời lượng) và
> qua hệ số nhân (cung–cầu/giờ) — nhưng 2 kênh này có "chất lượng dữ liệu" hoàn toàn khác nhau.**
> Hệ số nhân gần như tất định (96,6%), còn giá cơ bản có nhiễu per-quote thật sự (~81%). Vì vậy
> dù model hệ số nhân có tốt đến đâu, **độ chính xác của giá cuối vẫn bị giới hạn bởi nhiễu trong
> giá cơ bản** — đây là bottleneck chính, đã xác nhận bằng nhiều phương pháp độc lập (phân rã
> phương sai, permutation importance, kiểm định thu hẹp quãng đường tới 2 mét).
