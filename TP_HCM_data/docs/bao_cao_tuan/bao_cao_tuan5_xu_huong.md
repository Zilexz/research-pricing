# Báo cáo tuần 5 — model đang đoán cao hay đoán thấp

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

Đây là bằng chứng độc lập ủng hộ phương án ghép GAM–GBM của tuần 5: lợi thế của GAM ở chuyến dài không phải may rủi thống kê trên vài trăm chuyến, mà có **cơ chế giải thích được** — khả năng ngoại suy.

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

1. Dùng bản ghép GAM–GBM đã chốt ở `HUONG_2_GAM_GBM` — nó xoá được xu hướng thứ nhất, và mục 2 ở đây cho biết vì sao nó xoá được chứ không phải trùng hợp.
2. Gắn cờ cảnh báo cho hai tình huống trên vào đầu ra của model, đọc thẳng từ bảng tình huống mục 6.
3. Không hiệu chỉnh toàn cục. Mọi thiên lệch đo được đều là cục bộ theo tình huống; cộng trừ một hằng số sẽ làm hỏng phần đang đúng.

Câu hỏi cho mentor: đội pricing muốn model **báo đúng trung bình** hay **báo thận trọng lệch lên** ở nhóm chuyến dài? Hai mục tiêu này cho hai cách hiệu chỉnh khác nhau, và hiện model đang ở mục tiêu thứ nhất.

---

## Phụ lục — tái lập

Notebook tái lập: `tuan_5/XU_HUONG_DU_DOAN.ipynb` — 25 ô, 9 hình `XH1`–`XH9`, không train lại, chạy khoảng 2 phút.

Bảng số gốc ở `tuan_5/ket_qua/`: `XH_tong_the.csv`, `XH_theo_km.csv`, `XH_theo_bien_dong.csv`, `XH_bang_tinh_huong.csv`, `XH_thong_ke_theo_km.csv`, `XH_cau_hinh.json`.

Đầu vào: `model/evaluation/uq_pred_test.parquet`, `pred_gam.parquet`, `pred_gia_co_ban.parquet`, `pred_heso.parquet` và `data/hcm_train_ready.parquet` (chỉ cho hình `XH3`).
