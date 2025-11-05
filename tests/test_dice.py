"""Tests for dice rolling functionality.

Converted from features/dice.feature
"""

import pytest


@pytest.mark.parametrize(
    ('dice_expr', 'min_sum', 'max_sum', 'min_roll', 'max_roll'),
    [
        # Normal dice
        ('1d6', 1, 6, 1, 6),
        ('2d6', 2, 12, 1, 6),
        # Fudge dice
        ('1dF', -1, 1, -1, 1),
        ('2dF', -2, 2, -1, 1),
    ],
    ids=[
        '1d6',
        '2d6',
        '1dF',
        '2dF',
    ],
)
def test_dice_rolling(dice_expr: str, min_sum: int, max_sum: int, min_roll: int, max_roll: int) -> None:
    """Test rolling dice with various expressions.

    Scenario Outline: Rolling dice
    - Compile dice expression
    - Roll dice 10000 times
    - Verify sums and individual rolls are within expected ranges
    """
    from blueprint import dice

    # Compile the dice expression
    compiled_dice_expr = dice.dcompile(dice_expr)

    # Roll the dice 10000 times
    rolls = [dice.roll(compiled_dice_expr) for _ in range(10000)]

    # Verify all rolls are within expected ranges
    for roll in rolls:
        # Check sum is within expected range
        assert sum(roll) >= min_sum, f'Sum {sum(roll)} < min_sum {min_sum}'
        assert sum(roll) <= max_sum, f'Sum {sum(roll)} > max_sum {max_sum}'

        # Check individual rolls are within expected range
        assert min(roll) >= min_roll, f'Min roll {min(roll)} < min_roll {min_roll}'
        assert max(roll) <= max_roll, f'Max roll {max(roll)} > max_roll {max_roll}'


class TestDiceResults:
    """Test the results class operators."""

    def test_results_int_conversion(self) -> None:
        """Test converting results to int."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert int(r) == 6
        assert isinstance(int(r), int)

    def test_results_str_conversion(self) -> None:
        """Test converting results to string."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert str(r) == '6'

    def test_results_float_conversion(self) -> None:
        """Test converting results to float."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert float(r) == 6.0
        assert isinstance(float(r), float)

    def test_results_hash(self) -> None:
        """Test hashing results."""
        from blueprint.dice import results

        r1 = results([1, 2, 3])
        r2 = results([3, 2, 1])
        r3 = results([1, 1, 1, 1, 1, 1])
        assert hash(r1) == hash(r2)
        assert hash(r1) == hash(r3)

    def test_results_add(self) -> None:
        """Test adding results to other values."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert r + 10 == 16
        assert 10 + r == 16

    def test_results_subtract(self) -> None:
        """Test subtracting results from other values."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert r - 2 == 4
        assert 10 - r == 4

    def test_results_multiply(self) -> None:
        """Test multiplying results with other values."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert r * 2 == 12
        assert 2 * r == 12

    def test_results_divide(self) -> None:
        """Test dividing results by other values."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert r / 2 == 3.0
        assert 12 / r == 2.0

    def test_results_floor_divide(self) -> None:
        """Test floor division with results."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert r // 2 == 3
        assert 13 // r == 2

    def test_results_equality(self) -> None:
        """Test equality comparison with results."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert r == 6
        assert r == 6
        assert r != 5

    def test_results_inequality(self) -> None:
        """Test inequality comparison with results."""
        from blueprint.dice import results

        r = results([1, 2, 3])
        assert r != 5
        assert r != 5
        assert r == 6


def test_dcompile_invalid_expression() -> None:
    """Test that invalid dice expressions raise an assertion error."""
    from blueprint.dice import dcompile

    with pytest.raises(AssertionError, match='Invalid dice expression'):
        dcompile('rm -rf /')

    with pytest.raises(AssertionError, match='Invalid dice expression'):
        dcompile('import os')


def test_roll_with_string_expression() -> None:
    """Test rolling dice with a string expression."""
    from blueprint.dice import roll

    result = roll('1d6')
    assert 1 <= int(result) <= 6


def test_roll_with_custom_random() -> None:
    """Test rolling dice with a custom random object."""
    import random

    from blueprint.dice import roll

    custom_random = random.Random(12345)  # noqa: S311
    result1 = roll('2d6', random_obj=custom_random)

    custom_random = random.Random(12345)  # noqa: S311
    result2 = roll('2d6', random_obj=custom_random)

    assert list(result1) == list(result2)
