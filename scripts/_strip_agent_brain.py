#!/usr/bin/env python3
"""One-shot strip of agent-brain substitutes."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch_service() -> None:
    p = ROOT / "agents/data-agent/src/data_agent/service.py"
    text = p.read_text(encoding="utf-8")

    # Soften clarify hint
    start = text.find('"hint": (\n                                "product_codes already select SKUs')
    if start < 0:
        raise SystemExit("clarify hint not found")
    end = text.find("),\n                        }\n                    )\n                    _audit_turn", start)
    if end < 0:
        raise SystemExit("clarify hint end not found")
    text = (
        text[:start]
        + '"hint": (\n'
        '                                "product_codes already select SKUs — skip soft "\n'
        '                                "product_type / ITEM_TYPE / display-name clarify; "\n'
        '                                "continue with fetch/ops using those identities."\n'
        "                            )"
        + text[end:]
    )

    # Rewrite _args_from_hints query/export/op sections by marker replacement
    old_args_marker = '        if tool_id in {"query_rows", "preview_table", "aggregate_rows", "lookup_distinct"}:'
    new_query = '''        if tool_id in {"query_rows", "preview_table", "aggregate_rows", "lookup_distinct"}:
            # Coerce shapes only — do not invent table/path for the agent.
            table_hint = hints.get("table")
            if not isinstance(table_hint, str) or looks_like_prose_placeholder(table_hint):
                table_hint = None
            limit_raw = hints.get("limit")
            if not isinstance(limit_raw, int) or limit_raw <= 0:
                limit_raw = 5000 if tool_id == "query_rows" else 30

            args: dict[str, Any] = {
                "time_range": coerce_time_range(
                    hints.get("time_range"),
                    fallback=tr if isinstance(tr, dict) else None,
                ),
                "limit": limit_raw,
            }
            if table_hint:
                args["table"] = coerce_table_name(table_hint, fallback=table_hint)
            else:
                # Fail closed at execute if missing; do not pick STRANS/TRANSHDR for the agent.
                args["table"] = ""

            cleaned_filters = sanitize_filter_clauses(hints.get("filters"))
            if checklist.get("min_bill_value") is not None:
                cleaned_filters = [
                    c
                    for c in cleaned_filters
                    if str(c.get("column") or "").strip().upper()
                    not in {"BILL_AMT", "BILL_AMOUNT", "BILL_VALUE", "TOTAL_AMT", "TOTAL_AMOUNT"}
                ]
            if cleaned_filters:
                args["filters"] = cleaned_filters

            # Brief value sugar only when agent already targeted TRANSHDR.
            if checklist.get("min_bill_value") is not None and str(args.get("table", "")).upper() == "TRANSHDR":
                args["min_amount"] = checklist["min_bill_value"]

            # Honor agent-named dataset refs / id lists only — no auto-injection.
            table_u = str(args.get("table", "")).upper()
            sku_capable = table_u in {"STRANS", "PMTRANS"} or table_u.startswith("STRANS_") or table_u.startswith("PMTRANS_")
            if sku_capable:
                sku_hint = hints.get("sku_ids")
                if isinstance(sku_hint, str) and sku_hint in known_refs:
                    args["sku_ids"] = sku_hint
                elif isinstance(sku_hint, list) and sku_hint and not any(looks_like_prose_placeholder(x) for x in sku_hint):
                    args["sku_ids"] = sku_hint

            trans_hint = hints.get("trans_nums")
            if isinstance(trans_hint, str) and trans_hint in known_refs:
                args["trans_nums"] = trans_hint
            elif isinstance(trans_hint, list) and trans_hint and not any(looks_like_prose_placeholder(x) for x in trans_hint):
                args["trans_nums"] = trans_hint

            if tool_id == "aggregate_rows":
                aggs = hints.get("aggs")
                if isinstance(aggs, list) and aggs:
                    args["aggs"] = aggs
                if isinstance(hints.get("group_by"), list):
                    args["group_by"] = hints["group_by"]

            if tool_id == "lookup_distinct":
                col = hints.get("column")
                if isinstance(col, str) and col.strip() and not looks_like_prose_placeholder(col):
                    args["column"] = col

            save_raw = hints.get("save_as")
            if isinstance(save_raw, str) and save_raw.strip() and not looks_like_prose_placeholder(save_raw):
                args["save_as"] = save_raw
            return args
'''

    i = text.find(old_args_marker)
    if i < 0:
        raise SystemExit("query_rows block not found")
    j = text.find('        if tool_id == "export_excel":', i)
    if j < 0:
        raise SystemExit("export_excel block not found")
    text = text[:i] + new_query + text[j:]

    new_export = '''        if tool_id == "export_excel":
            refs = known_refs
            filename = hints.get("filename") or "analysis_result.xlsx"
            raw_sheets = hints.get("sheets") or hints.get("sheet_map") or hints.get("workbook")
            if isinstance(raw_sheets, dict) and raw_sheets:
                cleaned_sheets: dict[str, str] = {}
                for sheet_name, ref in raw_sheets.items():
                    if not isinstance(ref, str) or looks_like_prose_placeholder(ref):
                        continue
                    if refs and ref not in refs:
                        continue
                    if not working_set.has(ref):
                        continue
                    cleaned_sheets[str(sheet_name)] = ref
                if cleaned_sheets:
                    return {"sheets": cleaned_sheets, "filename": filename}

            dataset = hints.get("dataset")
            if not isinstance(dataset, str) or looks_like_prose_placeholder(dataset):
                dataset = None
            elif refs and dataset not in refs and not working_set.has(dataset):
                dataset = None
            return {"dataset": dataset, "filename": filename}

'''
    i = text.find('        if tool_id == "export_excel":')
    j = text.find('        if tool_id in {"filter_rows", "top_n_per_group", "join_datasets", "groupby_agg", "select_columns"}:', i)
    if i < 0 or j < 0:
        raise SystemExit("export/filter markers missing")
    text = text[:i] + new_export + text[j:]

    # Remove companion left rewrite and prefer_export dataset injection in op args
    old_ops = '''        if tool_id in {"filter_rows", "top_n_per_group", "join_datasets", "groupby_agg", "select_columns"}:
            args = {k: v for k, v in hints.items() if not looks_like_prose_placeholder(v)}
            if "dataset" not in args and known_refs:
                needs_bill = bool(
                    checklist.get("needs_bill")
                    or needs_bill_deliverable(brief)
                    or checklist.get("min_bill_value") is not None
                )
                args["dataset"] = prefer_export_dataset_ref(
                    working_set,
                    needs_bill=needs_bill,
                    product_codes=list(checklist.get("product_codes") or []),
                ) or known_refs[-1]
            elif isinstance(args.get("dataset"), str) and args["dataset"] not in known_refs and known_refs:
                args["dataset"] = known_refs[-1]
            if tool_id == "join_datasets":
                # Prefer companion bill-line frames over product-only left inputs.
                left = str(args.get("left") or args.get("left_dataset") or "").strip()
                if left and working_set.has(left):
                    companion = f"{left}_all_bill_lines"
                    if working_set.has(companion):
                        args["left"] = companion
                        args.pop("left_dataset", None)
'''
    # Find more flexibly
    i = text.find('        if tool_id in {"filter_rows", "top_n_per_group", "join_datasets", "groupby_agg", "select_columns"}:')
    if i < 0:
        raise SystemExit("ops block missing")
    # Replace prefer_export injection inside this block
    text2 = text[i:]
    # Remove needs_bill prefer_export for missing dataset
    text2 = text2.replace(
        '''            if "dataset" not in args and known_refs:
                needs_bill = bool(
                    checklist.get("needs_bill")
                    or needs_bill_deliverable(brief)
                    or checklist.get("min_bill_value") is not None
                )
                args["dataset"] = prefer_export_dataset_ref(
                    working_set,
                    needs_bill=needs_bill,
                    product_codes=list(checklist.get("product_codes") or []),
                ) or known_refs[-1]
            elif isinstance(args.get("dataset"), str) and args["dataset"] not in known_refs and known_refs:
                args["dataset"] = known_refs[-1]
            if tool_id == "join_datasets":
                # Prefer companion bill-line frames over product-only left inputs.
                left = str(args.get("left") or args.get("left_dataset") or "").strip()
                if left and working_set.has(left):
                    companion = f"{left}_all_bill_lines"
                    if working_set.has(companion):
                        args["left"] = companion
                        args.pop("left_dataset", None)
''',
        '''            # Do not invent dataset/left for the agent — only drop prose.
            if isinstance(args.get("dataset"), str) and args["dataset"] not in known_refs and known_refs:
                # Keep agent string; toolkit/op will fail closed if missing.
                pass
''',
        1,
    )
    text = text[:i] + text2

    # _execute_tool: blocked export returns error, no swap
    old_blocked = '''                if blocked:
                    preferred = prefer_export_dataset_ref(
                        working_set,
                        needs_bill=bool(
                            checklist.get("needs_bill")
                            or needs_bill_deliverable(brief)
                            or checklist.get("min_bill_value") is not None
                        ),
                        product_codes=list(checklist.get("product_codes") or []),
                    )
                    if preferred:
                        args = {
                            "dataset": preferred,
                            "filename": args.get("filename") or "analysis_result.xlsx",
                        }
                    else:
'''
    if old_blocked not in text:
        # try alternate with sheets
        raise SystemExit("blocked swap block not found exactly — check manually")
    # Actually replace whole if blocked block with return error
    i = text.find("                if blocked:")
    # Find the execute_op for export after blocked handling - better read approach
    # Simpler: replace prefer swap with return blocked observation
    # Find from "if blocked:" to next "export =" or "result = execute_op"
    
    # Use a different approach - replace the preferred swap body
    text = text.replace(
        old_blocked,
        '''                if blocked:
                    return {
                        "ok": False,
                        "error": blocked,
                        "op_id": "export_excel",
                        "hint": "export blocked as premature for current checklist; pick a bill/ranked frame",
                    }
                    if False:
''',
        1,
    )

    # Simplify _finalize to coverage-only
    fin = text.find("    def _finalize(")
    if fin < 0:
        raise SystemExit("_finalize not found")
    # Find next method after _finalize - ToolSelectorFallback or similar
    next_m = text.find("\nclass ", fin + 1)
    if next_m < 0:
        next_m = text.find("\ndef ", fin + 400)
    # Find end of _finalize by locating "return {" near end of method before class
    # Actually locate ToolSelectorFallback
    next_class = text.find("class ToolSelectorFallback", fin)
    if next_class < 0:
        raise SystemExit("ToolSelectorFallback not found")
    # Walk back to start of that class's preceding content - _finalize ends before it
    # There may be helpers between - check
    between = text[fin:next_class]
    # Replace entire _finalize method
    new_finalize = '''    def _finalize(
        self,
        brief: AnalysisBrief,
        checklist: dict[str, Any],
        working_set: DatasetWorkingSet,
        observations: list[dict[str, Any]],
        steps_trace: list[dict[str, Any]],
        stages_trail: list[dict[str, Any]],
        tokens: int,
        chunk: dict[str, Any],
    ) -> dict[str, Any]:
        """Score what the agent already produced — never join/rank/export for it."""
        codes = list(checklist.get("product_codes") or [])
        arts = list(working_set.artifact_paths)
        coverage = assess_deliverable_coverage(
            brief,
            working_set,
            product_codes=codes,
            top_n=checklist.get("top_n"),
        )
        caveats = as_str_list(chunk.get("caveats"))
        caveats.extend(as_str_list(coverage.get("caveats") if coverage else None))
        caveats.extend(as_str_list(coverage.get("gaps") if coverage else None))
        status = str(chunk.get("status") or "complete")
        action = "complete" if status == "complete" and arts else "partial"
        if coverage_forces_partial(list(coverage.get("gaps") or [])):
            action = "partial"
        tool_chain: list[dict[str, Any]] = []
        for o in observations:
            if not o.get("ok"):
                continue
            if o.get("tool_id"):
                tool_chain.append(
                    {
                        "kind": "fetch",
                        "server": "data-query" if o.get("tool_id") != "resolve_products" else "product-lookup",
                        "tool_id": o.get("tool_id"),
                        "args": (o.get("lineage") or {}).get("params") or {},
                        "save_as": o.get("save_as"),
                    }
                )
            elif o.get("op_id"):
                tool_chain.append(
                    {
                        "kind": "op",
                        "server": "deliverables" if str(o.get("op_id")).startswith("export") or o.get("op_id") == "plot_chart" else "dataframe-ops",
                        "tool_id": o.get("op_id"),
                        "args": o.get("args") or {},
                    }
                )
        return {
            "action": action,
            "insight_vi": chunk.get("insight_vi") or chunk.get("explanation_vi") or "",
            "headline_metrics": chunk.get("headline_metrics") or {},
            "caveats": caveats,
            "artifact_paths": arts,
            "excel_artifacts": list(working_set.excel_artifacts),
            "chart_artifacts": list(working_set.chart_artifacts),
            "coverage": coverage,
            "steps_trace": steps_trace,
            "stages": stages_trail,
            "observations": observations,
            "usage_tokens": tokens,
            "tool_chain": tool_chain,
            "checklist": checklist,
        }

'''
    text = text[:fin] + new_finalize + text[next_class:]

    # Clean unused imports
    for unused in [
        "ensure_bill_customer_join,\n    ",
        "is_partitioned_top_n_ref,\n    ",
        "prefer_export_dataset_ref,\n    ",
        "rank_bill_frame_for_export,\n    ",
        "resolved_sku_ids_from_working_set,\n    ",
    ]:
        text = text.replace(unused, "")
    # may still need prefer/is_blocked for other code - check
    if "prefer_export_dataset_ref" in text or "is_blocked_premature_export" in text:
        # re-add if still referenced
        if "prefer_export_dataset_ref" in text and "prefer_export_dataset_ref," not in text.split("from project_core.domain.analysis.data_agent_guards import")[1][:800]:
            text = text.replace(
                "needs_bill_deliverable,\n",
                "needs_bill_deliverable,\n    prefer_export_dataset_ref,\n",
                1,
            )
        if "is_blocked_premature_export" in text and "is_blocked_premature_export," not in text.split("from project_core.domain.analysis.data_agent_guards import")[1][:800]:
            text = text.replace(
                "infer_top_n,\n",
                "infer_top_n,\n    is_blocked_premature_export,\n",
                1,
            )

    # Remove unused vars in _args_from_hints
    text = text.replace(
        '''        known_refs = list(working_set.refs())
        has_product_ref = any(
            "resolv" in r.lower() or "product" in r.lower() for r in known_refs
        )
        has_line_ref = any(
            "strans" in r.lower() or "line" in r.lower() or "bill_lines" in r.lower()
            for r in known_refs
        )
''',
        "        known_refs = list(working_set.refs())\n",
        1,
    )

    p.write_text(text, encoding="utf-8")
    print("patched", p)


def patch_guards() -> None:
    p = ROOT / "packages/project-core/src/project_core/domain/analysis/data_agent_guards.py"
    text = p.read_text(encoding="utf-8")
    old = '''    filters = brief.filters or {}
    if any(
        str(filters.get(k) or "").strip()
        for k in ("product_name", "product_code", "name_contains")
    ):
        return True
    for item in _brief_deliverable_items(brief):'''
    new = '''    # Product filters alone do not imply bill grain — agent chooses the path.
    for item in _brief_deliverable_items(brief):'''
    if old not in text:
        raise SystemExit("needs_bill product-filter block not found")
    text = text.replace(old, new, 1)

    # Soften needs_customer_profile intent keyword sniffing — keep grain dims only
    old_c = '''    intent = str(getattr(brief, "intent", "") or "").lower()
    if any(
        tok in intent
        for tok in ("customer", "khách", "thẻ", "sdt", "sđt", "phone", "card", "tên khách")
    ):
        return True
    for item in _brief_deliverable_items(brief):'''
    new_c = '''    for item in _brief_deliverable_items(brief):'''
    if old_c not in text:
        raise SystemExit("needs_customer intent block not found")
    text = text.replace(old_c, new_c, 1)
    p.write_text(text, encoding="utf-8")
    print("patched", p)


def patch_toolkit() -> None:
    p = ROOT / "packages/project-core/src/project_core/domain/data_fetch/toolkit.py"
    text = p.read_text(encoding="utf-8")
    marker = "        # After a product-SKU line fetch, also materialize *all* lines on those bills."
    i = text.find(marker)
    if i < 0:
        raise SystemExit("companion expand marker not found")
    j = text.find("        return payload\n\n    def _route_targets(", i)
    if j < 0:
        raise SystemExit("companion expand end not found")
    text = text[:i] + "        return payload\n\n    def _route_targets(" + text[j + len("        return payload\n\n    def _route_targets(") :]
    # Fix double return
    # Actually the slice might be wrong. Let me do cleaner:
    text = p.read_text(encoding="utf-8")
    i = text.find(marker)
    j = text.find("\n        return payload\n\n    def _route_targets(", i)
    if i < 0 or j < 0:
        raise SystemExit("companion markers fail")
    text = text[:i] + text[j + 1 :]  # keep "        return payload\n\n    def _route_targets..."
    p.write_text(text, encoding="utf-8")
    print("patched", p)


def patch_brain() -> None:
    p = ROOT / "packages/project-core/src/project_core/domain/analysis/data_agent_brain.py"
    text = p.read_text(encoding="utf-8")
    # Remove auto export on budget block
    marker = "    # Best-effort export so partial runs still leave deliverables when data exists."
    i = text.find(marker)
    if i < 0:
        print("brain budget export already gone?")
    else:
        j = text.find("    coverage = assess_deliverable_coverage(", i)
        if j < 0:
            raise SystemExit("brain coverage after budget not found")
        text = text[:i] + text[j:]

    # Remove finalize auto join+export when no arts
    old = '''                arts = list(working_set.artifact_paths)
                if not arts and working_set.refs():
                    codes = list(checklist.get("product_codes") or [])
                    joined_ref = ensure_bill_customer_join(
                        working_set,
                        out_dir=out_dir,
                        product_codes=codes,
                    )
                    ref0 = joined_ref or prefer_export_dataset_ref(
                        working_set,
                        needs_bill=_needs_bill_deliverable(brief),
                        product_codes=codes,
                    )
                    if ref0:
                        execute_op(
                            working_set,
                            "export_excel",
                            {"dataset": ref0, "filename": "analysis_result.xlsx"},
                            out_dir=out_dir,
                        )
                        arts = list(working_set.artifact_paths)
                coverage = assess_deliverable_coverage('''
    new = '''                arts = list(working_set.artifact_paths)
                coverage = assess_deliverable_coverage('''
    if old in text:
        text = text.replace(old, new, 1)
    else:
        print("brain finalize auto-export block not exact — searching alternate")
        if "ensure_bill_customer_join" in text:
            print("WARNING: ensure_bill_customer_join still referenced in brain")

    # Remove other ensure_bill_customer_join usages if present
    # Keep prefer_export only for hints in stub if stub still uses it under ALLOW_LLM_STUB

    p.write_text(text, encoding="utf-8")
    print("patched", p)


def patch_skills() -> None:
    guide = ROOT / "agents/data-agent/src/data_agent/skills/data_agent/prompts/chunk_guide.md"
    text = guide.read_text(encoding="utf-8")
    text = """# Next chunk guide

Given brief + checklist + recent observations, choose ONE next chunk_goal.

You are the planner. Tools and observations are hints — do not assume a fixed path.

Examples of chunk_goal phrasing (optional, not mandatory):
- Resolve product identity from the brief
- Fetch fact rows for the chosen table/grain in time_range
- Aggregate / rank / join working-set frames as needed
- Export the frame that answers the brief, then finalize

Rules:
1. Call `export_excel` before `finalize` when a deliverable is ready.
2. Do not finalize with only a catalog/resolve frame when the brief needs fact rows you have not fetched.
3. Prefer tools that match the brief grain; observations and coverage gaps are feedback, not recipes.
"""
    guide.write_text(text, encoding="utf-8")
    print("patched", guide)

    tools = ROOT / "agents/data-agent/src/data_agent/skills/data_agent/TOOLS.md"
    t = tools.read_text(encoding="utf-8")
    t = t.replace(
        """- **`export_excel`**: call **before** `finalize`. Export the preferred analytical
  frame for the brief (ranked top-N, bill lines, aggregate — whichever matches).
  Optional multi-sheet maps are fine when the planner names distinct frames;
  do not invent fixed sheet/file recipes. Do not re-slice a correct per-group
  ranked dataset to N global rows.""",
        """- **`export_excel`**: call **before** `finalize` on the frame you chose.
  Optional multi-sheet maps are allowed when you name distinct existing refs.
  Do not re-slice a correct per-group ranked dataset to N global rows.""",
    )
    tools.write_text(t, encoding="utf-8")
    print("patched", tools)


def main() -> None:
    patch_service()
    patch_guards()
    patch_toolkit()
    patch_brain()
    patch_skills()
    print("done")


if __name__ == "__main__":
    main()
