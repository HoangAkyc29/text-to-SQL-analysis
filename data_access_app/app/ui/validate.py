"""Pre-search / pre-export form validation — field-level red borders + messages."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Iterable

import flet as ft

from app import theme
from app.export.splitters import parse_point_buckets

# Mã thẻ kiểu A10000054973 / E10000000053 …
_CARD_LIKE = re.compile(r"^[A-Za-z][A-Za-z0-9]{6,}$")
_NUM_RE = re.compile(r"^-?\d+(\.\d+)?$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def card_prefix_value(field: ft.Dropdown | ft.TextField | None) -> str:
    """Read prefix from TextField or editable Dropdown (maps __none__ → empty).

    Important: do **not** fall back to Dropdown.text when value is __none__.
    Editable dropdowns can expose stale/filter text (e.g. a digit from another
    control) which would wrongly become CARD_ID LIKE '2%' and zero out results.
    Typed prefixes are synced into .value via on_text_change in form_kit.
    """
    if field is None:
        return ""
    raw = (field.value or "").strip()
    if raw in {"", "__none__"}:
        return ""
    return raw


def parse_birth_month(value: str | None) -> int | None:
    """Parse UI month value: '2', 'Tháng 2', or None/'any' → 1..12 or None."""
    raw = (value or "").strip()
    if not raw or raw.lower() in {"any", "__none__"}:
        return None
    if raw.isdigit():
        m = int(raw)
    else:
        m_match = re.search(r"(\d{1,2})", raw)
        if not m_match:
            raise ValueError("Tháng sinh không hợp lệ")
        m = int(m_match.group(1))
    if m < 1 or m > 12:
        raise ValueError("Tháng sinh phải từ 1–12")
    return m


def clear_errors(*fields: ft.Control | None) -> None:
    for f in fields:
        if f is None:
            continue
        target: ft.Control | None = None
        if isinstance(f, (ft.TextField, ft.Dropdown)):
            target = f
        else:
            data = getattr(f, "data", None) or {}
            inner = data.get("field")
            if isinstance(inner, ft.TextField):
                target = inner
        if target is None:
            continue
        target.error_text = None  # type: ignore[attr-defined]
        target.border_color = theme.BORDER_STRONG  # type: ignore[attr-defined]
        target.focused_border_color = theme.ACCENT  # type: ignore[attr-defined]


def set_error(field: ft.Control, message: str) -> None:
    data = getattr(field, "data", None) or {}
    if not isinstance(field, (ft.TextField, ft.Dropdown)) and isinstance(data.get("field"), ft.TextField):
        field = data["field"]
    field.error_text = message  # type: ignore[attr-defined]
    field.border_color = theme.DANGER  # type: ignore[attr-defined]
    field.focused_border_color = theme.DANGER  # type: ignore[attr-defined]


def looks_like_card_id(token: str) -> bool:
    t = (token or "").strip()
    return bool(t and _CARD_LIKE.match(t))


def split_tokens(raw: str) -> list[str]:
    """Split by newline / comma / semicolon / pipe (preserve spaces inside a token only if one piece)."""
    if not raw or not str(raw).strip():
        return []
    parts: list[str] = []
    for line in str(raw).replace(",", "\n").replace(";", "\n").replace("|", "\n").splitlines():
        line = line.strip()
        if not line:
            continue
        # Space-separated many card-like codes → separate tokens
        bits = [b for b in re.split(r"\s+", line) if b]
        if len(bits) > 1 and sum(1 for b in bits if looks_like_card_id(b)) >= 2:
            parts.extend(bits)
        else:
            parts.append(line)
    return parts


def line_looks_like_card_list(line: str) -> bool:
    """True nếu một dòng chứa ≥2 mã giống CARD_ID (thường dán nhầm vào ô SP)."""
    bits = [b for b in re.split(r"[\s,;|/]+", (line or "").strip()) if b]
    if len(bits) < 2:
        return False
    return sum(1 for b in bits if looks_like_card_id(b)) >= 2


def validate_date_field(field: ft.Control, *, label: str = "Ngày") -> date | None:
    from app.ui.widgets import unwrap_date_field

    try:
        field = unwrap_date_field(field)
    except TypeError:
        pass
    raw = (field.value or "").strip()  # type: ignore[attr-defined]
    if not raw:
        set_error(field, f"{label}: bắt buộc (định dạng YYYY-MM-DD)")
        return None
    if not _DATE_RE.match(raw):
        set_error(field, f"{label}: sai định dạng — dùng YYYY-MM-DD (vd 2026-07-01)")
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        set_error(field, f"{label}: ngày không hợp lệ")
        return None


def validate_date_range(
    d_from: ft.Control,
    d_to: ft.Control,
) -> tuple[date, date] | None:
    a = validate_date_field(d_from, label="Từ ngày")
    b = validate_date_field(d_to, label="Đến ngày")
    if a is None or b is None:
        return None
    if a > b:
        set_error(d_from, "Từ ngày phải ≤ Đến ngày")
        set_error(d_to, "Đến ngày phải ≥ Từ ngày")
        return None
    return a, b


# Without store chips, wide windows can scan huge STRANS/TRANSHDR sets.
MAX_OPEN_FACT_DAYS = 31


def validate_fact_scope(
    d_from: ft.Control,
    d_to: ft.Control,
    *,
    date_start: date,
    date_end: date,
    store_ids: list[str] | None,
    max_days: int = MAX_OPEN_FACT_DAYS,
) -> bool:
    """Require store filter when the inclusive date span exceeds ``max_days``."""
    stores = [s for s in (store_ids or []) if s and str(s).strip()]
    if stores:
        return True
    days = (date_end - date_start).days + 1
    if days <= max_days:
        return True
    msg = (
        f"Chưa chọn siêu thị — khoảng ngày tối đa {max_days} ngày "
        f"(hiện {days}). Chọn STK hoặc thu hẹp ngày."
    )
    set_error(d_from, msg)
    set_error(d_to, msg)
    return False


def validate_optional_number(
    field: ft.TextField,
    *,
    label: str = "Giá trị",
) -> tuple[bool, float | None]:
    """
    Returns (ok, value). Empty → (True, None).
    Non-numeric → (False, None) + field error.
    """
    raw = (field.value or "").strip().replace(" ", "").replace(",", "")
    if not raw:
        return True, None
    if not _NUM_RE.match(raw):
        set_error(
            field,
            f"{label}: chỉ nhập số (vd 100000 hoặc 1500.5), không nhập chữ",
        )
        return False, None
    try:
        return True, float(raw)
    except ValueError:
        set_error(field, f"{label}: không đọc được số")
        return False, None


def validate_number_range(
    min_f: ft.TextField,
    max_f: ft.TextField,
    *,
    label: str = "Khoảng giá trị",
) -> tuple[bool, float | None, float | None]:
    ok_lo, lo = validate_optional_number(min_f, label=f"{label} — từ")
    ok_hi, hi = validate_optional_number(max_f, label=f"{label} — đến")
    if not ok_lo or not ok_hi:
        return False, None, None
    if lo is not None and hi is not None and lo > hi:
        set_error(min_f, f"{label}: 'từ' phải ≤ 'đến'")
        set_error(max_f, f"{label}: 'đến' phải ≥ 'từ'")
        return False, None, None
    return True, lo, hi


def validate_card_list(
    field: ft.TextField,
    *,
    required: bool = True,
) -> list[str] | None:
    raw = field.value or ""
    cards = split_tokens(raw)
    if required and not cards:
        set_error(field, "Nhập ít nhất một mã thẻ (mỗi dòng một mã, hoặc cách bằng phẩy)")
        return None
    bad = [c for c in cards if not looks_like_card_id(c)]
    if bad:
        sample = ", ".join(bad[:3])
        more = f" … (+{len(bad) - 3})" if len(bad) > 3 else ""
        set_error(
            field,
            f"Mã thẻ không đúng dạng (chữ cái + số, vd E10000000053): {sample}{more}",
        )
        return None
    return cards


def validate_product_query_single(
    field: ft.TextField,
    *,
    required: bool = False,
) -> str | None:
    """F4 ô SP đơn — không cho dán nhiều mã thẻ vào một dòng."""
    raw = (field.value or "").strip()
    if not raw:
        if required:
            set_error(field, "Nhập mã hoặc tên sản phẩm")
            return None
        return ""
    if line_looks_like_card_list(raw):
        set_error(
            field,
            "Ô này là mã/tên sản phẩm — không dán nhiều mã thẻ. "
            "Danh sách thẻ hãy dán vào ô «Danh sách thẻ».",
        )
        return None
    # Nhiều dòng trong ô SP đơn cũng lệch UX
    if "\n" in (field.value or "") and len([ln for ln in raw.splitlines() if ln.strip()]) > 1:
        set_error(
            field,
            "Chỉ nhập một mã hoặc một tên SP. Nhiều SP → dùng chức năng Đơn theo sản phẩm (F5).",
        )
        return None
    return raw


def validate_product_token_list(
    field: ft.TextField,
    *,
    required: bool = True,
) -> list[str] | None:
    """F5 — mỗi dòng một SP; chặn dòng chứa nhiều mã thẻ.

    ``required=False`` cho phép danh sách trống (= tất cả SP trong kỳ ở domain).
    """
    raw = field.value or ""
    lines = [ln.strip() for ln in raw.replace(",", "\n").splitlines() if ln.strip()]
    if required and not lines:
        set_error(field, "Nhập ít nhất một mã hoặc tên SP (mỗi dòng một mục)")
        return None
    if not lines:
        return []
    bad_lines = [ln for ln in lines if line_looks_like_card_list(ln)]
    if bad_lines:
        set_error(
            field,
            "Phát hiện dòng chứa nhiều mã thẻ — ô này tìm sản phẩm, không phải danh sách thẻ. "
            "Mỗi dòng chỉ một mã/tên SP.",
        )
        return None
    # Too many card-like single tokens pasted as "products"
    cardish = [ln for ln in lines if looks_like_card_id(ln)]
    if len(lines) >= 3 and len(cardish) == len(lines):
        set_error(
            field,
            "Các dòng giống mã thẻ hết — có lẽ bạn đang dán danh sách thẻ. "
            "Dùng chức năng Đơn theo khách (F4) cho danh sách thẻ.",
        )
        return None
    return lines


def validate_card_prefix(field: ft.TextField | ft.Dropdown) -> str | None:
    raw = card_prefix_value(field)
    if not raw:
        return ""
    if line_looks_like_card_list(raw) or (looks_like_card_id(raw) and len(raw) > 8):
        set_error(
            field,
            "Tiền tố ngắn (vd A, E) — không dán cả mã thẻ đầy đủ hay danh sách thẻ",
        )
        return None
    if len(raw) > 8:
        set_error(field, "Tiền tố quá dài (tối đa ~8 ký tự, vd A / E / F)")
        return None
    # Digit-only (e.g. "2") is almost always birth-month key leakage → silent 0 rows.
    if raw.isdigit():
        set_error(
            field,
            "Tiền tố thẻ phải bắt đầu bằng chữ (vd A, E, F) — không dùng số thuần",
        )
        return None
    if not re.match(r"^[A-Za-z][A-Za-z0-9]{0,7}$", raw):
        set_error(field, "Tiền tố không hợp lệ (vd A, E, F12)")
        return None
    return raw


def validate_point_buckets(field: ft.TextField, *, required_on_export: bool = False) -> bool:
    raw = (field.value or "").strip()
    if not raw:
        if required_on_export:
            set_error(field, "Nhập mức điểm chia file (vd 0-200,200-500,>500) hoặc để trống nếu không chia")
            # empty is allowed for export without buckets — return True
        return True
    try:
        parse_point_buckets(raw)
    except Exception as exc:  # noqa: BLE001
        set_error(
            field,
            f"Sai cú pháp mức điểm: {exc}. Ví dụ đúng: 0-200,200-500,>500",
        )
        return False
    return True


def fail_status(status: ft.Text, page: ft.Page, *, message: str = "Kiểm tra lại các ô khoanh đỏ") -> None:
    status.value = message
    status.color = theme.DANGER
    page.update()


def any_errors(fields: Iterable[ft.TextField]) -> bool:
    return any(bool(getattr(f, "error_text", None)) for f in fields)
