# Việc tuần 4 — từ feedback mentor

> Cập nhật 07/08/2026, sau khi phân tích kỹ 5 ý của mentor.

---

## Thông điệp xuyên suốt cả 5 ý

> Đừng báo cáo model **chính xác bao nhiêu**. Chỉ ra model **sai ở đâu**, **vì sao**, và **giá phản
> ứng thế nào với từng yếu tố** — để người nghe tin, và để nhóm biết đầu tư công sức vào đâu.

Từ nặng nhất trong feedback: ***"thay vì chung chung model mình chính xác tới mức nào"***.
Anh ấy đang gọi cách báo cáo hiện tại là **mơ hồ**.

| | Đang làm | Cần chuyển sang |
|---|---|---|
| Kiểu báo cáo | **Mô tả** — MAE 18.045đ | **Chẩn đoán** — sai ở đâu, sửa thế nào |
| Vai trò của giá | Thứ cần **dự đoán** | **Phản ứng** với yếu tố thị trường |
| Mục đích | Báo cáo | **Ra quyết định** + **demo đáng tin** |

**Việc kỹ thuật đã đủ. Thứ thiếu là diễn giải và tính khả dụng.**

---

# ✅ ĐÃ XONG

| # | Việc | Kết quả |
|---|---|---|
| **A1** | Bảng UQ theo band giá | Coverage lệch **7,3 điểm**: >300k chỉ **82,72%** vs <50k **92,40%** |
| **A2** | Notebook tái lập | `uncertainty/01_conformal_chuan_hoa.ipynb` — 4 hình `BG1`–`BG4` |
| **A3** | Đường tin cậy từng band | Band >300k **hứa quá ở mọi mức** tin cậy, không riêng 90% |
| **B1** | Trả lời câu 3-model của mentor | Model thuộc **loại 1 — đều ~30%** mọi khung giờ (MAPE chênh 0,09 điểm) |
| **C1** | Mondrian theo band giá | Lệch tối đa **7,28 → 1,24 điểm** (−83%), chỉ tốn **+0,53%** độ rộng |
| **C2** | Trả lời "improve model hay giảm uncertainty" | **2/3 vấn đề** sửa được không cần train lại |

**Phát hiện quan trọng nhất:** `q` thật của band >300k là **41,01%** nhưng chỉ được cho **30,09%**
— đó là toàn bộ nguyên nhân lệch coverage.

---

# 🔴 A. Đưa phân rã vào báo cáo

**✅ A4 · A5 XONG**

| # | Việc | Kết quả |
|---|---|---|
| **A4** | Bảng band cho cả 3 phương pháp × 3 mức tin cậy | `uncertainty/04_SO_SANH.ipynb` · `BM1`–`BM3` · 54 dòng |
| **A5** | Rà báo cáo, tìm câu nêu số trung bình thiếu phân rã | Kiểm tự động trong `TUAN4_DA_LAM.ipynb` — **6 chỗ** cần bổ sung |
| A6 | Chốt mốc chia band | ❓ Hỏi mentor |

### 🔴 A4 sửa lại kết luận tuần 3

Tuần 3 chọn **Conformal** vì coverage tổng thể đẹp và khoảng hẹp nhất — đúng kiểu đánh giá mentor
phê bình ở ý 1. Nhìn theo band thì khác hẳn:

| Phương pháp | Lệch tối đa giữa band (TB 3 mức) | Độ rộng TB 90% |
|---|---:|---:|
| Conformal chuẩn hoá | **8,53 điểm** | 72.630đ |
| QR thô | 3,25 điểm | 75.783đ |
| **CQR** | **2,75 điểm** | 76.449đ |

Conformal áp **một tỷ lệ `q` chung** cho mọi chuyến nên band giá cao bị khoảng quá hẹp.
QR/CQR sinh phân vị riêng từng chuyến nên tự thích ứng. **Đây là vấn đề của phương pháp, không
phải của dữ liệu.**

Cách sửa rẻ nhất vẫn là **Mondrian** (lệch tối đa 1,24 điểm, chỉ +0,53% độ rộng) — rẻ hơn chuyển
sang CQR (+5,3% độ rộng, cần 21 model quantile).

---

# 🔴 B. Chuỗi thời gian có chú thích

> *"plot price over time với 1 đường predicted + vùng uncertainty và 1 đường ground truth và có
> annotate rush hour hay weather… một cách **trực quan**"*

Từ **"trực quan"** đáng chú ý — anh ấy muốn **nhìn thấy**, không muốn đọc bảng.

**✅ XONG — `model/uncertainty/05_PHAN_RA_theo_thoi_gian.ipynb`**

| # | Việc | Hình | Kết quả |
|---|---|---|---|
| **B2** | Chuỗi thời gian: ground truth + predicted + dải UQ, đánh dấu cao điểm/mưa | `TT1` | Ngày 27/03 (50% mưa), khống chế 4–6 km, gộp 30 phút, 3 panel |
| **B3** | Đo sai số tại từng thời điểm nhạy cảm | `TT2` | Sai số tương đối 24 giờ chỉ dao động **3,8%**; cao điểm 14,74% vs giờ thường 14,75% |
| **B4** | Tìm các đợt demand surge, đo riêng sai số | `TT3` | 53/528 bucket vượt ngưỡng hệ số 1,367 → sai số **giảm** 1,1% (14,60%), coverage 88,45% |
| **B5** | Hình so 3 kịch bản của mentor | `TT4` | Model = **kịch bản A**, độ rộng 60,2% cả hai khung, chênh 0,00% |

**MAE tuyệt đối có chênh 67%** (12.655đ giờ 3h → 21.186đ giờ 18h) nhưng đó là do **giá cao hơn**,
không phải model kém đi — sai số tương đối phẳng. Cần nói rõ chỗ này để tránh hiểu nhầm.

**Lưu ý khi trình bày B1:** model đều ~30% là tin **tốt** (không mù ở chỗ quan trọng) nhưng cũng
**trung tính** — không có gì đặc biệt để khoe. Nên nói thẳng.

---

# 🔴 D. Ceteris paribus — ý quan trọng nhất

> *"Ở các version pricing của bọn anh… bọn anh đều **measure price như là kết quả của một thay đổi
> của yếu tố thị trường**"*

Đây không phải gợi ý phân tích — đây là **cách team mentor nghĩ về bài toán**, và anh ấy đang mời
mình nghĩ giống vậy.

### 🔵 D0. Đóng khung lại phần GAM — việc rẻ nhất, giá trị cao

**Công việc GAM tuần 3 chính là dạng phân tích này** mà báo cáo chưa đóng khung như vậy:

| GAM đã cho | Trả lời ý 4 thế nào |
|---|---|
| Đường cong `f(feature)` kèm khoảng tin cậy | Chính là *"đổi 1 yếu tố thì giá đổi thế nào"* |
| p-value từng feature | Yếu tố nào **thật sự** cấu thành giá |
| Biên độ từng feature | Yếu tố nào **mạnh** nhất |
| Phát hiện: giá cơ bản cộng dồn thuần, hệ số nhân có tương tác | Cấu trúc quan hệ |

⚠️ **Mentor không nhắc GAM lần nào** — có thể chưa đọc kỹ. Tuần 4 nên trình bày lại phần này
**như câu trả lời cho ý 4**, thay vì để riêng như thí nghiệm thuật toán. **Ước tính 1 h.**

### Kiểm tra dữ liệu — yếu tố nào có

| Yếu tố mentor nhắc | Có? | Ghi chú |
|---|---|---|
| Distance | ✅ | `quote_distance`, `quote_duration` |
| Weather | ✅ | **20 cột** |
| Rush hour | ✅ | `gio_vn`, `target_is_weekend` |
| **Public holiday** | ❌ | **KHÔNG CÓ** — cần hỏi mentor hoặc tự map lịch VN |
| Demand–supply | ✅ | 4 cột |
| Vị trí | ✅ | hex, lat/lon, tên địa điểm |
| Loại xe | ✅ | 2 loại |
| **Khách hàng** | ❌ | **KHÔNG CÓ** — *personalized multiplier* bất khả thi |

### Việc chính

**✅ D1–D5 XONG — `analysis/14_ceteris_paribus.ipynb`**

| # | Việc | Hình | Kết quả |
|---|---|---|---|
| **D1** | Chốt yếu tố + cách khống chế | — | 7/9 yếu tố mentor nhắc có sẵn; thiếu `public_holiday` và thông tin khách hàng |
| **D2** | Partial dependence có kiểm soát | `CP1`–`CP4` | Đo cả 2 định nghĩa khống chế (quần thể / hồ sơ tham chiếu) |
| **D3** | Đối chứng ghép cặp | `CP6` | 1.696 ô · 493.128 chuyến · tối thiểu 30 chuyến/nhóm |
| **D4** | Model vs thực tế | `CP7` `CP7b` `CP7c` | **Model lệch 10 điểm** — xem dưới |
| **D5** | Tách giá cơ bản vs hệ số nhân | `CP5` | Hai tầng học hai nhóm yếu tố **rời nhau hoàn toàn** |
| **D6** | Encode quan hệ vào model | — | ❓ Chờ mentor chọn hướng |
| **D7** | Đo hiệu quả sau khi encode | — | Chặn bởi D6 |

**🔴 Phát hiện quan trọng nhất tuần 4:** model **dự đoán giỏi nhưng không hiểu cơ chế**.
Hỏi *"trời mưa thì giá đổi bao nhiêu"* → model nói **+0,93%**, dữ liệu thật nói **+11,05%**.
Cao điểm: model **+2,42%** vs thật **+12,82%**. Lệch cùng hướng cùng cỡ ⇒ triệu chứng cấu trúc,
không phải nhiễu.

Nguyên nhân đã truy được: model bám `latest_observed_*` và `history_60m_*` — giá đối thủ vừa quan
sát **đã chứa sẵn** tác động của mưa và giờ. Bỏ nhóm feature đó đi thì hiệu ứng cao điểm bật lên
**+13,4%**, khớp thực tế. Riêng mưa thì đi qua **cung–cầu** (mưa làm cầu +15,5%, cung −7,0%).

**Hệ quả:** số đem đi demo phải lấy từ **đối chứng ghép cặp**, không lấy từ partial dependence.

> **D3 là chỗ khác biệt so với tuần 1.** Tuần 1 đo **tương quan**; D3 đo **thay đổi có kiểm soát**
> — gần nhân quả hơn. Đây đúng thứ mentor muốn.

---

# 🟠 E. Làm kết quả đáng tin để demo

> *"Khi các em trình bày được những yếu tố này as part of **demo** thì kết quả của mình sẽ rất
> **đáng tin cậy**"*

Hàm ý ngược lại: **kết quả hiện tại chưa đủ đáng tin để demo**. Một con số MAE từ hộp đen không
thuyết phục ai; *"trời mưa làm giá tăng 7,3%"* thì người không chuyên cũng gật đầu.

**✅ XONG — cùng notebook `analysis/14_ceteris_paribus.ipynb`, phần 6**

| # | Việc | Kết quả |
|---|---|---|
| **E1** | Bảng phản ứng giá | Bảng `E1` — mỗi dòng ghi rõ **model nói gì · dữ liệu thật nói gì · lấy số nào** |
| **E2** | Hình tổng | `CP8` — quãng đường +106% · cao điểm +12,8% · cung–cầu +11,9% · mưa +11,1% · cuối tuần +6,0% |

Quy tắc chọn số: **yếu tố nào ghép cặp được thì lấy số thực nghiệm**, vì đã chứng minh model
lệch 10 điểm ở mưa và cao điểm.

---

# ⚪ F. Acceptance — hạ xuống side objective

> *"nên treat nó như một cái side objective… đừng đi sâu vào nó quá.
> Anh sẽ gửi data bổ sung"*

Không phải làm sai — **sai thứ tự ưu tiên**. Anh ấy công nhận rào cản dữ liệu là thật (nên mới gửi
data), nhưng phần forecast giá mới là trọng tâm.

| # | Việc | Trạng thái |
|---|---|---|
| F1 | **Dừng** phát triển thêm | ⏸️ |
| F2 | Giữ bản v1 + notebook trình bày | ✅ đã có |
| F3 | Khi có data: kiểm tra có `outcome` + `exposure denominator` không | 🔒 |

---

# Thứ tự đề xuất

| Ưu tiên | Việc | Giờ | Lý do |
|---|---|---:|---|
| ✅ | ~~**B2–B5**~~ — chuỗi thời gian, surge, 3 kịch bản | — | `uncertainty/08`, hình TT1–TT4 |
| ✅ | ~~**Vá lỗ hổng tái lập**~~ (TC1) | — | `train/07_sinh_du_lieu_UQ`, hết file mồ côi |
| ✅ | ~~**D1–D5**~~ — ceteris paribus | — | `analysis/14_ceteris_paribus`, hình CP1–CP8 |
| ✅ | ~~**E1, E2**~~ — chuẩn bị demo | — | Bảng `E1` + hình `CP8` |
| ✅ | ~~**D0**~~ — đóng khung lại GAM | — | Ghi trong `TUAN4_DA_LAM.ipynb` mục C |
| ✅ | ~~**A4, A5**~~ — bảng band 3pp × 3 mức + rà báo cáo | — | `uncertainty/09`, hình BM1–BM3 |
| ✅ | ~~Khép khoảng cách ở `CP7c`~~ | — | `CP9` — khép **83%**, đường chính là **thời lượng** |
| ✅ | ~~Thêm **ngày** vào khoá ghép cặp~~ | — | Hiệu ứng ổn định 9,82–11,05% ⇒ không phải nhiễu |
| 🟠 **1** | **D6, D7** — encode vào model | 4 | ❓ Chặn bởi câu hỏi mentor |
| 🟠 **2** | Cân nhắc bỏ feature giá quan sát khỏi model chính | 2 | ❓ Chặn bởi câu hỏi mentor |
| ⚪ **3** | **F** — acceptance | — | 🔒 Chờ data |

**Mọi việc không bị chặn đã xong.** Còn lại đều chờ mentor trả lời.

📓 **Sổ rà soát chi tiết: [`TUAN4_DA_LAM.ipynb`](TUAN4_DA_LAM.ipynb)** — có cell kiểm tự động.

---

# Câu hỏi cần hỏi mentor

| # | Câu hỏi | Chặn việc |
|---|---|---|
| **1** ⭐ | Team ưu tiên **độ chính xác** hay **khả năng giải thích**? Model bỏ feature giá quan sát kém **8% MAE** (19.660 vs 18.208đ) nhưng **trả lời được câu hỏi what-if** của anh. | Hướng đi cả tuần |
| **2** | *"Encode causality vào model"* — anh muốn **ràng buộc đơn điệu**, **feature biến đổi**, hay **mô hình cấu trúc**? | D6 |
| **3** | Dữ liệu **không có `public_holiday`** — anh bổ sung được không, hay tự map lịch VN? | D1 |
| **4** | Band giá nên chia theo mốc nào cho khớp cách team đang dùng? | A6 |
| **5** | Data acceptance bổ sung khi nào có, gồm trường gì? | F3 |

> Câu **1** là câu đáng hỏi nhất tuần này. Chính ý 4 của anh ấy (*"trình bày được những yếu tố này
> as part of demo thì kết quả sẽ rất đáng tin cậy"*) hàm ý coi trọng giải thích được — nhưng đánh
> đổi 8% độ chính xác là quyết định của team.

---

# Những gì mentor **không** nhắc — coi như chấp nhận

| | |
|---|---|
| Kiến trúc Hybrid | ✅ |
| Chọn 3 phương pháp UQ | ✅ |
| Kết luận trần dữ liệu | ✅ |
| **GAM** | ❓ Có thể chưa đọc — xem D0 |
