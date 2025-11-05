"""Tests for dice rolling functionality.

Converted from features/dice.feature
"""

import pytest


@pytest.mark.parametrize(
    'dice_expr,min_sum,max_sum,min_roll,max_roll',
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
def test_dice_rolling(dice_expr, min_sum, max_sum, min_roll, max_roll):
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
