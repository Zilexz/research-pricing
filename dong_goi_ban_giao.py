# -*- coding: utf-8 -*-
"""Gom moi thu can ban giao vao mot thu muc BAN_GIAO/.

Chay:  py -3 dong_goi_ban_giao.py

Thu muc nay chi chua BAN SAO cua cac file da co trong repo, nen no khong duoc
theo doi bang git (xem .gitignore). Mat thi chay lai script nay la co lai.
"""
import io
import shutil
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
DICH = GOC / "BAN_GIAO"
TL = GOC / "TP_HCM_data" / "docs" / "tai_lieu_bao_cao"
BC = GOC / "TP_HCM_data" / "docs" / "bao_cao_tuan"
DEMO = GOC / "TP_HCM_data" / "demo_v2"


def chep(nguon: Path, thu_muc: Path) -> bool:
    if not nguon.exists():
        print("   ! thieu:", nguon.name)
        return False
    thu_muc.mkdir(parents=True, exist_ok=True)
    shutil.copy2(nguon, thu_muc / nguon.name)
    return True


def main() -> int:
    if DICH.exists():
        shutil.rmtree(DICH)
    DICH.mkdir()

    dem = 0

    # ── 1. Slide ────────────────────────────────────────────────────
    d = DICH / "1_slide"
    for f in ("slide_trinh_bay.pdf", "slide_trinh_bay.html"):
        dem += chep(TL / f, d)

    # ── 2. Tai lieu chinh ───────────────────────────────────────────
    d = DICH / "2_tai_lieu"
    for f in ("TECH_DOC.pdf", "TECH_DOC.docx",
              "RESEARCH_PAPER.pdf", "RESEARCH_PAPER.docx"):
        dem += chep(TL / f, d)

    # ── 3. Bao cao tuan — chi ban .docx cho gon ─────────────────────
    d = DICH / "3_bao_cao_tuan"
    for f in sorted(BC.glob("*.docx")):
        dem += chep(f, d)

    # ── 4. Demo chay duoc offline ───────────────────────────────────
    if DEMO.exists():
        shutil.copytree(DEMO, DICH / "4_demo")
        dem += sum(1 for _ in (DICH / "4_demo").rglob("*") if _.is_file())
    else:
        print("   ! thieu thu muc demo_v2")

    # ── 5. Trang muc luc ────────────────────────────────────────────
    io.open(DICH / "00_DOC_TRUOC.md", "w", encoding="utf-8").write(MUC_LUC)
    dem += 1

    co = sum(f.stat().st_size for f in DICH.rglob("*") if f.is_file())
    print("Da gom {} file vao {} ({:.1f} MB)".format(dem, DICH.name, co / 1048576))
    return 0


MUC_LUC = """# Bàn giao — Competitor Fare Forecasting (TP.HCM)

Toàn bộ thành phẩm gom về một chỗ. Mọi file ở đây là **bản sao** — bản gốc vẫn nằm trong repo,
dựng lại bằng `py -3 dong_goi_ban_giao.py` ở thư mục cha.

> ⚠️ Dữ liệu là **synthetic** — 1 nền tảng đối thủ, 2 dịch vụ, 3 khu vực, 11 ngày rời rạc.
> Mọi con số mô tả hành vi bộ sinh dữ liệu, **không phải thị trường TP.HCM thật**.
> Nói rõ chỗ này ngay đầu buổi trình bày.

## Nên mở theo thứ tự nào

| # | Mở cái gì | Khi nào dùng |
|---|---|---|
| 1 | `1_slide/slide_trinh_bay.pdf` | Trình bày. 23 slide, đọc được không cần cài gì |
| 2 | `4_demo/index.html` | Nháy đúp là chạy. Không cần mạng, không cần cài |
| 3 | `2_tai_lieu/TECH_DOC.pdf` | Ai hỏi sâu về kỹ thuật — 42 trang |
| 4 | `2_tai_lieu/RESEARCH_PAPER.pdf` | Bản viết theo lối bài báo — 27 trang |
| 5 | `3_bao_cao_tuan/` | Truy lại việc của từng tuần |

## 1_slide

| File | Nội dung |
|---|---|
| `slide_trinh_bay.pdf` | 23 slide, bản in — dùng khi trình chiếu bằng máy người khác |
| `slide_trinh_bay.html` | Bản **tương tác**: bấm ← → chuyển slide, có nút toàn màn hình. Cần mạng để tải phông |

## 2_tai_lieu

| File | Trang | Nội dung |
|---|---|---|
| `TECH_DOC.pdf` · `.docx` | 42 | Tài liệu kỹ thuật: bài toán, dữ liệu, kiến trúc, đánh giá, uncertainty, vận hành, nhật ký đính chính |
| `RESEARCH_PAPER.pdf` · `.docx` | 27 | Bản viết theo lối bài báo, có tóm tắt và tài liệu tham khảo |

## 3_bao_cao_tuan

Báo cáo từng tuần, bản `.docx`. Của tuần 5 có bốn file — **`bao_cao_tuan5_TONG_HOP.docx` là bản
nộp**, gộp cả ba phần; ba file còn lại là từng phần tách riêng.

## 4_demo

Demo mô phỏng trên bản đồ. **Nháy đúp `index.html`** — không cần cài gì, không cần server,
không cần mạng. Đọc `CHAY_DEMO.md` trong đó trước: có kịch bản trình bày 4 bước và ba điều
phải nói trước nếu bị hỏi.

---

## Kết quả một trang

| Cấu phần | Kết quả chốt |
|---|---|
| **(i)** Yếu tố cấu thành giá | `giá = giá cơ bản × hệ số nhân` · cung–cầu mạnh nhất **+35,08%** · 80–96% tác động thị trường đi qua hệ số nhân |
| **(ii)** Model dự báo | Hybrid hai tầng · MAE **18.048đ** · MAPE **14,74%** · vượt persistence **47,4%** |
| **(iii)** Khoảng tin cậy | Conformal chuẩn hoá `p̂ × (1 ± 30,07%)` · coverage **89,81%** |
| Giảm sai số nhóm khó | Ghép GAM–GBM: `>15 km` **18,12% → 15,61%**, `>300k` **24,04% → 22,49%**, toàn tập không xấu đi |

**Đang chờ mentor quyết:** chọn Mondrian (+0,21% độ rộng, rẻ) hay CQR (+3,2% độ rộng, kéo band
`>300k` từ 83,79% lên 88,03%) cho khoảng dự báo.
"""


if __name__ == "__main__":
    sys.exit(main())
