# Tài liệu vận hành Monorepo-Trading-Agent (docs2)

Bộ tài liệu được **tách theo chủ đề** từ file gốc [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) để dễ đọc và tra cứu.

**Phiên bản:** 1.0 — cùng nội dung với tài liệu gốc, chỉ phân mảnh.

---

## Tài liệu thiết kế mục tiêu (đọc trước khi refactor)

| Tệp | Nội dung |
|-----|----------|
| [00-THIET-KE-HE-AGENT-MUC-TIEU.md](00-THIET-KE-HE-AGENT-MUC-TIEU.md) | **Thiết kế should-have** của hệ multi-agent: reasoning loop, clarify loop, phân quyền tool, bảo mật, và **16 sơ đồ Mermaid**. Chuẩn để refactor Agent IV. |

---

## Mục lục theo chủ đề

| # | Tệp | Nội dung |
|---|-----|----------|
| 1 | [01-gioi-thieu-va-kien-truc.md](01-gioi-thieu-va-kien-truc.md) | Giới thiệu, actor, kiến trúc tổng thể |
| 2 | [02-monorepo-va-cau-truc-thu-muc.md](02-monorepo-va-cau-truc-thu-muc.md) | uv workspace, cây thư mục repo |
| 3 | [03-libs-va-project-core-tong-quan.md](03-libs-va-project-core-tong-quan.md) | libs/* và packages/project-core (overview) |
| 4 | [04-agents-va-mcp-tong-quan.md](04-agents-va-mcp-tong-quan.md) | Agents I–IV, sql-gateway, python-sandbox |
| 5 | [05-database-auth-va-session.md](05-database-auth-va-session.md) | AUTH DB, analytics db1/db2, Redis, RBAC |
| 6 | [06-pipeline-va-luong-agent.md](06-pipeline-va-luong-agent.md) | SupermarketAnalysisPipeline, modes từng agent |
| 7 | [07-trien-khai-docker.md](07-trien-khai-docker.md) | docker-compose, prod, Caddy |
| 8 | [08-ma-nguon-agents-chat-gateway.md](08-ma-nguon-agents-chat-gateway.md) | Source walkthrough: service.py, app, auth, clients |
| 9 | [09-pipeline-tung-dong.md](09-pipeline-tung-dong.md) | pipeline.py line-by-line (§Z.3) |
| 10 | [10-domain-analysis-sql-access-mcp.md](10-domain-analysis-sql-access-mcp.md) | decomposer, policy_engine, iv_analyzer, tools_impl |
| 11 | [11-bo-sung-domain-data-dictionary-luong.md](11-bo-sung-domain-data-dictionary-luong.md) | execution_composer, bảng STRANS/PMTRANS, sơ đồ E2E |
| 12 | [12-contracts-pydantic.md](12-contracts-pydantic.md) | Toàn bộ Pydantic contracts |
| 13 | [13-chat-gateway-orchestrator.md](13-chat-gateway-orchestrator.md) | orchestrator.py, app.py, auth flow |
| 14 | [14-bien-moi-truong.md](14-bien-moi-truong.md) | Biến môi trường — tóm tắt |
| 15 | [14-bien-moi-truong-chi-tiet.md](14-bien-moi-truong-chi-tiet.md) | Từng biến .env — prod/dev, compose |
| 16 | [15-cau-hinh-yaml.md](15-cau-hinh-yaml.md) | config/project.yaml, models, platform (tóm tắt) |
| 17 | [15-cau-hinh-chi-tiet.md](15-cau-hinh-chi-tiet.md) | Mọi khóa YAML chi tiết |
| 18 | [16-libs-framework-chi-tiet.md](16-libs-framework-chi-tiet.md) | platform-core, agent-core, mcp-core |
| 19 | [17-kiem-thu.md](17-kiem-thu.md) | Tests — tổng quan |
| 20 | [17-kiem-thu-chi-tiet.md](17-kiem-thu-chi-tiet.md) | project-test từng file |
| 21 | [18-data-dictionary-tong-quan.md](18-data-dictionary-tong-quan.md) | Data dictionary — mục lục |
| 22 | [18-scripts-van-hanh.md](18-scripts-van-hanh.md) | Scripts — tổng quan |
| 23 | [18-scripts-chi-tiet.md](18-scripts-chi-tiet.md) | scripts/ từng file |

---

## Gợi ý đọc theo vai trò

| Vai trò | Đọc trước |
|---------|----------|
| Dev mới | 01 → 02 → 04 → 06 |
| Backend / pipeline | 06 → 09 → 10 → 12 |
| Gateway / auth | 05 → 13 → 14 |
| DevOps | 07 → 14 → 18 |
| QA | 17 |

---

*Sinh bởi `scripts/split_docs_to_docs2.py` — 23 tệp, nguồn 30691 dòng.*
