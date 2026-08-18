# Tuần 5 — giảm sai số ở nhóm chuyến dài và giá cao

> Triển khai `../VIEC_TUAN_5.md`. Mỗi notebook một việc, chạy theo số thứ tự.

## Câu hỏi của tuần

> **Có thể giảm sai số ở nhóm chuyến dài và giá cao mà không làm kết quả chung tệ đi đáng kể
> hay không?**

## Thứ tự chạy

| # | Notebook | Việc | Cần train lại | Thời gian |
|---|---|---|---|---|
| 1 | `01_TRONG_SO_CHUYEN_HIEM.ipynb` | A · đặt trọng số cho chuyến hiếm | **Có** — nhánh giá cơ bản | ~20 ph *(nhanh)* · ~70 ph *(đầy đủ)* |
| 2 | `02_GAM_ON_DINH.ipynb` | B1 · lợi thế GAM có ổn định không | Không | ~2 ph |
| 3 | `03_GHEP_GAM_GBM.ipynb` | B2 · ghép hai model theo quãng đường | Không | ~3 ph |
| 4 | `04_MONDRIAN_QUANG_DUONG.ipynb` | C1 · hiệu chỉnh khoảng tin cậy | Không | ~1 ph |
| 5 | `05_GAM_CHI_TIET.ipynb` | GAM so với **từng** model + phân rã theo tầng | Không | ~3 ph |
| 6 | `00_TONG_HOP.ipynb` | D4 · bảng nộp mentor | Không | <1 ph |

`00` chạy **sau cùng** — nó chỉ đọc lại kết quả đã lưu trong `ket_qua/`.

`03` có **cổng quyết định**: chỉ chạy nếu `02` kết luận lợi thế của GAM ổn định ở nhóm `>15 km`.

## Quy tắc chung — nhóm cố định

Mentor tuần 4:

> *"Các em cần giữ nguyên nhóm chuyến giữa các model. Không nên để mỗi model tự chia nhóm theo giá
> mà chính nó dự đoán, vì như vậy các model có thể đang được đánh giá trên những nhóm chuyến khác
> nhau."*

Mọi notebook trong thư mục này dùng chung một bộ nhóm, định nghĩa trong ô `NHOM_CO_DINH`:

| Chia theo | Nhóm |
|---|---|
| Giá **thật** | `<50k` · `50–100k` · `100–150k` · `150–200k` · `200–300k` · `>300k` |
| Quãng đường | `<2` · `2–5` · `5–8` · `8–12` · `12–15` · `>15` km |

Cả hai đều **không phụ thuộc model nào**. Mức độ ảnh hưởng của việc này không nhỏ: nhóm `>300k` có
869 chuyến theo giá thật nhưng chỉ 327 theo giá Hybrid dự đoán, và lợi thế của GAM đo được chênh
nhau 4,02 so với 1,65 điểm.

**Ngoại lệ có chủ ý:** `04_MONDRIAN` chia nhóm theo giá **dự đoán**, vì coverage là lời hứa đưa ra
tại thời điểm dự báo nên nhóm phải định nghĩa bằng thông tin có sẵn lúc đó. Chia theo giá thật sẽ
điều kiện hoá lên chính kết quả cần đo.

## Kết quả đã chạy thử

`02`, `03`, `04`, `05` đã chạy trọn, không lỗi. `01` chưa chạy vì cần train lại.

| Notebook | Kết quả |
|---|---|
| `02` | Nhóm `>15 km`: **8/9 lát GAM thắng rõ, 0 lát Hybrid thắng rõ** → ổn định. Điểm giao ~13 km |
| `03` | Ghép **14,62%** vs Hybrid 14,63% trên hai tháng chưa đụng tới · `d₀=6, d₁=14, α_max=0,8` |
| `04` | Mondrian theo quãng đường: lệch coverage **12,6 → 2,42 điểm**, độ rộng chỉ +0,34% |
| `05` | Lợi thế của GAM nằm **hoàn toàn ở nhánh giá cơ bản** (+2,30 điểm ở `>15 km`); nhánh hệ số nhân GAM kém đều ~0,5 điểm ở mọi nhóm |

### Bốn model, hai kiến trúc — toàn tập, test độ trễ 5 phút

| Model | Hai tầng | Trực tiếp |
|---|---:|---:|
| HistGB *(mốc)* | **14,65%** | 15,36% |
| LightGBM | 14,66% | 15,34% |
| XGBoost | 14,66% | 15,34% |
| GAM | 14,89% | 15,57% |
| Persistence | — | 27,84% |

Kiến trúc quan trọng hơn thuật toán: chênh lệch giữa hai tầng và trực tiếp (~0,7 điểm) lớn hơn
chênh lệch giữa các thuật toán trong cùng kiến trúc (~0,01 điểm giữa ba loại cây).

### Phân rã GAM theo tầng

| Nhóm km | Nhánh cơ bản: GBM → GAM | Nhánh hệ số: GBM → GAM |
|---|---|---|
| `<2` | 8,91% → 13,16% *(−4,25)* | 1,60% → 2,11% *(−0,51)* |
| `8–12` | 14,84% → 14,87% *(−0,02)* | 1,33% → 1,78% *(−0,45)* |
| `12–15` | 15,18% → 14,77% *(**+0,41**)* | 1,42% → 1,92% *(−0,50)* |
| `>15` | 17,52% → 15,22% *(**+2,30**)* | 1,54% → 2,06% *(−0,52)* |

Nhánh hệ số nhân của GAM kém đều ở **mọi** nhóm, không có xu hướng theo quãng đường — nên toàn bộ
lợi thế ở chuyến dài đến từ nhánh giá cơ bản. Vì vậy `03` thử **hai mức trộn**: trộn giá cuối và
trộn riêng nhánh giá cơ bản (giữ hệ số nhân của GBM).

## Đầu ra

**`ket_qua/`** — CSV và JSON để `00_TONG_HOP` đọc lại:

| File | Từ notebook |
|---|---|
| `A_danh_doi_trong_so.csv` · `A_kiem_dinh_phuong_an_tot.csv` · `A_pred_tot.npy` · `A_cau_hinh.json` | 01 |
| `B1_on_dinh_theo_lat.csv` · `B1_tong_ket_on_dinh.csv` · `B1_loi_the_theo_km.csv` · `B1_ket_luan.json` | 02 |
| `B2_ghep_vs_hybrid.csv` · `B2_theo_quang_duong.csv` · `B2_luoi_tham_so.csv` · `B2_cau_hinh.json` | 03 |
| `C1_so_sanh_hieu_chinh.csv` · `C1_nhom_yeu.csv` · `C1_q_theo_km.csv` · `C1_ket_luan.json` | 04 |
| `D4_bang_nop_mentor.csv` · `D4_khoang_tin_cay.csv` | 00 |

**Hình** — ghi vào `../docs/hinh_anh/`, tiền tố riêng cho tuần 5:

| Tiền tố | Notebook | Chủ đề |
|---|---|---|
| `TS` | 01 | Trọng số — đường đánh đổi, kiểm định |
| `OD` | 02 | Ổn định của GAM qua các lát thời gian |
| `GG` | 03 | Ghép GAM–GBM |
| `MQ` | 04 | Mondrian theo quãng đường |
| `T5` | 00 | Bảng đánh đổi tổng hợp |

## Ba điều dễ vấp

**Nhóm `>15 km` chỉ có 660 chuyến** trong tập test. Một cải thiện 1–2 điểm rất dễ là nhiễu, nên mọi
chênh lệch trong các notebook này đều kèm khoảng tin cậy bootstrap. Đừng kết luận từ chênh lệch điểm
đơn.

**Đếm dấu không phải đếm bằng chứng.** Ở `02`, một lát có chênh lệch −0,12 điểm với CI
[−1,75, +1,49] không phải bằng chứng đảo chiều — chỉ là nhiễu từ 121 chuyến. Tiêu chí ổn định vì thế
đếm số lát có CI **loại trừ được 0**, không đếm dấu của ước lượng điểm.

**`01` mặc định chạy ở chế độ nhanh.** `NHANH = True` lấy mẫu 500.000 dòng train mỗi tháng. Số cuối
cùng đưa vào báo cáo phải chạy lại với `NHANH = False`; notebook có in cảnh báo ở cuối nếu quên.
