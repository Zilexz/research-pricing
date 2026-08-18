# -*- coding: utf-8 -*-
"""Dịch công thức LaTeX sang chuỗi Unicode đọc được trong Word.

Không dựng OMML (equation thật của Word) — chỉ cần công thức hiện ra đúng ký hiệu
thay vì lòi ra `$$\\hat p = \\mathbb{E}...$$` như văn bản thô.

Hàm chính:
    dich(s) -> [(chữ, kiểu), ...]   kiểu ∈ {"", "sub", "sup"}

Bên gọi tự tạo run cho từng đoạn và bật subscript/superscript tương ứng —
nhờ vậy chỉ số dưới kiểu `t-Δ` hay `firm` hiện đúng, không phải hạ cấp thành `_(...)`.

Phạm vi: đủ cho các lệnh có trong TECH_DOC. Lệnh lạ thì bỏ dấu `\\` và giữ tên,
để người đọc vẫn đoán được chứ không mất chữ.
"""
import re
import unicodedata

# ── ký hiệu một-đối-một ──────────────────────────────────────────────────
KY_HIEU = {
    # chữ Hy Lạp
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "Delta": "Δ",
    "epsilon": "ε", "varepsilon": "ε", "theta": "θ", "lambda": "λ", "mu": "μ",
    "sigma": "σ", "Sigma": "Σ", "pi": "π", "rho": "ρ", "tau": "τ", "phi": "φ",
    "omega": "ω", "Omega": "Ω", "eta": "η",
    # toán tử và quan hệ
    "in": "∈", "notin": "∉", "times": "×", "cdot": "·", "pm": "±", "mp": "∓",
    "ge": "≥", "geq": "≥", "le": "≤", "leq": "≤", "ne": "≠", "neq": "≠",
    "approx": "≈", "equiv": "≡", "sim": "∼", "propto": "∝",
    "to": "→", "rightarrow": "→", "Rightarrow": "⇒", "leftarrow": "←",
    "mid": "|", "cup": "∪", "cap": "∩", "subset": "⊂", "forall": "∀",
    "exists": "∃", "infty": "∞", "partial": "∂", "nabla": "∇", "sum": "Σ",
    "prod": "Π", "int": "∫", "sqrt": "√", "cdots": "⋯", "ldots": "…",
    "ell": "ℓ", "hbar": "ℏ", "circ": "∘", "star": "⋆", "perp": "⊥",
    # khoảng trắng
    "quad": "  ", "qquad": "    ",
    ",": " ", ";": " ", ":": " ", " ": " ", "!": "",
    # dấu ngoặc chỉ để chỉnh cỡ — bỏ, giữ lại ký tự ngoặc đứng sau
    "left": "", "right": "", "big": "", "Big": "", "bigg": "", "Bigg": "",
    "bigl": "", "bigr": "", "Bigl": "", "Bigr": "",
    "displaystyle": "", "limits": "",
    # hàm giữ nguyên tên, viết đứng
    "log": "log", "ln": "ln", "exp": "exp", "min": "min", "max": "max",
    "sin": "sin", "cos": "cos", "tan": "tan", "det": "det", "dim": "dim",
    "arg": "arg", "argmin": "argmin", "argmax": "argmax", "mathrm": None,
}

MATHBB = {"E": "𝔼", "P": "ℙ", "R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ",
          "1": "𝟙", "I": "𝕀"}
MATHCAL = {"H": "ℋ", "F": "ℱ", "L": "ℒ", "D": "𝒟", "N": "𝒩", "X": "𝒳",
           "C": "𝒞", "B": "ℬ", "T": "𝒯"}

# dấu phụ chồng lên ký tự đứng ngay sau
DAU_PHU = {"hat": "̂", "bar": "̄", "tilde": "̃",
           "vec": "⃗", "dot": "̇", "check": "̌"}

HAM = {"log", "ln", "exp", "min", "max", "sin", "cos", "tan", "det", "dim",
       "arg", "argmin", "argmax"}

# ký tự có nguy cơ cần bọc ngoặc khi làm tử/mẫu phân số
CAN_NGOAC = re.compile(r"[+\-−±·×/∈≥≤=,\s]")


def _doc_nhom(s, i):
    """s[i] == '{' -> trả (nội dung bên trong, chỉ số sau dấu '}')."""
    assert s[i] == "{"
    sau, i = 1, i + 1
    dau = i
    while i < len(s) and sau:
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "{":
            sau += 1
        elif s[i] == "}":
            sau -= 1
        i += 1
    return s[dau:i - 1], i


def _doc_lenh(s, i):
    """s[i] == '\\' -> trả (tên lệnh, chỉ số sau tên)."""
    j = i + 1
    if j < len(s) and s[j].isalpha():
        while j < len(s) and s[j].isalpha():
            j += 1
        return s[i + 1:j], j
    return s[i + 1:i + 2], i + 2      # lệnh một ký tự: \, \; \{ \}


def _doc_don_vi(s, i):
    """Đọc một 'đơn vị' mà ^ _ \\hat áp lên: nhóm {..}, một lệnh, hoặc một ký tự."""
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return "", i
    if s[i] == "{":
        noi, j = _doc_nhom(s, i)
        return noi, j
    if s[i] == "\\":
        ten, j = _doc_lenh(s, i)
        return "\\" + ten, j
    return s[i], i + 1


def _phang(s):
    """Dịch s thành chuỗi phẳng (bỏ phân biệt sub/sup) — dùng cho tử/mẫu phân số."""
    return "".join(t for t, _ in dich(s))


def dich(s):
    """LaTeX -> [(chữ, kiểu)] với kiểu ∈ {'', 'sub', 'sup'}."""
    ra, i = [], 0

    def them(chu, kieu=""):
        if not chu:
            return
        if ra and ra[-1][1] == kieu:
            ra[-1] = (ra[-1][0] + chu, kieu)
        else:
            ra.append((chu, kieu))

    while i < len(s):
        c = s[i]

        if c == "\\":
            ten, j = _doc_lenh(s, i)

            if ten in DAU_PHU:                       # \hat p -> p̂
                don, j = _doc_don_vi(s, j)
                goc = _phang(don) if don.startswith("\\") or len(don) > 1 else don
                them(unicodedata.normalize("NFC", goc + DAU_PHU[ten]))
                i = j
                continue

            if ten == "frac":                        # \frac{a}{b} -> a/b
                tu, j = _doc_don_vi(s, j)
                mau, j = _doc_don_vi(s, j)
                a, b = _phang(tu), _phang(mau)
                if CAN_NGOAC.search(a):
                    a = f"({a})"
                if CAN_NGOAC.search(b):
                    b = f"({b})"
                them(f"{a}/{b}")
                i = j
                continue

            if ten in ("text", "textrm", "textbf", "textit", "mathrm", "operatorname"):
                noi, j = _doc_don_vi(s, j)
                them(noi.replace("\\ ", " "))        # giữ nguyên, kể cả tiếng Việt
                i = j
                continue

            if ten in ("mathbb", "mathcal", "mathbf", "mathsf"):
                noi, j = _doc_don_vi(s, j)
                bang = MATHBB if ten == "mathbb" else MATHCAL if ten == "mathcal" else {}
                them(bang.get(noi.strip(), noi.strip()))
                i = j
                continue

            if ten in KY_HIEU:
                kh = KY_HIEU[ten]
                if kh:
                    them(kh)
                    # \log\frac{p}{q} -> "log p/q", khong dinh thanh "logp/q"
                    if ten in HAM and j < len(s) and s[j] not in " ({[":
                        them(" ")
                i = j
                continue

            if ten in ("{", "}", "$", "%", "&", "#", "_"):
                them(ten)
                i = j
                continue

            them(ten)                                # lệnh lạ: giữ tên, bỏ dấu \
            i = j
            continue

        if c in "_^":
            don, j = _doc_don_vi(s, i + 1)
            for t, k in dich(don):
                them(t, "sub" if c == "_" else "sup")
            i = j
            continue

        if c == "{":
            noi, j = _doc_nhom(s, i)
            if noi == ",":                           # 0{,}90 -> 0,90
                them(",")
            else:
                for t, k in dich(noi):
                    them(t, k)
            i = j
            continue

        if c == "}":
            i += 1
            continue

        # gach noi trong cong thuc la dau TRU, khong phai hyphen
        them("−" if c == "-" else c)
        i += 1

    return [(t, k) for t, k in ra if t]


def phang(s):
    """Tiện ích: LaTeX -> một chuỗi duy nhất, chỉ số viết liền."""
    return "".join(t for t, _ in dich(s))


if __name__ == "__main__":
    THU = [
        r"\hat p = \mathbb{E}[\,p \mid x,\ \mathcal{H}_{t-\Delta}\,], "
        r"\qquad \Delta \in \{5, 10, 15, 30\}\ \text{phút}",
        r"\text{giá} = \text{giá cơ bản} \times \text{hệ số nhân}",
        r"\log\frac{\hat p}{p} = \log\frac{\hat b}{b} + \log\frac{\hat m}{m}",
        r"q = \text{Quantile}_{0{,}90}\big(\{res_i\}_{i \in \text{calib}}\big)",
        r"[\ell, u] = \hat p \cdot (1 \pm q)",
        r"\varepsilon_{\text{firm}} = -\beta(1-s_1)",
        r"s_0 = \frac{1-m}{R-m}",
        r"\mathbb{P}(p \in [\ell, u]) \ge 1 - \alpha",
        r"\alpha = 0{,}10",
        r"t - \Delta",
    ]
    for t in THU:
        print(f"  {phang(t)}")
        print(f"      {dich(t)}")
