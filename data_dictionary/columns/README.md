# Column semantic dictionary

484 semantic chunks — mô tả nghiệp vụ tiếng Việt tự nhiên (không dump sample).

Regenerate:
0. `.env.dictionary_exploration` (local DB)
1. `uv run python scripts/explore_columns_for_dictionary.py` (null-filter + profiles)
2. `uv run python scripts/enrich_column_docs_from_samples.py`
