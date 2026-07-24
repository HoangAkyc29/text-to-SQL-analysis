from pathlib import Path

servers = {
    "product-lookup": ("product_lookup", "Product / SKU lookup MCP", ["resolve_products"]),
    "data-query": (
        "data_query",
        "Flexible parameterized SQL query MCP",
        ["preview_table", "query_rows", "aggregate_rows", "lookup_distinct"],
    ),
    "dataframe-ops": (
        "dataframe_ops",
        "Working-set dataframe ops MCP",
        [
            "list_datasets",
            "filter_rows",
            "groupby_agg",
            "join_datasets",
            "head_rows",
            "select_columns",
            "sort_rows",
            "limit_rows",
            "top_n_per_group",
            "describe_columns",
            "value_counts",
        ],
    ),
    "deliverables": (
        "deliverables",
        "Export / chart deliverables MCP",
        [
            "export_excel",
            "export_csv",
            "plot_chart",
            "bundle_deliverables",
            "inspect_excel",
            "validate_export",
        ],
    ),
}

for name, (pkg, desc, tools) in servers.items():
    root = Path("mcp-servers") / name
    src = root / "src" / pkg
    skills = root / "skills"
    src.mkdir(parents=True, exist_ok=True)
    skills.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text(
        f"""[project]
name = "{name}"
version = "0.1.0"
description = "{desc}"
requires-python = ">=3.11"
dependencies = [
    "mcp-core",
    "project-core",
    "pandas>=2.0",
    "pyarrow>=14",
]

[project.scripts]
{name} = "{pkg}.app:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{pkg}"]

[tool.hatch.metadata]
allow-direct-references = true
""",
        encoding="utf-8",
    )
    (src / "__init__.py").write_text('"""MCP server package."""\n', encoding="utf-8")
    (root / "README.md").write_text(
        f"# {name}\n\n{desc}\n\nTransport: stdio (MCP).\n",
        encoding="utf-8",
    )
    for t in tools:
        (skills / f"{t}.md").write_text(
            f"""# Tool: `{t}`

## Purpose
Parameterized handler — agent never authors SQL / free pandas scripts beyond catalog ops.

## Notes
- Values come from brief/chunk goals, never hardcoded business recipes in this skill.
- Fact tables require `time_range` when applicable.
""",
            encoding="utf-8",
        )
print("ok", list(servers))
