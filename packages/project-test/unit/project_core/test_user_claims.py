"""User claims normalization."""

from __future__ import annotations

import pytest

from project_core.domain.access.user_claims import claims_from_user_dict, normalize_store_ids

pytestmark = pytest.mark.unit


def test_normalize_store_ids_empty_list():
    assert normalize_store_ids([]) is None
