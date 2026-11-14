import pytest

from app.rules import evaluate_temperature

WARN = 18.0
CRITICAL = 16.0


@pytest.mark.parametrize(
    "temperature, occupied, expected",
    [
        (19.0, True, None),
        (18.0, True, None),
        (17.0, True, ("yellow", "normal")),
        (15.9, True, ("red", "urgent")),
        (17.5, False, ("yellow", "low")),
        (18.0, True, ("yellow", "normal")),
    ],
)
def test_evaluate_temperature(temperature, occupied, expected):
    assert evaluate_temperature(temperature, occupied, WARN, CRITICAL) == expected