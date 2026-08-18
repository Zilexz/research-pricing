# Báo cáo Tuần 4 — Uncertainty Quantification và Chẩn đoán model

Báo cáo gồm **hai phần độc lập nhưng bổ sung nhau**, cùng làm trên bộ dữ liệu TP.HCM tháng 01–03/2026:

| | Nội dung | Trọng tâm |
|---|---|---|
| **Phần I** | Uncertainty Quantification | Chất lượng khoảng dự báo · benchmark phương pháp hiệu chỉnh · mô hình phụ dùng lịch sử sai số |
| **Phần II** | Chẩn đoán model và cơ chế cấu thành giá | Model sai ở đâu · so sánh 10 model · yếu tố nào cấu thành giá · encode causality |

Phần III đối chiếu hai phần: chỗ nào xác nhận chéo, chỗ nào bổ sung, chỗ nào **tưởng mâu thuẫn mà
không phải**.

---

## Tóm tắt chung

**Phần I — Uncertainty Quantification**

1. Chất lượng khoảng suy giảm theo mức giá: coverage 90,78% ở nhóm dưới 50k xuống **82,56%** ở nhóm
   trên 300k. Độ rộng tương đối giữ nguyên **60,09%** ở cả sáu nhóm.
2. Sáu họ phương pháp hiệu chỉnh mới đều **chưa đạt** tiêu chí không suy giảm theo phân đoạn.
   HGB Residual CQR cải thiện score 2,50% nhưng coverage tụt hơn 1 điểm ở 9 phân đoạn.
3. Ứng viên **Q1-Guarded HGB Residual CQR** giảm interval score **1,90%** trên backtest hồi cứu,
   không phân đoạn nào dưới 85% coverage — nhưng chưa thay thế phương pháp chính thức.
4. Ba mô hình phụ dự báo signed residual đều **không** cải thiện MAE ở bối cảnh trọng yếu và mức giá
   cao. Ba mô hình phụ dự báo uncertainty scale đều **không** vượt normalized-P6.
5. Cấu hình giữ nguyên: **P6** cho point prediction, **normalized-P6** cho uncertainty.

**Phần II — Chẩn đoán model và cơ chế giá**

1. Model fail theo **quãng đường** (η² = 0,0106), **không phải** theo thời điểm (η² ≈ 0) — chênh
   khoảng 100 lần.
2. Bốn hướng cải thiện lần lượt bị đóng bằng số đo. **98,9%** sai số nằm ở tầng giá cơ bản, mà tầng
   đó có trần thông tin **14,98%** trong khi model đạt **14,58%** — đã vượt trần.
3. **10 model** dừng trong dải chưa tới 1 điểm MAPE, kể cả transformer trên GPU. Nhưng **GAM thắng
   GBM +4,02 điểm ở band >300k** và **+2,16 điểm ở chuyến >15 km**.
4. **Cung–cầu là yếu tố mạnh nhất (+35,1%)**; mọi yếu tố thị trường đi 80–96% qua hệ số nhân.
5. Encode causality làm được nhưng là **đánh đổi**: bắt 63% hiệu ứng mưa phải trả +10,9% MAE.

---

# PHẦN I — UNCERTAINTY QUANTIFICATION

> Nguồn: `bao_cao_tuan4_uncertainty_quantification.pdf`. Phần này giữ nguyên kết quả và kết luận
> của bản gốc, rút gọn phần diễn giải.

## I.1 Phạm vi và phương pháp

Tuần 3 đã so sánh ba nhóm phương pháp — conformal chuẩn hoá, quantile regression, CQR — ở ba mức tin
cậy 70/80/90%. Conformal chuẩn hoá cho coverage gần mục tiêu và cấu trúc đơn giản, nhưng **độ rộng
khoảng chủ yếu tỷ lệ thuận với giá dự báo**.

Tuần 4 chuyển trọng tâm từ chỉ số tổng hợp sang **chất lượng có điều kiện**.

| Nội dung | Phương pháp | Mục tiêu đánh giá |
|---|---|---|
| Phân rã độ bất định | Coverage, độ rộng, tỷ lệ vượt cận theo 6 khoảng giá | Xác định nhóm giá rủi ro cao |
| Benchmark đa hướng | Cây, clustering, KNN, weighted conformal, hai phương pháp HGB | Hiệu quả và ổn định theo phân đoạn |
| Ứng viên kết hợp | HGB Residual CQR + khoảng bảo thủ theo cây tại Q1 | Cân bằng cải thiện score với bảo vệ phân đoạn |
| Phân tích theo thời gian | Giá dự báo, vùng bất định, giá thực tế, cao điểm, thời tiết | Sai số tại thời điểm nhạy cảm |
| Phản ứng theo biến | Đổi từng nhóm biến trong miền dữ liệu quan sát | Chiều và quy mô phản ứng |
| Error-memory cho point model | Signed residual: phân cấp, Ridge, CatBoost Q50 | Sửa sai ở mức giá cao và bối cảnh biến động |
| Error-memory cho uncertainty | Absolute-error scale + hiệu chỉnh conformal F1–F2–F3 | Coverage, độ rộng, interval score |

**Thiết kế dữ liệu**

- Mức tin cậy mục tiêu **90%**; phân tích tham chiếu trên **216.090** quan sát.
- Benchmark dùng **153.977** quan sát calibration chia theo thứ tự thời gian: 46.192 fit · 46.193
  conformal calibration · 61.592 để so sánh.
- Error-memory dùng **523.095** dự báo P6 train-OOF, chín lát cắt theo thời gian. Mỗi nhãn sai số
  chỉ vào lịch sử sau tối thiểu 15 phút; lịch sử không truyền qua ranh giới tháng.
- Bộ đặc trưng error-memory gồm **48 biến** ở bốn cấp (toàn cục, dịch vụ, dịch vụ–vùng đón,
  dịch vụ–vùng đón–vùng trả), mỗi cấp hai cửa sổ 1 giờ và 24 giờ.

**Chỉ tiêu đánh giá.** Coverage là **ràng buộc**; độ rộng và mean interval score chỉ được so sánh
sau khi phương pháp giữ được chất lượng theo tháng và theo các phân đoạn đủ mẫu. Tiêu chí "không
suy giảm theo phân đoạn" đặt ở mức chênh lệch coverage không thấp hơn **1 điểm phần trăm** so với
tham chiếu.

## I.2 Chất lượng tham chiếu theo khoảng giá

| Khoảng giá | Số quan sát | Coverage | Trung vị độ rộng | P90 độ rộng | Độ rộng tương đối | Vượt trên / dưới |
|---|---:|---:|---:|---:|---:|---|
| <50k | 2.593 | 90,78% | 26.132 | 29.390 | 60,09% | 8,91% / 0,31% |
| 50–100k | 65.508 | 90,43% | 50.761 | 58.497 | 60,09% | 7,12% / 2,45% |
| 100–150k | 102.633 | 89,28% | 72.438 | 85.823 | 60,09% | 7,89% / 2,83% |
| 150–200k | 37.707 | 89,56% | 100.297 | 113.871 | 60,09% | 7,74% / 2,70% |
| 200–300k | 7.368 | 88,79% | 130.196 | 154.231 | 60,09% | 8,71% / 2,50% |
| >300k | 281 | **82,56%** | 192.712 | 216.553 | 60,09% | **14,23%** / 3,20% |

Nhóm trên 300k chỉ có 281 quan sát nên chịu ảnh hưởng lớn hơn của biến động lấy mẫu.

**Ba nhận xét**

- Coverage giảm từ 90,78% xuống 82,56% khi mức giá tăng.
- Trung vị độ rộng tăng từ 26.132 lên 192.712 đồng, nhưng **độ rộng tương đối giữ nguyên 60,09%**
  ở cả sáu nhóm.
- Tỷ lệ vượt cận trên cao hơn vượt cận dưới ở **mọi** khoảng giá; chênh lệch lớn nhất ở nhóm >300k.

Phương pháp tham chiếu phản ánh **quy mô giá** nhưng chưa điều chỉnh theo **mức độ khó** của từng
quan sát. Rủi ro tập trung ở phía giá thực tế vượt cận trên, đặc biệt tại mức giá lớn.

## I.3 Benchmark sáu họ phương pháp

| Phương pháp | Coverage | Độ rộng bình quân | Cải thiện score | Kết quả |
|---|---:|---:|---:|---|
| Tham chiếu chuẩn hoá | 90,21% | 67.489 | — | Tham chiếu |
| Conformal cục bộ theo cây | 90,09% | 67.026 | 0,33% | Chưa đạt |
| Conformal cục bộ theo cụm | 90,06% | 67.219 | 0,04% | Chưa đạt |
| Conformal theo lân cận gần | 90,29% | 67.784 | 0,07% | Chưa đạt |
| Conformal có trọng số dịch chuyển | 90,07% | 67.164 | 0,01% | Chưa đạt |
| HGB dự báo độ lớn sai số | 90,26% | 67.938 | 0,18% | Chưa đạt |
| HGB Residual CQR | 90,00% | 68.377 | **2,50%** | Chưa đạt |

{{IMG:TM1_benchmark_6_pp.png|Hình I.1 — Coverage, độ rộng bình quân và mean interval score của sáu phương pháp mới cùng ba đối chứng CQR lịch sử, trên chronological calibration holdout 61.592 quan sát. Vùng xanh nhạt là khoảng coverage 88–92%.}}

HGB Residual CQR cải thiện score nhiều nhất (**2,50%**) nhưng coverage tụt hơn một điểm phần trăm ở
**chín phân đoạn đủ mẫu**, tập trung ở nhóm quãng đường Q1 và các giao cắt với giờ cao điểm hoặc
mất cân đối thị trường. Vì vậy chưa đạt tiêu chí.

## I.4 Ứng viên kết hợp bảo vệ Q1

Dùng HGB Residual CQR cho phần lớn quan sát, chuyển sang khoảng conformal theo cây trong nhóm quãng
đường Q1 — quy tắc áp dụng cho **15.225 / 61.592** quan sát.

| Phương pháp | Coverage | Độ rộng bình quân | Mean interval score | Vượt trên / dưới | Cải thiện score |
|---|---:|---:|---:|---|---:|
| Tham chiếu chuẩn hoá | 90,21% | 67.489 | 88.905 | 7,23% / 2,56% | — |
| Q1-Guarded HGB Residual CQR | 90,26% | 68.333 | **87.218** | 5,58% / 4,16% | **1,90%** |

{{IMG:TM2_q1_guarded.png|Hình I.2 — So sánh coverage, độ rộng bình quân và mean interval score giữa ứng viên kết hợp và phương pháp tham chiếu trên cùng 61.592 quan sát.}}

{{IMG:TM3_coverage_cao_diem.png|Hình I.3 — Coverage trong giờ bình thường và giờ cao điểm của phương pháp tham chiếu và ứng viên kết hợp. Đường gạch đỏ là ngưỡng 85%.}}

Trong **68 phân đoạn đủ mẫu**, không phân đoạn nào có coverage dưới 85%; mức suy giảm lớn nhất so
với tham chiếu là **0,91 điểm phần trăm**. Kết quả mang tính **hồi cứu** và chưa được dùng để thay
thế phương pháp chính thức.

Kết quả theo tháng ổn định:

| Tháng | Coverage | Cải thiện score | Khoảng chênh lệch score 95% |
|---|---:|---:|---|
| 2026-01 | 90,19% | 1,84% | [−2,038; −1,539] |
| 2026-02 | 90,29% | 1,40% | [−1,276; −1,117] |
| 2026-03 | 90,31% | 2,29% | [−2,095; −1,784] |

Cả ba khoảng chênh lệch đều nằm hoàn toàn dưới 0.

## I.5 Diễn biến theo thời gian và bối cảnh

{{IMG:TM4_chuoi_thoi_gian.png|Hình I.4 — Giá dự báo, vùng bất định 90% và giá thực tế ngày 26/03/2026. Nền vàng là giờ cao điểm; tam giác là thời điểm mưa; hình vuông là thời tiết chưa xác định.}}

Trong cửa sổ minh hoạ, giá dự báo bám xu hướng chung của giá thực tế và vùng bất định bao phủ phần
lớn dao động khi chuyển sang giờ cao điểm.

{{IMG:TM5_mua_va_mat_can_doi.png|Hình I.5 — Diễn biến giá trên tuyến SYN_ZONE_001→SYN_ZONE_000 trong một ngày có tỷ trọng mưa cao. Biểu đồ dưới là chỉ số mất cân đối thị trường trễ 5 phút.}}

| Số quan sát | Coverage | MAE | Trung vị độ rộng tương đối | Tỷ trọng thời điểm mưa |
|---:|---:|---:|---:|---:|
| 300 | 90,7% | 15.746 | 60,1% | 43,7% |

Một số mức tăng đột biến của giá thực tế vượt cận trên và đồng thời rơi vào giai đoạn mưa hoặc chỉ
số mất cân đối tăng. Quan hệ quan sát được **chưa đủ để kết luận nhân quả**; phương pháp tham chiếu
cũng chưa điều chỉnh độ rộng theo trạng thái thời tiết hay mất cân đối.

## I.6 Phản ứng của model khi biến đầu vào thay đổi

{{IMG:TM6_phan_ung_bien.png|Hình I.6 — Mức thay đổi trung bình của giá dự báo và độ rộng khoảng khi nhóm biến chuyển từ phân vị 10 lên phân vị 90 trong miền dữ liệu quan sát. Kết quả mô tả phản ứng của model, không đại diện cho tác động nhân quả.}}

| Nhóm biến | Chênh lệch giá dự báo | Chênh lệch độ rộng | Điều kiện |
|---|---:|---:|---|
| Quãng đường và thời lượng | 60.136đ | 36.437đ | Đổi đồng thời để giữ vận tốc tuyến |
| Hệ số giá quan sát gần nhất | 18.340đ | 11.112đ | Biến đầu vào trực tiếp |
| Mất cân đối thị trường trễ 5 phút | 22.393đ | 13.570đ | Biến đầu vào trực tiếp |

Bổ sung theo hồ sơ thị trường: giờ cao điểm sáng và chiều cao hơn hồ sơ 13:00 lần lượt **218đ** và
**429đ**; hồ sơ mưa cao hơn trời quang **8.579đ**; nhu cầu Q4 cao hơn Q1 **30.696đ**; cung Q4 thấp
hơn Q1 **12.121đ**. Dữ liệu **không có biến ngày lễ**.

Độ rộng của phương pháp tham chiếu biến thiên gần tỷ lệ thuận với giá dự báo — tức khoảng còn phụ
thuộc chủ yếu vào **quy mô giá**.

## I.7 Mô hình phụ dùng lịch sử sai số

**Nhánh 1 — hiệu chỉnh point prediction** (523.095 quan sát train-OOF)

| Phương pháp | MAE | Δ MAE | Δ critical | Δ giá cao | Δ positive residual | Tháng cải thiện | Kết quả |
|---|---:|---:|---:|---:|---:|---:|---|
| P6 | 17.736 | — | — | — | — | — | Tham chiếu |
| Hierarchical EWMA | 17.813 | +0,435% | −1,030% | −1,105% | +3,909% | 0/3 | Không đạt |
| Ridge error-memory | 17.738 | +0,012% | −0,029% | −0,040% | +1,398% | 1/3 | Không đạt |
| CatBoost Q50 | 17.749 | +0,073% | −0,173% | −0,196% | −0,666% | 0/3 | Không đạt |

Không phương pháp nào **đồng thời** cải thiện critical MAE, high-price MAE, upper-tail error và giữ
ổn định theo tháng. P6 tiếp tục làm point model.

**Nhánh 2 — ước lượng uncertainty scale** (173.966 quan sát F3, point prediction P6 cố định)

| Phương pháp | Coverage | Trung vị độ rộng | Độ rộng bình quân | Mean interval score | Δ score | Kết quả |
|---|---:|---:|---:|---:|---:|---|
| Normalized-P6 | 90,136% | 68.824 | 71.854 | 95.115 | — | Tham chiếu |
| Hierarchical absolute-error | 90,050% | 71.814 | 74.891 | 102.603 | −7,873% | Không đạt |
| Ridge log-absolute-error | 88,648% | 69.127 | ≈5,41×10¹⁴ | ≈5,41×10¹⁴ | Không ổn định | Không đạt |
| CatBoost Q90 absolute-error | 89,345% | 69.121 | 70.545 | 95.207 | −0,097% | Không đạt |

{{IMG:TM7_uncertainty_scale.png|Hình I.7 — Coverage, độ rộng và mean interval score của các uncertainty policy. Ridge cho thấy median width có thể che khuất bất ổn ở phần đuôi.}}

CatBoost Q90 gần tham chiếu nhất — độ rộng bình quân giảm 1,82% — nhưng coverage giảm **0,791 điểm
phần trăm** và interval score tăng 0,097%.

{{IMG:TM8_catboost_that_bai.png|Hình I.8 — Chuỗi giá của CatBoost Q90 trên một tuyến mật độ cao. Vùng uncertainty đặt quanh cùng point prediction P6; giờ cao điểm và thời điểm mưa được chú thích. Hình phục vụ phân tích bối cảnh thất bại.}}

| Bối cảnh | Chênh coverage so với normalized-P6 |
|---|---:|
| Giá dự báo dưới 50k | **−5,011 điểm** |
| Quãng đường Q4 × mất cân đối Q4 | −1,272 điểm |
| Giá dự báo 200–300k | −1,193 điểm |
| Thời điểm mưa | −0,816 điểm |
| Giờ cao điểm | −0,697 điểm |

Error-memory **có chứa tín hiệu** về độ lớn sai số, nhưng mức giảm độ rộng bình quân không bù được
suy giảm coverage ở nhóm giá thấp, nhóm giá cao và các bối cảnh thị trường biến động.

**Một bài học phương pháp:** Ridge có median width 69.127đ nhưng mean width ≈5,41×10¹⁴đ — chỉ số
trung vị có thể che khuất hoàn toàn bất ổn ở phần đuôi. Đánh giá uncertainty phải xem đồng thời
coverage, median width, mean width và interval score.

## I.8 Kết luận Phần I

Điểm yếu chính tập trung ở **mức giá cao** và **trạng thái thị trường biến động**, nơi giá thực tế
có xu hướng vượt cận trên nhiều hơn và coverage suy giảm.

Ứng viên Q1-Guarded ghi nhận cải thiện trên backtest hồi cứu nhưng **chưa thay thế** phương pháp
chính thức. Cả sáu mô hình phụ error-memory — ba cho point prediction, ba cho uncertainty scale —
đều không đạt tiêu chí.

Lịch sử sai số có giá trị **nhận diện quan sát khó dự báo và bối cảnh thất bại**, nhưng chưa đủ ổn
định để hiệu chỉnh point prediction hoặc vận hành như một uncertainty policy độc lập.

**Cấu hình giữ nguyên: P6 cho point model, normalized-P6 cho uncertainty reference.**

---

# PHẦN II — CHẨN ĐOÁN MODEL VÀ CƠ CHẾ CẤU THÀNH GIÁ

> Phần này do nhóm phân tích model thực hiện, độc lập với Phần I.

## II.0 Vì sao làm phần này

Kết thúc tuần 3, hệ thống đã có model dự báo giá đối thủ (MAE ~18.000đ, MAPE 14,65%) và khoảng bất
định 90% (±30%). Nhưng cả hai mới chỉ được báo cáo dưới dạng một con số trung bình — và đó là
giới hạn mà feedback tuần 3 chỉ thẳng vào:

> *"Việc mình forecast giá đối thủ mình cũng sẽ đào sâu được vào là: model mình đang fail ở đâu và
> làm sao để khắc phục thay vì là chung chung model mình chính xác tới mức nào."*

Rà lại kết quả tuần 3 dưới góc nhìn đó, nhóm xác định bốn vấn đề mở — đây là động lực thật sự
của tuần 4:

**① Một con số trung bình có thể đang che một nhóm bị phục vụ tệ.**
Coverage tổng 89,8% nghe như đã đạt cam kết 90%. Nhưng chưa ai kiểm từng mức giá. Nếu có nhóm
hụt sâu — nhất là nhóm chuyến đắt tiền, nơi sai một khoảng tin cậy tốn nhiều nhất — thì con số tổng
sẽ không bao giờ để lộ ra. Rủi ro này chưa được loại trừ.

**② Biết model sai *bao nhiêu* nhưng không biết sai *ở đâu*.**
MAPE 14,65% không nói được nên đầu tư vào đâu. Trước mặt có hai hướng cải thiện với chi phí lệch
nhau cả chục lần — đổi cách hiệu chỉnh khoảng mất vài giờ, train lại model mất vài tuần. Chọn sai
là đốt thời gian, mà hiện chưa có căn cứ nào để chọn.

**③ Chưa loại trừ được khả năng model đơn giản là chưa đủ mạnh.**
Trước khi kết luận "hết dư địa cải thiện", phải thử một họ kiến trúc khác hẳn. Nếu không, mọi
kết luận về giới hạn đều có thể chỉ là giới hạn của lựa chọn kỹ thuật hiện tại.

**④ Model dự báo tốt nhưng chưa giải thích được giá.**
Nó cho ra một con số, không cho biết yếu tố nào đẩy giá và đẩy bao nhiêu. Nên nó chưa dùng được
để ra quyết định pricing, và chưa trả lời được câu what-if — *"nếu cầu tăng 20% thì giá bao nhiêu"*.

Bốn vấn đề này định hình năm mục II.1–II.5 dưới đây.

---


## II.1 Phân rã uncertainty theo mức giá

### II.1.1 Bảng phân rã theo band giá

Khoảng dự báo hiện tại: `giá dự đoán × (1 ± 30,07%)`, mức tin cậy danh nghĩa 90%.
Đo trên tập test 216.090 chuyến (lag 5 phút):

| Predicted-price band | Number of quotes | Actual coverage | Median full width | P90 full width | Median relative width | Upper miss | Lower miss |
|---|---:|---:|---:|---:|---:|---:|---:|
| <50k | 2.716 | 92,42% | 26.729đ | 29.569đ | 60,1% | 7,03% | 0,55% |
| 50–100k | 66.035 | 90,52% | 50.854đ | 58.531đ | 60,1% | 7,07% | 2,40% |
| 100–150k | 102.331 | 89,39% | 72.490đ | 85.914đ | 60,1% | 7,91% | 2,71% |
| 150–200k | 37.353 | 89,61% | 100.328đ | 114.072đ | 60,1% | 7,87% | 2,52% |
| 200–300k | 7.328 | 89,52% | 130.619đ | 154.668đ | 60,1% | 8,01% | 2,47% |
| >300k | 327 | 83,79% | 196.175đ | 226.836đ | 60,1% | 11,62% | 4,59% |
| Tổng | 216.090 | 89,81% | 69.389đ | 103.745đ | 60,1% | 7,64% | 2,55% |

### II.1.2 Ba điều bảng này chỉ ra

**① Cột *Median relative width* bằng nhau ở mọi band — 60,1% — vì đó là hệ quả số học của phương
pháp, không phải kết quả đo được.** Conformal toàn cục dùng một hệ số `q` duy nhất cho mọi
chuyến:

```
khoảng = pred × (1 ± q),  q = 30,07%
⇒ full width    = 2q × pred
⇒ relative width = 2q = 60,1%      ← không phụ thuộc mức giá
```

Nên cột đó bắt buộc hằng số. Bản thân nó không nói lên điều gì; cái đáng đọc là hệ quả của
việc cấp cùng một độ rộng tương đối cho chuyến 50k lẫn chuyến 300k — tức ② ngay dưới. II.1 cho
thấy hai phương pháp UQ khác không có tính chất này.

**② Nhóm `>300k` bị phục vụ tệ nhất.** Coverage 83,79% so với cam kết 90% — hụt 6,2 điểm, và
lệch 8,62 điểm so với nhóm tốt nhất. Đây lại chính là nhóm chuyến đắt tiền nhất, nơi sai một
khoảng tin cậy tốn nhiều nhất. Để đạt 90% nhóm này cần ±41,2% chứ không phải ±30,1%.

**③ Sai lệch không đối xứng.** Ở mọi band, tỷ lệ vượt cận trên cao gấp 3 lần thủng cận dưới
(7,64% vs 2,55%). Nguyên nhân là đuôi phải của phân phối giá — khoảng đối xứng quanh giá dự đoán
không phù hợp với phân phối lệch phải. Ở nhóm `>300k` cả hai loại sai đều tăng vọt (11,62% và 4,59%).

Con số tổng 89,81% trông đạt yêu cầu và che kín cả ba vấn đề trên.

{{IMG:PR1_khoang_theo_muc_gia.png|Hình PR1 — Khoảng bất định theo mức giá. ① một khoảng ±30% thật sự trông ra sao ở từng band: chuyến ~44k ra khoảng 31–58k, chuyến ~326k ra khoảng 228–424k · ② coverage theo band ở 4 phương pháp — chỉ conformal toàn cục tụt ở nhóm >300k · ③ độ rộng tương đối: conformal là đường phẳng, ba phương pháp kia đều nới ra ở band cao. Sinh bởi `tuan_4/ve_uq_truc_quan.py`.}}

**Khoảng thật ở từng band** (trung vị):

| Band | Giá dự đoán | Khoảng 90% | Rộng |
|---|---:|---:|---:|
| <50k | 44k | 31k – 58k | 27k |
| 50–100k | 85k | 59k – 110k | 51k |
| 100–150k | 121k | 84k – 157k | 72k |
| 150–200k | 167k | 117k – 217k | 100k |
| 200–300k | 217k | 152k – 282k | 131k |
| >300k | 326k | 228k – 424k | 196k |

Đây là điều mentor nêu, nhìn bằng hình: khoảng `31–58k` cho chuyến 44k còn dùng để định giá được;
khoảng `228–424k` cho chuyến 326k thì rộng gần 200.000đ — gần như vô dụng cho quyết định.

### II.1.3 Điền bảng cho cả bốn phương pháp

Bảng ở 1.1 mới điền cho một phương pháp — conformal chuẩn hoá, bản đang dùng. Điền nốt cho hai
phương pháp UQ còn lại đã cài đặt (và cả Mondrian ở 1.5) thì thấy ngay: hằng số 60,1% là đặc tính
riêng của conformal toàn cục, không phải của hệ thống.

**Median relative width theo band:**

| Band | Conformal | QR thô | CQR | Mondrian |
|---|---:|---:|---:|---:|
| <50k | 60,1% | 58,4% | 59,9% | 55,3% |
| 50–100k | 60,1% | 62,7% | 63,5% | 59,2% |
| 100–150k | 60,1% | 63,1% | 63,7% | 60,9% |
| 150–200k | 60,1% | 61,8% | 62,2% | 60,3% |
| 200–300k | 60,1% | 61,1% | 61,4% | 60,9% |
| >300k | 60,1% | 69,7% | 69,9% | 82,5% |

Quantile regression học độ rộng riêng cho từng chuyến nên nó tự nới ra ở band cao — chính là
thứ conformal toàn cục không làm được.

**Actual coverage theo band:**

| Band | Conformal | QR thô | CQR | Mondrian |
|---|---:|---:|---:|---:|
| <50k | 92,42% | 86,86% | 90,68% | 90,57% |
| 50–100k | 90,52% | 89,17% | 89,84% | 90,03% |
| 100–150k | 89,39% | 89,40% | 89,73% | 89,75% |
| 150–200k | 89,61% | 89,06% | 89,30% | 89,67% |
| 200–300k | 89,52% | 88,73% | 88,88% | 89,83% |
| >300k | 83,79% | 88,38% | 88,38% | 91,13% |
| Tổng | 89,81% | 89,22% | 89,67% | 89,84% |
| Lệch tối đa | 8,62 điểm | 2,55 điểm | 2,31 điểm | 1,46 điểm |

**Kết luận quan trọng của mục này:** vấn đề nhóm `>300k` không phải chỗ hỏng của model, mà là
chỗ hỏng của một lựa chọn hiệu chỉnh. Ba phương pháp còn lại đều giữ nhóm này quanh 88–91% mà
không cần can thiệp gì thêm.

Conformal toàn cục vẫn là lựa chọn mặc định vì nó hẹp nhất (60,1% so với 62,7% và 63,3%) và có
bảo đảm hữu hạn mẫu. Nhưng cái giá của độ hẹp đó là tính công bằng giữa các nhóm — và II.1.5
cho thấy cách lấy lại tính công bằng mà gần như không tốn thêm độ rộng.

### II.1.4 Khoảng bất định theo khung giờ và thời tiết

Phân rã theo mức giá xong, câu tiếp theo là khoảng có ổn định qua bối cảnh không.

{{IMG:PR2_uq_theo_boi_canh.png|Hình PR2 — Khoảng bất định theo bối cảnh. ① coverage qua 24 giờ, nền cam là giờ cao điểm — biên độ chỉ 1,1 điểm · ② độ rộng tuyệt đối bám sát đường giá dự đoán, tức khoảng nới theo MỨC GIÁ chứ không theo giờ · ③ bốn loại thời tiết cho coverage 89,7–90,1% và độ rộng tương đối y hệt nhau.}}

| Chiều | Coverage | Nhận xét |
|---|---|---|
| Giờ (24 mức) | 89,29% (20h) → 90,42% (9h) | Biên độ 1,13 điểm — gần như phẳng |
| Thời tiết | Rain 89,82% · Clouds 89,67% · Clear 89,91% · Mist 90,10% | Chênh 0,43 điểm |

**Độ rộng tuyệt đối** thì thay đổi rõ theo giờ — từ 50k (3h sáng) lên 82k (18h) — nhưng đó
là vì giá thay đổi theo giờ, không phải vì độ bất định thay đổi. Đường độ rộng ở panel ② bám sát
đường giá dự đoán.

⇒ Khoảng nới ra theo mức giá, không theo bối cảnh. Model không kém tin cậy hơn ở giờ cao điểm
hay khi trời mưa. Kết luận này nhất quán với II.3.1: thời điểm và thời tiết đều có η² ≈ 0.

### II.1.5 Cách sửa — hiệu chỉnh Mondrian theo band

Cấp cho mỗi band một hệ số riêng, tính từ tập calibration:

| Band | Hệ số riêng | Coverage sau | Median full width sau | Relative width sau |
|---|---:|---:|---:|---:|
| <50k | ±27,7% | 90,57% | 24.579đ | 55,3% |
| 50–100k | ±29,6% | 90,03% | 50.047đ | 59,2% |
| 100–150k | ±30,4% | 89,75% | 73.351đ | 60,9% |
| 150–200k | ±30,1% | 89,67% | 100.541đ | 60,3% |
| 200–300k | ±30,5% | 89,83% | 132.353đ | 60,9% |
| >300k | ±41,2% | 91,13% | 269.077đ | 82,5% |
| Tổng | | 89,84% | 70.213đ | 60,9% |

| | Toàn cục | Mondrian |
|---|---:|---:|
| Coverage band `>300k` | 83,79% | 91,13% |
| Lệch coverage tối đa giữa các band | 8,62 điểm | 1,46 điểm |
| Nửa độ rộng trung bình | ±30,07% | ±30,11% |

{{IMG:QD1_mondrian_lam_deu.png|Hình QD1 — Mondrian không làm khoảng HẸP hơn, nó làm khoảng ĐỀU hơn. Trái: theo band giá, lệch coverage 8,62 → 1,46 điểm. Phải: theo quãng đường, 12,61 → 2,53 điểm. Cột xám là hiệu chỉnh toàn cục (một hệ số cho tất cả), cột xanh là Mondrian. Sinh bởi `tuan_4/02_IMPROVE_HAY_GIAM_UNCERTAINTY.ipynb`.}}

**Chi phí: +0,04% độ rộng, vài giờ triển khai, không train lại.**

---

## II.2 Giá theo thời gian, dải bất định và chú thích bối cảnh

### II.2.1 Cách dựng hình

Ba lựa chọn thiết kế, mỗi cái loại một nguồn nhiễu:

| Lựa chọn | Vì sao |
|---|---|
| Khống chế quãng đường 4–6 km | Để đường giá phản ánh thời điểm, không phải độ dài chuyến |
| Gộp bucket 30 phút | Giảm nhiễu cấp chuyến mà vẫn giữ nhịp trong ngày |
| Thời tiết vẽ thành dải sát đáy | Không chồng nền mờ lên nền cao điểm — hai kênh thị giác tách bạch |

{{IMG:TT0_chuoi_thoi_gian.png|Hình TT0 — Giá thật vs dự đoán trong một ngày, kèm dải bất định 90% hiệu chỉnh riêng từng band giá. Nền cam = giờ cao điểm, dải tím sát đáy = đang mưa. Ba tầng: giá (trên), sai số từng bucket (giữa), coverage từng bucket (dưới). Sinh bởi `model/uncertainty/ve_chuoi_thoi_gian.py`.}}

### II.2.2 Sai số ở thời điểm nhạy cảm

| | MAPE |
|---|---:|
| Giờ cao điểm | 14,74% |
| Giờ thường | 14,75% |
| Biên độ qua 24 giờ | 3,8% |

### II.2.3 Model thuộc kịch bản nào

Mentor nêu ba model cùng MAE nhưng phân bổ độ rộng khác nhau. Chạy thật trên tập test:

| Kịch bản | ± cao điểm | Coverage cao điểm | ± giờ thường | Coverage giờ thường |
|---|---:|---:|---:|---:|
| A · đều ±30% | 30,0% | 89,9% | 30,0% | 89,7% |
| B · ±10% CĐ / ±40% GT | 10,0% | 42,3% | 40,0% | 96,3% |
| C · ±40% CĐ / ±10% GT | 40,0% | 96,5% | 10,0% | 42,3% |
| Model của mình | 30,2% | 90,1% | 30,1% | 89,7% |

{{IMG:TT5_ba_kich_ban_theo_thoi_gian.png|Hình TT5 — Ba kịch bản mentor nêu, đặt lên CÙNG một ngày giá thật. Cùng đường giá, cùng dự đoán, chỉ khác cách phân bổ độ rộng khoảng. Chấm đỏ = bucket có coverage cấp chuyến dưới 90%. Ở kịch bản B chấm đỏ dồn hết vào hai vệt cao điểm; ở kịch bản C phủ kín phần còn lại của ngày. Sinh bởi `tuan_4/01_BA_KICH_BAN.ipynb`.}}

{{IMG:TT6_coverage_ba_kich_ban.png|Hình TT6 — Độ rộng mình HỨA (trái) vs coverage mình GIỮ ĐƯỢC (phải). Khung giờ được cấp ±10% chỉ giữ 42% coverage ở cả hai kịch bản B và C, hụt gần 48 điểm so với cam kết 90%.}}

**Ba kết quả:**

1. **Con số ±30% mentor đưa ra trúng phóc.** Chạy thật cho coverage 89,7% — sát cam kết.
2. Model là kịch bản A, tỷ lệ độ rộng cao điểm / giờ thường = 1,004.
3. Kịch bản B và C không tồn tại được trên tập này. Muốn hẹp ở cao điểm mà vẫn giữ 90% thì sai
   số ở cao điểm phải nhỏ hơn *thật sự* — mà II.2.2 cho thấy nó bằng giờ thường.

**Đánh giá:** tin trung tính. Model không mù ở chỗ quan trọng, nhưng cũng không sắc hơn ở đó.

> **Ghi chú về cách vẽ.** Chấm đỏ bám coverage cấp chuyến, không phải phép thử *"đường trung
> bình rơi ngoài dải trung bình"*. Ở kịch bản B, đường giá trung bình vẫn nằm gọn trong dải suốt cao
> điểm dù coverage thật chỉ 42% — đúng kiểu trung bình hoá che mất vấn đề mà mentor cảnh báo ở đề
> xuất 1.

---

## II.3 Model đang fail ở đâu

### II.3.1 Chẩn đoán — model fail ở đâu

Xếp hạng các chiều bằng η² — tỷ lệ phương sai sai số mà chiều đó giải thích được:

| Chiều | η² | MAPE thấp → cao |
|---|---:|---|
| Quãng đường | 0,0106 | 9,16% → 17,52% |
| Tuyến | 0,0079 | 10,96% → 15,00% |
| Band giá | 0,0015 | 13,46% → 18,55% |
| Giờ trong ngày | 0,0001 | 14,48% → 14,85% |
| Thời tiết · cao điểm · cuối tuần | ≤0,0001 | biên độ ≤0,4 điểm |

**Giờ cao điểm không phải chỗ hỏng** — η² gần bằng 0, biên độ 0,05 điểm, dù mentor nêu ba kịch bản
uncertainty quanh nó. Chiều thật sự quan trọng là quãng đường, mạnh gấp khoảng 100 lần. Tuyến
tương quan 0,894 với quãng đường nên là cùng một nguyên nhân.

**Nhưng chuyến dài không phải model làm ẩu:**

| Quãng đường | MAPE model | MAPE persistence | Model vượt |
|---|---:|---:|---:|
| <2 km | 9,16% | 28,0% | 67,3% |
| 4–6 km | 14,95% | 29,7% | 49,7% |
| 8–10 km | 14,90% | 26,0% | 42,8% |
| >15 km | 17,52% | 52,6% | 66,7% |
| *Trung bình* | 14,65% | 27,84% | 47,4% |

{{IMG:QD3_fail_o_dau.png|Hình QD3 — Nhóm sai nhiều nhất (>15 km) cũng chính là nhóm model đóng góp NHIỀU NHẤT. Trái: MAPE theo quãng đường. Giữa: so với mốc persistence. Phải: mức vượt persistence — cao nhất ở cả hai đầu dải. Kết luận: chuyến dài khó một cách nội tại, không phải model kém ở đó.}}

**Hai kiểm tra bổ sung, cả hai đều âm:**

- **Không có thiên lệch hệ thống.** Trung bình lệch +1,60% nhưng trung vị +0,01%, tỷ lệ đoán cao
  hơn thật 50,02%. Nguyên nhân là đuôi phải của phân phối giá. Trừ đi một hằng số sẽ làm hỏng nửa số
  chuyến đang đoán thấp.
- Không có nhóm ngoại lai chi phối. 1% chuyến sai nhất (sai ≥53,1%) chỉ đóng góp 2,7% tổng
  sai số tuyệt đối. Không có phím tắt.

### II.3.2 Hướng ① — hiệu chỉnh lại khoảng

Thử 4 cách chia nhóm (Mondrian), mỗi nhóm một hệ số riêng lấy từ tập calibration:

| Cách hiệu chỉnh | Nửa độ rộng | Coverage | Hẹp hơn gốc |
|---|---:|---:|---:|
| Conformal toàn cục | ±30,07% | 89,81% | — |
| Mondrian theo band giá | ±30,11% | 89,84% | +0,11% |
| Mondrian theo quãng đường | ±29,96% | 89,77% | −0,37% |
| Mondrian theo giờ | ±30,07% | 89,78% | −0,02% |
| Mondrian theo thời tiết | ±30,07% | 89,80% | −0,01% |

**Không cách nào làm hẹp được.** Tốt nhất −0,37%, không đổi gì trên thực tế.

**Vì sao:** mọi cách hiệu chỉnh đều dựa trên ý tưởng *cấp khoảng hẹp cho chuyến dễ, rộng cho chuyến
khó*. Ý tưởng đó chỉ chạy được nếu biết trước chuyến nào khó. Train hẳn một GBM để dự đoán độ
lớn sai số → tương quan hạng với sai số thật chỉ 0,053.

{{IMG:QD2_tran_ly_thuyet.png|Hình QD2 — Dư địa lý thuyết rất lớn nhưng KHÔNG với tới được. Trái: nếu biết trước chuyến nào khó thì chỉ cần ±14,7% thay vì ±30,1% (−51%), nhưng thực tế thu được chỉ −0,37%. Phải: độ khó GBM dự đoán trước vs sai số thật — đám mây điểm là một cột dựng đứng, tương quan hạng 0,053.}}

### II.3.3 Hướng ② — Mondrian để làm *đều*

Mondrian không làm khoảng hẹp hơn, nhưng làm khoảng đều hơn:

| Lệch coverage tối đa | Toàn cục | Mondrian |
|---|---:|---:|
| Giữa các band giá | 8,62 điểm | 1,46 điểm |
| Giữa các nhóm quãng đường | 12,61 điểm | 2,53 điểm |

Nhóm `>15 km` từ 82,58% lên 87,58%. Đây là việc nên làm ngay — vài giờ, không train lại.

### II.3.4 Hướng ③ — quan sát giá nhanh hơn

Đề xuất *"giá đối thủ biến động liên tục, quan sát nhanh hơn thì dự đoán sát hơn và khoảng hẹp
lại"*. Kiểm trực tiếp vì dữ liệu có sẵn bốn mức độ trễ:

| Độ trễ | MAPE model | MAPE persistence | Nửa độ rộng | Coverage |
|---|---:|---:|---:|---:|
| 5′ | 14,65% | 27,84% | ±30,07% | 89,81% |
| 10′ | 14,69% | 28,03% | ±30,05% | 89,66% |
| 15′ | 14,74% | 28,19% | ±30,08% | 89,54% |
| 30′ | 14,91% | 28,67% | ±30,19% | 89,24% |

Rút độ trễ từ 30′ xuống 5′ chỉ cải thiện MAPE 0,26 điểm, độ rộng gần như không đổi (−0,4%).

Để so sánh: `persistence` — thứ *hoàn toàn* phụ thuộc độ tươi của giá quan sát — tệ đi 3,0% khi
độ trễ dài ra. Phép đo có đủ độ nhạy; nó chỉ cho thấy model gần như miễn nhiễm với độ trễ.

{{IMG:QD4_bien_dong_vs_khoang.png|Hình QD4 — Khoảng rộng vì NHIỄU NGANG giữa các báo giá, không phải vì thị trường trôi. Trái: ba đường gần như phẳng theo độ trễ — nếu khoảng rộng do thị trường trôi thì đường xanh phải dốc xuống rõ khi độ trễ ngắn lại. Phải: khống chế quãng đường và thời lượng xong, thêm điều kiện cùng giờ hầu như không hạ được nhiễu (18,6% → 18,5%).}}

**Vậy biến động giá đến từ đâu — ba nguồn, tách bạch:**

| Nguồn | Độ lớn | Model xử lý được không |
|---|---:|---|
| Nhịp thị trường — hệ số nhân theo giờ | biên độ 87,2% (0,851 → 1,592) | ✅ Có — MAPE 1,42% ở tầng này |
| Nhiễu ngang — giữa các báo giá cùng bối cảnh | CV 18,5% | ❌ Không feature nào giải thích được |
| Trôi theo thời gian — 5′ → 30′ | 0,26 điểm MAPE | Quá nhỏ để đáng xử lý |

Giá quan sát trong cửa sổ 60 phút dao động CV 24,9% (trung vị 63 báo giá/cửa sổ), nhưng phần lớn
là do các chuyến khác nhau: khống chế quãng đường và thời lượng còn 18,6%, thêm điều kiện
cùng giờ hầu như không giảm nữa (18,5%).

> Thị trường có động và động rất mạnh — nhưng model đã bắt được nhịp đó. Khoảng ±30% là ảnh
> phản chiếu của nhiễu ngang, không phải cái giá phải trả cho việc quan sát trễ.

### II.3.5 Vậy dư địa còn ở đâu — phân rã sai số theo tầng

Bốn hướng trên đều đóng. Để trả lời *"improve model thì improve chỗ nào"*, phân rã sai số theo hai
tầng của kiến trúc hybrid. Vì `giá = cơ bản × hệ số nhân`, lấy log là tách được thành tổng hai
thành phần (kiểm tra phép tách: sai lệch tối đa 5,8·10⁻⁸).

| | Giá cơ bản | Hệ số nhân |
|---|---:|---:|
| Tỷ trọng phương sai sai số | 98,9% | 1,1% |
| MAPE riêng tầng | 14,58% | 1,42% |

**Thí nghiệm oracle** — cho một tầng dự đoán hoàn hảo, giữ nguyên tầng kia:

| Kịch bản | MAPE giá cuối | Giảm |
|---|---:|---:|
| Hiện tại | 14,65% | — |
| Giá cơ bản hoàn hảo | 1,42% | −90% |
| Hệ số nhân hoàn hảo | 14,58% | −0% |

{{IMG:TK1_sai_so_o_tang_nao.png|Hình TK1 — 98,9% sai số nằm ở tầng giá cơ bản, và tầng đó ĐÃ chạm trần thông tin. ① tỷ trọng phương sai theo tầng · ② thí nghiệm oracle: sửa hệ số nhân về hoàn hảo giảm 0% · ③ trần lý thuyết khi biết thêm thông tin, so với model hiện tại · ④ phân bố giá cơ bản trong một ô chuyến giống hệt nhau — vẫn trải rộng CV 18,7%.}}

Sửa hệ số nhân về hoàn hảo không cải thiện được gì. Toàn bộ dư địa nằm ở tầng giá cơ bản.

### II.3.6 Tầng giá cơ bản còn cải thiện được không

Đo trần thông tin: gom các chuyến giống hệt nhau ở mọi thuộc tính quan sát được, lấy trung bình
nhóm làm dự đoán. Đó là mức chính xác tốt nhất về lý thuyết mà bất kỳ model nào chỉ dùng các
thuộc tính đó có thể đạt.

| Oracle được biết | MAPE trần | % dữ liệu dùng được |
|---|---:|---:|
| Quãng đường (ô 0,5 km) | 16,74% | 100% |
| + thời lượng (ô 5 phút) | 15,22% | 100% |
| + tuyến | 15,19% | 99% |
| + dịch vụ | 14,98% | 99% |
| ◆ Model hiện tại | 14,58% | 100% |


## II.4 Kết quả train các model và so sánh

### II.4.1 Bảng tổng — 10 model trên cùng tập test

Mọi model đánh giá trên cùng 216.090 chuyến (lag 5 phút); các file dự đoán đã kiểm căn hàng
theo `gia_that`.

| # | Model | Kiến trúc | MAPE | So với tốt nhất |
|---|---|---|---:|---:|
| 1 | Hybrid HistGB *(production)* | cơ bản × hệ số nhân | 14,65% | — |
| 2 | Hybrid LightGBM | cơ bản × hệ số nhân | 14,66% | +0,01 |
| 3 | Hybrid XGBoost | cơ bản × hệ số nhân | 14,66% | +0,01 |
| 4 | Transformer | chuỗi 32 báo giá → 2 đầu ra | 14,80%\* | +0,15 |
| 5 | GAM hybrid | cộng dồn, cơ bản × hệ số | 14,89% | +0,24 |
| 6 | Trực tiếp XGBoost | đoán thẳng giá cuối | 15,19% | +0,54 |
| 7 | Trực tiếp LightGBM | đoán thẳng giá cuối | 15,20% | +0,55 |
| 8 | Trực tiếp HistGB | đoán thẳng giá cuối | 15,22% | +0,57 |
| 9 | GAM trực tiếp | đoán thẳng giá cuối | 15,57% | +0,92 |
| 10 | — Persistence *(mốc)* | dùng thẳng giá quan sát trễ | 27,84% | +13,19 |

\* Transformer đo trên tập test đầy đủ 864.360 chuyến (chạy trên Kaggle), các model còn lại trên
tập lag 5 phút.

**Ba điều đọc được từ bảng:**

**① Kiến trúc quan trọng hơn thuật toán.** Ba thuật toán cây trong cùng kiến trúc hybrid chênh nhau
0,01 điểm; nhưng chuyển từ hybrid sang đoán thẳng giá cuối thì mất 0,54 điểm — gấp 50 lần.
Việc tách `giá = cơ bản × hệ số nhân` đáng giá hơn mọi lựa chọn thuật toán.

**② Transformer không mở ra gì mới.** 90.792 tham số, GPU T4, đọc thẳng chuỗi 32 báo giá thay vì ba
con số `mean · std · slope`. Kết quả: MAE 18.008đ so với 18.048đ của Hybrid (tốt hơn 0,22%)
nhưng MAPE 14,80% so với 14,74% (tệ hơn 0,06 điểm). Hai metric ngược chiều ⇒ hoà, chỉ là
phân bổ sai số khác nhau. Không đưa vào pipeline — đổi 0,22% MAE lấy một model cần GPU và train
gấp 4 lần thời gian.

**③ Mọi model đều cách persistence khoảng 13 điểm và cách nhau chưa tới 1 điểm.** Cả một dải kiến
trúc — cây, cộng dồn, attention — dừng ở cùng một chỗ.

### II.4.2 Model sai ở đâu — theo bốn chiều

{{IMG:MS1_sai_so_theo_chieu.png|Hình MS1 — MAPE của 6 model theo band giá · quãng đường · giờ · thời tiết. Mọi model bung sai số ở cùng hai chiều đầu và gần như phẳng ở hai chiều sau. Persistence (đường chấm xám) cũng theo đúng hình dạng đó, chỉ ở mức cao hơn. Sinh bởi `tuan_4/ve_so_sanh_model.py`.}}

Biên độ MAPE của model production theo từng chiều:

| Chiều | Thấp nhất → cao nhất | Biên độ |
|---|---|---:|
| Quãng đường | 9,16% (<2 km) → 17,52% (>15 km) | 8,37 điểm |
| Band giá | 13,46% (<50k) → 18,55% (>300k) | 5,08 điểm |
| Giờ trong ngày | 14,48% → 14,85% | 0,37 điểm |
| Thời tiết | 14,56% → 14,68% | 0,13 điểm |

**Sai số bung ra theo cấu trúc chuyến, không theo bối cảnh.** Hai chiều đầu chênh gấp 20–60 lần hai
chiều sau. Quan trọng hơn: persistence cũng có đúng hình dạng đó — nghĩa là chuyến dài và chuyến
đắt khó dự đoán một cách nội tại, không phải do model làm ẩu.

### II.4.3 Nhưng GAM và GBM sai ở hai chỗ khác nhau

Đây là phát hiện không thấy được nếu chỉ nhìn MAPE tổng.

{{IMG:MS3_gam_vs_gbm.png|Hình MS3 — Chênh lệch MAPE giữa GAM hybrid và Hybrid production, kèm khoảng tin cậy bootstrap 95%. Cột xanh = GAM tốt hơn có ý nghĩa thống kê, đỏ = GBM tốt hơn. GBM thắng ở giữa dải, GAM thắng ở cả hai đuôi.}}

| Nhóm | n | Hybrid | GAM | GAM tốt hơn | KTC 95% |
|---|---:|---:|---:|---:|---|
| Band `<50k` | 2.716 | 13,46% | 17,13% | −3,67 điểm | [−3,98; −3,36] |
| Band `100–150k` | 102.331 | 14,94% | 14,99% | −0,05 điểm | [−0,07; −0,04] |
| Band `>300k` | 327 | 18,55% | 14,52% | +4,02 điểm | [+2,86; +5,25] |
| Quãng đường `<2 km` | 8.314 | 9,16% | 13,32% | −4,16 điểm | [−4,34; −3,97] |
| Quãng đường `>15 km` | 660 | 17,52% | 15,37% | +2,16 điểm | [+1,35; +2,93] |

GAM tệ hơn ở tổng thể (14,89% vs 14,65%) nhưng thắng rõ rệt ở đúng hai nhóm mà GBM yếu nhất.
Khoảng tin cậy bootstrap không chứa 0 nên chênh lệch là thật trên tập test này, dù cỡ mẫu hai nhóm
đuôi nhỏ (327 và 660 chuyến).

**Cách đọc:** GBM chia không gian thành các ô và học trung bình từng ô — rất mạnh ở vùng dày dữ
liệu, nhưng ở đuôi thì mỗi ô chỉ còn vài chuyến. GAM ép quan hệ thành đường cong trơn nên ngoại
suy vào vùng thưa tốt hơn.

⇒ Một hướng đáng thử tuần sau: ghép hai model — dùng GBM cho vùng giữa, GAM cho `>300k` và
`>15 km`. Chi phí thấp vì cả hai model đã có sẵn.

### II.4.4 Dự đoán rơi ra ngoài khoảng ở đâu

{{IMG:MS2_ra_ngoai_khoang.png|Hình MS2 — Tỷ lệ giá thật rơi ngoài khoảng 90%, tách riêng vượt cận trên (cam, phía trên trục) và thủng cận dưới (xanh, phía dưới trục), theo bốn chiều. Đường đứt = mức 10% tương ứng cam kết coverage 90%.}}

| Chiều | Tệ nhất | Tốt nhất |
|---|---|---|
| Band giá | `>300k` — 16,21% rơi ngoài | `<50k` — 7,58% |
| Quãng đường | `>15 km` — 17,42% | `<2 km` — 4,81% |
| Giờ | 8,0% (21h) | 7,1% (3h) |
| Thời tiết | Clouds 7,8% | Mist 7,2% |

**Hai điều:**

**① Lệch chủ yếu về phía vượt cận trên.** Ở mọi nhóm, tỷ lệ giá thật cao hơn cận trên gấp ~3 lần
tỷ lệ thấp hơn cận dưới (7,64% vs 2,55% toàn tập). Khoảng đối xứng quanh giá dự đoán không hợp với
phân phối giá lệch phải — muốn sửa phải dùng khoảng bất đối xứng, không phải nới đều hai bên.

**② Rơi ngoài khoảng bám đúng hai chiều gây sai số.** Nhóm `>15 km` rơi ngoài 17,42% trong khi
cam kết chỉ 10%; nhóm `<2 km` chỉ 4,81% — tức khoảng đang quá rộng ở đó. Theo giờ và thời
tiết thì gần như phẳng.

---

## II.5 Phân tích kỹ hơn các yếu tố cấu thành một mức giá

### II.5.1 Cấu trúc hai tầng của giá

`giá = giá cơ bản × hệ số nhân`

Giá cơ bản trung bình 103.642đ × hệ số nhân trung bình 1,165 = giá cuối 121.367đ. Đây chính là cấu
trúc *market signal multiplier* mentor mô tả.

### II.5.2 Phương pháp — đối chứng ghép cặp

Không chạy được thí nghiệm thật (không ai bật/tắt mưa được), nên chia dữ liệu thành các ô giống
nhau ở mọi yếu tố khống chế, so hai nhóm trong từng ô, rồi bình quân theo số chuyến.

**Ví dụ một ô** — `quãng đường 5–6 km · 18h · ngày thường`:

| | Số chuyến | Giá TB | = Giá cơ bản | × Hệ số nhân |
|---|---:|---:|---:|---:|
| Không mưa | 9.457 | 107.582đ | 89.641đ | 1,199 |
| Có mưa | 6.710 | 119.078đ | 92.417đ | 1,287 |
| Chênh | | +10,69% | +3,10% | +7,33% |

Trong ô này mọi thứ giống nhau nên chênh lệch quy được cho mưa. Làm vậy với 1.050 ô, phủ
1.724.332 chuyến, rồi bình quân → +9,72%.

**Vì sao phải khống chế:** so thẳng mưa vs không mưa trên toàn bộ dữ liệu ra +7,78% — thấp hơn
thật 2 điểm, vì mưa hay rơi vào khung giờ và loại chuyến vốn rẻ hơn. Con số ngây thơ đánh giá
thấp tác động của mưa.

**Khác biệt so với tuần 1** — đây là chỗ mentor nhấn *"natural step further"*:

| | Tuần 1 | Tuần 4 |
|---|---|---|
| Đo gì | Tương quan / hệ số hồi quy | Thay đổi có kiểm soát |
| Cách làm | Trên toàn bộ dữ liệu | Chia ô, so trong từng ô |
| Đo trên | Giá cuối | Cả ba: giá cuối · giá cơ bản · hệ số nhân |

Điểm thứ ba là cái mới quan trọng nhất — nó cho biết yếu tố đi vào tầng nào.

### II.5.3 Bảng phản ứng giá — đủ bộ yếu tố mentor liệt kê

| Yếu tố | Giá cuối | Qua giá cơ bản | Qua hệ số nhân | Phần qua HSN |
|---|---:|---:|---:|---:|
| Cung–cầu (Q1→Q5) | +35,08% | +5,60% | +27,90% | 80% |
| Đường tắc (cùng quãng đường) | +16,52% | +13,43% | +2,70% | 16% |
| Giờ cao điểm | +11,86% | +0,80% | +11,07% | 93% |
| Trời mưa | +9,70% | +3,18% | +6,10% | 63% |
| Cuối tuần | +6,30% | +0,24% | +6,38% | 96% |
| Dịch vụ Premium | −1,29% | −1,02% | −0,25% | — |
| Ngày lễ | *không có* | — | — | — |

{{IMG:CG1_xep_hang_yeu_to.png|Hình CG1 — Cung–cầu là yếu tố mạnh nhất và đi gần như trọn vẹn qua HỆ SỐ NHÂN. Trái: mỗi thanh tách hai màu — xanh là phần đi qua giá cơ bản, cam là phần đi qua hệ số nhân. Phải: đường phản ứng giá theo mất cân đối cung–cầu, ba đường tách bạch giá cuối / hệ số nhân / giá cơ bản. Sinh bởi `tuan_4/04_CAU_THANH_GIA.ipynb`.}}

{{IMG:CG2_cau_truc_vs_thi_truong.png|Hình CG2 — Hai loại yếu tố, hai đường đi tách bạch. ① giá cơ bản tăng theo quãng đường · ② nhưng giá MỖI KM giảm dần, tức có chiết khấu chuyến dài · ③ giờ trong ngày chỉ tác động lên hệ số nhân, đường giá cơ bản phẳng suốt 24 giờ.}}

**Ba kết quả:**

1. **Cung–cầu là yếu tố mạnh nhất** — gấp ba lần giờ cao điểm, gần bốn lần trời mưa. Xác nhận trực
   tiếp cách team mentor nghĩ: giá là kết quả của thay đổi yếu tố thị trường.
2. Quy luật tách bạch. Yếu tố *thị trường* (cung–cầu, giờ, cuối tuần) đi qua hệ số nhân; yếu
   tố *cấu trúc chuyến* (quãng đường, tắc đường) đi qua giá cơ bản.
3. Mưa là ngoại lệ duy nhất — đi cả hai đường: vừa tăng cầu, vừa làm đường tắc khiến chuyến lâu
   hơn. Chuỗi nhân quả khép kín, và điều này sẽ quan trọng ở II.5.6.

**Quãng đường** đo riêng vì là biến liên tục: giá cơ bản mỗi km giảm từ 32.534đ (1–2 km) xuống
13.168đ (17–18 km), tức −60% — chiết khấu rõ cho chuyến dài.

### II.5.4 Ngày lễ — mentor nêu đích danh nhưng dữ liệu không có

Hai vấn đề riêng biệt, cần nói rõ cả hai:

1. **Không có trường** `public_holiday` trong 72 cột.
2. Hiện tượng cũng không có. Kỳ dữ liệu chứa Tết Nguyên Đán 17/02/2026 — dịp giá gọi xe tăng
   mạnh nhất năm ở thực tế:

| | Giá TB |
|---|---:|
| Toàn kỳ 90 ngày | 121.178đ (độ lệch chuẩn theo ngày 4.709đ) |
| Ngày Tết 17/02 | 116.173đ |
| Xếp hạng ngày Tết | 81/90 (1 = đắt nhất) |

⇒ Bộ sinh dữ liệu không mô hình hoá ngày lễ. Câu hỏi cho mentor không phải *"bổ sung cột được
không"* mà là *"dữ liệu thật có hiệu ứng ngày lễ không"* — thêm cột vào bộ hiện tại sẽ tạo ra một
feature rỗng tín hiệu.

### II.5.5 Đường phản ứng — *"price sẽ diễn biến thế nào"*

Mở rộng phép ghép cặp từ hai nhóm lên nhiều mức, mỗi ô tự làm đối chứng cho chính nó:

| Yếu tố | Biên độ | Dạng quan hệ |
|---|---:|---|
| Giờ trong ngày | +54,1% | hai đỉnh (sáng · chiều tối) |
| Mất cân đối cung–cầu (D1→D10) | +50,6% | đơn điệu, lõm |
| Chỉ số cầu | +34,3% | gần tuyến tính |
| Tắc đường (T5→T1) | +27,5% | đơn điệu giảm theo tốc độ |
| Chỉ số cung | −18,3% | đơn điệu ngược chiều |
| Quãng đường | — | luỹ thừa, độ co giãn 0,689 |

{{IMG:DP1_tin_hieu_thi_truong.png|Hình DP1 — Đường phản ứng giá theo ba tín hiệu thị trường, chia 10 nhóm thập phân vị. Cả ba đơn điệu và liên tục, KHÔNG có ngưỡng nhảy bậc. Mất cân đối cung–cầu có độ cong lõm: từ D1 lên D5 giá tăng ~32%, từ D5 lên D10 chỉ thêm ~18% nữa. Chỉ số cung đi ngược chiều như kỳ vọng. Sinh bởi `tuan_4/05_DUONG_PHAN_UNG.ipynb`.}}

{{IMG:DP2_quangduong_tacduong.png|Hình DP2 — Hai yếu tố cấu trúc chuyến. ① giá cơ bản theo quãng đường, độ co giãn 0,689 · ② giá mỗi km giảm từ 32.534đ xuống 13.168đ, chiết khấu chuyến dài · ③ đường tắc đẩy giá qua GIÁ CƠ BẢN chứ không phải hệ số nhân — vì đường tắc làm chuyến lâu hơn.}}

{{IMG:DP3_nhip_gia_theo_gio.png|Hình DP3 — Nhịp giá 24 giờ và xếp hạng biên độ. Trái: hai đỉnh sáng và chiều tối, đường giá cơ bản phẳng suốt ngày — giờ tác động gần như hoàn toàn qua hệ số nhân. Phải: xếp hạng biên độ các yếu tố, màu cam = đi qua hệ số nhân, xanh = qua giá cơ bản.}}

**Hai kết quả đáng chú ý:**

**Surge có hãm.** Đường mất cân đối cung–cầu lõm: từ D1 lên D5 giá tăng ~32%, từ D5 lên D10 chỉ
thêm ~18% nữa. Cơ chế nhân giá không tăng vô hạn ở vùng cầu rất cao.

**Không có ngưỡng nhảy bậc** ở bất kỳ tín hiệu thị trường nào. Đây là câu trả lời cho một câu hỏi đã
gửi mentor tuần trước: không dùng được Regression Discontinuity để ước lượng elasticity nhân quả
từ dữ liệu lịch sử — elasticity vẫn phải dựa vào giả định cho tới khi có thí nghiệm giá hoặc dữ liệu
outcome.

### II.5.6 Encode causality vào model — thử năm biến thể

#### Vấn đề xuất phát

Đo trên tập test xuất hiện một khoảng cách 9 điểm cần giải thích:

| Đo gì | Kết quả |
|---|---:|
| Giá thực tế đổi khi mưa (ghép cặp) | +9,98% |
| Model quy cho bản thân việc trời mưa (partial dependence) | +0,93% |

Cách đọc ở báo cáo tuần 3: *model dùng đường tắt — nó chép giá đối thủ quan sát ở thời điểm trễ thay
vì hiểu mưa*. Tuần này kiểm cách đọc đó bằng cách rút đường tắt ra và train lại.

#### 🔴 Phát hiện — cách đọc cũ quá đơn giản

Rút hẳn feature giá quan sát mà PDP mưa không nhảy (chỉ +1,12%), trong khi hiệu ứng giờ cao
điểm thì nhảy rõ lên +6,90%. Hai yếu tố phản ứng khác nhau ⇒ truy nguyên bằng cách rút từng kênh:

| Cấu hình | MAE | PDP mưa | PDP cao điểm |
|---|---:|---:|---:|
| ① Gốc | 17.983đ | +0,93% | +0,80% |
| ② Bỏ đường tắt (giá quan sát trễ) | 19.269đ | +1,12% | +6,90% |
| ③ Bỏ trung gian (cung–cầu) | 18.005đ | +1,49% | +0,52% |
| ④ Bỏ cả hai | 19.947đ | +6,33% | +7,32% |

*(Mốc thực tế: mưa +9,98% · cao điểm +13,18%)*

{{IMG:EC1_hai_kenh_trung_gian.png|Hình EC1 — Mưa tác động lên giá QUA cung–cầu, không phải trực tiếp. Trái: phải rút CẢ HAI kênh thì hiệu ứng mưa mới hiện ra; giờ cao điểm hiện ngay khi bỏ đường tắt vì gio_vn là feature trực tiếp. Phải: đánh đổi giữa mất độ chính xác và bắt được hiệu ứng, sáu biến thể. Sinh bởi `tuan_4/06_ENCODE_CAUSALITY.ipynb`.}}

**Mưa tác động lên giá hoàn toàn thông qua cung–cầu:**

```
mưa ──► cầu tăng ──► hệ số nhân tăng ──► giá tăng
 └────► đường tắc ──► chuyến lâu hơn ──► giá cơ bản tăng
```

Partial dependence giữ cung–cầu cố định, tức đã chặn mất con đường mà mưa đi qua. Kết quả gần 0
là đúng về mặt toán học, không phải model dốt.

> **Khoảng cách 9 điểm không phải lỗi model.** Nó là chênh lệch giữa hiệu ứng tổng (ghép cặp —
> qua mọi con đường) và hiệu ứng trực tiếp (partial dependence — giữ mọi trung gian cố định).
> Đây là đính chính quan trọng nhất của tuần, xem thêm mục Đính chính.

Kết quả này cũng khớp với một phép đo độc lập ở `tuan_4/03`: rút dần độ tươi của giá quan sát, ở lag
30′ model tự bù 94% phần hiệu ứng mà giá trễ không còn giải thích được.

{{IMG:PU1_rut_cai_nang.png|Hình PU1 — Model KHÔNG chỉ biết chép giá trễ. Càng rút cái nạng ra (độ trễ càng dài), persistence càng tụt nhưng model vẫn giữ hiệu ứng — phần vùng xanh là phần model tự bổ sung, luôn khớp gần đúng phần thiếu. Ở lag 30′ model tự bù 94%.}}

#### Năm biến thể, ba thước đo mỗi biến thể

Đây là bài toán đánh đổi nên phải báo cáo đủ ba con số: độ chính xác · độ rộng khoảng · khoảng
cách so với hiệu ứng thật.

| Biến thể | Δ MAE | Nửa độ rộng | Bắt được hiệu ứng mưa |
|---|---:|---:|---:|
| Gốc (production) | — | ±29,5% | 9% |
| A · ràng buộc đơn điệu | +0,2% | ±29,5% | 8% |
| B · bỏ đường tắt | +7,1% | ±30,1% | 11% |
| C · cấu trúc tách bạch | +0,4% | ±29,6% | 14% |
| D · train ở lag 30′ | +0,7% | ±29,6% | 19% |
| E · bỏ cả hai kênh | +10,9% | ±31,3% | 63% |

Chiều của ràng buộc đơn điệu ở biến thể A lấy trực tiếp từ đường phản ứng ở II.4.5 — đây là chỗ
hai mục nối vào nhau.

#### Trả lời mentor

Mentor viết *"encode được causality info này vào 1 model sẽ khá là tốt trong việc improve accuracy
hay uncertainty"*. Đo được rồi, và trên bộ dữ liệu này câu trả lời là không:

- Không biến thể nào vừa hiểu cơ chế hơn vừa chính xác hơn
- Độ rộng khoảng không cải thiện ở biến thể nào
- Biến thể bắt được nhiều hiệu ứng nhất cũng là biến thể mất nhiều accuracy nhất

Lý do đã có ở II.3.6: model đã chạm sàn sai số của bộ dữ liệu, nên không còn dư địa để vừa thêm
ràng buộc vừa giữ độ chính xác. ⇒ Đây là đánh đổi, không phải cải thiện.

**Điểm cần nói rõ:** model gốc đã trả lời được câu what-if quan trọng nhất — *"cung–cầu đổi thì
giá đổi thế nào"* — vì cung–cầu là feature trực tiếp của nó. Đó chính là *market signal multiplier*.
Cái nó không trả lời được là what-if theo yếu tố nằm thượng nguồn của cung–cầu, như thời
tiết. Ba tình huống cần khả năng đó:

| Tình huống | Vì sao model gốc hỏng |
|---|---|
| Câu what-if — *"mai mưa thì giá bao nhiêu"* | Chưa có giá quan sát để chép |
| Dự báo horizon xa (30–60 phút) | Giá trễ đã cũ |
| Thị trường mới chưa có lịch sử giá đối thủ | Không có đường tắt |

**Khuyến nghị:**

| | Khuyến nghị | Vì sao |
|---|---|---|
| Nên làm | Biến thể A — ràng buộc đơn điệu | Gần như miễn phí (+0,2% MAE), chặn phản ứng ngược dấu khi ngoại suy |
| Chỉ nếu cần what-if thời tiết | Biến thể E | Đắt (+10,9% MAE), chỉ đáng khi thật sự cần |
| Không nên | B, C, D | Mất accuracy mà không bắt thêm được bao nhiêu |

---

## II.6 Hai việc còn lại theo feedback

Hai đề xuất còn lại của mentor, mỗi cái một đoạn — không phát sinh việc mới trong tuần.

### Đưa kết quả vào demo

> **Mentor nói:** *"Khi các em trình bày được những yếu tố này as part of demo thì kết quả của mình
> sẽ rất đáng tin cậy."*

| | |
|---|---|
| Bản demo | `demo/index.html` — bản đồ thật khu Phú Mỹ Hưng, nháy đúp là chạy, không cần cài đặt |
| Dữ liệu | 900 chuyến đại diện + 327 chuyến `>300k` |
| Điểm mạnh | Nút bật/tắt hiệu chỉnh theo band → thấy ngay coverage nhóm `>300k` nhảy từ 84% lên 91% |

Nút bật/tắt là chỗ demo trả lời trực tiếp đề xuất 1 của mentor: người xem nhìn thấy tác động của
việc phân rã theo band thay vì đọc bảng số.

**Hạn chế phải nói trước khi demo:** dữ liệu chỉ phát sinh quanh 3 khu vực, nên bản đồ không
phản ánh độ phủ thật của thành phố.

---

### Acceptance rate — giữ ở mức side objective

> **Mentor nói:** *"Còn về phần acceptance rate thì theo anh các em nên treat nó như một cái side
> objective. Anh sẽ gửi cho các em data bổ sung để làm bài này, tuy nhiên thì đừng đi sâu vào nó
> quá."*

| | |
|---|---|
| Đã làm | Dừng phát triển, giữ nguyên bản v1 và notebook trình bày |
| Trạng thái | Chờ dữ liệu bổ sung mentor gửi |
| Khi có dữ liệu | Kiểm ngay hai trường: `outcome` và `exposure denominator` |

Không đầu tư thêm công sức trong tuần này.

---


---

# PHẦN III — ĐỐI CHIẾU HAI PHẦN

Hai phần làm độc lập trên cùng bộ dữ liệu nên đối chiếu được. Ba nhóm quan hệ:

## III.1 Xác nhận chéo — bốn phát hiện trùng khớp

| Phát hiện | Phần I | Phần II |
|---|---|---|
| Độ rộng tương đối là hằng số theo mức giá | 60,09% ở cả 6 band | 60,1% ở cả 6 band |
| Coverage tụt ở nhóm giá cao nhất | 82,56% (>300k) | 83,79% (>300k) |
| Sai lệch bất đối xứng, nghiêng về vượt cận trên | Ở mọi khoảng giá | 7,64% vs 2,55% |
| Giờ và thời tiết ảnh hưởng nhỏ | CatBoost Q90 chỉ tụt 0,70–0,82 điểm ở hai bối cảnh này | η² ≈ 0 cho cả hai chiều |

Hai phần dùng **hai point model khác nhau** và hai cách chia dữ liệu khác nhau, nhưng ra cùng kết
luận. Đây là bằng chứng chéo mạnh hơn việc một phía đo hai lần.

## III.2 Bổ sung nhau — mỗi phần trả lời một nửa câu hỏi

| Câu hỏi | Phần I trả lời | Phần II trả lời |
|---|---|---|
| Khoảng hiệu chỉnh lại được không? | **Sâu**: 6 họ phương pháp + ứng viên kết hợp + error-memory | Nông: 4 biến thể Mondrian |
| Model sai ở đâu? | Theo phân đoạn, phục vụ chọn uncertainty policy | Theo chiều, kèm η² và so với persistence |
| Model có còn cải thiện được không? | Không đo trần | **Có**: trần thông tin 14,98% vs model 14,58% |
| Giá phản ứng thế nào với từng yếu tố? | **Model nói gì** (P90–P10 trên đầu vào) | **Dữ liệu nói gì** (ghép cặp trên giá thực tế) |

Cặp cuối đáng chú ý: Phần I đo phản ứng **của model**, Phần II đo phản ứng **của thị trường**. Đặt
cạnh nhau thành một phép kiểm định — model có phản ánh đúng cơ chế thật không.

| Yếu tố | Model nói *(Phần I)* | Thực tế nói *(Phần II)* |
|---|---:|---:|
| Mưa vs trời quang | +8.579đ | +9,70% (≈ +11.800đ trên giá TB) |
| Cao điểm chiều vs 13:00 | +429đ | +11,86% (≈ +14.400đ) |
| Cung–cầu Q4 vs Q1 | +30.696đ | +35,08% (≈ +42.600đ) |

Ba dòng cùng chiều, nhưng **model phản ứng yếu hơn thực tế** ở cả ba yếu tố, mạnh nhất ở cao điểm.
Phần II §II.5.6 giải thích: đó là chênh lệch giữa **hiệu ứng trực tiếp** và **hiệu ứng tổng**, không
phải lỗi model.

## III.3 Tưởng mâu thuẫn nhưng không

Hai kết luận dưới đây đọc lướt thì nghịch nhau:

> **Phần I:** Ứng viên Q1-Guarded giảm interval score **1,90%**.
> **Phần II:** Hiệu chỉnh lại khoảng đã cạn, tốt nhất chỉ **−0,37%**.

**Không mâu thuẫn — hai đại lượng khác nhau.** Phần II đo **độ rộng**; Phần I đo **interval score**
(tổng hợp độ rộng và mức phạt khi ra ngoài khoảng). Ứng viên Q1-Guarded thực tế làm độ rộng **tăng**
67.489 → 68.333 đồng, nhưng score vẫn giảm nhờ ít vi phạm hơn.

⇒ Phát biểu đúng cho cả hai: **không có cách nào làm khoảng hẹp hơn đáng kể; nhưng có cách phân bổ
lại độ rộng cho hợp lý hơn.** Đó chính là điều Mondrian làm ở II.1.5 và Q1-Guarded làm ở I.4 — hai
cách tiếp cận khác nhau cho cùng một mục tiêu.

## III.4 Hai chỗ cần thống nhất trước khi trình bày

| # | Điểm lệch | Chi tiết | Cần làm |
|---|---|---|---|
| 1 | **Point model khác nhau** | Phần I dùng **P6** (MAE 17.736đ trên train-OOF); Phần II dùng **Hybrid HistGB** (MAE 18.048đ trên test) | Xác nhận đây là hai model khác nhau hay hai tên gọi; nếu khác thì chốt một model chung |
| 2 | **Số quan sát mỗi band lệch** | Nhóm >300k: 281 *(I)* vs 327 *(II)*; nhóm <50k: 2.593 vs 2.716 | Do band gán theo giá **dự báo** mà hai point model khác nhau. Thống nhất point model là hết lệch |

Cả hai đều **không ảnh hưởng kết luận** — mọi phát hiện đều lặp lại ở cả hai phía — nhưng cần nói
rõ để mentor không hiểu nhầm là số liệu chưa khớp.

## III.5 Việc tuần sau, gộp từ hai phần

| Việc | Nguồn | Chi phí | Vì sao |
|---|---|---|---|
| Thống nhất một point model chung | III.4 | thấp | Điều kiện để hai nhánh dùng chung bảng số |
| Bật Mondrian theo band hoặc quãng đường | II.1.5 | vài giờ | Lệch coverage 12,6 → 2,5 điểm, không train lại |
| Đưa Q1-Guarded vào đánh giá tiến cứu | I.4 | vừa | Đã đạt tiêu chí hồi cứu, cần kiểm trên dữ liệu mới |
| Thử ghép GAM cho nhóm >300k và >15 km | II.4.3 | thấp | GAM thắng +4,02 và +2,16 điểm ở đúng hai nhóm yếu nhất |
| Ràng buộc đơn điệu cho model giá | II.5.6 | ~1 ngày | +0,2% MAE, chặn phản ứng ngược dấu |
| Khoảng bất đối xứng | I.2 + II.4.4 | vừa | Cả hai phần đều thấy lệch nghiêng về vượt cận trên |

## 🔴 Đính chính — ba kết luận tuần trước phải sửa

Ba kết luận báo cáo tuần trước đã phải sửa sau khi đo lại:

### ① *"Model bám giá quan sát chứ không hiểu cơ chế"* — quá nặng

| | |
|---|---|
| Kết luận cũ | Model chép giá quan sát trễ, không hiểu cơ chế mưa |
| Nguyên nhân sai | Chỉ đo partial dependence ở lag 5′ (+0,93%) và so thẳng với hiệu ứng thật (+9,98%). Chưa tách bạch hiệu ứng trực tiếp với hiệu ứng tổng, chưa thử rút từng kênh trung gian |
| Kết luận đúng | Mưa tác động hoàn toàn thông qua cung–cầu. PDP giữ cung–cầu cố định nên đo được hiệu ứng trực tiếp ≈ 0 — điều đó đúng. Rút cả hai kênh thì hiệu ứng hiện ra (+6,33%) |
| Bằng chứng | II.5.6, Hình EC1 |

Đây là đính chính quan trọng nhất vì nó đổi hẳn cách hiểu về việc encode causality.

### ② *"Phải improve model"* — chưa đủ

| | |
|---|---|
| Kết luận cũ | Đường giảm uncertainty đã cạn ⇒ phải improve model |
| Bổ sung | Đường improve model cũng cạn trên bộ dữ liệu này (II.3.6–3.7) |
| Kết luận đúng | Ràng buộc thật sự là dữ liệu, không phải model |

### ③ *"CQR có coverage điều kiện tốt nhất"* — so thiếu đối thủ

| | |
|---|---|
| Kết luận cũ | CQR tốt nhất về coverage điều kiện |
| Nguyên nhân sai | Chỉ so với QR thô, chưa so với Mondrian |
| Kết luận đúng | Không phương pháp nào thắng tuyệt đối trên cả 3 chiều. Mondrian tốt hơn CQR cả về công bằng (0,81 vs 1,09) lẫn độ rộng |

---

## Phụ lục A — Kiểm chứng đã chạy

| Kiểm chứng | Kết quả |
|---|---|
| Phép tách log theo tầng: `log(p̂/p) = log(b̂/b) + log(m̂/m)` | ✅ sai lệch tối đa 5,8·10⁻⁸ |
| Hàm đường phản ứng chạy lại hiệu ứng mưa ở `04` | ✅ khớp +9,72% |
| Chống rò rỉ khi dựng chuỗi cho transformer (`ts ≤ cutoff`) | ✅ assert pass, 99,96% mẫu đủ 32 báo giá |
| Coverage của cả 5 cách hiệu chỉnh ≥ 89% | ✅ cả 5 |
| Tương quan sai số giữa hai tầng giá | ✅ −0,001 — độc lập |
| Ràng buộc đơn điệu áp đúng chiều lấy từ `05` | ✅ 7 feature |
| Sáu biến thể model đánh giá trên cùng tập test | ✅ 216.090 chuyến |
