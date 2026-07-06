#!/usr/bin/env python3
"""Split docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md into themed files under docs2/."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md"
OUT = ROOT / "docs2"

# (filename, title, start_line, end_line) — 1-indexed inclusive
SPLITS: list[tuple[str, str, int, int]] = [
    (
        "01-gioi-thieu-va-kien-truc.md",
        "Giới thiệu và kiến trúc tổng thể",
        44,
        141,
    ),
    (
        "02-monorepo-va-cau-truc-thu-muc.md",
        "Monorepo và cây thư mục",
        142,
        254,
    ),
    (
        "03-libs-va-project-core-tong-quan.md",
        "Thư viện libs và project-core (tổng quan)",
        255,
        328,
    ),
    (
        "04-agents-va-mcp-tong-quan.md",
        "Agents I–IV, MCP servers (tổng quan)",
        329,
        416,
    ),
    (
        "05-database-auth-va-session.md",
        "Cơ sở dữ liệu, Redis, MongoDB, RBAC",
        459,
        506,
    ),
    (
        "06-pipeline-va-luong-agent.md",
        "Pipeline, Agent I–IV chi tiết luồng",
        507,
        632,
    ),
    (
        "07-trien-khai-docker.md",
        "Triển khai Docker và compose",
        633,
        646,
    ),
    (
        "08-ma-nguon-agents-chat-gateway.md",
        "Mã nguồn chi tiết: agents và chat-gateway (§Z.2)",
        679,
        2910,
    ),
    (
        "09-pipeline-tung-dong.md",
        "Phân tích từng dòng pipeline.py (§Z.3)",
        2911,
        14258,
    ),
    (
        "10-domain-analysis-sql-access-mcp.md",
        "Domain: analysis, access, SQL, MCP (Phần AB)",
        14259,
        16758,
    ),
    (
        "11-bo-sung-domain-data-dictionary-luong.md",
        "Bổ sung domain, data dictionary, luồng E2E",
        16761,
        17645,
    ),
    (
        "12-contracts-pydantic.md",
        "Hợp đồng Pydantic (§AH.1)",
        17646,
        24387,
    ),
    (
        "13-chat-gateway-orchestrator.md",
        "ChatOrchestrator và gateway (§Z.4)",
        24389,
        26416,
    ),
    (
        "14-bien-moi-truong.md",
        "Biến môi trường (khái quát + chi tiết)",
        417,
        458,  # J stub — merged below with detail
    ),
    (
        "14-bien-moi-truong-chi-tiet.md",
        "Biến môi trường chi tiết (§J.1)",
        26417,
        28212,
    ),
    (
        "15-cau-hinh-yaml.md",
        "Cấu hình YAML (tổng quan)",
        387,
        416,
    ),
    (
        "15-cau-hinh-chi-tiet.md",
        "Cấu hình chi tiết (project, models, platform)",
        29184,
        29692,
    ),
    (
        "16-libs-framework-chi-tiet.md",
        "Libs framework chi tiết (§AP)",
        28213,
        29183,
    ),
    (
        "17-kiem-thu.md",
        "Kiểm thử (tổng quan + project-test)",
        647,
        656,
    ),
    (
        "17-kiem-thu-chi-tiet.md",
        "Kiểm thử chi tiết (§W.1)",
        29693,
        30305,
    ),
    (
        "18-data-dictionary-tong-quan.md",
        "Data dictionary (mục lục bảng)",
        657,
        664,
    ),
    (
        "18-scripts-van-hanh.md",
        "Scripts vận hành (tổng quan)",
        665,
        678,
    ),
    (
        "18-scripts-chi-tiet.md",
        "Scripts chi tiết (§Y.1)",
        30306,
        999999,
    ),
]

README_SECTIONS = [
    ("01-gioi-thieu-va-kien-truc.md", "Giới thiệu, actor, kiến trúc tổng thể"),
    ("02-monorepo-va-cau-truc-thu-muc.md", "uv workspace, cây thư mục repo"),
    ("03-libs-va-project-core-tong-quan.md", "libs/* và packages/project-core (overview)"),
    ("04-agents-va-mcp-tong-quan.md", "Agents I–IV, sql-gateway, python-sandbox"),
    ("05-database-auth-va-session.md", "AUTH DB, analytics db1/db2, Redis, RBAC"),
    ("06-pipeline-va-luong-agent.md", "SupermarketAnalysisPipeline, modes từng agent"),
    ("07-trien-khai-docker.md", "docker-compose, prod, Caddy"),
    ("08-ma-nguon-agents-chat-gateway.md", "Source walkthrough: service.py, app, auth, clients"),
    ("09-pipeline-tung-dong.md", "pipeline.py line-by-line (§Z.3)"),
    ("10-domain-analysis-sql-access-mcp.md", "decomposer, policy_engine, iv_analyzer, tools_impl"),
    ("11-bo-sung-domain-data-dictionary-luong.md", "execution_composer, bảng STRANS/PMTRANS, sơ đồ E2E"),
    ("12-contracts-pydantic.md", "Toàn bộ Pydantic contracts"),
    ("13-chat-gateway-orchestrator.md", "orchestrator.py, app.py, auth flow"),
    ("14-bien-moi-truong.md", "Biến môi trường — tóm tắt"),
    ("14-bien-moi-truong-chi-tiet.md", "Từng biến .env — prod/dev, compose"),
    ("15-cau-hinh-yaml.md", "config/project.yaml, models, platform (tóm tắt)"),
    ("15-cau-hinh-chi-tiet.md", "Mọi khóa YAML chi tiết"),
    ("16-libs-framework-chi-tiet.md", "platform-core, agent-core, mcp-core"),
    ("17-kiem-thu.md", "Tests — tổng quan"),
    ("17-kiem-thu-chi-tiet.md", "project-test từng file"),
    ("18-data-dictionary-tong-quan.md", "Data dictionary — mục lục"),
    ("18-scripts-van-hanh.md", "Scripts — tổng quan"),
    ("18-scripts-chi-tiet.md", "scripts/ từng file"),
]


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing source: {SRC}")

    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    total = len(lines)
    OUT.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for filename, title, start, end in SPLITS:
        end = min(end, total)
        if start > total:
            continue
        body = "".join(lines[start - 1 : end])
        header = (
            f"# {title}\n\n"
            f"Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) "
            f"(dòng {start}–{end}).\n\n"
            f"← [Mục lục docs2](README.md)\n\n---\n\n"
        )
        path = OUT / filename
        path.write_text(header + body, encoding="utf-8")
        written.append(filename)

    # README
    readme_lines = [
        "# Tài liệu vận hành Monorepo-Trading-Agent (docs2)\n",
        "\n",
        "Bộ tài liệu được **tách theo chủ đề** từ file gốc "
        "[`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) "
        "để dễ đọc và tra cứu.\n",
        "\n",
        "**Phiên bản:** 1.0 — cùng nội dung với tài liệu gốc, chỉ phân mảnh.\n",
        "\n",
        "---\n",
        "\n",
        "## Mục lục theo chủ đề\n",
        "\n",
        "| # | Tệp | Nội dung |\n",
        "|---|-----|----------|\n",
    ]
    for i, (fname, desc) in enumerate(README_SECTIONS, 1):
        readme_lines.append(f"| {i} | [{fname}]({fname}) | {desc} |\n")

    readme_lines.extend(
        [
            "\n",
            "---\n",
            "\n",
            "## Gợi ý đọc theo vai trò\n",
            "\n",
            "| Vai trò | Đọc trước |\n",
            "|---------|----------|\n",
            "| Dev mới | 01 → 02 → 04 → 06 |\n",
            "| Backend / pipeline | 06 → 09 → 10 → 12 |\n",
            "| Gateway / auth | 05 → 13 → 14 |\n",
            "| DevOps | 07 → 14 → 18 |\n",
            "| QA | 17 |\n",
            "\n",
            "---\n",
            "\n",
            f"*Sinh bởi `scripts/split_docs_to_docs2.py` — {len(written)} tệp, nguồn {total} dòng.*\n",
        ]
    )
    (OUT / "README.md").write_text("".join(readme_lines), encoding="utf-8")
    print(f"Wrote {len(written)} files + README to {OUT}")


if __name__ == "__main__":
    main()
