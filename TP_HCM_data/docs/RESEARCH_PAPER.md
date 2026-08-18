# Dự báo giá đối thủ và lượng hoá độ bất định cho bài toán định giá gọi xe

**Nhóm R&D — GSM/XanhSM · Bộ dữ liệu TP.HCM**
**Phạm vi:** 01/01–31/03/2026 · 1.724.714 lần báo giá · dữ liệu mô phỏng
**Phiên bản:** 1.0 — 17/08/2026

---

## Tóm tắt

Bài báo này trình bày một hệ thống dự báo mức giá mà đối thủ sẽ hiển thị cho một yêu cầu chuyến đi,
tại thời điểm chỉ quan sát được giá đối thủ trễ 5–30 phút, kèm một khoảng tin cậy cho từng dự báo.

Hệ thống dựa trên quan sát rằng giá đối thủ có cấu trúc tích hai tầng — một mức giá nền theo cấu
trúc chuyến, nhân với một hệ số phản ánh trạng thái thị trường. Chúng tôi học riêng từng tầng rồi
nhân lại. Trên tập test tách theo thời gian, hệ thống đạt MAE 18.048đ và MAPE 14,74%, vượt baseline
persistence 47,4%. Khoảng tin cậy dựng bằng conformal chuẩn hoá đạt coverage 89,81% ở mức danh mục
90%, với độ rộng trung bình 72.637đ.

Ngoài kết quả dự báo, chúng tôi báo cáo bốn phân tích:

Thứ nhất, **phân rã sai số theo tầng**: 98,9% phương sai sai số nằm ở tầng giá cơ bản, trong khi
tầng hệ số nhân đã đạt MAPE 1,42%. Điều này định vị lại toàn bộ nỗ lực cải thiện.

Thứ hai, **chẩn đoán theo chiều**: quãng đường là chiều giải thích sai số mạnh nhất (η² = 0,0106),
mạnh hơn khoảng 100 lần so với thời điểm trong ngày (η² ≈ 0,0001) — đi ngược trực giác thông thường
rằng giờ cao điểm là chỗ khó.

Thứ ba, **so sánh model trên nhóm cố định**: khi mỗi model tự chia nhóm theo giá chính nó dự đoán,
lợi thế của GAM ở nhóm giá cao bị phóng đại từ +1,65 lên +4,02 điểm. Chúng tôi trình bày cả hai con
số và giải thích cơ chế tạo ra chênh lệch.

Thứ tư, **cơ chế phản ứng giá**: đo bằng đối chứng ghép cặp trên 1,72 triệu chuyến, cung–cầu là yếu
tố mạnh nhất (+35,08%), và 80–96% tác động của các yếu tố thị trường đi qua tầng hệ số nhân.

---

## Mục lục

> Bấm vào mục để nhảy tới phần tương ứng. Trong Word/WPS còn có thanh điều hướng bên
> trái: **View → Navigation Pane**.

- **[1. Bài toán](#m_1_Bai_toan)**
    - [1.1 Phát biểu](#m_1_1_Phat_bieu)
    - [1.2 Ba cấu phần](#m_1_2_Ba_cau_phan)
    - [1.3 Đơn vị quan sát](#m_1_3_Don_vi_quan_sat)
    - [1.4 Tiêu chí và baseline](#m_1_4_Tieu_chi_va_baseline)
- **[2. Dữ liệu](#m_2_Du_lieu)**
    - [2.1 Phạm vi](#m_2_1_Pham_vi)
    - [2.2 Bản chất dữ liệu và bốn hệ quả](#m_2_2_Ban_chat_du_lieu_va_bon_he_qua)
    - [2.3 Chia tập theo thời gian](#m_2_3_Chia_tap_theo_thoi_gian)
- **[3. Cấu phần (i) — Yếu tố cấu thành giá](#m_3_Cau_phan_i_Yeu_to_cau_thanh_gia)**
    - [3.1 Cấu trúc hai tầng](#m_3_1_Cau_truc_hai_tang)
    - [3.2 Phương pháp — đối chứng ghép cặp](#m_3_2_Phuong_phap_doi_chung_ghep_cap)
    - [3.3 Bảng phản ứng giá](#m_3_3_Bang_phan_ung_gia)
    - [3.4 Ngày lễ — thiếu cả cột lẫn hiện tượng](#m_3_4_Ngay_le_thieu_ca_cot_lan_hien_tuon)
- **[4. Cấu phần (ii) — Kiến trúc model](#m_4_Cau_phan_ii_Kien_truc_model)**
    - [4.1 Vì sao hybrid hai tầng](#m_4_1_Vi_sao_hybrid_hai_tang)
    - [4.2 Đặc trưng](#m_4_2_Dac_trung)
    - [4.3 Huấn luyện](#m_4_3_Huan_luyen)
- **[5. Kết quả dự báo](#m_5_Ket_qua_du_bao)**
    - [5.1 Kết quả tổng](#m_5_1_Ket_qua_tong)
    - [5.2 Kiến trúc neural](#m_5_2_Kien_truc_neural)
    - [5.3 Sai số nằm ở tầng nào](#m_5_3_Sai_so_nam_o_tang_nao)
- **[6. Chẩn đoán — model khó ở đâu](#m_6_Chan_doan_model_kho_o_dau)**
    - [6.1 Xếp hạng các chiều](#m_6_1_Xep_hang_cac_chieu)
    - [6.2 Chuyến dài khó, nhưng không phải model làm ẩu](#m_6_2_Chuyen_dai_kho_nhung_khong_phai_mo)
    - [6.3 Không có phím tắt](#m_6_3_Khong_co_phim_tat)
    - [6.4 Giới hạn thông tin của bộ feature](#m_6_4_Gioi_han_thong_tin_cua_bo_feature)
    - [6.5 So sánh model trên nhóm cố định](#m_6_5_So_sanh_model_tren_nhom_co_dinh)
- **[7. Cấu phần (iii) — Lượng hoá độ bất định](#m_7_Cau_phan_iii_Luong_hoa_do_bat_dinh)**
    - [7.1 Ba phương pháp](#m_7_1_Ba_phuong_phap)
    - [7.2 Coverage điều kiện](#m_7_2_Coverage_dieu_kien)
    - [7.3 Hiệu chỉnh Mondrian](#m_7_3_Hieu_chinh_Mondrian)
    - [7.4 Ba kịch bản phân bổ độ rộng](#m_7_4_Ba_kich_ban_phan_bo_do_rong)
    - [7.5 Sai lệch bất đối xứng](#m_7_5_Sai_lech_bat_doi_xung)
    - [7.6 Vì sao khoảng không hẹp lại được](#m_7_6_Vi_sao_khoang_khong_hep_lai_duoc)
- **[8. Model có học đúng cơ chế giá không](#m_8_Model_co_hoc_dung_co_che_gia_khong)**
    - [8.1 Vấn đề](#m_8_1_Van_de)
    - [8.2 Hiệu ứng trực tiếp và hiệu ứng tổng](#m_8_2_Hieu_ung_truc_tiep_va_hieu_ung_ton)
    - [8.3 Kiểm chứng bằng cách cắt từng kênh](#m_8_3_Kiem_chung_bang_cach_cat_tung_kenh)
- **[9. Hệ thống demo](#m_9_He_thong_demo)**
- **[10. Giới hạn](#m_10_Gioi_han)**
- **[11. Hướng tiếp theo](#m_11_Huong_tiep_theo)**
- **[Phụ lục A — Quy ước tái lập](#m_Phu_luc_A_Quy_uoc_tai_lap)**
- **[Phụ lục B — Nhật ký đính chính](#m_Phu_luc_B_Nhat_ky_dinh_chinh)**

---

# 1. Bài toán

## 1.1 Phát biểu

Tại thời điểm $t$, cho một yêu cầu chuyến đi với đặc trưng $x$ (quãng đường, thời lượng, tuyến,
dịch vụ, thời tiết, giờ), và lịch sử giá đối thủ quan sát được đến $t - \Delta$, cần dự báo mức giá
đối thủ sẽ hiển thị:

$$\hat p = \mathbb{E}[\,p \mid x,\ \mathcal{H}_{t-\Delta}\,], \qquad \Delta \in \{5, 10, 15, 30\}\ \text{phút}$$

trong đó $p$ là `target_shown_price`. Đồng thời dựng khoảng $[\ell, u]$ sao cho
$\mathbb{P}(p \in [\ell, u]) \ge 1 - \alpha$ với $\alpha = 0{,}10$.

Độ trễ $\Delta$ là thứ khiến bài toán không tầm thường. Nếu quan sát được giá đối thủ ngay tại thời
điểm cần ra quyết định thì chỉ cần đọc giá, không cần model. Dataset mô phỏng đúng ràng buộc thực
tế: giá đối thủ luôn đến muộn.

## 1.2 Ba cấu phần

Đề bài được chia thành ba cấu phần, và bài báo trình bày kết quả theo đúng thứ tự này:

| Cấu phần | Câu hỏi | Trình bày ở |
|---|---|---|
| (i) | Yếu tố nào cấu thành một mức giá, và đổi một yếu tố thì giá đổi bao nhiêu | §3 |
| (ii) | Dự báo giá đối thủ chính xác đến đâu | §4, §5 |
| (iii) | Mỗi dự báo đáng tin đến mức nào | §7 |

Cấu phần (i) không chỉ là phân tích mô tả. Nó quyết định kiến trúc model ở §4 và cho phép kiểm định
xem model đã học đúng cơ chế hay chưa ở §8.

## 1.3 Đơn vị quan sát

Dataset có **hai mức hạt**, và lẫn lộn hai mức này là lỗi phổ biến nhất khi đọc số:

| Mức | Khoá | Số dòng | Dùng khi |
|---|---|---:|---|
| Forecast example | `forecast_example_id` | 6.897.051 | Huấn luyện và đánh giá model |
| Target request | `target_request_id` | 1.724.714 | Phân tích cấu thành giá |

Mỗi `target_request` xuất hiện **4 lần**, một lần cho mỗi mức độ trễ. Nghĩa là khi phân tích yếu tố
cấu thành giá, phải khử trùng theo `target_request_id` trước — nếu không, mỗi chuyến được đếm bốn
lần và mọi kiểm định thống kê đều sai mức ý nghĩa.

## 1.4 Tiêu chí và baseline

Baseline là **persistence**: lấy luôn giá quan sát được gần nhất làm dự báo. Đây là cách làm ngây
thơ nhất và là ngưỡng tối thiểu — một model không vượt được persistence thì không đáng vận hành.

Metric chính là MAPE, chia cho giá thật. Chúng tôi cũng báo cáo MAE và R². Với khoảng tin cậy, hai
metric là coverage (tỷ lệ giá thật rơi trong khoảng) và độ rộng trung bình. Hai metric này phải đọc
cùng nhau: nới khoảng ra vô hạn thì coverage đạt 100% mà vô dụng.

---

# 2. Dữ liệu

## 2.1 Phạm vi

| | |
|---|---|
| Kỳ dữ liệu | 01/01/2026 – 31/03/2026 (90 ngày) |
| Số lần báo giá | 1.724.714 |
| Số forecast example | 6.897.051 |
| Số trường | 72 |
| Khu vực | 3 điểm quanh Phú Mỹ Hưng, Quận 7 |
| Dịch vụ | 2 (Standard, Premium) |
| Nền tảng đối thủ | 1 |

## 2.2 Bản chất dữ liệu và bốn hệ quả

Toàn bộ dữ liệu có `is_synthetic = True`. Đây không phải chi tiết phụ mà là ràng buộc định hình cách
đọc mọi kết quả trong bài báo:

1. **Mọi con số mô tả hành vi của bộ sinh dữ liệu**, không phải bằng chứng về thị trường TP.HCM
   thật. Khi chúng tôi viết "mưa làm giá tăng 9,70%", phát biểu đúng là "bộ sinh dữ liệu đặt hệ số
   mưa tương đương 9,70%".
2. **Cấu trúc sinh dữ liệu có thể đơn giản hơn thực tế**, nên độ chính xác đạt được ở đây là cận
   trên lạc quan cho dữ liệu thật.
3. **Một số hiện tượng thực tế không tồn tại trong dữ liệu.** §3.4 chỉ ra rằng ngày lễ không được mô
   hình hoá.
4. **Không có nhãn chấp nhận/từ chối giá**, nên mọi phân tích về hành vi khách hàng chỉ dừng ở mô
   hình cấu trúc có giả định, không train được.

## 2.3 Chia tập theo thời gian

Chia theo thời gian, không chia ngẫu nhiên. Chia ngẫu nhiên sẽ để chuyến của cùng một khoảng thời
gian rơi vào cả train lẫn test, và vì các chuyến gần nhau về thời gian có giá tương quan mạnh, kết
quả sẽ lạc quan giả.

Hai quy ước tập test cùng tồn tại trong dự án và cần nói rõ khi trích dẫn:

| Tập | Số dòng | MAPE Hybrid | MAPE persistence |
|---|---:|---:|---:|
| Test đầy đủ (4 độ trễ) | 864.360 | 14,74% | 28,18% |
| Test độ trễ 5 phút | 216.090 | 14,65% | 27,84% |

Tập calibration dùng để hiệu chỉnh khoảng tin cậy gồm 615.908 chuyến (153.977 ở độ trễ 5 phút),
tách riêng và model chưa từng thấy.

---

# 3. Cấu phần (i) — Yếu tố cấu thành giá

## 3.1 Cấu trúc hai tầng

Phân tích dữ liệu cho thấy giá đối thủ có dạng tích:

$$\text{giá} = \text{giá cơ bản} \times \text{hệ số nhân}$$

Giá cơ bản trung bình 103.642đ, hệ số nhân trung bình 1,165, cho giá cuối trung bình 121.367đ.

Phân biệt hai tầng có ý nghĩa vận hành trực tiếp, vì mỗi tầng đòi hỏi một loại phản ứng khác nhau:

| Tầng | Phản ánh | Bài toán tương ứng |
|---|---|---|
| Giá cơ bản | Cấu trúc chuyến — dài hơn, lâu hơn, tuyến khác | Ước lượng thời lượng, quy hoạch tuyến |
| Hệ số nhân | Trạng thái thị trường — cung cầu lệch | Điều phối cung |

## 3.2 Phương pháp — đối chứng ghép cặp

Không chạy được thí nghiệm thật (không ai bật tắt mưa được), nên chúng tôi dùng đối chứng ghép cặp:

1. Chia dữ liệu thành các **ô** giống nhau ở mọi yếu tố khống chế.
2. Trong từng ô, so hai nhóm chỉ khác nhau ở đúng yếu tố đang xét.
3. Bình quân các ô theo số chuyến.

Mỗi yếu tố có bộ khống chế riêng, chọn để chặn đúng đường nhiễu đặc thù của nó:

| Yếu tố xét | Khống chế | Vì sao |
|---|---|---|
| Trời mưa | quãng đường · giờ · cuối tuần | Mưa hay rơi buổi chiều — không khống chế giờ sẽ tính nhầm hiệu ứng cao điểm thành hiệu ứng mưa |
| Giờ cao điểm | quãng đường · thời tiết · cuối tuần | Cao điểm chỉ có ngày thường |
| Cung–cầu | quãng đường · giờ · thời tiết | Cung–cầu tương quan mạnh với giờ |

Điểm mấu chốt: cùng một hàm chạy trên giá cuối, giá cơ bản và hệ số nhân. Nhờ vậy ba con số so sánh
trực tiếp được với nhau, và cho biết yếu tố đó đi vào tầng nào.

## 3.3 Bảng phản ứng giá

Đo trên 1.724.714 chuyến độc lập (đã khử trùng theo `target_request_id`):

| Yếu tố | Giá cuối | Qua giá cơ bản | Qua hệ số nhân | Phần qua hệ số nhân |
|---|---:|---:|---:|---:|
| Cung–cầu (Q1→Q5) | +35,08% | +5,60% | +27,90% | 80% |
| Đường tắc (cùng quãng đường) | +16,52% | +13,43% | +2,70% | 16% |
| Giờ cao điểm | +11,86% | +0,80% | +11,07% | 93% |
| Trời mưa | +9,70% | +3,18% | +6,10% | 63% |
| Cuối tuần | +6,30% | +0,24% | +6,38% | 96% |
| Dịch vụ Premium | −1,29% | −1,02% | −0,25% | — |

🖼️ `CG1_xep_hang_yeu_to.png` · `CG2_cau_truc_vs_thi_truong.png`

Ba điều rút ra:

**Cung–cầu mạnh nhất**, gấp ba lần giờ cao điểm. Giá về bản chất là kết quả của thay đổi yếu tố thị
trường, không phải một bảng giá tĩnh cộng phụ phí.

**Quy luật tách bạch.** Yếu tố *thị trường* (cung–cầu, giờ, cuối tuần) đi qua hệ số nhân với tỷ lệ
80–96%. Yếu tố *cấu trúc chuyến* (quãng đường, tắc đường) đi qua giá cơ bản. Đây là bằng chứng thực
nghiệm cho kiến trúc hai tầng ở §4, chứ không phải chọn kiến trúc rồi đi tìm số ủng hộ.

**Mưa là ngoại lệ duy nhất** — nó đi cả hai đường. Chuỗi nhân quả khép kín: mưa làm tăng cầu nên hệ
số nhân tăng 6,10%, đồng thời mưa làm đường tắc nên chuyến lâu hơn và giá cơ bản tăng 3,18%. Điều
này quay lại có ý nghĩa ở §8.

Quãng đường không đo bằng ghép cặp nhị phân vì nó là biến liên tục và chính là thứ đang được khống
chế ở mọi phép đo khác. Đo riêng: giá cơ bản trên mỗi km giảm từ 32.534đ (chuyến 1–2 km) xuống
13.168đ (chuyến 17–18 km), tức **−60%** — có chiết khấu rõ rệt cho chuyến dài.

## 3.4 Ngày lễ — thiếu cả cột lẫn hiện tượng

Dataset không có trường `public_holiday`. Quan trọng hơn, **hiện tượng cũng không tồn tại**. Kỳ dữ
liệu chứa Tết Nguyên Đán 17/02/2026 — dịp giá gọi xe tăng mạnh nhất năm trong thực tế:

| | Giá trung bình |
|---|---:|
| Toàn kỳ 90 ngày | 121.178đ (độ lệch chuẩn theo ngày 4.709đ) |
| Ngày Tết 17/02 | 116.173đ |
| Xếp hạng ngày Tết | 81/90 (1 = đắt nhất) |

Bộ sinh dữ liệu không mô hình hoá ngày lễ. Thêm cột `public_holiday` vào bộ hiện tại sẽ tạo ra một
feature rỗng tín hiệu. Đây là ví dụ cho hệ quả (3) ở §2.2.

---

# 4. Cấu phần (ii) — Kiến trúc model

## 4.1 Vì sao hybrid hai tầng

Thay vì học thẳng giá cuối, chúng tôi học riêng hai tầng rồi nhân lại:

```
Đặc trưng chuyến ──┬─→ [Model giá cơ bản]  → b̂
                   │
Tín hiệu thị trường ┴─→ [Model hệ số nhân] → m̂
                                              │
                                    p̂ = b̂ × m̂
```

Ba lý do:

1. **Khớp cơ chế sinh giá thật** — §3.3 cho thấy hai nhóm yếu tố đi vào hai tầng khác nhau. Học
   riêng cho phép mỗi nhánh dùng bộ feature phù hợp.
2. **Chẩn đoán được** — khi sai, biết ngay sai ở tầng nào. §5.3 khai thác điều này.
3. **Hai tầng có độ khó rất khác nhau** — hệ số nhân đạt R² 0,96 còn giá cơ bản chỉ 0,66. Gộp
   chung sẽ để bài toán dễ bị bài toán khó kéo xuống.

## 4.2 Đặc trưng

Điểm quan trọng nhất trong thiết kế feature là **chống rò rỉ**. Nhánh giá cơ bản dùng
`latest_observed_base` — giá quan sát trễ đã bóc phần surge ra. Nhánh hệ số nhân dùng nhóm feature
cung–cầu. Baseline dự đoán trực tiếp dùng `latest_observed_price` vốn đã gồm surge.

Nếu để nhánh giá cơ bản nhìn thấy giá đã gồm surge, nó sẽ học lại một phần hệ số nhân, và phép phân
rã sai số ở §5.3 mất ý nghĩa vì hai tầng không còn độc lập.

Mọi feature lịch sử đều tính đến mốc $t - \Delta$, không bao giờ vượt qua thời điểm dự báo.

## 4.3 Huấn luyện

Thuật toán chính là gradient boosting trên cây (HistGradientBoosting cho cấu hình chốt, có đối chiếu
LightGBM và XGBoost). Toàn bộ pipeline chạy lại trong khoảng 45 phút trên máy phát triển.

Chúng tôi đã thử tinh chỉnh siêu tham số bằng Optuna 40 trial — cải thiện thu được là **2 VND** trên
MAE. Ném thêm 49 cột feature vào — cải thiện **6 VND**. Hai kết quả này là chỉ dấu sớm cho §6.

---

# 5. Kết quả dự báo

## 5.1 Kết quả tổng

Trên tập test đầy đủ 864.360 chuyến, tách theo thời gian:

| Model | MAE | MAPE | R² |
|---|---:|---:|---:|
| **Hybrid (chốt)** | **18.048đ** | **14,74%** | ~0,73 |
| ├─ nhánh giá cơ bản | 15.030đ | 14,58% | 0,6564 |
| └─ nhánh hệ số nhân | 0,0232 | 1,90% | 0,9609 |
| XGBoost dự đoán trực tiếp | 18.807đ | 15,34% | |
| LightGBM dự đoán trực tiếp | 18.809đ | 15,34% | |
| HistGB dự đoán trực tiếp | 18.834đ | 15,36% | |
| GAM | 19.170đ | 15,70% | |
| Persistence *(baseline)* | 33.683đ | 28,18% | 0,0191 |

Trên tập độ trễ 5 phút, model vượt persistence **47,4%**.

Hai điều đáng chú ý ngay ở bảng này. Thứ nhất, **kiến trúc hai tầng thắng dự đoán trực tiếp** khoảng
0,6 điểm MAPE — không lớn nhưng nhất quán trên cả ba thuật toán cây. Thứ hai, **bốn thuật toán khác
nhau chỉ chênh nhau 1,9%**, tức lựa chọn thuật toán gần như không quyết định kết quả.

## 5.2 Kiến trúc neural

Chúng tôi đã dựng và huấn luyện một Transformer đọc thẳng chuỗi 32 báo giá gần nhất:

```
CHUỖI K×7 → Linear → + positional → TransformerEncoder ×2, 4 head → mean pool
                                                                        │
TĨNH (embedding danh mục + 12 feature số) ──────────────────────────────┤
                                                                        ▼
                                                            MLP → 2 đầu ra
                                                    log(giá cơ bản) · hệ số nhân
```

90.792 tham số, dự đoán hai đầu ra rồi nhân lại giống kiến trúc Hybrid.

| Model | MAE | MAPE |
|---|---:|---:|
| Hybrid GBM | 18.048đ | 14,74% |
| Transformer | 18.008đ | 14,80% |

Kết quả **hoà**: MAE tốt hơn 0,22% nhưng MAPE kém 0,06 điểm. Trước khi chạy Transformer đầy đủ,
chúng tôi làm một phép thử rẻ bằng LightGBM để xem chuỗi thô có mang thêm thông tin so với nhóm
thống kê tổng hợp hay không:

| Bộ feature | MAE | MAPE |
|---|---:|---:|
| A. Chỉ feature cơ bản, không lịch sử giá | 19.258đ | 15,34% |
| B. + nhóm thống kê tổng hợp *(mốc)* | 18.407đ | 14,81% |
| C. + chuỗi 32 báo giá thô, bỏ nhóm tổng hợp | 18.397đ | 14,81% |
| D. + cả hai | 18.402đ | 14,81% |

Lịch sử giá có giá trị thật (bỏ đi tệ hơn 4,4%), nhưng chuỗi thô và nhóm tổng hợp cho kết quả y hệt.
Nhóm `mean/std/slope` cùng giá quan sát gần nhất đã là **thống kê đủ** cho chuỗi. Transformer đọc
chuỗi vì thế không có gì mới để đọc — và kết quả thực nghiệm xác nhận đúng dự đoán đó.

## 5.3 Sai số nằm ở tầng nào

Vì giá là tích của hai tầng, lấy log là tách được sai số:

$$\log\frac{\hat p}{p} = \log\frac{\hat b}{b} + \log\frac{\hat m}{m}$$

Kiểm tra phép tách trên dữ liệu: sai lệch tối đa 5,8·10⁻⁸, tức tách chuẩn.

| | Giá cơ bản | Hệ số nhân | Tương tác |
|---|---:|---:|---:|
| Tỷ trọng phương sai sai số | **98,9%** | 1,1% | −0,0% |
| MAPE riêng tầng | 14,58% | **1,42%** | — |

Tương quan giữa sai số hai tầng là −0,001, tức độc lập — xác nhận thiết kế chống rò rỉ ở §4.2 hoạt
động đúng.

Thí nghiệm oracle: cho một tầng dự đoán hoàn hảo, giữ nguyên tầng kia.

| Kịch bản | MAPE giá cuối | Giảm |
|---|---:|---:|
| Hiện tại | 14,65% | — |
| Giá cơ bản hoàn hảo | 1,42% | −90% |
| Hệ số nhân hoàn hảo | 14,58% | −0% |

🖼️ `TK1_sai_so_o_tang_nao.png`

**Sửa hệ số nhân về hoàn hảo không cải thiện được gì.** Toàn bộ dư địa nằm ở tầng giá cơ bản. Kết
quả này có hệ quả trực tiếp lên kế hoạch: mọi feature thị trường thêm vào sẽ rơi vào tầng đã gần
hoàn hảo, nên không nên kỳ vọng chúng cải thiện giá cuối.

---

# 6. Chẩn đoán — model khó ở đâu

## 6.1 Xếp hạng các chiều

Xếp hạng bằng η², tỷ lệ phương sai sai số mà mỗi chiều giải thích được:

| Chiều | η² | MAPE thấp → cao |
|---|---:|---|
| **Quãng đường** | **0,0106** | 9,16% → 17,52% |
| Tuyến | 0,0079 | 10,96% → 15,00% |
| Band giá | 0,0015 | 13,46% → 18,55% |
| Giờ trong ngày | 0,0001 | 14,48% → 14,85% |
| Thời tiết · cao điểm · cuối tuần | ≤0,0001 | biên độ ≤0,4 điểm |

🖼️ `QD3_fail_o_dau.png`

**Phát hiện đi ngược trực giác:** giờ cao điểm — chiều mà mọi thảo luận về uncertainty thường xoay
quanh — có η² ≈ 0. Chiều thật sự quan trọng là quãng đường, mạnh hơn khoảng 100 lần. Tuyến đứng thứ
hai nhưng tương quan 0,894 với quãng đường, tức cùng một nguyên nhân.

## 6.2 Chuyến dài khó, nhưng không phải model làm ẩu

So sánh model với persistence theo từng nhóm quãng đường:

| Quãng đường | MAPE model | MAPE persistence | Model vượt |
|---|---:|---:|---:|
| <2 km | 9,16% | 28,04% | 67,3% |
| 5–8 km | 14,99% | 27,81% | 46,1% |
| 8–12 km | 14,90% | 26,33% | 43,4% |
| **>15 km** | **17,52%** | 52,66% | **66,7%** |
| *Toàn tập* | 14,65% | 27,84% | 47,4% |

Nhóm `>15 km` sai nhiều nhất **và** là nơi model đóng góp nhiều nhất so với baseline. Chuyến dài khó
một cách nội tại — bản thân giá của chúng biến động mạnh hơn — chứ không phải model kém ở đó.

## 6.3 Không có phím tắt

Hai kiểm tra loại trừ các cách sửa rẻ tiền:

**Không có thiên lệch hệ thống.** Trung bình lệch +1,60% nhưng trung vị chỉ +0,01%, và tỷ lệ đoán
cao hơn thật là 50,02%. Chênh lệch giữa trung bình và trung vị đến từ đuôi phải của phân phối giá,
không phải model lệch. Trừ đi một hằng số sẽ làm hỏng nửa số chuyến đang đoán thấp.

**Không có nhóm ngoại lai chi phối.** 1% chuyến sai nhất (sai ≥53,1%) chỉ đóng góp 2,7% tổng sai số
tuyệt đối. Không thể cải thiện đáng kể bằng cách xử lý riêng một nhóm nhỏ.

## 6.4 Giới hạn thông tin của bộ feature

Câu hỏi tự nhiên tiếp theo: giá cơ bản còn dao động bao nhiêu sau khi đã biết mọi thứ quan sát được
về chuyến?

Chúng tôi ước lượng bằng phương pháp oracle: gom các chuyến giống hệt nhau ở mọi thuộc tính quan sát
được, lấy trung bình nhóm làm dự đoán. Đó là mức chính xác tốt nhất về lý thuyết mà bất kỳ model nào
chỉ dùng các thuộc tính đó có thể đạt.

| Oracle được biết | MAPE | % dữ liệu phủ |
|---|---:|---:|
| Quãng đường (ô 0,5 km) | 16,74% | 100% |
| + thời lượng (ô 5 phút) | 15,22% | 100% |
| + tuyến | 15,19% | 99% |
| + dịch vụ | 14,98% | 99% |
| ◆ Model hiện tại | **14,58%** | 100% |

🖼️ `CG3_tran_thong_tin_gia_co_ban.png`

Model đạt 14,58%, tức đã ngang mức oracle — nhờ dùng thêm giá cơ bản quan sát trễ, thứ oracle không
có. Bằng chứng bổ trợ: các chuyến cùng 5,5–6,0 km và 15–20 phút (n = 83.427) vẫn có giá cơ bản trải
rộng với hệ số biến thiên 18,7%.

Cần nói rõ giới hạn của phép đo này. Trung bình ô được tính in-sample nên đây là ước lượng **lạc
quan** cho oracle. Ngoài ra nó chỉ nói về **bộ feature hiện tại** trên **bộ dữ liệu này** — không
loại trừ khả năng feature mới hoặc dữ liệu thật cho kết quả khác. Cách đọc đúng là: trong phạm vi
những gì đang quan sát được, dư địa cải thiện tầng giá cơ bản là nhỏ, nên nếu muốn tiến thêm thì
phải thêm thông tin mới chứ không phải tinh chỉnh model.

Kết luận này nhất quán với bốn quan sát độc lập đã nêu: bốn thuật toán chênh nhau 1,9% (§5.1),
Transformer hoà (§5.2), Optuna 40 trial cho +2 VND (§4.3), và 49 cột feature thêm cho +6 VND (§4.3).

## 6.5 So sánh model trên nhóm cố định

Ở nhóm chuyến dài và giá cao — hai nhóm §6.1 chỉ ra là khó nhất — chúng tôi kiểm tra xem GAM có lợi
thế so với gradient boosting hay không.

**Điểm phương pháp quan trọng:** khi so sánh nhiều model, nhóm chuyến phải được cố định trước và
giống nhau cho mọi model. Nếu để mỗi model tự chia nhóm theo giá chính nó dự đoán thì các model
đang được chấm trên những tập chuyến khác nhau, và chênh lệch quan sát được lẫn cả hiệu ứng chọn
mẫu.

Mức độ ảnh hưởng không nhỏ. Số chuyến rơi vào nhóm `>300k` theo ba cách chia:

| Cách chia nhóm | Số chuyến `>300k` |
|---|---:|
| Theo giá thật | 869 |
| Theo giá Hybrid dự đoán | 327 |
| Theo giá GAM dự đoán | 330 |

Bảng dưới đây trình bày chênh lệch MAPE giữa GAM và Hybrid theo cả ba cách chia. Số dương nghĩa là
GAM tốt hơn; khoảng tin cậy 95% tính bằng bootstrap 2.000 lần lấy mẫu lại.

| Chia theo | Nhóm | n | Hybrid | GAM | Chênh (điểm) | CI 95% |
|---|---|---:|---:|---:|---:|---|
| Giá **thật** | `>300k` | 869 | 23,67% | 22,03% | **+1,65** | [+1,17, +2,12] |
| Giá **Hybrid dự đoán** | `>300k` | 327 | 18,55% | 14,52% | **+4,02** | [+2,74, +5,32] |
| **Quãng đường** | `>15 km` | 660 | 17,52% | 15,37% | **+2,16** | [+1,36, +2,91] |
| **Quãng đường** | `12–15 km` | 2.045 | 15,26% | 14,91% | +0,35 | [+0,15, +0,56] |
| — | *Toàn tập* | 216.090 | 14,65% | 14,89% | −0,24 | [−0,25, −0,22] |

Ba kết luận:

**Lợi thế của GAM ở nhóm giá cao là có thật nhưng nhỏ hơn báo cáo ban đầu.** Con số +4,02 điểm tính
trên nhóm chia theo giá model tự dự đoán bị phóng đại. Trên nhóm cố định theo giá thật, lợi thế còn
+1,65 điểm. Cả hai đều có khoảng tin cậy không chứa 0, nhưng chỉ con số sau là so sánh công bằng.

**Lợi thế ở chuyến dài vững hơn**, vì quãng đường quan sát được và không phụ thuộc model nào. GAM
tốt hơn +2,16 điểm ở nhóm `>15 km` và +0,35 điểm ở nhóm `12–15 km`, cả hai đều có ý nghĩa thống kê.
Đây là kết quả đáng tin cậy nhất trong bảng.

**Trên toàn tập GAM kém hơn 0,24 điểm.** Nên GAM không phải model thay thế mà là ứng viên cho một
cách kết hợp có trọng số theo quãng đường — hướng này chưa được triển khai, xem §10.

---

# 7. Cấu phần (iii) — Lượng hoá độ bất định

## 7.1 Ba phương pháp

Giữ riêng tập calibration mà model chưa từng thấy, đo sai số trên đó, rồi lấy phân vị 90%:

| Phương pháp | Coverage | Độ rộng TB | Bảo đảm lý thuyết |
|---|---:|---:|---|
| **Conformal chuẩn hoá** | 89,81% | **72.637đ** | Hữu hạn mẫu, phân phối tự do |
| Quantile Regression | 89,18% | 75.977đ | Không |
| CQR | 89,56% | 76.546đ | Hữu hạn mẫu |

Conformal chuẩn hoá được chọn làm mặc định: hẹp nhất và có bảo đảm lý thuyết.

$$q = \text{Quantile}_{0{,}90}\big(\{res_i\}_{i \in \text{calib}}\big), \qquad
[\ell, u] = \hat p \cdot (1 \pm q)$$

Kết quả $q = 30{,}07\%$, tức khoảng bằng giá dự đoán nhân $(1 \pm 30\%)$, coverage thực tế 89,81%.

Một chi tiết dễ sai: phần dư dùng để hiệu chỉnh phải chia cho **giá dự đoán** chứ không phải giá
thật, vì tại thời điểm dự báo chưa biết giá thật.

## 7.2 Coverage điều kiện

Coverage trung bình 89,81% đạt mức danh mục. Nhưng trung bình che mất chênh lệch giữa các nhóm. Chia
theo band giá dự đoán — nhóm biết được tại thời điểm ra quyết định:

| Band giá dự đoán | n | Coverage | Độ rộng TB |
|---|---:|---:|---:|
| `<50k` | 2.716 | 92,42% | 26.271đ |
| `50–100k` | 66.035 | 90,52% | 49.369đ |
| `100–150k` | 102.331 | 89,39% | 73.409đ |
| `150–200k` | 37.353 | 89,61% | 101.710đ |
| `200–300k` | 7.328 | 89,52% | 134.769đ |
| **`>300k`** | 327 | **83,79%** | 201.658đ |

🖼️ `PR1_khoang_theo_muc_gia.png` · `PR2_uq_theo_boi_canh.png`

Nhóm giá cao nhất bị phục vụ tệ nhất — hụt 6,2 điểm so với lời hứa. Đây cũng là nhóm mà một khoảng
tin cậy sai gây thiệt hại lớn nhất về giá trị tuyệt đối.

Cần lưu ý về cách chia nhóm ở bảng này. Khác với §6.5, ở đây chúng tôi cố ý chia theo giá **dự
đoán** chứ không phải giá thật. Lý do: coverage là lời hứa đưa ra *tại thời điểm dự báo*, nên nhóm
phải định nghĩa bằng thông tin có sẵn lúc đó. Chia theo giá thật sẽ điều kiện hoá lên chính kết quả
cần đo — những chuyến có giá thật rất cao đúng là những chuyến model đoán thấp, nên coverage đo được
sẽ tụt xuống 47,99% một cách giả tạo. Đây là hai câu hỏi khác nhau và cần hai cách chia nhóm khác
nhau: so sánh model dùng nhóm độc lập với model, đánh giá coverage dùng nhóm quan sát được lúc dự
báo.

## 7.3 Hiệu chỉnh Mondrian

Conformal toàn cục cho một hệ số $q$ chung. Mondrian cho mỗi nhóm một hệ số riêng.

| Cách hiệu chỉnh | Nửa độ rộng | Coverage | So với gốc |
|---|---:|---:|---:|
| Conformal toàn cục | ±30,07% | 89,81% | — |
| Mondrian theo band giá | ±30,11% | 89,84% | +0,11% |
| **Mondrian theo quãng đường** | **±29,96%** | 89,77% | **−0,37%** |
| Mondrian theo giờ | ±30,07% | 89,78% | −0,02% |
| Mondrian theo thời tiết | ±30,07% | 89,80% | −0,01% |

Mondrian **không làm khoảng hẹp hơn** — thay đổi độ rộng đều dưới 0,4%. Giá trị của nó nằm ở chỗ
khác: làm coverage **đều** giữa các nhóm.

| Lệch coverage lớn nhất giữa các nhóm | Toàn cục | Mondrian |
|---|---:|---:|
| Theo band giá | 8,62 điểm | **1,46 điểm** |
| Theo quãng đường | 12,61 điểm | **2,53 điểm** |

🖼️ `QD1_mondrian_lam_deu.png`

Hai nhóm bị phục vụ tệ nhất được cải thiện rõ:

| Nhóm | Coverage toàn cục | Coverage Mondrian |
|---|---:|---:|
| Band `>300k` | 83,79% | **91,13%** |
| Quãng đường `>15 km` | 82,58% | **87,58%** |

Chi phí: vài giờ triển khai, không train lại model, tốn thêm 0,04% độ rộng. Đây là cải thiện có tỷ
lệ lợi ích trên chi phí cao nhất trong toàn dự án.

## 7.4 Ba kịch bản phân bổ độ rộng

Một câu hỏi thường gặp: hai model có cùng MAE nhưng phân bổ độ rộng khoảng khác nhau thì khác nhau
thế nào? Chúng tôi dựng ba kịch bản và chạy thật trên tập test:

| Kịch bản | ± cao điểm | Coverage cao điểm | ± giờ thường | Coverage giờ thường |
|---|---:|---:|---:|---:|
| A · đều ±30% | 30,0% | 89,9% | 30,0% | 89,7% |
| B · ±10% cao điểm / ±40% thường | 10,0% | **42,3%** | 40,0% | 96,3% |
| C · ±40% cao điểm / ±10% thường | 40,0% | 96,5% | 10,0% | **42,3%** |
| **Model thực tế** | 30,2% | **90,1%** | 30,1% | **89,7%** |

🖼️ `TT5_ba_kich_ban_theo_thoi_gian.png` · `TT6_coverage_ba_kich_ban.png`

Model rơi đúng vào kịch bản A, tỷ lệ độ rộng cao điểm trên giờ thường là 1,004. Kịch bản B và C
không tồn tại được trên bộ dữ liệu này: khung nào được cấp ±10% cũng chỉ giữ được 42,3% coverage.
Muốn hẹp ở cao điểm mà vẫn giữ 90% thì sai số ở cao điểm phải nhỏ hơn **thật sự** — mà §6.1 cho thấy
sai số cao điểm và giờ thường gần như bằng nhau.

Một lưu ý về cách trình bày: trong hình chuỗi thời gian, điểm đánh dấu phải bám coverage **cấp
chuyến**, không phải phép thử "đường trung bình có rơi ngoài dải trung bình hay không". Ở kịch bản
B, đường giá trung bình vẫn nằm gọn trong dải suốt giờ cao điểm dù coverage thật chỉ 42% — đúng kiểu
trung bình hoá che mất vấn đề.

## 7.5 Sai lệch bất đối xứng

Khoảng hiện tại đối xứng quanh giá dự đoán, nhưng sai lệch thực tế thì không:

| | Tỷ lệ |
|---|---:|
| Giá thật vượt cận trên | **7,64%** |
| Giá thật thấp hơn cận dưới | 2,55% |
| Tỷ lệ giữa hai phía | **3,00×** |

Model bỏ sót phía giá cao thường xuyên gấp ba lần phía giá thấp. Nguyên nhân là phân phối giá lệch
phải: đuôi trên dài hơn đuôi dưới.

Chúng tôi đã thử phương án khoảng bất đối xứng — giữ tổng mức rủi ro 10% nhưng chia lại cho hai
phía, dùng phân vị một phía trên tập calibration:

| Chia rủi ro (dưới/trên) | q dưới | q trên | Coverage | Độ rộng | Vượt trên | Dưới |
|---|---:|---:|---:|---:|---:|---:|
| 5,0% / 5,0% *(đối xứng theo phân vị)* | 26,18% | 34,76% | 89,92% | 73.598đ | — | — |
| 4,0% / 6,0% | 27,63% | 32,61% | 89,88% | 72.753đ | — | — |
| **3,0% / 7,0%** | 29,37% | 30,70% | 89,81% | **72.541đ** | 7,30% | 2,90% |
| 2,5% / 7,5% | 30,38% | 29,80% | 89,77% | 72.676đ | 7,81% | 2,42% |
| 2,0% / 8,0% | 31,57% | 28,93% | 89,73% | 73.071đ | 8,34% | 1,93% |
| *Đối xứng hiện tại ±30,07%* | 30,07% | 30,07% | 89,81% | 72.637đ | 7,64% | 2,55% |

Kết quả là **âm tính**. Phương án tốt nhất (3%/7%) cho coverage y hệt 89,81% với độ rộng hẹp hơn
0,13% — thay đổi không đáng kể. Tỷ lệ bỏ sót hai phía cũng chỉ chuyển từ 7,64/2,55 sang 7,30/2,90.
Và khi xét theo band giá, lệch coverage lớn nhất giữa các nhóm còn **tăng nhẹ** từ 6,21 lên 6,51
điểm.

Lý giải: khoảng hiện tại là **nhân tính** ($\hat p \cdot (1 \pm q)$) chứ không phải cộng tính, nên
nó đã hấp thụ sẵn phần lớn độ lệch phải của phân phối giá. Phần bất đối xứng còn lại quá nhỏ để một
phép dịch phân vị đơn giản khai thác được. Muốn xử lý triệt để thì phải cho độ bất đối xứng **thay
đổi theo từng chuyến**, chứ không phải một cặp hằng số dùng chung.

## 7.6 Vì sao khoảng không hẹp lại được

Nếu biết trước độ khó của từng chuyến thì chỉ cần ±14,68% thay vì ±30,07% — dư địa lý thuyết −51%.

Nhưng độ khó từng chuyến không dự đoán được từ các thuộc tính quan sát được. Chúng tôi đã thử huấn
luyện một model riêng để dự báo sai số của model chính, rồi dùng nó điều chỉnh độ rộng theo chuyến.
Kết quả: cải thiện tốt nhất **−0,37%** độ rộng, tương đương phương án Mondrian theo quãng đường mà
đơn giản hơn nhiều.

Đây là lý do khoảng ±30% không phải dấu hiệu của hiệu chỉnh kém, mà phản ánh mức bất định thực sự
còn lại trong dữ liệu sau khi model đã làm hết phần của nó.

---

# 8. Model có học đúng cơ chế giá không

## 8.1 Vấn đề

§3.3 đo phản ứng giá trên **dữ liệu thật**. Một câu hỏi kiểm định tự nhiên: model có tái hiện được
những phản ứng đó không?

Khi so partial dependence của model với hiệu ứng đo bằng ghép cặp, xuất hiện khoảng cách khoảng 9
điểm phần trăm ở yếu tố mưa. Cách đọc ban đầu — và cũng là cách đọc sai — là "model chỉ bám giá quan
sát trễ chứ không hiểu cơ chế".

## 8.2 Hiệu ứng trực tiếp và hiệu ứng tổng

Cách đọc đúng: hai con số đo hai đại lượng khác nhau.

Partial dependence đo **hiệu ứng trực tiếp** — đổi biến `weather` mà giữ nguyên mọi biến khác, gồm
cả các biến trung gian như chỉ số cầu và thời lượng chuyến. Ghép cặp đo **hiệu ứng tổng** — bao gồm
cả đường đi gián tiếp.

Mà §3.3 đã chỉ ra mưa tác động chủ yếu **qua** cầu và **qua** thời lượng. Nếu giữ nguyên hai biến
trung gian đó thì hiệu ứng trực tiếp của mưa gần như bằng 0 — đúng như model thể hiện.

## 8.3 Kiểm chứng bằng cách cắt từng kênh

Để xác nhận, chúng tôi huấn luyện lại model sau khi bỏ đi từng nhóm feature:

| Bỏ đi | MAPE tăng thêm | Đọc |
|---|---:|---|
| Chỉ bỏ giá quan sát trễ | +1,12% | Model tự bù bằng các kênh khác |
| Chỉ bỏ nhóm trung gian (cầu, thời lượng) | +1,49% | Model tự bù bằng giá quan sát trễ |
| Bỏ **cả hai** | **+6,33%** | Không còn gì để bù |

🖼️ `PU1_rut_cai_nang.png` · `PU2_di_qua_tang_nao.png`

Bỏ riêng từng kênh gây thiệt hại nhỏ, bỏ cả hai gây thiệt hại lớn hơn tổng của hai phần riêng lẻ.
Đó là dấu hiệu của **thông tin dư thừa giữa hai kênh** — model biết cơ chế qua nhiều đường và tự
chuyển sang đường còn lại khi một đường bị cắt.

Cụ thể với mưa: khi rút giá quan sát trễ ra, model tự bù lại **94%** hiệu ứng mưa bằng các feature
còn lại. Kết luận "model chỉ bám giá quan sát" là sai, và chúng tôi đã ghi nhận đính chính này.

---

# 9. Hệ thống demo

Toàn bộ kết quả được đóng gói thành một demo chạy trong trình duyệt, không cần cài đặt hay server.
Demo chạy tập test qua model và mô phỏng từng chuyến trên bản đồ, hiển thị giá dự đoán, khoảng tin
cậy, hệ số nhân dự đoán, rồi lộ ra giá thật và hệ số nhân thật khi chuyến kết thúc.

Ba bảng biểu đồ tương ứng ba cấu phần: độ chính xác dự báo và đối chiếu baseline; sai lệch phân rã
theo mức giá, khung giờ, quãng đường và thời tiết; coverage và độ rộng khoảng theo từng nhóm.

Demo cho phép chọn khung giờ để mô phỏng riêng một khoảng thời gian trong ngày, và chuyển qua lại
giữa hiệu chỉnh toàn cục và Mondrian. Thao tác thứ hai tái hiện trực tiếp kết quả §7.3: ở nhóm
`>300k`, coverage nhảy từ khoảng 84% lên khoảng 91% ngay trên màn hình, kèm chi phí phải trả là
khoảng rộng hơn.

---

# 10. Giới hạn

Năm giới hạn cần nêu rõ khi sử dụng kết quả của bài báo này.

**Dữ liệu mô phỏng.** Đây là giới hạn lớn nhất. Toàn bộ kết quả mô tả hành vi bộ sinh dữ liệu. Chưa
có kiểm chứng nào trên dữ liệu thật, và §3.4 cho thấy bộ sinh dữ liệu bỏ sót ít nhất một hiện tượng
quan trọng của thị trường thật (ngày lễ).

**Phạm vi hẹp.** Ba khu vực quanh một quận, hai dịch vụ, một nền tảng đối thủ, 90 ngày. Không đủ để
kết luận về tính khái quát theo không gian hoặc theo mùa.

**Đánh giá hồi cứu.** Mọi con số đo trên một tập test cố định tách theo thời gian. Chưa có đánh giá
tiến cứu trên dữ liệu mới đến theo thời gian thực, và chưa có kiểm tra độ ổn định qua nhiều lần chia
dữ liệu khác nhau.

**Tầng chấp nhận giá chỉ là giả định.** Dữ liệu không có nhãn accept/reject nên tầng mô hình hoá
hành vi khách hàng dựa trên mô hình cấu trúc có tham số giả định, không train và không kiểm chứng
được. Mọi kết quả liên quan đến tầng này nằm ngoài phạm vi bài báo.

**Trần thông tin ở §6.4 là ước lượng lạc quan và chỉ áp dụng cho bộ feature hiện tại.** Trung bình ô
tính in-sample. Kết luận đúng là dư địa nhỏ *trong phạm vi những gì đang quan sát được*, không phải
là một giới hạn tuyệt đối.

---

# 11. Hướng tiếp theo

Bốn hướng, xếp theo tỷ lệ lợi ích trên chi phí.

**Bật Mondrian theo quãng đường.** Chi phí vài giờ, không train lại. Đưa lệch coverage giữa các nhóm
từ 12,61 xuống 2,53 điểm với chi phí 0,04% độ rộng. Đây là việc nên làm trước tiên.

**Đặt trọng số cao hơn cho chuyến hiếm.** Giữ model hiện tại làm mốc, tăng trọng số cho chuyến
`>300k` hoặc `>15 km` khi huấn luyện, rồi đo hai con số: sai số ở hai nhóm này giảm bao nhiêu, và
kết quả toàn tập phải đánh đổi bao nhiêu. Cần dùng nhóm cố định theo §6.5 để kết quả so sánh được.

**Kiểm định lại lợi thế của GAM qua nhiều lần chia dữ liệu theo thời gian.** §6.5 cho thấy lợi thế ở
chuyến dài là có thật trên một lần chia. Nếu nó ổn định qua nhiều lần chia, một cách kết hợp đơn
giản là cho trọng số của GAM tăng dần theo quãng đường, ưu tiên gradient boosting cho chuyến bình
thường. Không cần kiến trúc mới.

**Khoảng bất đối xứng phụ thuộc chuyến.** §7.5 cho thấy một cặp hằng số bất đối xứng không giúp gì.
Nếu theo đuổi hướng này thì phải để độ bất đối xứng thay đổi theo từng chuyến, chẳng hạn ước lượng
riêng hai phân vị điều kiện — chi phí cao hơn hẳn và cần cân nhắc với lợi ích còn chưa rõ.

Ngoài ra, hai câu hỏi cần trả lời trước khi mở rộng phạm vi: dữ liệu thật có mức nhiễu báo giá tương
đương bộ mô phỏng không, và có hiệu ứng ngày lễ không. Cả hai đều quyết định hướng đi và không thể
trả lời từ bên trong bộ dữ liệu hiện tại.

---

# Phụ lục A — Quy ước tái lập

| | |
|---|---|
| Python | 3.11.8 |
| Thư viện chính | pandas, numpy, scikit-learn, lightgbm, xgboost, pygam, scipy, matplotlib |
| Thời gian chạy lại toàn bộ | ~45 phút |
| Số notebook | 59, đã chạy lại toàn bộ để kiểm tính tái lập |

**Hai quy ước dễ nhầm khi đối chiếu số:**

Tập test tồn tại hai phiên bản — đầy đủ 864.360 dòng (4 độ trễ) và lag 5 phút 216.090 dòng. Chênh
lệch MAPE giữa hai tập là 0,09 điểm. Khi trích dẫn phải nói rõ tập nào.

Sai số tương đối có hai mẫu số — chia cho giá thật khi báo cáo MAPE, chia cho giá dự đoán khi dựng
khoảng conformal. Dùng nhầm mẫu số sẽ làm coverage lệch.

**Đơn vị.** Trường `quote_duration` tính bằng **giây**, không phải phút. Đây là lỗi đã từng mắc và
làm sai một phần kết quả ở §6.4 trước khi phát hiện.

# Phụ lục B — Nhật ký đính chính

Bốn phát biểu đã từng đưa ra và sau đó được sửa. Ghi lại để người đọc phân biệt được kết luận nào
đã qua kiểm chứng lại.

| # | Phát biểu ban đầu | Sửa thành | Nguồn |
|---|---|---|---|
| 1 | CQR có coverage điều kiện tốt nhất | Conformal chuẩn hoá hẹp hơn ở cùng coverage; CQR không vượt trội | §7.1 |
| 2 | Model bám giá quan sát chứ không hiểu cơ chế | Khoảng cách 9 điểm là chênh lệch giữa hiệu ứng trực tiếp và hiệu ứng tổng | §8 |
| 3 | Trần thông tin 14,84% | 14,98% — do `quote_duration` tính bằng giây, không phải phút | §6.4 |
| 4 | GAM tốt hơn Hybrid +4,02 điểm ở nhóm `>300k` | +1,65 điểm khi nhóm được cố định theo giá thật | §6.5 |
