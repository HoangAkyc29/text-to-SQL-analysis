from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProductQueryCandidate:
    strategy: str
    sql_predicate: str
    confidence: float
    explanation_vi: str


@dataclass
class ResolvedProductQuery:
    user_input: str
    candidates: list[ProductQueryCandidate] = field(default_factory=list)
    probe_sql: list[str] = field(default_factory=list)


def _digits_only(value: str) -> str:
    return "".join(c for c in value if c.isdigit())


def resolve_product_code(user_input: str) -> ResolvedProductQuery:
    """Suggest SQL predicates and probe queries for ambiguous product identifiers."""
    raw = (user_input or "").strip()
    digits = _digits_only(raw)
    if not digits:
        return ResolvedProductQuery(user_input=raw)

    candidates: list[ProductQueryCandidate] = []
    probe_sql: list[str] = []

    candidates.append(
        ProductQueryCandidate(
            strategy="exact",
            sql_predicate=f"SKU_CODE = '{raw}' OR BARCODE = '{raw}'",
            confidence=0.5,
            explanation_vi="Khớp chính xác mã người dùng nhập",
        )
    )

    if len(digits) < 8:
        padded = digits.zfill(8)
        candidates.append(
            ProductQueryCandidate(
                strategy="lpad8",
                sql_predicate=f"SKU_CODE = '{padded}' OR BARCODE = '{padded}'",
                confidence=0.75,
                explanation_vi=f"Thêm số 0 đầu → {padded}",
            )
        )

    if len(digits) >= 10:
        candidates.append(
            ProductQueryCandidate(
                strategy="ean_barcode",
                sql_predicate=f"BARCODE = '{digits}' OR UPC_CODE = '{digits}'",
                confidence=0.7,
                explanation_vi="Mã dài 10–13 số — thử barcode/EAN",
            )
        )

    if len(digits) > 8:
        suffix = digits[-8:]
        candidates.append(
            ProductQueryCandidate(
                strategy="suffix8",
                sql_predicate=f"SKU_CODE LIKE '%{suffix}' OR BARCODE LIKE '%{suffix}'",
                confidence=0.6,
                explanation_vi=f"Có thể dư số đầu/cuối — thử 8 số cuối {suffix}",
            )
        )

    probe_sql.extend(
        [
            (
                f"SELECT TOP 5 SKU_ID, SKU_CODE, BARCODE FROM SKU_DEF "
                f"WHERE SKU_CODE = '{digits}' OR SKU_CODE = '{digits.zfill(8)}' OR BARCODE LIKE '%{digits[-8:]}%'"
            ),
            (
                f"SELECT TOP 5 BARCODE, SKU_ID FROM BARCODE "
                f"WHERE BARCODE = '{digits}' OR BARCODE LIKE '%{digits[-8:]}%'"
            ),
        ]
    )

    return ResolvedProductQuery(user_input=raw, candidates=candidates, probe_sql=probe_sql)
