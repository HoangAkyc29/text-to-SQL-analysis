"""Generate deterministic Vietnamese test images for vision benchmarks."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent


def chart_revenue_vi() -> Path:
    """Bar chart with known ground-truth values (triệu VND)."""
    months = ["Tháng 1", "Tháng 2", "Tháng 3"]
    values = [120, 150, 90]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(months, values, color=["#2563eb", "#16a34a", "#dc2626"])
    ax.set_title("Doanh thu cửa hàng 10001 (triệu VND)", fontsize=12)
    ax.set_ylabel("Triệu VND")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3, str(val), ha="center")
    fig.tight_layout()
    out = FIXTURES_DIR / "chart_doanh_thu_vi.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def table_sku_vi() -> Path:
    """Simple SKU table for OCR / reading test."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis("off")
    rows = [
        ["Mã SKU", "Tên hàng", "Doanh thu (triệu)"],
        ["SKU-001", "Sữa tươi 1L", "45"],
        ["SKU-002", "Gạo ST25 5kg", "62"],
        ["SKU-003", "Nước suối 500ml", "28"],
    ]
    table = ax.table(cellText=rows, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.6)
    ax.set_title("Top SKU — tuần 12/2025", fontsize=12, pad=20)
    out = FIXTURES_DIR / "table_sku_vi.png"
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    chart = chart_revenue_vi()
    table = table_sku_vi()
    print(f"Wrote {chart.name}, {table.name}")


if __name__ == "__main__":
    main()
