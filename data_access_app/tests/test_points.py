"""points_from_value always floors after /50000."""
from __future__ import annotations

import pytest

from app.domain.columns import points_from_value


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, 0.0),
        (49_999, 0.0),
        (50_000, 1.0),
        (99_999, 1.0),
        (100_000, 2.0),
        (250_000.9, 5.0),
        (None, 0.0),
    ],
)
def test_points_from_value_floors(value, expected):
    assert points_from_value(value) == expected
