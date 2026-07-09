# Column semantic dictionary

484 semantic chunks — tên có nghĩa (`loyalty_card_master_id`, `cscard_alternate_card_slot`, …).

Regenerate:
0. Copy `.env.dictionary_exploration.example` → `.env.dictionary_exploration` (local: DESKTOP-AUQEDC5)
1. `uv run python scripts/explore_db_samples.py`
2. `uv run python scripts/explore_columns_for_dictionary.py`
3. `uv run python scripts/enrich_column_docs_from_samples.py`
