# Báo cáo tuần 5 — khoảng dự đoán bất đối xứng

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
