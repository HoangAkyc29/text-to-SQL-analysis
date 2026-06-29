"""TCVN3 (ABC / VNI legacy) to Unicode Vietnamese conversion.

Used when SQL Server returns legacy-encoded text (often via varchar/char or
mis-decoded cp1252) instead of proper nvarchar Unicode.
"""
from __future__ import annotations

# Parallel mapping from user-provided PHP arrays (UNICODE[i] <-> TCVN3[i]).
UNICODE_CHARS: list[str] = [
    "À", "Á", "Â", "Ã", "È", "É", "Ê", "Ì", "Í", "Ò",
    "Ó", "Ô", "Õ", "Ù", "Ú", "Ý", "à", "á", "â", "ã",
    "è", "é", "ê", "ì", "í", "ò", "ó", "ô", "õ", "ù",
    "ú", "ý", "Ă", "ă", "Đ", "đ", "Ĩ", "ĩ", "Ũ", "ũ",
    "Ơ", "ơ", "Ư", "ư", "Ạ", "ạ", "Ả", "ả", "Ấ", "ấ",
    "Ầ", "ầ", "Ẩ", "ẩ", "Ẫ", "ẫ", "Ậ", "ậ", "Ắ", "ắ",
    "Ằ", "ằ", "Ẳ", "ẳ", "Ẵ", "ẵ", "Ặ", "ặ", "Ẹ", "ẹ",
    "Ẻ", "ẻ", "Ẽ", "ẽ", "Ế", "ế", "Ề", "ề", "Ể", "ể",
    "Ễ", "ễ", "Ệ", "ệ", "Ỉ", "ỉ", "Ị", "ị", "Ọ", "ọ",
    "Ỏ", "ỏ", "Ố", "ố", "Ồ", "ồ", "Ổ", "ổ", "Ỗ", "ỗ",
    "Ộ", "ộ", "Ớ", "ớ", "Ờ", "ờ", "Ở", "ở", "Ỡ", "ỡ",
    "Ợ", "ợ", "Ụ", "ụ", "Ủ", "ủ", "Ứ", "ứ", "Ừ", "ừ",
    "Ử", "ử", "Ữ", "ữ", "Ự", "ự", "Ỳ", "ỳ", "Ỵ", "ỵ",
    "Ỷ", "ỷ", "Ỹ", "ỹ",
]

TCVN3_CHARS: list[str] = [
    "Aµ", "A¸", "¢", "A·", "EÌ", "EÐ", "£", "I×", "IÝ", "Oß",
    "Oã", "¤", "Oâ", "Uï", "Uó", "Yý", "µ", "¸", "©", "·",
    "Ì", "Ð", "ª", "×", "Ý", "ß", "ã", "«", "â", "ï",
    "ó", "ý", "¡", "¨", "§", "®", "IÜ", "Ü", "Uò", "ò",
    "¥", "¬", "¦", "­", "A¹", "¹", "A¶", "¶", "¢Ê", "Ê",
    "¢Ç", "Ç", "¢È", "È", "¢É", "É", "¢Ë", "Ë", "¡¾", "¾",
    "¡»", "»", "¡¼", "¼", "¡½", "½", "¡Æ", "Æ", "EÑ", "Ñ",
    "EÎ", "Î", "EÏ", "Ï", "£Õ", "Õ", "£Ò", "Ò", "£Ó", "Ó",
    "£Ô", "Ô", "£Ö", "Ö", "IØ", "Ø", "IÞ", "Þ", "Oä", "ä",
    "Oá", "á", "¤è", "è", "¤å", "å", "¤æ", "æ", "¤ç", "ç",
    "¤é", "é", "¥í", "í", "¥ê", "ê", "¥ë", "ë", "¥ì", "ì",
    "¥î", "î", "Uô", "ô", "Uñ", "ñ", "¦ø", "ø", "¦õ", "õ",
    "¦ö", "ö", "¦÷", "÷", "¦ù", "ù", "Yú", "ú", "Yþ", "þ",
    "Yû", "û", "Yü", "ü",
]

if len(UNICODE_CHARS) != len(TCVN3_CHARS):
    raise ValueError(f"TCVN3 map length mismatch: {len(UNICODE_CHARS)} vs {len(TCVN3_CHARS)}")

# Multi-char TCVN3 sequences (VNI-style), longest first for greedy left-to-right scan.
_MULTI_TCVN3: list[tuple[str, str]] = sorted(
    ((t, u) for t, u in zip(TCVN3_CHARS, UNICODE_CHARS, strict=True) if len(t) > 1),
    key=lambda pair: len(pair[0]),
    reverse=True,
)

# Single TCVN3 byte/char → Unicode (ABC-style legacy in varchar fields).
_SINGLE_TCVN3: dict[str, str] = {
    t: u for t, u in zip(TCVN3_CHARS, UNICODE_CHARS, strict=True) if len(t) == 1
}

def tcvn3_to_unicode(value: str | None) -> str | None:
    """Convert a string from TCVN3 legacy encoding to Unicode Vietnamese.

    Single left-to-right pass: match multi-char TCVN3 at cursor, else map one
    character. Never re-process Unicode output (avoids â→õ→ừ corruption).
    """
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    if not value:
        return value

    out: list[str] = []
    i = 0
    n = len(value)
    while i < n:
        matched = False
        for tcvn3, uni in _MULTI_TCVN3:
            end = i + len(tcvn3)
            if end <= n and value[i:end] == tcvn3:
                out.append(uni)
                i = end
                matched = True
                break
        if matched:
            continue
        ch = value[i]
        out.append(_SINGLE_TCVN3.get(ch, ch))
        i += 1
    return "".join(out)


def maybe_decode_row(row: dict[str, object]) -> dict[str, object]:
    """Return row copy with all string values passed through TCVN3 conversion."""
    out: dict[str, object] = {}
    for key, val in row.items():
        if isinstance(val, str):
            out[key] = tcvn3_to_unicode(val)
        else:
            out[key] = val
    return out

# Backward-compatible alias used by tests / introspection.
TCVN3_TO_UNICODE: list[tuple[str, str]] = list(
    zip(TCVN3_CHARS, UNICODE_CHARS, strict=True)
)
