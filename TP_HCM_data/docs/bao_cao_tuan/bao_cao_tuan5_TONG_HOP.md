# Báo cáo tuần 5

Bốn phần, tương ứng bốn việc mentor giao trong tuần.

| Phần | Nội dung | Kết quả một dòng |
|---|---|---|
| Hướng 1 | Đặt trọng số cao hơn cho chuyến hiếm khi train | Kéo được nhóm giá cao xuống nhưng nhóm chuyến dài xấu đi nhiều hơn phần thu được |
| Hướng 2 | Ghép GAM với GBM theo quãng đường | Cải thiện cả hai nhóm mục tiêu mà toàn tập không xấu đi |
| Uncertainty | Dành nhiều khoảng hơn cho phía giá cao | Chia lại rủi ro hai phía không đổi được gì; hướng đúng là cho độ rộng thay đổi theo từng chuyến |
| Xu hướng | Model thường báo cao hay báo thấp so với giá thật | Tổng thể không lệch phía nào, nhưng báo thấp ở chuyến dài và lúc thị trường vừa tăng giá |

Hướng 1 và hướng 2 nằm ở phần A, uncertainty ở phần B, xu hướng dự đoán ở phần C. Mỗi phần giữ nguyên cách đánh số mục riêng.

---

# Phần A — hai hướng giảm sai số ở nhóm chuyến hiếm

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

---

# Phần B — khoảng dự đoán bất đối xứng

Đề xuất của mentor: khoảng hiện tại chia độ rộng khá đều cho hai phía, trong khi model bỏ sót phía giá cao nhiều hơn. Thử giữ độ rộng tương đương nhưng dành nhiều khoảng hơn cho phía giá cao, rồi kiểm tra coverage có tốt hơn không mà khoảng không rộng thêm.

Dữ liệu: calibration 153.977 chuyến, test 216.090 chuyến, độ trễ 5 phút, mức tin cậy danh nghĩa 90%. Nhóm chia theo giá dự đoán, vì khoảng là lời hứa đưa ra khi chưa biết giá thật.

Kết quả ngắn: chẩn đoán của mentor đúng, nhưng cách sửa bằng chia lại rủi ro hai phía không hiệu quả. Nguyên nhân và cách sửa thay thế ở mục 4.

---

## 1. Model đang lệch về phía nào

Khoảng hiện tại là `p̂ · (1 ± 30,07%)`, đối xứng quanh giá dự đoán. Sai lệch thực tế thì không:

| Chỉ số | Giá trị |
|---|---:|
| Coverage tổng | 89,81% |
| Giá thật vượt cận trên | 7,64% |
| Giá thật thấp hơn cận dưới | 2,55% |
| Tỷ lệ hai phía | 3,00× |

{{IMG:U1_chan_doan_bat_doi_xung.png|Trái: phân phối sai lệch lệch phải (skew +0,58). Phải: tỷ lệ trượt hai phía theo band giá.}}

Lệch nặng nhất ở band giá cao. Band `>300k` có 11,62% vượt cận trên so với 4,59% dưới cận dưới — cả hai đều vượt mức 5% lý tưởng, tức band này vừa lệch vừa hụt coverage.

| Band giá dự đoán | Vượt cận trên | Dưới cận dưới |
|---|---:|---:|
| `<50k` | 7,03% | 0,55% |
| `50–100k` | 7,07% | 2,40% |
| `100–150k` | 7,91% | 2,71% |
| `150–200k` | 7,87% | 2,52% |
| `200–300k` | 8,01% | 2,47% |
| `>300k` | 11,62% | 4,59% |

---

## 2. Chia lại khoảng giữa hai phía

Giữ tổng rủi ro 10%, chia lại thành `α dưới` và `α trên`. Hai cận lấy từ phân vị một phía của sai lệch có dấu trên tập calibration. `α trên` càng nhỏ thì cận trên càng cao, tức dành nhiều khoảng hơn cho phía giá cao.

| α dưới / α trên | Khoảng phía dưới | Khoảng phía trên | Coverage | Độ rộng TB | Vượt trên | Dưới cận dưới |
|---|---:|---:|---:|---:|---:|---:|
| Đối xứng hiện tại | 30,07% | 30,07% | 89,81% | 72.637đ | 7,64% | 2,55% |
| 1% / 9% | 34,88% | 27,43% | 89,66% | 75.249đ | 9,39% | 0,95% |
| 2% / 8% | 31,57% | 28,93% | 89,73% | 73.071đ | 8,34% | 1,93% |
| 3% / 7% | 29,37% | 30,70% | 89,81% | 72.541đ | 7,30% | 2,90% |
| 4% / 6% | 27,63% | 32,61% | 89,88% | 72.753đ | 6,26% | 3,86% |
| 5% / 5% | 26,18% | 34,76% | 89,92% | 73.598đ | 5,27% | 4,81% |
| 6% / 4% | 24,93% | 37,43% | 90,02% | 75.319đ | 4,19% | 5,78% |
| 7% / 3% | 23,84% | 40,73% | 90,08% | 77.979đ | 3,16% | 6,76% |
| 8% / 2% | 22,85% | 45,40% | 90,20% | 82.431đ | 2,09% | 7,71% |
| 9% / 1% | 21,91% | 52,88% | 90,26% | 90.331đ | 1,05% | 8,68% |

{{IMG:U2_chia_lai_khoang.png|Ba góc nhìn về cùng một lưới chia, đo trên 216.090 chuyến test. Trái: hai cận dịch chuyển ra sao. Giữa: coverage và độ rộng. Phải: tỷ lệ trượt hai phía.}}

Ba panel đọc theo thứ tự:

1. Panel trái cho thấy hình học của phép chia. Với một chuyến 200k, đi từ `1%/9%` sang `9%/1%` thì cận trên bốc từ 255k lên 306k trong khi cận dưới chỉ nhích từ 130k lên 156k. Đuôi phải dài nên kéo cận trên tốn hơn nhiều so với phần tiết kiệm được ở cận dưới — đó là lý do độ rộng phình ra.
2. Panel giữa cho thấy cái giá. Độ rộng chạm đáy tại `3%/7%` (72.541đ, hẹp hơn hiện tại 0,13%) rồi tăng liên tục; coverage đi lên nhưng rất chậm, từ 89,66% tới 90,26% trên toàn bộ lưới.
3. Panel phải cho thấy điểm cân bằng. Hai phía trượt bằng nhau tại `5%/5%` (5,27% và 4,81%), đúng thứ mentor muốn — và cái giá của nó là độ rộng tăng 1,32%.

Không mốc chia nào vừa hẹp hơn vừa phủ tốt hơn đáng kể. Đây là câu trả lời trực tiếp cho vế "coverage có tốt hơn không mà khoảng không rộng thêm": trên dữ liệu này thì không.

{{IMG:U6_coverage_band_theo_moc_chia.png|Coverage từng band qua mọi mốc chia. Cột đầu là phương án hiện tại.}}

Tách theo band thì thấy rõ hơn nữa. Năm band dưới đều quanh 89–93% ở mọi mốc chia, còn band `>300k` nằm trong khoảng 81,0–84,4% suốt cả lưới — biên độ 3,4 điểm và không mốc nào đưa nó về gần 90%. Chia lại rủi ro chỉ dịch khoảng cho toàn bộ chuyến như nhau, nên nhóm hụt nặng nhất vẫn hụt.

---

## 3. Khoảng cho một chuyến giá dự đoán 200k

{{IMG:U3_vi_du_200k.png|Khoảng 90% cho một chuyến có giá dự đoán 200k, theo từng phương án.}}

| Phương án | Khoảng | Độ rộng | Phía dưới | Phía trên |
|---|---|---:|---:|---:|
| Đối xứng hiện tại | 139,9k – 260,1k | 120,3k | 60,1k | 60,1k |
| Bất đối xứng 3%/7% | 141,3k – 261,4k | 120,1k | 58,7k | 61,4k |
| Bất đối xứng 5%/5% | 147,6k – 269,5k | 121,9k | 52,4k | 69,5k |
| Bất đối xứng 7%/3% | 152,3k – 281,5k | 129,1k | 47,7k | 81,5k |
| Mentor gợi ý (ví dụ) | 150,0k – 270,0k | 120,0k | 50,0k | 70,0k |

Con số thật của phương án hiện tại là 139,9k–260,1k, gần đúng ví dụ 140k–260k mentor nêu.

Khoảng mentor gợi ý (150k–270k) nằm rất sát phương án `5%/5%` (147,6k–269,5k). Phương án đó có thật trong lưới, và cái giá của nó là độ rộng tăng 1,3% để đổi lấy coverage tăng 0,11 điểm — gần như hoà.

Một điểm dễ bỏ qua: khoảng hiện tại đã bất đối xứng sẵn theo đơn vị tiền. Vì nó nhân tính, chuyến 200k được ±60,1k còn chuyến 400k được ±120,3k, nên phần dành cho phía trên tự động lớn hơn khi giá cao. Đó là lý do phép dịch phân vị không còn nhiều dư địa.

---

## 4. Khi độ rộng thay đổi theo từng chuyến

Nếu một cặp hằng số không đủ, có hai hướng nâng cấp: tính cặp phân vị riêng cho từng band giá (Mondrian), hoặc cho độ bất đối xứng thay đổi theo từng chuyến bằng CQR — dựng khoảng từ hai phân vị điều kiện `q05`/`q95` của quantile regression rồi hiệu chỉnh riêng từng phía.

| Phương án | Coverage | Độ rộng TB | Vượt trên | Dưới cận dưới | Lệch coverage giữa band | Coverage band `>300k` |
|---|---:|---:|---:|---:|---:|---:|
| Đối xứng hiện tại | 89,81% | 72.637đ | 7,64% | 2,55% | 8,62 điểm | 83,79% |
| Bất đối xứng 3%/7% | 89,81% | 72.541đ | 7,30% | 2,90% | 9,11 điểm | 83,49% |
| Mondrian band + 5%/5% | 89,91% | 73.823đ | 5,26% | 4,83% | 7,44 điểm | 82,87% |
| Mondrian band + 3%/7% | 89,84% | 72.787đ | 7,28% | 2,88% | 6,58 điểm | 83,49% |
| CQR đối xứng | 89,67% | 75.999đ | 5,56% | 4,78% | 2,29 điểm | 88,03% |
| CQR bất đối xứng 5%/5% | 89,60% | 75.562đ | 5,99% | 4,41% | 2,29 điểm | 88,03% |
| CQR bất đối xứng 3%/7% | 89,04% | 74.954đ | 8,27% | 2,69% | 1,55 điểm | 88,03% |

{{IMG:U4_coverage_theo_band.png|Trái: coverage theo band trước và sau. Phải: đánh đổi giữa độ đều và độ rộng.}}

CQR là phương án duy nhất kéo được band `>300k` từ 83,79% lên 88,03%, và giảm lệch coverage giữa các band từ 8,62 xuống 1,55 điểm. Cái giá là độ rộng tăng 3,2%.

Mondrian rẻ hơn nhiều: lệch giữa band giảm 8,62 → 6,58 điểm với độ rộng chỉ tăng 0,21%, nhưng không kéo được band `>300k` lên.

{{IMG:U5_can_doi_hai_phia.png|Trái: cân đối hai phía trước và sau. Phải: phân phối độ rộng của phương án hiện tại so với CQR.}}

Hình bên phải cho thấy khác biệt bản chất: phương án hiện tại cấp độ rộng tỷ lệ thuận với giá dự đoán, còn CQR cấp theo mức khó của từng chuyến — chuyến dễ được khoảng hẹp, chuyến khó được khoảng rộng.

---

## 5. Kết luận và việc nên làm

Đề xuất chia lại rủi ro hai phía cho kết quả âm tính. Phương án tốt nhất trong lưới hẹp hơn hiện tại 0,13% với coverage không đổi; muốn coverage nhích 0,27 điểm thì phải chấp nhận rộng thêm 7,5%. Lý do là khoảng nhân tính đã hấp thụ sẵn phần lớn độ lệch phải của phân phối giá.

Chẩn đoán của mentor vẫn đúng, nhưng vấn đề gốc không phải chia khoảng lệch giữa hai phía mà là độ rộng không thay đổi theo từng chuyến. Bằng chứng: mọi chuyến đều nhận cùng tỷ lệ ±30,07%, nên band `>300k` chỉ đạt 83,79% trong khi band thấp vượt 92%.

Việc nên làm tiếp:

1. Giữ Mondrian theo quãng đường đã chốt ở `04_MONDRIAN_QUANG_DUONG` — rẻ nhất, đã có kết quả.
2. Nếu team chấp nhận đánh đổi 3–5% độ rộng, làm tiếp CQR bất đối xứng. Đây là cách duy nhất trong các phương án đã thử kéo được band `>300k` lên sát cam kết.
3. Không lặp lại thí nghiệm cặp hằng số — đã thử đủ 9 mức chia rủi ro, kết quả âm tính và giải thích được bằng dạng nhân tính của khoảng.

Câu hỏi cho mentor: team chấp nhận khoảng rộng thêm bao nhiêu phần trăm để đổi lấy coverage đều giữa các band? Con số này quyết định chọn Mondrian hay CQR.

---

## Phụ lục — tái lập

Notebook tái lập: `tuan_5/HUONG_3_KHOANG_BAT_DOI_XUNG.ipynb` — 20 ô, 6 hình `U1`–`U6`, không train lại, chạy khoảng 2 phút.

Bảng số gốc ở `tuan_5/ket_qua/`: `U_chia_rui_ro.csv`, `U_bon_ho_phuong_an.csv`, `U_coverage_theo_band.csv`.

Kết quả này thay thế phần thí nghiệm bất đối xứng ghi ở `RESEARCH_PAPER` §7.5 — số liệu trùng khớp, nhưng lần này có notebook tái lập được và mở rộng thêm hai họ phương án.

---

# Phần C — model đang đoán cao hay đoán thấp

Câu hỏi của mentor: *"Mình vẫn có một độ thiếu chính xác nhất định á. Thì anh muốn hiểu rõ là thường nó predict giá thấp hơn hay cao hơn ground truth ấy mà."*

Mọi báo cáo trước đo bằng MAPE, mà MAPE lấy trị tuyệt đối nên **mất dấu**. Đoán 90k cho chuyến 100k và đoán 110k cho chuyến 100k cùng ra MAPE 10%, nhưng với người định giá thì đó là hai chuyện ngược nhau: báo thấp thì tưởng đối thủ đang rẻ nên hạ giá theo và mất doanh thu; báo cao thì tưởng đối thủ đang đắt nên để giá cao và mất khách.

Báo cáo này đo **sai lệch có dấu** `r = (giá dự đoán − giá thật) / giá thật` thay cho sai số tuyệt đối, tách theo từng model, từng nhánh và từng tình huống.

Dữ liệu: 216.090 chuyến test độc lập, độ trễ 5 phút, quãng đường 1,1–45,0 km, giá thật trung vị 116.000đ. Dữ liệu synthetic.

Kết quả ngắn: xét tổng thể model **không thiên lệch phía nào** — nên không được hiệu chỉnh bằng một hằng số cộng trừ. Nhưng có hai xu hướng cục bộ rất rõ, và cả hai đều nhận ra được **trước** khi dự báo, tức sửa được.

---

## 1. Tổng thể — không lệch phía nào

Hai chỉ số nên đọc trước là trung vị và tỷ lệ đoán cao, vì chúng không bị một nhóm ngoại lai chi phối. Trung bình luôn dương hơn trung vị do đuôi phải của phân phối giá kéo lên.

| Model | Trung vị | Trung bình | % đoán cao | Đoán cao quá 10% | Đoán thấp quá 10% | MAPE |
|---|---:|---:|---:|---:|---:|---:|
| **GBM Hybrid** *(đang dùng)* | **+0,01%** | +1,60% | **50,02%** | 29,58% | 28,12% | 14,65% |
| GAM Hybrid | −0,35% | +1,50% | 49,20% | 29,76% | 28,89% | 14,89% |
| Ghép | +0,01% | +1,60% | 50,03% | 29,57% | 28,06% | 14,64% |
| Persistence *(mốc tham chiếu)* | 0,00% | +5,97% | 49,02% | 37,87% | 37,07% | 27,84% |

{{IMG:XH1_phan_phoi_sai_lech.png|Trái: phân phối sai lệch có dấu của bốn model. Phải: trung vị và trung bình cạnh nhau — khoảng cách giữa hai cột chính là phần đuôi phải kéo lên.}}

Trung vị +0,01% và tỷ lệ đoán cao 50,02% là câu trả lời trực tiếp cho câu hỏi của mentor: **model không thiên về phía nào**. Vì vậy không nên hiệu chỉnh bằng cách cộng hay nhân thêm một hằng số — làm thế chỉ đẩy sai lệch sang phía kia.

Điều đáng chú ý nằm ở cột `Đoán cao quá 10%` và `Đoán thấp quá 10%`: hai đuôi gần bằng nhau (29,58% và 28,12%), tức độ thiếu chính xác còn lại là **phân tán hai phía**, không phải lệch một chiều. Persistence có cùng đặc điểm nhưng hai đuôi dày gần gấp rưỡi (37,9% và 37,1%) — đó là toàn bộ giá trị mà model tạo ra so với việc lấy thẳng giá quan sát được.

---

## 2. Theo quãng đường — chỗ có chuyện

Đây là lát cắt quan trọng nhất, vì quãng đường **biết trước lúc dự báo**. Bất kỳ thiên lệch nào theo chiều này đều sửa được ngay mà không cần train lại.

| Nhóm km | n | GBM Hybrid | GAM Hybrid | Ghép | Persistence |
|---|---:|---:|---:|---:|---:|
| `<5` | 35.158 | +0,54% | −0,66% | +0,54% | +4,35% |
| `5–8` | 125.255 | −0,11% | −0,28% | −0,11% | +1,54% |
| `8–12` | 52.972 | −0,22% | −0,28% | −0,19% | −6,62% |
| `12–15` | 2.045 | +0,54% | −0,10% | −0,08% | −36,18% |
| `15–18` | 422 | +1,71% | −1,29% | −0,55% | −50,97% |
| `18–20` | 99 | **−7,08%** | −3,29% | −4,06% | −55,73% |
| `20–25` | 97 | **−13,30%** | −0,73% | −4,04% | −63,55% |
| `>25` | 42 | **−25,08%** | +3,68% | −1,76% | −74,64% |

{{IMG:XH2_xu_huong_theo_km.png|Trung vị sai lệch theo nhóm quãng đường. Dải xanh là vùng ±1%, coi như không lệch. Ba model bám sát 0 tới 15 km rồi tách hẳn nhau.}}

Từ 18 km trở đi GBM tụt dốc đơn điệu và không quay lại. Quy ra tiền thì mức độ rõ hơn nhiều:

| Nhóm km | n | Giá thật TB | GBM báo | GAM báo | Ghép báo |
|---|---:|---:|---:|---:|---:|
| `15–18` | 422 | 262.991đ | 265.429đ *(+0,9%)* | 257.131đ *(−2,2%)* | 259.277đ *(−1,4%)* |
| `18–20` | 99 | 289.717đ | 268.836đ *(−7,2%)* | 280.345đ *(−3,2%)* | 278.509đ *(−3,9%)* |
| `20–25` | 97 | 332.072đ | 290.119đ *(−12,6%)* | 332.494đ *(+0,1%)* | 324.449đ *(−2,3%)* |
| `>25` | 42 | 463.286đ | 328.995đ *(−29,0%)* | 462.720đ *(−0,1%)* | 439.039đ *(−5,2%)* |

{{IMG:XH9_quy_ra_tien.png|Trái: giá thật và giá từng model báo theo quãng đường, đơn vị nghìn đồng. Phải: chênh tiền trung bình mỗi chuyến.}}

Nhóm trên 25 km: giá thật trung bình 463k mà GBM báo 329k — **hụt 134.291đ mỗi chuyến**. GAM báo 462,7k, gần như trùng khít. Bản ghép nằm giữa, hụt 24.247đ.

### Vì sao GBM tụt ở đuôi

{{IMG:XH3_vi_sao_tut_o_duoi.png|Trái: phân phối quãng đường trong tập train, thang log — vùng xa cực thưa. Phải: giá thật so với giá từng model báo ở vùng đó.}}

Cây quyết định **không ngoại suy được**: qua nhát cắt cuối cùng, dự đoán trở thành hằng số. Mà vùng quãng đường xa lại cực thưa trong tập train — trên 20 km chỉ chiếm 0,06% số dòng — nên gần như không có nhát cắt nào ở đó. Kết quả là mọi chuyến rất dài đều nhận chung một mức giá trần do cây học được từ vùng dày dữ liệu.

GAM không bị vì nó khớp một hàm trơn theo quãng đường, hàm đó vẫn đi lên khi ra ngoài vùng dày. Trên nhóm `>20 km` (139 chuyến): giá thật TB 371.719đ · GBM 301.866đ (−18,8%) · GAM 371.843đ (+0,0%) · Ghép 359.073đ (−3,4%) · Persistence 126.252đ (−66,0%).

Đây là bằng chứng độc lập ủng hộ phương án ghép ở mục 3 phần A: lợi thế của GAM ở chuyến dài không phải may rủi thống kê trên vài trăm chuyến, mà có **cơ chế giải thích được** — khả năng ngoại suy.

---

## 3. Thiên lệch nằm ở tầng nào

Model là hai tầng nhân nhau, nên phải tách xem độ dốc theo quãng đường đến từ nhánh giá cơ bản hay nhánh hệ số nhân.

{{IMG:XH4_hai_nhanh.png|Trung vị sai lệch của từng nhánh theo quãng đường. Đường liền là nhánh giá cơ bản, đường đứt là nhánh hệ số nhân.}}

Trên nhóm `>20 km`, tách riêng hai nhánh của GBM:

| Nhánh | Trung vị lệch | Sai số tuyệt đối TB |
|---|---:|---:|
| Giá cơ bản | **−14,82%** | 19,10% |
| Hệ số nhân | −0,53% | **1,61%** |

**Nhánh hệ số nhân không phải thủ phạm.** Nó sai đều khoảng 1,4–1,6% ở mọi cự ly và trung vị gần như phẳng. Toàn bộ độ dốc theo quãng đường nằm ở nhánh giá cơ bản.

Kết luận này khớp với `05_GAM_CHI_TIET` của tuần 5 — ở đó lợi thế của GAM cũng nằm hoàn toàn ở nhánh giá cơ bản (+2,30 điểm ở `>15 km`) trong khi nhánh hệ số nhân của GAM kém đều ~0,5 điểm ở mọi nhóm. Hai phân tích đi từ hai hướng khác nhau (sai số tuyệt đối và sai lệch có dấu) nhưng chỉ về cùng một chỗ, nên phương án ghép chỉ trộn nhánh giá cơ bản là đúng chỗ cần trộn.

---

## 4. Theo biến động thị trường

Model chỉ được nhìn giá đối thủ **trễ 5 phút**. Câu hỏi: khi giá vừa nhảy, model có đuổi kịp không hay bám lại mức cũ?

Chia theo mức giá đã dịch chuyển kể từ lần quan sát gần nhất:

| Thị trường vừa | n | GBM Hybrid | GAM Hybrid | Ghép | Persistence |
|---|---:|---:|---:|---:|---:|
| giảm >15% | 66.098 | **+11,85%** | +12,13% | +11,85% | +40,15% |
| giảm 5–15% | 27.343 | +3,53% | +3,38% | +3,50% | +10,98% |
| đi ngang ±5% | 28.179 | +0,45% | −0,59% | +0,44% | 0,00% |
| tăng 5–15% | 22.695 | −2,97% | −3,13% | −3,00% | −8,94% |
| tăng >15% | 71.775 | **−10,59%** | −10,67% | −10,55% | −27,46% |

{{IMG:XH5_theo_bien_dong.png|Sai lệch có dấu theo mức biến động giá. Độ dốc âm nghĩa là model chạy sau thị trường.}}

Tương quan giữa mức dịch chuyển giá và sai lệch có dấu: GBM −0,492 · GAM −0,492 · Ghép −0,490 · Persistence −0,847.

Giá vừa giảm mạnh thì model đoán cao, giá vừa tăng mạnh thì model đoán thấp — nó **chạy sau thị trường**. Đây là hệ quả trực tiếp của việc chỉ được nhìn giá trễ 5 phút, không phải lỗi thuật toán: cả ba model đều có cùng một con số −0,49, và đổi thuật toán không đụng được tới nó.

Điểm đáng chú ý là model đã hấp thụ được khoảng **43%** độ trễ đó: persistence lệch −27,46% ở nhóm giá tăng mạnh, model còn −10,59%. Phần còn lại không sửa được bằng model — muốn giảm tiếp thì phải rút ngắn độ trễ dữ liệu.

---

## 5. Hiệu chuẩn — model báo X thì thực tế bao nhiêu

Đây là góc nhìn dùng được lúc vận hành, vì khi đó chỉ biết giá model báo chứ chưa biết giá thật.

{{IMG:XH6_hieu_chuan.png|Trái: giá thật trung bình theo từng nhóm hai chục phân vị của giá model báo. Đường chéo là hiệu chuẩn hoàn hảo.}}

| GBM báo ~ | n | Giá thật TB | Lệch |
|---:|---:|---:|---:|
| 54k | 10.805 | 55k | −1,02% |
| 91k | 10.805 | 93k | −1,68% |
| 113k | 10.804 | 115k | −1,90% |
| 140k | 10.804 | 143k | −1,62% |
| 181k | 10.804 | 184k | −1,89% |
| 219k | 10.805 | 224k | −2,30% |

Model hiệu chuẩn tốt: lệch đều trong khoảng −1,0% đến −2,3% trên toàn dải giá, không có đoạn nào vỡ. Mức hụt nhẹ và ổn định này là do đuôi phải của phân phối giá — trung bình có điều kiện luôn cao hơn một chút so với mức model báo.

Đọc theo hướng vận hành: **khi model báo X, kỳ vọng giá đối thủ thật là khoảng X + 1,5% đến X + 2,3%**, và mức bù tăng nhẹ theo giá.

---

## 6. Bảng tình huống

Gom hai chiều đã phân tích vào một bảng, dùng làm bảng tra khi vận hành.

{{IMG:XH7_tung_model_theo_tinh_huong.png|Từng model một cột. Hàng trên theo quãng đường, hàng dưới theo mức biến động giá. Đỏ là đoán thấp hơn thật, xanh là đoán cao hơn, xám là trong ±1%.}}

{{IMG:XH8_ban_do_nhiet_lech.png|Bản đồ nhiệt trung vị sai lệch, ba model × tám nhóm quãng đường.}}

| Tình huống | n | GBM Hybrid | GAM Hybrid | Ghép |
|---|---:|---:|---:|---:|
| quãng đường `<5 km` | 35.158 | +0,54 | −0,66 | +0,54 |
| quãng đường `5–8 km` | 125.255 | −0,11 | −0,28 | −0,11 |
| quãng đường `8–12 km` | 52.972 | −0,22 | −0,28 | −0,19 |
| quãng đường `12–15 km` | 2.045 | +0,54 | −0,10 | −0,08 |
| quãng đường `15–18 km` | 422 | +1,71 | −1,29 | −0,55 |
| quãng đường `18–20 km` | 99 | −7,08 | −3,29 | −4,06 |
| quãng đường `20–25 km` | 97 | −13,30 | −0,73 | −4,04 |
| quãng đường `>25 km` | 42 | −25,08 | +3,68 | −1,76 |
| giá vừa giảm >15% | 66.098 | +11,85 | +12,13 | +11,85 |
| giá vừa giảm 5–15% | 27.343 | +3,53 | +3,38 | +3,50 |
| giá đi ngang ±5% | 28.179 | +0,45 | −0,59 | +0,44 |
| giá vừa tăng 5–15% | 22.695 | −2,97 | −3,13 | −3,00 |
| giá vừa tăng >15% | 71.775 | −10,59 | −10,67 | −10,55 |

Đơn vị: điểm phần trăm, âm là model báo **thấp** hơn giá thật.

Hai chiều này độc lập nhau và cộng dồn được: một chuyến 22 km vào lúc thị trường vừa tăng trên 15% là tình huống xấu nhất cho GBM — hai thiên lệch cùng dấu âm chồng lên nhau.

---

## 7. Kết luận

**Tổng thể model không thiên lệch.** Trung vị sai lệch +0,01%, tỷ lệ đoán cao 50,02%. Không cần và không nên hiệu chỉnh bằng một hằng số.

**Nhưng có hai xu hướng rõ, cả hai đều nhận ra được trước khi dự báo:**

1. **Chuyến càng dài, GBM càng báo thấp.** Từ 18 km trở đi trung vị bắt đầu âm; tới nhóm trên 25 km thì giá thật TB 463k mà model báo 329k. Nguyên nhân là cây không ngoại suy được và vùng đó chỉ chiếm 0,06% tập train. GAM không bị, nên bản ghép sửa được chỗ này — hụt giảm từ 29,0% xuống 5,2%.
2. **Model chạy sau biến động.** Giá vừa giảm mạnh thì báo cao, vừa tăng mạnh thì báo thấp, tương quan −0,49. Đây là hệ quả của độ trễ 5 phút chứ không phải lỗi thuật toán, và đổi model không đụng được tới nó.

**Nhánh hệ số nhân không phải thủ phạm.** Nó sai đều ~1,4% ở mọi cự ly, trung vị phẳng. Toàn bộ độ dốc theo quãng đường nằm ở nhánh giá cơ bản — cùng kết luận với `05_GAM_CHI_TIET`.

**Ý nghĩa vận hành.** Hai chỗ cần gắn cảnh báo là **chuyến đường dài** và **thời điểm thị trường vừa tăng giá**. Cả hai đều là lúc model báo thấp hơn giá đối thủ thật, tức có nguy cơ để giá thấp hơn mức lẽ ra bán được. Cả hai đều biết trước lúc dự báo nên cảnh báo được ngay, không cần đợi giá thật.

Việc nên làm tiếp:

1. Dùng bản ghép GAM–GBM ở mục 3 phần A — nó xoá được xu hướng thứ nhất, và mục 2 ở đây cho biết vì sao nó xoá được chứ không phải trùng hợp.
2. Gắn cờ cảnh báo cho hai tình huống trên vào đầu ra của model, đọc thẳng từ bảng tình huống mục 6.
3. Không hiệu chỉnh toàn cục. Mọi thiên lệch đo được đều là cục bộ theo tình huống; cộng trừ một hằng số sẽ làm hỏng phần đang đúng.

Câu hỏi cho mentor: đội pricing muốn model **báo đúng trung bình** hay **báo thận trọng lệch lên** ở nhóm chuyến dài? Hai mục tiêu này cho hai cách hiệu chỉnh khác nhau, và hiện model đang ở mục tiêu thứ nhất.

---

## Phụ lục — tái lập

Notebook tái lập: `tuan_5/XU_HUONG_DU_DOAN.ipynb` — 25 ô, 9 hình `XH1`–`XH9`, không train lại, chạy khoảng 2 phút.

Bảng số gốc ở `tuan_5/ket_qua/`: `XH_tong_the.csv`, `XH_theo_km.csv`, `XH_theo_bien_dong.csv`, `XH_bang_tinh_huong.csv`, `XH_thong_ke_theo_km.csv`, `XH_cau_hinh.json`.

Đầu vào: `model/evaluation/uq_pred_test.parquet`, `pred_gam.parquet`, `pred_gia_co_ban.parquet`, `pred_heso.parquet` và `data/hcm_train_ready.parquet` (chỉ cho hình `XH3`).
