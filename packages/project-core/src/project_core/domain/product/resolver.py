"""Product-code helpers for offline/stub tooling.

**Not** injected into Agent II production prompts as ready-made SQL.
Agent II must invent filters from brief + dictionary + text-filter rule.
"""

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


def _escape_like(value: str) -> str:
    return value.replace("'", "''").replace("[", "[[]").replace("%", "[%]").replace("_", "[_]")


def substring_ci_predicate(column: str, value: str) -> str:
    lit = _escape_like((value or "").strip())
    return f"LOWER({column}) LIKE '%' + LOWER('{lit}') + '%'"


def resolve_product_code(user_input: str) -> ResolvedProductQuery:
    """Build deterministic predicates for ALLOW_LLM_STUB / unit tests only."""
    raw = (user_input or "").strip()
    digits = _digits_only(raw)
    if not digits:
        return ResolvedProductQuery(user_input=raw)

    candidates: list[ProductQueryCandidate] = []
    probe_sql: list[str] = []

    def _or_sku_barcode(val: str) -> str:
        return (
            f"({substring_ci_predicate('SKU_CODE', val)} OR "
            f"{substring_ci_predicate('BARCODE', val)})"
        )

    candidates.append(
        ProductQueryCandidate(
            strategy="substring_ci",
            sql_predicate=_or_sku_barcode(raw),
            confidence=0.7,
            explanation_vi="substring case-insensitive (stub/test helper)",
        )
    )
    if len(digits) < 8:
        padded = digits.zfill(8)
        candidates.append(
            ProductQueryCandidate(
                strategy="lpad8_substring_ci",
                sql_predicate=_or_sku_barcode(padded),
                confidence=0.8,
                explanation_vi="padded substring (stub/test helper)",
            )
        )

    probe_vals = [digits]
    if len(digits) < 8:
        probe_vals.append(digits.zfill(8))
    sku_pred = " OR ".join(substring_ci_predicate("SKU_CODE", v) for v in probe_vals)
    bar_pred = substring_ci_predicate("BARCODE", digits)
    probe_sql.append(f"SELECT TOP 5 SKU_ID, SKU_CODE, BARCODE FROM SKU_DEF WHERE {sku_pred} OR {bar_pred}")
    probe_sql.append(f"SELECT TOP 5 BARCODE, SKU_ID FROM BARCODE WHERE {bar_pred}")

    return ResolvedProductQuery(user_input=raw, candidates=candidates, probe_sql=probe_sql)
