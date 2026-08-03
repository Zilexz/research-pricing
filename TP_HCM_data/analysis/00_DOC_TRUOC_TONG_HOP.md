# ĐỌC FILE NÀY TRƯỚC — Bản đồ toàn bộ phân tích key feature (bộ TP.HCM)

19 notebook trong thư mục này trả lời **1 câu hỏi duy nhất**, chỉ khác góc nhìn. File này tổng hợp
lại thành 1 bức tranh, kèm bản đồ notebook nào trả lời phần nào.

---

## 1. Khung sườn — mọi thứ đều xoay quanh công thức này

```
Giá cuối (khách trả) = Giá cơ bản × Hệ số nhân (surge)
```

Đây là lý do phải **luôn phân biệt 3 đối tượng** khi nói "yếu tố X ảnh hưởng giá":
- Ảnh hưởng đến **giá cuối** (cái khách thấy)
- Ảnh hưởng đến **giá cơ bản** (phần do quãng đường/thời gian quyết định, trước khi nhân surge)
- Ảnh hưởng đến **hệ số nhân** (phần điều chỉnh theo cung–cầu)

Nhầm giữa 3 cái này là nguồn gốc chính gây "mung lung" — vì 1 yếu tố có thể **không ảnh hưởng giá
cơ bản** nhưng **ảnh hưởng cực mạnh hệ số nhân**, và vì giá cuối = tích của 2 cái nên vẫn ảnh hưởng
giá cuối.

---

## 2. ⭐ Bảng tổng hợp cuối cùng — yếu tố nào ảnh hưởng cái gì

| Yếu tố | → Giá cơ bản | → Hệ số nhân | Ghi chú |
|---|---|---|---|
| **Quãng đường** | 🔴 Rất mạnh (~65-92% importance) | Yếu | Trục giá cơ sở |
| **Thời lượng đi / tắc đường** | 🔴 Mạnh (~19-32% biên độ) | Vừa (η~0,2) | Nhưng **tự nó không dự đoán được** từ giờ/thời tiết (chỉ ~3,5%) — xem mục 4 |
| **Cung–cầu (demand/supply/imbalance)** | ~0 | 🔴 **Rất mạnh** (corr~0,8) | Nguồn chính của surge |
| **Giờ trong ngày** | Rất yếu (~0,03-0,05) | 🔴 **Cực mạnh** (η~0,70) | Tác động **qua** cung–cầu, không trực tiếp lên giá cơ bản |
| **Vị trí/khu vực** | Yếu (sau kiểm soát quãng đường) | Vừa (η~0,3) | Chỉ 3 khu, kết luận còn hạn chế |
| **Thời tiết** | Yếu (~0,04-0,07) | Yếu-vừa (η~0,15) | Tác động qua tắc đường + cầu, yếu hơn giờ nhiều |
| **Thứ / cuối tuần** | Rất yếu | Yếu-vừa | |
| **Loại dịch vụ** | Rất yếu | Rất yếu | |
| **Giá/hệ số quan sát gần nhất** | Yếu với giá cơ bản | 🔴 **Rất mạnh** (corr~0,95) | Vì hệ số nhân dai dẳng theo thời gian |

🔴 = yếu tố quan trọng nhất trong nhóm của nó.

---

## 3. Sự bất đối xứng quan trọng nhất — GIÁ CƠ BẢN vs HỆ SỐ NHÂN

Đây là phát hiện cốt lõi, giải thích được gần như mọi thứ khác:

| | Giá cơ bản | Hệ số nhân |
|---|---|---|
| Dữ liệu giải thích được bao nhiêu? | **~19%** | **~96,6%** |
| Bản chất | Có **nhiễu ngẫu nhiên per-quote** lớn (~20%, không giảm dù kiểm soát quãng đường tới 2 mét) | Gần như **giá trị thị trường dùng chung** (hằng số trong 1 khu vực + 1 khung 5 phút) |
| Vì sao | ETA/tắc đường là yếu tố chính, nhưng bản thân nó **ngẫu nhiên** (chỉ ~3,5% dự đoán được) | Sinh trực tiếp từ công thức cung–cầu có sẵn trong data (gần tất định) |

→ **"Nút thắt cổ chai" của độ chính xác dự đoán giá nằm hoàn toàn ở giá cơ bản**, không phải hệ số
nhân — dù model hệ số nhân gần như hoàn hảo (ROC-AUC 0,998), model giá cuối vẫn bị giới hạn bởi
phần nhiễu không giải thích được trong giá cơ bản.

---

## 4. Chuỗi nhân quả đầy đủ (đọc từ trên xuống)

```
Giờ trong ngày / Mưa
        │  (η~0,70 / khá mạnh)
        ▼
Cầu tăng vọt giờ cao điểm (demand_index)
        │  (corr~0,69)
        ▼
Mất cân bằng cung–cầu (market_imbalance = cầu − cung)
        │  (corr~0,80)
        ▼
HỆ SỐ NHÂN tăng                          Thời lượng đi (tắc đường)
        │  (corr~0,48)                    │  ⚠️ CHỈ ~3,5% dự đoán được
        │                                  │  từ giờ/thời tiết — phần lớn
        ▼                                  │  là NGẪU NHIÊN theo từng chuyến
   GIÁ CUỐI = Giá cơ bản × Hệ số nhân  ◄───┘  (corr~0,43 với giá cơ bản)
        │
        ▼
   ~65% chênh lệch giá cuối (cùng tuyến/xe/km) VẪN KHÔNG GIẢI THÍCH ĐƯỢC
   → đây là SÀN NHIỄU của dữ liệu, không phải thiếu feature
```

---

## 5. Bản đồ notebook — cái nào trả lời phần nào

### Nhóm A — Khảo sát nền tảng (từng yếu tố riêng lẻ)
| File | Trả lời |
|---|---|
| `overview_data.ipynb`, `tong_quan_data_moi.ipynb` | Tổng quan 70 cột, dữ liệu mẫu |
| `01_location.ipynb` | Vị trí ↔ giá & hệ số nhân |
| `02_time.ipynb` | Giờ/thứ ↔ giá & hệ số nhân |
| `03_weather.ipynb` | Thời tiết ↔ giá & hệ số nhân |
| `04_traffic.ipynb` | Tắc đường ↔ giá & hệ số nhân |
| `key_feature_analysis_hcm.ipynb` | Bảng xếp hạng tổng hợp tất cả yếu tố (mục 2 ở trên lấy từ đây) |

### Nhóm B — So sánh Boston vs HCM (trả lời câu hỏi mentor)
| File | Trả lời |
|---|---|
| `00_TONG_HOP_SO_SANH.ipynb` | ⭐ Xác nhận mentor đúng: HCM bị giờ/mưa ảnh hưởng mạnh hơn Boston 74-97 lần, qua kênh hệ số nhân |

### Nhóm C — Thử feature engineering (đã kết luận: KHÔNG cần thêm)
| File | Kết luận |
|---|---|
| `05_kmpertime.ipynb` | Thêm tốc độ/đơn giá-km tường minh: không cải thiện (cây đã tự học) |
| `05b_kmpertime_gia_coban.ipynb` | Tương tự, trên giá cơ bản |
| `06_tuyen_chuanhoa.ipynb` | Chuẩn hóa theo 18 tuyến: xác nhận giờ/thứ/tháng không có tín hiệu ẩn bị gộp lẫn |

### Nhóm D — ⭐ Chuỗi phân rã nguyên nhân sâu (quan trọng nhất, mới nhất)
| File | Câu hỏi | Trả lời |
|---|---|---|
| `07_bien_do_surge_gia.ipynb` | Biên độ dao động thật (không chỉ tần suất) là bao nhiêu? | Hệ số nhân dao động ~50%, giá cơ bản chỉ ~4% |
| `08_yeu_to_giai_thich_gia.ipynb` | Cùng tuyến/xe/km, cái gì giải thích giá cuối? | Hệ số nhân ~35%, còn lại ~65% là nhiễu nằm trong giá cơ bản |
| `09_yeuto_gia_co_ban.ipynb` | Cùng quãng đường, cái gì giải thích giá cơ bản? | Chỉ thời lượng đi (~19%), còn lại là nhiễu |
| `10_yeuto_he_so_nhan.ipynb` | Bộ dữ liệu giải thích được bao nhiêu % hệ số nhân? | ~96,6% — gần tất định |
| `11_yeuto_thoi_luong.ipynb` | Bản thân thời lượng đi có dự đoán được không? | Không — chỉ ~3,5%, ngẫu nhiên theo chuyến |
| `12_truc_quan_gio_thoitiet.ipynb` | Trực quan hóa cả 3 đại lượng theo giờ/thời tiết | Biểu đồ tổng hợp minh họa mục 2-4 ở trên |

### Nhóm E — Feature Selection cho model (đầu ra: bộ feature đang dùng trong `model/`)
| File | Chốt feature cho |
|---|---|
| `FS_model_gia.ipynb` | Model giá trực tiếp (Hướng 1) |
| `FS_model_gia_coban.ipynb` | Model giá cơ bản (lõi Hybrid) |
| `FS_model_heso.ipynb` | Model hệ số nhân |

---

## 6. Vậy hướng đi hiện tại là gì — chốt lại

1. **Phần (i) — Study relation: ĐÃ XONG**, kết luận vững (nhiều bằng chứng độc lập, số liệu nhất quán qua 19 notebook).
2. **Phần (ii) — Build model: ĐÃ XONG kiến trúc chính** (Hybrid: giá cơ bản × hệ số nhân, 3 thuật toán, vượt baseline 44%), và đã **chứng minh bằng 8 hướng thử độc lập** rằng MAE ~15k VND là **sàn nhiễu của dữ liệu** — không còn dư địa cải thiện bằng cách đổi feature/thuật toán/tham số.
3. **Phần (iii) — Uncertainty Quantification: CHƯA LÀM** — đây là hướng hợp lý nhất tiếp theo, vì đã biết chắc chắn có ~65-81% nhiễu không giải thích được trong giá cơ bản → đưa ra khoảng dự đoán có giá trị hơn cố ép 1 con số.
4. **Acceptance rate model** (theo yêu cầu mentor): đã xác định rõ hướng (2 model xu hướng, mô phỏng dựa trên literature) — **chưa build**.

→ Không có gì "lung lay" cả — **hướng phân tích đã đóng hoàn toàn (kết luận nhất quán ở mọi góc
kiểm tra)**. Việc còn "mung lung" nhiều khả năng chỉ do khối lượng notebook lớn (19 file) chứ không
phải do kết luận mâu thuẫn nhau. Bước tiếp theo hợp lý: **Uncertainty Quantification**.
