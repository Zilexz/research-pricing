# Chạy demo — đọc file này trước

## Mở

**Nháy đúp `index.html`.** Hết. Không cài gì, không server, không mạng.

Nếu Windows mở bằng trình duyệt lạ: chuột phải → *Open with* → **Chrome** hoặc **Edge**.

## Không có mạng thì sao

Vẫn chạy đủ. Chỉ mất **ảnh nền đường phố** của bản đồ — ba khu vực, tuyến đi, xe chạy, mọi
biểu đồ và bảng đều bình thường. Toàn bộ dữ liệu và thư viện đã nằm trong gói này.

## Gói này có gì

| | |
|---|---|
| `index.html` | Toàn bộ demo — 14,8 MB, dữ liệu 216.090 chuyến nhúng sẵn bên trong |
| `vendor/` | Thư viện bản đồ Leaflet 1.9.4, để chạy được khi mạng chặn CDN |
| `du_lieu/` | JSON nguồn, chỉ cần khi muốn sinh lại `index.html` |
| `sinh_du_lieu.py` | Script sinh lại dữ liệu demo khi model được train lại |
| `anh_chay_thu/` | 6 ảnh chụp một lượt chạy thật, để đối chiếu khi nghi hiển thị sai |
| `README.md` | Tài liệu đầy đủ: từng tab, từng biểu đồ, cách đọc |

## Chạy thử 30 giây

1. Bấm **▶ Chạy liên tục** — xe bắt đầu chạy trên bản đồ
2. Đợi tới khi chip **Coverage** ở thanh trên cùng ổn định quanh **90%**
3. Bấm qua lại các tab dưới bản đồ để xem từng góc nhìn

Mặc định dừng sau 200 chuyến rồi in tổng kết. Bấm ▶ lần nữa để chạy tiếp.

## Kịch bản nên trình bày

| # | Làm gì | Câu cần nói |
|---|---|---|
| 1 | Chạy mặc định tới ~40 chuyến | Model không chỉ đoán một con số, nó nói luôn mình chắc tới đâu — và giữ được lời hứa đó |
| 2 | Hạ **Độ tin cậy** xuống **70%** | Khoảng hẹp lại nhưng cứ 10 chuyến thì 3 chuyến ra ngoài. Đây là nút **đánh đổi**, không phải nút cải thiện |
| 3 | Đổi **Nhóm** sang `>300k`, để **`q chung`** | Coverage rơi xuống **~84%** dù hứa 90% — con số trung bình che mất chuyện nhóm khách đắt tiền nhất bị phục vụ tệ nhất |
| 4 | Vẫn nhóm đó, bấm sang **`theo band giá`** | Coverage bật lên **~91%**. Sửa được mà **không cần train lại model** |

Bước 3 → 4 là phần đáng cho xem nhất. Mở tab **Khoảng tin cậy** trong lúc bấm qua lại thì thấy
luôn cái giá phải trả: cột `>300k` ở biểu đồ độ rộng nhảy từ **±30,1%** lên **±41,0%**.

## Ba câu phải nói trước nếu bị hỏi

**Dữ liệu là synthetic.** Toàn bộ `is_synthetic = True` — 1 nền tảng đối thủ, 2 dịch vụ,
3 khu vực, 11 ngày. Mọi con số mô tả hành vi bộ sinh dữ liệu, **không phải thị trường TP.HCM thật**.

**Điểm đón/trả rải ngẫu nhiên** trong bán kính 620 m quanh mỗi khu, chỉ để nhìn cho sinh động.
Dữ liệu gốc chỉ có 3 toạ độ cố định, nên quãng đường và giá **không đổi** theo vị trí rải.

**Đường đi là đường cong nội suy**, không phải lộ trình thật — dữ liệu chỉ có điểm đầu và cuối.

## Nếu màn hình bị chật

Bấm nút **⤢ Trải dài** ở góc phải thanh trên cùng để chuyển sang chế độ cuộn, mọi thứ to hẳn lên.
Bấm lại để về chế độ vừa một màn hình.
