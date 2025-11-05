"""blueprint.dice -- a magic bag of dice."""

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
    """Compile the given dice expression into a code object.

    This expands all ``NdS``-style dice expressions into valid python
    code (list comprehensions), and compiles the rest for a future
    ``eval``.
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
    """Return the result of evaluating the given dice expression.

    ``dice_expr`` may be either a dice expression as a string, or a
    code object as returned by ``dcompile``.
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
