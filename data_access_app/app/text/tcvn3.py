"""TCVN3 (ABC / VNI legacy) to Unicode — standalone copy for this app."""
from __future__ import annotations

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

_MULTI_TCVN3: list[tuple[str, str]] = sorted(
    ((t, u) for t, u in zip(TCVN3_CHARS, UNICODE_CHARS, strict=True) if len(t) > 1),
    key=lambda pair: len(pair[0]),
    reverse=True,
)
_SINGLE_TCVN3: dict[str, str] = {
    t: u for t, u in zip(TCVN3_CHARS, UNICODE_CHARS, strict=True) if len(t) == 1
}


def tcvn3_to_unicode(value: str | None) -> str | None:
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


def is_unicode_text_column(name: str | None) -> bool:
    if not name:
        return False
    return str(name).upper().endswith("_U")


def decode_dataframe(df, text_columns: set[str] | None = None):
    """Decode TCVN3 string columns in-place copy; skip *_U columns."""
    import pandas as pd

    if df is None or getattr(df, "empty", True):
        return df
    out = df.copy()
    for col in out.columns:
        if not pd.api.types.is_object_dtype(out[col]) and not pd.api.types.is_string_dtype(out[col]):
            continue
        if is_unicode_text_column(str(col)):
            continue
        if text_columns is not None and str(col).upper() not in {c.upper() for c in text_columns}:
            # still decode common name-like object columns
            if str(col).upper() not in {
                "NAME",
                "FULL_NAME",
                "GRP_NAME",
                "CUST_NAME",
                "REMARK",
                "ADDRESS",
            }:
                # decode all non-_U object strings by default for safety
                pass
        out[col] = out[col].map(
            lambda v: tcvn3_to_unicode(v) if isinstance(v, str) else v
        )
    return out
