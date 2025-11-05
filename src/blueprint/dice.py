"""Dice rolling and expression evaluation for procedural generation.

This module provides a flexible dice rolling system that supports standard RPG dice
notation (e.g., '3d6', '2d20+5') and Fudge/FATE dice. Dice expressions are compiled
into Python code for efficient evaluation and can include mathematical operations,
function calls like sum(), min(), max(), and random.choice().

The module uses regex-based parsing to convert dice notation into executable Python
expressions, with safety checks to prevent code injection.

Example:
    >>> import random
    >>> random.seed(42)
    >>> roll('3d6 + 2')  # Returns sum as int when adding constant
    10
    >>> roll('3d6')  # Returns results list when no operations
    [6, 3, 2]
    >>> int(roll('2d20 + 5'))
    18

"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from types import CodeType

__all__ = ['dcompile', 'roll']

T = TypeVar('T')


dice_cp: re.Pattern[str] = re.compile(r'(?P<num>\d+)d(?P<sides>\d+)')
fudge_cp: re.Pattern[str] = re.compile(r'(?P<num>\d+)d[fF]')

safe_cp: re.Pattern[str] = re.compile(
    r"""
^(?:
    \d+d\d+  # Dice expression
  | \d+d[Ff] # Fudge dice
  | \d+
  | sum\(
  | sorted\(
  | max\(
  | min\(
  | abs\(
  | random\.choice\(
  | \(
  | \)
  | [+-/*%]
  | \s
)+$
""",
    re.VERBOSE,
)


class results(list[int]):
    """List of dice roll results that behaves like a number in arithmetic operations.

    This class extends list to store individual dice roll results while allowing the
    collection to be used directly in mathematical expressions. When used in arithmetic
    or comparison operations, the results list automatically converts itself to the
    appropriate numeric type (int or float) by summing all dice values.

    The class maintains both the individual roll results (as a list) and provides
    numeric behavior for convenience in dice expression evaluation.

    Attributes:
        Inherits all list attributes. Contains integer dice roll results.

    Example:
        >>> r = results([3, 5, 2])
        >>> int(r)
        10
        >>> r + 5
        15
        >>> 10 - r
        0
        >>> float(r) * 2.5
        25.0

    """

    def __int__(self) -> int:
        return int(sum(self))

    def __str__(self) -> str:
        return str(int(self))

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(int(self))

    def __float__(self) -> float:
        return float(sum(self))

    def _convert(self, other: Any) -> Any:  # noqa: ANN401
        return type(other)(self)

    def __add__(self, b: Any) -> Any:  # noqa: ANN401
        return self._convert(b) + b

    def __radd__(self, a: Any) -> Any:  # noqa: ANN401
        return a + self._convert(a)

    def __sub__(self, b: Any) -> Any:  # noqa: ANN401
        return self._convert(b) - b

    def __rsub__(self, a: Any) -> Any:  # noqa: ANN401
        return a - self._convert(a)

    def __mul__(self, b: Any) -> Any:  # noqa: ANN401
        return self._convert(b) * b

    def __rmul__(self, a: Any) -> Any:  # noqa: ANN401
        return a * self._convert(a)

    def __div__(self, b: Any) -> Any:  # noqa: ANN401, PLW3201
        return self._convert(b) / b

    __truediv__ = __div__

    def __floordiv__(self, b: Any) -> Any:  # noqa: ANN401
        return self._convert(b) // b

    def __rdiv__(self, a: Any) -> Any:  # noqa: ANN401, PLW3201
        return a / self._convert(a)

    __rtruediv__ = __rdiv__

    def __rfloordiv__(self, a: Any) -> Any:  # noqa: ANN401
        return a // self._convert(a)

    def __eq__(self, b: object) -> bool:
        return bool(b == self._convert(b))

    def __ne__(self, b: object) -> bool:
        return bool(b != self._convert(b))


def dcompile(dice_expr: str) -> CodeType:
    """Compile a dice expression string into an executable code object.

    This function parses and compiles dice notation expressions into Python code objects
    that can be evaluated efficiently. It supports standard RPG dice notation (NdS format,
    where N is the number of dice and S is the number of sides) and Fudge dice (NdF format).

    The function performs safety validation to prevent code injection by checking the
    expression against a whitelist of allowed operations. Dice expressions are transformed
    into list comprehensions that generate random values, then compiled for later evaluation.

    Supported dice notations:
        - Standard dice: '3d6', '2d20', '1d100'
        - Fudge dice: '4dF', '2df' (results in -1, 0, or 1)
        - Math operations: '+', '-', '*', '/', '//', '%'
        - Functions: sum(), sorted(), max(), min(), abs(), random.choice()

    Args:
        dice_expr: A string containing the dice expression to compile. Must match the
            safety regex pattern to prevent code injection. Examples: '3d6+2', '2d20-5',
            'max(4d6)', '4dF'.

    Returns:
        A compiled code object that can be passed to the roll() function or evaluated
        directly with eval() using the appropriate namespace.

    Raises:
        AssertionError: If the dice expression contains unsafe or invalid syntax that
            doesn't match the safety validation pattern.

    Example:
        >>> code = dcompile('3d6 + 2')
        >>> code  # doctest: +ELLIPSIS
        <code object <module> at 0x...>
        >>> code = dcompile('2d20 + sum(3d6)')
        >>> code  # doctest: +ELLIPSIS
        <code object <module> at 0x...>

    Note:
        The compiled code object expects specific variables in its evaluation namespace:
        'random' (a random module or object), 'results' (the results class), and
        'xrange' (mapped to range).

    """
    assert safe_cp.match(dice_expr), f'Invalid dice expression: {dice_expr}'  # noqa: S101
    expr = dice_cp.sub(
        r'results(random.randint(1, \g<sides>) '
        r'for x in xrange(\g<num>))',
        dice_expr,
    )
    expr = fudge_cp.sub(
        (
            'results(random.choice([-1, -1, 0, 0, 1, 1]) '
            r'for x in xrange(\g<num>))'
        ),
        expr,
    )
    return compile(expr, f'dice_expression: ({dice_expr})', 'eval')


def roll(dice_expr: str | CodeType, random_obj: Any = None, **kwargs: Any) -> Any:  # noqa: ANN401
    """Evaluate a dice expression and return the rolled result.

    This function evaluates dice expressions to produce random results according to
    standard RPG dice notation. It accepts either a string expression (which is compiled
    automatically) or a pre-compiled code object from dcompile(). Results are returned
    as a results object that can be used as a list of individual rolls or as a numeric
    sum in arithmetic operations.

    The function handles the complete evaluation context, including importing the random
    module if needed, setting up the namespace with required functions and classes, and
    executing the compiled expression.

    Args:
        dice_expr: Either a string containing a dice expression (e.g., '3d6+2', '2d20')
            or a pre-compiled code object from dcompile(). String expressions are
            automatically compiled before evaluation.
        random_obj: Optional random number generator object or module. If None (default),
            the standard library random module is imported and used. Can be any object
            with randint() and choice() methods for custom random behavior or seeding.
        **kwargs: Additional keyword arguments to add to the evaluation namespace. This
            allows passing custom variables that can be referenced in the dice expression.

    Returns:
        A results object containing the dice roll outcomes. This can be used as a list
        to access individual roll values, or as a number (via int() or float()) to get
        the sum of all rolls. The exact type depends on the expression evaluated.

    Example:
        >>> import random
        >>> random.seed(42)
        >>> result = roll('3d6')
        >>> result
        [6, 1, 1]
        >>> int(result)
        8
        >>> roll('2d20 + 5', random_obj=random)
        22
        >>> int(roll('max(4d6)'))
        6

    Note:
        The evaluation uses eval() internally after safety validation. Only use dice
        expressions from trusted sources or those validated by dcompile().

    """
    if random_obj is None:
        import random

        random_obj = random
    if isinstance(dice_expr, str):
        dice_expr = dcompile(dice_expr)

    local_vars: dict[str, Any] = dict(**kwargs)
    local_vars['random'] = random_obj
    local_vars['results'] = results
    local_vars['xrange'] = range

    return eval(dice_expr, local_vars)  # noqa: S307
