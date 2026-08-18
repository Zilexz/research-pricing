# Thành phẩm 4 tuần — đọc file này trước

Trang này là đầu vào chung cho hai thứ mentor yêu cầu chuẩn bị: **tài liệu kỹ thuật** và **demo**.
Nó không chứa kết quả mới — chỉ nói rõ đang có gì, nằm ở đâu, và mở thế nào.

**Bài toán.** Dự báo mức giá đối thủ sẽ hiển thị cho một yêu cầu chuyến đi, tại thời điểm chỉ quan
sát được giá đối thủ trễ 5–30 phút, kèm một khoảng tin cậy cho mỗi dự báo.

> ⚠️ Dữ liệu là synthetic (`is_synthetic = True` toàn bộ · 1 nền tảng · 2 dịch vụ · 3 khu vực).
> Mọi con số mô tả hành vi bộ sinh dữ liệu, không phải thị trường TP.HCM thật. Cần nói rõ chỗ này
> ngay đầu buổi.

---

## 1. Bốn tuần đã dựng được gì

| Tuần | Việc chính | Thành phẩm để lại |
|---|---|---|
| 1 | Làm quen bài toán trên bộ Boston, dựng pipeline và baseline | `boston_data/` — 16 notebook |
| 2 | Chuyển sang TP.HCM: phân tích yếu tố ảnh hưởng giá, chốt kiến trúc hai tầng, train model điểm | `analysis/` 22 notebook · `model/train/` · `docs/bao_cao_tuan/bao_cao_tuan2_HOAN_CHINH` |
| 3 | Lượng hoá độ bất định: conformal chuẩn hoá, Mondrian, quantile regression | `model/uncertainty/` 7 notebook · `docs/bao_cao_tuan/bao_cao_uncertainty` |
| 4 | Chẩn đoán model, cấu thành giá, causality, transformer, so sánh nhiều model | `tuan_4/` 8 notebook · `docs/bao_cao_tuan/bao_cao_tuan4` |

Xuyên suốt bốn tuần, sản phẩm hội tụ về **ba cấu phần**: (i) yếu tố nào cấu thành giá, (ii) model
dự báo giá, (iii) khoảng tin cậy cho dự báo đó.

### Kiến trúc chốt lại

```
TẦNG 0   Dữ liệu — 1,72tr báo giá, KHÔNG có nhãn accept/reject
   │
   ▼
TẦNG 1   Model giá        [HỌC]      giá = giá cơ bản × hệ số nhân
   │  → một con số
   ▼
TẦNG 1b  Uncertainty      [HỌC]      conformal chuẩn hoá + Mondrian theo band
   │  → một khoảng
   ▼
TẦNG 2   Acceptance       [GIẢ ĐỊNH] mô hình cấu trúc McFadden, chưa train được vì thiếu nhãn
```

Tầng 1 là cấu trúc mentor mô tả bằng cụm *market signal multiplier*: một mức giá nền theo cấu trúc
chuyến, nhân với một hệ số phản ánh tín hiệu thị trường.

---

## 2. Tài liệu kỹ thuật

**File:** `docs/tai_lieu_bao_cao/TECH_DOC.docx` (bản đọc) · `docs/tai_lieu_bao_cao/TECH_DOC.md` (bản nguồn)

Khoảng 1.400 dòng, 5 phần và 3 phụ lục:

| Phần | Nội dung |
|---|---|
| §0 | Quy ước, tóm tắt điều hành, từ điển thuật ngữ |
| I | Định nghĩa bài toán · dữ liệu · cấu thành giá — *cấu phần (i)* |
| II | Kiến trúc · feature · huấn luyện · đánh giá và chẩn đoán — *cấu phần (ii)* |
| III | Ba phương pháp uncertainty · Mondrian · coverage điều kiện · vì sao không thu hẹp được khoảng — *cấu phần (iii)* |
| IV | Acceptance model · GAM và các kiến trúc đã thử (gồm transformer) · đối chiếu Boston |
| V | Tái lập · kiểm thử · quy ước repo · rủi ro và việc còn nợ |
| Phụ lục | A bản đồ notebook · B chỉ mục hình · C nhật ký đính chính |

Hai chỗ đáng chỉ cho mentor nếu chỉ có ít phút:

- **§0.2 Tóm tắt điều hành** — toàn bộ kết quả trong một trang.
- **§18 Rủi ro, giới hạn và việc còn nợ** — chỗ tự nhận những gì chưa làm được.

Nguyên tắc viết xuyên suốt: chỗ nào là số **đo được** và chỗ nào là **giả định** hoặc trích từ
literature chưa xác minh đều được đánh dấu rõ. Phụ lục C ghi lại mọi con số đã từng sai và đã sửa.

---

## 3. Demo

**Mở:** nháy đúp `demo/index.html`. Không cần cài gì, không cần server — dữ liệu đã nhúng sẵn
trong file. Cần mạng để tải nền bản đồ; không có mạng thì vẫn chạy, chỉ mất nền.

Demo chạy tập test qua model và mô phỏng từng chuyến trên bản đồ khu Phú Mỹ Hưng: bản đồ với xe
chạy, thẻ theo dõi một chuyến (cận dưới — dự đoán — cận trên, rồi giá thật khi tới nơi), một nhật
ký, và khu biểu đồ ba tab bám đúng ba cấu phần của sản phẩm:

| Tab | Trả lời | Gồm |
|---|---|---|
| Dự đoán giá | Dự đoán có sát không, hơn baseline bao nhiêu | Tán xạ dự đoán vs thật · phân bố sai số · model vs persistence |
| Sai lệch theo bối cảnh | Model sai ở đâu | Sai số theo mức giá · khung giờ · quãng đường · thời tiết |
| Khoảng tin cậy | Lời hứa có giữ được ở mọi nhóm không | Coverage hội tụ · coverage theo mức giá · độ rộng khoảng · coverage theo cao điểm × mưa |

Mọi biểu đồ cập nhật trực tiếp theo từng chuyến chạy xong. Tập test chưa từng dùng để huấn luyện
hay hiệu chỉnh.

### Kịch bản 5 bước — chạy đúng thứ tự này

| # | Thao tác | Sẽ thấy | Ý muốn nói |
|---|---|---|---|
| 1 | Để mặc định (đại diện · 90% · theo band), bấm ▶, chờ ~40 chuyến | Coverage hội tụ quanh 90%; tab 1 cho thấy model tốt hơn persistence khoảng 50% | Model không chỉ đoán một con số, nó nói luôn mình chắc tới đâu — và lời hứa đó giữ được |
| 2 | Hạ độ tin cậy xuống 70% | Khoảng hẹp rõ rệt, nhưng cứ 10 chuyến thì 3 chuyến ra ngoài | Đây là nút đánh đổi, không phải nút cải thiện |
| 3 | Chuyển sang `chỉ chuyến >300k`, để `q chung` | Coverage rơi xuống ~84% dù danh mục là 90% | Con số trung bình che mất chuyện nhóm khách đắt tiền nhất bị phục vụ tệ nhất |
| 4 | Vẫn nhóm đó, bấm sang `theo band giá`, mở tab `Khoảng tin cậy` | Coverage bật lên ~91%; cột `>300k` ở biểu đồ độ rộng nhảy từ ±30,1% lên ±41,0% | Sửa được mà không cần train lại — nhưng phải trả bằng khoảng rộng hơn, không có gì miễn phí |
| 5 | Về nhóm `đại diện`, chạy ~200 chuyến, mở tab `Sai lệch theo bối cảnh` | Sai số tách nhóm rõ theo quãng đường và mức giá, gần như không tách theo khung giờ | Model không yếu vào giờ cao điểm như trực giác — nó yếu ở chuyến dài và chuyến đắt |

Bước 3 → 4 là phần đáng cho xem nhất: nó là câu trả lời trực quan cho gợi ý của mentor về việc
đừng nhìn coverage trung bình. Bước 5 dựng lại kết quả chính của tuần 4 ngay trước mặt người xem.

### Nói trước bốn hạn chế này

| | |
|---|---|
| Điểm đón/trả rải ngẫu nhiên trong vùng | Chỉ để nhìn cho sinh động — quãng đường và giá lấy từ dữ liệu gốc, không tính lại theo toạ độ rải |
| Đường đi là đường cong nội suy | Dữ liệu chỉ có điểm đầu/cuối, không có lộ trình thật |
| Chỉ 3 khu vực | Dữ liệu synthetic chỉ phát sinh quanh 3 điểm này |
| Thời gian chạy đã nén | Để xem được nhiều chuyến trong ít phút |

Chi tiết đầy đủ về màn hình, các nút và cách đọc từng biểu đồ nằm ở `demo/README.md`.

### Sinh lại dữ liệu demo

Demo đọc `demo/du_lieu/chuyen.json` và `cauhinh.json`, xuất từ tập test và tập calibration hiện
tại. **Phải sinh lại khi model được train lại**, nếu không demo sẽ hiển thị dự đoán cũ. Quy trình
ghi ở cuối `demo/README.md`.

---

## 4. Đường đi trong 15 phút

Nếu mentor chỉ có 15 phút và muốn xem hết:

1. Trang này — 2 phút, để biết bố cục.
2. Demo, chạy kịch bản 4 bước — 6 phút. Đây là phần cho thấy sản phẩm *hoạt động*.
3. `TECH_DOC` §0.2 — 3 phút, kết quả trong một trang.
4. `tuan_4/00_TONG_HOP.ipynb` — 4 phút. Notebook này tự tính lại mọi con số từ dữ liệu chứ không
   chép sang, nên là chỗ kiểm chứng nhanh nhất.

---

## 5. Chưa có gì

Nói thẳng để mentor không phải đi tìm:

| Việc | Trạng thái | Vì sao |
|---|---|---|
| Acceptance model | Chỉ là mô hình cấu trúc giả định, chưa train | Dữ liệu không có nhãn accept/reject |
| Tầng quyết định giá | Chưa làm | Phụ thuộc acceptance model |
| API / service | Chưa có | Demo là file HTML tĩnh, chưa phải hệ thống chạy được |
| Kiểm định trên dữ liệu thật | Chưa | Toàn bộ kết quả đang trên bộ synthetic |
| Đánh giá tiến cứu | Chưa | Mọi con số hiện là hồi cứu trên tập test cố định |
