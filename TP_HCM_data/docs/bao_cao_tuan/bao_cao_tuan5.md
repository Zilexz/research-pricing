# Báo cáo tuần 5 — hai hướng giảm sai số ở nhóm chuyến hiếm

Câu hỏi của tuần: có thể giảm sai số ở nhóm chuyến dài và giá cao mà không làm kết quả chung tệ đi đáng kể hay không?

Hai hướng mentor giao: ① đặt trọng số cao hơn cho chuyến hiếm khi train; ② kiểm định lại lợi thế của GAM qua nhiều lần chia thời gian, nếu ổn định thì ghép GAM với GBM theo quãng đường.

Dữ liệu: 216.090 chuyến test độc lập, độ trễ 5 phút, ba tháng 2026-01 → 2026-03. Dữ liệu synthetic.

---

## Tóm tắt kết quả

Mốc để so: `>15 km` 17,52% · `>300k` 23,67% · toàn tập 14,65%.

| Hướng | `>15 km` | `>300k` | Toàn tập | Kết luận |
|---|---|---|---|---|
| ① Trọng số, gán theo giá, `w=10` | 21,69% *(−4,17)* | 20,44% *(+3,23)* | −0,063 | Đạt tiêu chí nhưng có đánh đổi |
| ① Trọng số, gán theo quãng đường | 18,51% *(−0,98)* | 23,53% *(+0,14)* | −0,009 | Không dùng được |
| ② Ghép GAM–GBM | 15,61% *(+2,50)* | 22,49% *(+1,55)* | +0,014 | Không phải đánh đổi |

Dấu dương là tốt lên, đơn vị điểm phần trăm.

---

## 1. Ràng buộc phương pháp

> *"Khi đánh giá, các em cần giữ nguyên nhóm chuyến giữa các model. Không nên để mỗi model tự chia nhóm theo giá mà chính nó dự đoán."*

Mọi nhóm trong báo cáo chia theo giá thật và quãng đường — hai đại lượng không phụ thuộc model nào. Mức ảnh hưởng đo riêng ở `06_NHOM_CO_DINH.ipynb`:

| Cách chia nhóm `>300k` | Số chuyến | Lợi thế đo được của GAM |
|---|---:|---:|
| Giá thật — trung lập | 869 | +1,65 điểm |
| Giá Hybrid dự đoán | 327 | +4,02 điểm |
| Giá GAM dự đoán | 330 | +3,13 điểm |

Chia theo giá model tự dự đoán làm lợi thế phồng 2,45 lần; chỉ 224 chuyến có mặt ở cả hai định nghĩa. Ngoại lệ có chủ ý: coverage vẫn chia theo giá dự đoán, vì khoảng tin cậy là lời hứa đưa ra khi chưa biết giá thật.

---

## 2. Hướng 1 — đặt trọng số cho chuyến hiếm

### 2.1 Thiết kế

Chỉ trọng số `w` của chuyến hiếm trong tập train thay đổi; thuật toán, siêu tham số, feature, cách chia tập giữ nguyên. Trọng số chỉ áp lên nhánh giá cơ bản.

| Thành phần | Giá trị |
|---|---|
| Lưới trọng số | `w ∈ {1, 2, 3, 5, 10, 20}` |
| Định nghĩa chuyến hiếm | ① `>15 km` · ② `>300k` · ③ cả hai |
| Số lượt train | 16 cấu hình × 3 tháng = 48 lượt, chế độ đầy đủ |
| Tỷ lệ chuyến hiếm trong train | 0,31% · 0,17% · 0,38% |

Điểm neo: `w = 1` train lại cho MAPE 14,6496%, trùng model mốc tới bốn chữ số thập phân.

### 2.2 Nhóm chuyến dài

{{IMG:W1_sai_so_nhom_15km.png|Sai số nhóm >15 km theo mức trọng số. Vùng xám là dải nhiễu 95% của chính model mốc.}}

Không mức trọng số nào cải thiện được nhóm `>15 km`. Cả ba cách gán đều làm nhóm này xấu đi đơn điệu theo `w`.

| Cách gán | w | MAPE `>15 km` | Chênh so với mốc | CI 95% |
|---|---:|---:|---:|---|
| quãng đường | 2 | 17,75% | −0,22 | [−0,43, −0,03] |
| quãng đường | 20 | 18,51% | −0,98 | [−1,46, −0,49] |
| giá | 10 | 21,69% | −4,17 | [−5,20, −3,14] |
| giá | 20 | 23,71% | −6,19 | [−7,43, −4,99] |
| cả hai | 20 | 18,31% | −0,78 | [−1,24, −0,35] |

Gán trọng số theo quãng đường không cứu được chính nhóm nó nhắm tới. Nhóm này chỉ có 14.206 dòng train và vốn rất nhiễu, nên tăng trọng số là khuếch đại nhiễu.

### 2.3 Nhóm giá cao

{{IMG:W2_sai_so_nhom_300k.png|Sai số nhóm >300k theo mức trọng số. Chỉ cách gán theo giá kéo được nhóm này xuống.}}

Gán theo giá thì có tác dụng thật. 7 phương án đạt tiêu chí đặt trước tuần: nhóm hiếm giảm ≥1 điểm, toàn tập xấu đi ≤0,15 điểm.

| Cách gán | w | MAPE `>300k` | Chênh so với mốc | CI 95% | Toàn tập xấu đi |
|---|---:|---:|---:|---|---:|
| giá | 3 | 22,12% | +1,55 | [+1,27, +1,81] | 0,018 |
| giá | 5 | 21,35% | +2,32 | [+1,93, +2,68] | 0,033 |
| giá | 10 | 20,44% | +3,23 | [+2,75, +3,68] | 0,063 |
| giá | 20 | 19,91% | +3,77 | [+3,20, +4,32] | 0,109 |
| cả hai | 10 | 21,68% | +1,99 | [+1,63, +2,36] | 0,050 |
| cả hai | 20 | 20,96% | +2,71 | [+2,28, +3,17] | 0,094 |

Đính chính: bản chạy thử lấy mẫu 500.000 dòng/tháng kết luận không phương án nào đạt tiêu chí. Chạy đầy đủ trên 1,55 triệu dòng/tháng cho kết quả ngược lại — nhóm hiếm chiếm chưa tới 0,4% dữ liệu nên lấy mẫu làm mất tín hiệu. Số trong báo cáo này là số chế độ đầy đủ.

### 2.4 Cái giá thật của trọng số

{{IMG:W5_lan_toa_moi_nhom.png|Trọng số lan sang toàn bộ 12 nhóm. Xanh là tốt lên, đỏ là xấu đi, đơn vị điểm phần trăm.}}

Ở cột `w=20` của cách gán theo giá: nhóm `giá >300k` được +3,77 điểm, đổi lại nhóm `km >15` mất 6,19 điểm và `km 12–15` mất 4,71 điểm.

Hai nhóm hiếm mà đề bài gộp làm một kéo model về hai hướng ngược nhau. Model không đủ tín hiệu để phân biệt "đắt vì đi xa" với "đắt vì hệ số nhân cao", nên ép nó chú ý nhóm này là lấy độ chính xác của nhóm kia bù vào.

{{IMG:W4_duong_danh_doi.png|Đường đánh đổi. Trục ngang là cái phải trả trên toàn tập, trục dọc là cái nhận được ở nhóm mục tiêu.}}

Bên trái: không đường nào chạm vùng đạt tiêu chí. Bên phải: cách gán theo giá đi thẳng lên vùng đó, cách gán theo quãng đường nằm bẹp ở đáy.

### 2.5 Kết luận hướng 1

Trọng số kéo được nhóm giá cao xuống nhưng nhóm chuyến dài xấu đi nhiều hơn phần thu được. Chi phí trên toàn tập rẻ (≤0,11 điểm). Nếu team ưu tiên nhóm `>300k`, phương án gán theo cả hai điều kiện với `w = 10` là điểm cân bằng tốt nhất: được 1,99 điểm ở nhóm giá cao, mất 0,60 điểm ở nhóm chuyến dài.

---

## 3. Hướng 2 — ghép GAM với GBM theo quãng đường

### 3.1 Điều kiện tiên quyết

Mentor đặt điều kiện: chỉ ghép nếu lợi thế của GAM ổn định. Kiểm định trên 9 lát thời gian (ba tháng, mỗi tháng thêm hai nửa):

{{IMG:H2_3_on_dinh_theo_lat.png|Lợi thế của GAM qua 9 lát thời gian. Xanh: GAM thắng rõ. Đỏ: GBM thắng rõ. Xám: không phân biệt được.}}

| Nhóm | GAM thắng rõ | GBM thắng rõ | Kết luận |
|---|---:|---:|---|
| `>15 km` | 8/9 | 0/9 | Ổn định — GAM thắng |
| `>300k` | 7/9 | 0/9 | Ổn định — GAM thắng |
| `12–15 km` | 2/9 | 0/9 | Ổn định — GAM thắng |
| `8–12 km` | 0/9 | 6/9 | Ổn định — GBM thắng |
| Toàn tập | 0/9 | 9/9 | Ổn định — GBM thắng |

Không lát nào đảo dấu ở nhóm `>15 km`, điều kiện thoả. Bảng này đồng thời cho thấy không thể thay hẳn GAM vào: trên toàn tập GBM thắng 9/9.

### 3.2 Cách ghép

$$\hat p = (1 - \alpha(d)) \cdot \hat p_{GBM} + \alpha(d) \cdot \hat p_{GAM}$$

với `d₀ = 6 km`, `d₁ = 14 km`, `α_max = 0,8`. Tham số dò trên test tháng 2026-01; mọi con số dưới đây báo cáo trên hai tháng chưa từng đụng tới (2026-02 và 2026-03, 137.250 chuyến).

Hàm liên tục nên không có bậc nhảy: bước nhảy giá lớn nhất giữa hai mốc 0,5 km liên tiếp là 11,51% ở cả ghép lẫn GBM đơn lẻ.

### 3.3 Bảng thống kê ba model

| Model | MAPE | MdAPE | MAE | % trong ±10% | % ngoài ±20% | Hơn persistence |
|---|---:|---:|---:|---:|---:|---:|
| GBM *(mốc)* | 14,63% | 12,15% | 18.027đ | 42,29% | 26,86% | 46,03% |
| GAM | 14,86% | 12,38% | 18.176đ | 41,37% | 27,43% | 45,58% |
| Ghép | 14,62% | 12,14% | 17.986đ | 42,37% | 26,81% | 46,15% |

Ghép thắng ở cả sáu chỉ số; chênh lệch toàn tập +0,014 điểm, CI [+0,010, +0,018].

### 3.4 Kết quả theo quãng đường

{{IMG:H2_1_ba_model_theo_km.png|Ba model theo quãng đường. Đường đứt là trọng số α(d) của GAM. Điểm giao nằm quanh 13 km.}}

| Nhóm km | n | GBM | GAM | Ghép | Ghép so với GBM | CI 95% |
|---|---:|---:|---:|---:|---:|---|
| `<2` | 5.288 | 9,25% | 13,47% | 9,25% | +0,00 | không đụng tới |
| `2–5` | 17.055 | 14,19% | 14,46% | 14,19% | +0,00 | không đụng tới |
| `5–8` | 79.498 | 14,97% | 15,02% | 14,96% | +0,00 | [+0,00, +0,00] |
| `8–12` | 33.712 | 14,84% | 14,90% | 14,83% | +0,01 | [−0,00, +0,02] |
| `12–15` | 1.269 | 15,18% | 14,79% | 14,80% | +0,38 | [+0,17, +0,59] |
| `>15` | 428 | 18,12% | 15,47% | 15,61% | +2,50 | [+1,73, +3,36] |

Theo giá thật, nhóm `>300k` (548 chuyến): 24,04% → 22,49%, tốt lên 1,55 điểm, CI [+1,04, +2,09].

GAM một mình hỏng nặng ở chuyến ngắn — nhóm `<2 km` sai 13,47% so với 9,25% của GBM. Đó là lý do hàm trộn giữ `α = 0` ở vùng ngắn, và là lý do ghép hơn cả hai model đơn lẻ.

### 3.5 Tổng kết đánh đổi

{{IMG:H2_6_tong_ket.png|Ba model trên cùng một mặt phẳng đánh đổi. Ghép nằm ở góc tốt nhất.}}

Ghép nhận gần hết phần lợi của GAM ở chuyến dài mà không phải trả gì trên toàn tập, vì hàm trộn chỉ chạm phần đuôi của phân phối quãng đường, nơi GBM vốn yếu. So từng chuyến ở vùng có trộn: ghép tốt hơn 50,3%, kém hơn 49,7%; riêng nhóm `>15 km` là 60,3% so với 39,7%.

---

## 4. Đối chiếu hai hướng

| Tiêu chí | ① Trọng số | ② Ghép GAM–GBM |
|---|---|---|
| Cải thiện nhóm `>15 km` | không mức nào cải thiện được | +2,50 điểm |
| Cải thiện nhóm `>300k` | tới +3,77 điểm | +1,55 điểm |
| Cái giá trên toàn tập | xấu đi 0,02–0,11 điểm | tốt lên 0,014 điểm |
| Tác dụng phụ | nhóm chuyến dài xấu đi tới 6,19 điểm | không thấy |
| Chi phí triển khai | train lại, giữ một model | nuôi hai model trong sản xuất |
| Cần train lại không | có, 48 lượt | không |

Trọng số ép một model duy nhất phải giỏi cả hai đầu phân phối, nên phải hy sinh đầu này cứu đầu kia. Ghép giao mỗi vùng cho model phù hợp, nên không có gì phải hy sinh.

---

## 5. Ba giới hạn

1. Tham số ghép dò trên 2026-01. Số chính thức đã báo cáo trên hai tháng chưa đụng tới, nhưng vẫn cùng một bộ sinh dữ liệu; với dữ liệu thật phải dò lại.
2. Nhóm mục tiêu rất nhỏ — `>15 km` có 428 chuyến trong tập đánh giá sạch, `>300k` có 548. Mọi kết luận phải đọc kèm khoảng tin cậy.
3. Hướng ② phải nuôi hai model trong sản xuất, cho phần cải thiện chỉ chạm khoảng 1% số chuyến.

## 6. Câu hỏi cho mentor

1. Nếu buộc phải chọn, team ưu tiên nhóm `>300k` hay nhóm `>15 km`? Dữ liệu tuần này cho thấy không thể có cả hai bằng cách đặt trọng số.
2. Chi phí nuôi hai model có chấp nhận được không, khi phần cải thiện chỉ chạm khoảng 1% số chuyến?
3. Ngưỡng đánh đổi trên toàn tập 0,15 điểm do nhóm tự đặt — team có con số riêng không?

---

## Phụ lục — tái lập

| Notebook | Nội dung | Cần train lại | Thời gian |
|---|---|---|---|
| `tuan_5/HUONG_1_THAY_DOI_WEIGHT.ipynb` | Hướng ① — 6 hình `W1`–`W6` | Có, 48 lượt | ~20 phút |
| `tuan_5/HUONG_2_GAM_GBM.ipynb` | Hướng ② — 6 hình `H2_1`–`H2_6` | Không | ~3 phút |
| `tuan_5/06_NHOM_CO_DINH.ipynb` | Ràng buộc nhóm cố định — 5 hình `NC1`–`NC5` | Không | ~2 phút |
| `tuan_5/02_GAM_ON_DINH.ipynb` | Kiểm định ổn định 9 lát | Không | ~2 phút |
| `tuan_5/03_GHEP_GAM_GBM.ipynb` | Dò tham số `d₀`, `d₁`, `α_max` | Không | ~3 phút |

Bảng số gốc ở `tuan_5/ket_qua/`: `W_bang_chinh.csv`, `W_bang_theo_km.csv`, `W_bang_theo_gia.csv` cho hướng ①; `H2_tong_ket_3_model.csv`, `H2_theo_km.csv`, `H2_theo_gia.csv` cho hướng ②.
