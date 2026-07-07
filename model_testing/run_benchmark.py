"""Benchmark OpenRouter models: Vietnamese text + vision image understanding.

Usage (from repo root):
    uv run --package python-sandbox python model_testing/run_benchmark.py
    uv run --package python-sandbox python model_testing/run_benchmark.py --models mimo,gemini,4o
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
RESULTS = Path(__file__).resolve().parent / "results"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class ModelSpec:
    key: str
    model_id: str
    vision: bool = True
    note: str = ""


MODEL_CATALOG: dict[str, ModelSpec] = {
    "mimo": ModelSpec("mimo", "xiaomi/mimo-v2.5", True, "Default trong config/models.yaml"),
    "gemini25flash": ModelSpec("gemini25flash", "google/gemini-2.5-flash", True, "Gemini 2.5 Flash"),
    "gemini20flash": ModelSpec("gemini20flash", "google/gemini-2.0-flash-exp:free", True, "Gemini 2.0 Flash (free tier)"),
    "gpt4o_mini": ModelSpec("gpt4o_mini", "openai/gpt-4o-mini", True, "OpenAI vision nhẹ"),
    "claude35haiku": ModelSpec("claude35haiku", "anthropic/claude-3-5-haiku-20241022", True, "Claude 3.5 Haiku"),
    "qwen_vl": ModelSpec("qwen_vl", "qwen/qwen2.5-vl-72b-instruct", True, "Vision chuyên dụng"),
    "llama33": ModelSpec("llama33", "meta-llama/llama-3.3-70b-instruct", False, "Text-only baseline"),
    "qwen72": ModelSpec("qwen72", "qwen/qwen-2.5-72b-instruct", False, "Text-only Qwen"),
}


@dataclass
class TestResult:
    model_key: str
    model_id: str
    test_id: str
    ok: bool
    score: float
    max_score: float
    latency_ms: int
    error: str | None = None
    response_preview: str = ""
    details: dict[str, Any] = field(default_factory=dict)


def load_api_key() -> str:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    key = os.getenv("OPENROUTER_API_KEY") or os.getenv("openroute_api_key")
    if not key:
        raise RuntimeError("Thiếu OPENROUTER_API_KEY trong .env hoặc môi trường")
    return key


def image_data_url(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def chat(
    *,
    api_key: str,
    model_id: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 1024,
    temperature: float = 0.2,
    timeout: float = 120.0,
) -> tuple[str, int, dict[str, Any]]:
    payload = {
        "model": model_id,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    t0 = time.perf_counter()
    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/supermarket-analysis-agent",
            "X-Title": "model_testing benchmark",
        },
        json=payload,
        timeout=timeout,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    if not resp.ok:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:400]}")
    data = resp.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    return content, latency_ms, data


def extract_json_blob(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def score_vi_brief(content: str) -> tuple[float, float, dict[str, Any]]:
    """Parse Vietnamese analytics question into structured brief."""
    max_score = 5.0
    details: dict[str, Any] = {}
    parsed = extract_json_blob(content)
    if not parsed:
        return 0.0, max_score, {"reason": "json_parse_failed"}
    score = 0.0
    intent = str(parsed.get("intent") or "").lower()
    metrics = [str(m).lower() for m in (parsed.get("metrics") or [])]
    dims = [str(d).lower() for d in (parsed.get("dimensions") or [])]
    filters = parsed.get("filters") or {}
    if "vip" in intent or "vip" in str(filters).lower():
        score += 1.0
    if any("revenue" in m or "doanh" in m for m in metrics):
        score += 1.0
    if any("store" in d or "stk" in d or "cửa" in d for d in dims):
        score += 1.0
    tr = parsed.get("time_range") or {}
    if tr.get("grain") == "month" or "tháng" in intent:
        score += 1.0
    if parsed.get("output_format") and "chart" in [str(x).lower() for x in parsed.get("output_format")]:
        score += 1.0
    details.update({"parsed": parsed, "checks": "vip,revenue,store,month,chart"})
    return score, max_score, details


def score_vi_domain(content: str) -> tuple[float, float, dict[str, Any]]:
    max_score = 4.0
    text = content.lower()
    checks = {
        "trans_code_113": "113" in text and ("doanh" in text or "bán" in text or "revenue" in text),
        "store_filter": "stk" in text or "cửa hàng" in text or "10001" in text,
        "deny_cogs": "cogs" in text or "giá vốn" in text or "spprice" in text,
        "vietnamese": any(w in text for w in ("cửa", "doanh", "quyền", "bảng", "cột", "không")),
    }
    score = float(sum(1 for ok in checks.values() if ok))
    return score, max_score, {"checks": checks}


def score_vi_reasoning(content: str) -> tuple[float, float, dict[str, Any]]:
    max_score = 2.0
    text = content.replace(",", ".")
    # Doanh thu T1=120, T2=150, T3=90 -> TB = 120
    nums = [int(x) for x in re.findall(r"\b(120|150|90)\b", text)]
    has_avg = "120" in text
    has_formula = "trung bình" in content.lower() or "average" in content.lower() or "/" in text
    score = 0.0
    if has_avg:
        score += 1.0
    if has_formula or len(nums) >= 3:
        score += 1.0
    return score, max_score, {"has_avg_120": has_avg, "nums_found": nums}


def score_vision_chart(content: str) -> tuple[float, float, dict[str, Any]]:
    max_score = 5.0
    text = content.lower()
    expected = {"120", "150", "90"}
    found = set(re.findall(r"\b(120|150|90)\b", content))
    score = 0.0
    if len(found & expected) >= 3:
        score += 2.0
    elif len(found & expected) >= 2:
        score += 1.0
    if "tháng 1" in text or "thang 1" in text:
        score += 0.5
    if "tháng 2" in text or "thang 2" in text:
        score += 0.5
    if "tháng 3" in text or "thang 3" in text:
        score += 0.5
    if "150" in found and ("cao nhất" in text or "lớn nhất" in text or "max" in text):
        score += 0.5
    if any(x in text for x in ("không nhìn", "cannot see", "no image", "không thấy")):
        score = 0.0
    return score, max_score, {"numbers_found": sorted(found), "expected": sorted(expected)}


def score_vision_table(content: str) -> tuple[float, float, dict[str, Any]]:
    max_score = 4.0
    text = content.lower()
    checks = {
        "sku001": "sku-001" in text or "sku 001" in text,
        "sku002": "sku-002" in text or "sku 002" in text,
        "milk": "sữa" in text,
        "revenue_62": "62" in content,
        "revenue_45": "45" in content,
    }
    if any(x in text for x in ("không nhìn", "cannot see", "no image")):
        return 0.0, max_score, {"checks": checks, "refused": True}
    score = float(sum(1 for ok in checks.values() if ok))
    return score, max_score, {"checks": checks}


TEXT_TESTS = [
    (
        "vi_brief",
        "system",
        (
            "Bạn là Agent I của hệ phân tích siêu thị. Trả lời CHỈ bằng JSON hợp lệ, không markdown.\n"
            'Schema: {"intent","metrics","dimensions","filters","time_range":{"grain"},"output_format"}'
        ),
        (
            "User: So sánh doanh thu khách VIP tháng 5 và tháng 6 theo từng cửa hàng, "
            "vẽ biểu đồ cột. Cửa hàng 10001."
        ),
        score_vi_brief,
    ),
    (
        "vi_domain",
        "system",
        "Trả lời ngắn bằng tiếng Việt (3-5 câu). Giải thích cho quản lý cửa hàng.",
        (
            "Vì sao store_manager không được SELECT cột cogs từ STRANS? "
            "TRANS_CODE '113' nghĩa là gì? Họ chỉ xem được cửa 10001."
        ),
        score_vi_domain,
    ),
    (
        "vi_reasoning",
        "system",
        "Trả lời bằng tiếng Việt, nêu rõ phép tính.",
        (
            "Doanh thu 3 tháng lần lượt 120, 150 và 90 triệu đồng. "
            "Trung bình mỗi tháng là bao nhiêu?"
        ),
        score_vi_reasoning,
    ),
]

VISION_TESTS = [
    (
        "vision_chart",
        "chart_doanh_thu_vi.png",
        (
            "Ảnh là biểu đồ doanh thu siêu thị. Trả lời tiếng Việt:\n"
            "1) Ba giá trị doanh thu từng tháng (số triệu VND)\n"
            "2) Tháng nào cao nhất?\n"
            "Nếu không đọc được ảnh, nói rõ."
        ),
        score_vision_chart,
    ),
    (
        "vision_table",
        "table_sku_vi.png",
        (
            "Ảnh là bảng SKU. Trả lời tiếng Việt:\n"
            "Liệt kê mã SKU, tên hàng và doanh thu bạn đọc được.\n"
            "Nếu không đọc được ảnh, nói rõ."
        ),
        score_vision_table,
    ),
]


def run_text_test(api_key: str, spec: ModelSpec, test_id: str, system: str, user: str, scorer) -> TestResult:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    try:
        content, latency_ms, _raw = chat(api_key=api_key, model_id=spec.model_id, messages=messages)
        score, max_score, details = scorer(content)
        return TestResult(
            model_key=spec.key,
            model_id=spec.model_id,
            test_id=test_id,
            ok=score >= max_score * 0.6,
            score=score,
            max_score=max_score,
            latency_ms=latency_ms,
            response_preview=content[:500],
            details=details,
        )
    except Exception as exc:  # noqa: BLE001
        return TestResult(
            model_key=spec.key,
            model_id=spec.model_id,
            test_id=test_id,
            ok=False,
            score=0.0,
            max_score=1.0,
            latency_ms=0,
            error=str(exc),
        )


def run_vision_test(
    api_key: str, spec: ModelSpec, test_id: str, image_name: str, prompt: str, scorer
) -> TestResult:
    if not spec.vision:
        return TestResult(
            model_key=spec.key,
            model_id=spec.model_id,
            test_id=test_id,
            ok=False,
            score=0.0,
            max_score=1.0,
            latency_ms=0,
            error="model_marked_text_only",
        )
    path = FIXTURES / image_name
    if not path.exists():
        return TestResult(
            model_key=spec.key,
            model_id=spec.model_id,
            test_id=test_id,
            ok=False,
            score=0.0,
            max_score=1.0,
            latency_ms=0,
            error=f"missing_fixture:{image_name}",
        )
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_data_url(path)}},
            ],
        }
    ]
    try:
        content, latency_ms, _raw = chat(api_key=api_key, model_id=spec.model_id, messages=messages)
        score, max_score, details = scorer(content)
        return TestResult(
            model_key=spec.key,
            model_id=spec.model_id,
            test_id=test_id,
            ok=score >= max_score * 0.6,
            score=score,
            max_score=max_score,
            latency_ms=latency_ms,
            response_preview=content[:500],
            details=details,
        )
    except Exception as exc:  # noqa: BLE001
        return TestResult(
            model_key=spec.key,
            model_id=spec.model_id,
            test_id=test_id,
            ok=False,
            score=0.0,
            max_score=1.0,
            latency_ms=0,
            error=str(exc),
        )


def ensure_fixtures() -> None:
    from fixtures.generate_fixtures import chart_revenue_vi, table_sku_vi

    chart_revenue_vi()
    table_sku_vi()


def summarize(results: list[TestResult]) -> dict[str, Any]:
    by_model: dict[str, dict[str, Any]] = {}
    for r in results:
        bucket = by_model.setdefault(
            r.model_key,
            {"model_id": r.model_id, "text_score": 0.0, "text_max": 0.0, "vision_score": 0.0, "vision_max": 0.0, "errors": []},
        )
        if r.test_id.startswith("vi_"):
            bucket["text_score"] += r.score
            bucket["text_max"] += r.max_score
        elif r.test_id.startswith("vision_"):
            bucket["vision_score"] += r.score
            bucket["vision_max"] += r.max_score
        if r.error:
            bucket["errors"].append(f"{r.test_id}:{r.error}")
    for bucket in by_model.values():
        bucket["text_pct"] = round(100 * bucket["text_score"] / bucket["text_max"], 1) if bucket["text_max"] else 0
        bucket["vision_pct"] = round(100 * bucket["vision_score"] / bucket["vision_max"], 1) if bucket["vision_max"] else 0
        bucket["combined_pct"] = round(
            100 * (bucket["text_score"] + bucket["vision_score"]) / (bucket["text_max"] + bucket["vision_max"]),
            1,
        ) if (bucket["text_max"] + bucket["vision_max"]) else 0
    ranked = sorted(by_model.items(), key=lambda x: x[1]["combined_pct"], reverse=True)
    return {"by_model": dict(ranked), "ranking": [k for k, _ in ranked]}


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenRouter Vietnamese + vision benchmark")
    parser.add_argument(
        "--models",
        default="all",
        help="Comma keys from catalog or 'all' (default). Keys: " + ",".join(MODEL_CATALOG),
    )
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    ensure_fixtures()

    if args.models.strip().lower() == "all":
        selected = list(MODEL_CATALOG.values())
    else:
        keys = [k.strip() for k in args.models.split(",") if k.strip()]
        missing = [k for k in keys if k not in MODEL_CATALOG]
        if missing:
            raise SystemExit(f"Unknown model keys: {missing}. Available: {list(MODEL_CATALOG)}")
        selected = [MODEL_CATALOG[k] for k in keys]

    api_key = load_api_key()
    RESULTS.mkdir(parents=True, exist_ok=True)
    results: list[TestResult] = []

    print(f"Benchmark {len(selected)} models x {len(TEXT_TESTS)} text + {len(VISION_TESTS)} vision tests\n")

    for spec in selected:
        print(f"=== {spec.key} ({spec.model_id}) ===")
        for test_id, _role, system, user, scorer in TEXT_TESTS:
            r = run_text_test(api_key, spec, test_id, system, user, scorer)
            results.append(r)
            status = "OK" if r.ok else "FAIL"
            err = f" err={r.error}" if r.error else ""
            print(f"  [{status}] {test_id}: {r.score}/{r.max_score} ({r.latency_ms}ms){err}")
            time.sleep(0.5)

        for test_id, image_name, prompt, scorer in VISION_TESTS:
            r = run_vision_test(api_key, spec, test_id, image_name, prompt, scorer)
            results.append(r)
            status = "OK" if r.ok else "FAIL"
            err = f" err={r.error}" if r.error else ""
            print(f"  [{status}] {test_id}: {r.score}/{r.max_score} ({r.latency_ms}ms){err}")
            time.sleep(0.5)
        print()

    summary = summarize(results)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS / f"benchmark_{stamp}.json"
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "models_tested": [asdict(s) for s in selected],
        "results": [asdict(r) for r in results],
        "summary": summary,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {out_path}")
    print("\n=== RANKING (combined %) ===")
    for key in summary["ranking"]:
        row = summary["by_model"][key]
        print(
            f"  {key:12} text={row['text_pct']:5.1f}%  vision={row['vision_pct']:5.1f}%  "
            f"combined={row['combined_pct']:5.1f}%  ({row['model_id']})"
        )


if __name__ == "__main__":
    main()
