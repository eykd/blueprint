"""blueprint.fields"""

# This module uses Any types extensively due to its dynamic field resolution design.
# ruff: noqa: ANN401
from __future__ import annotations

import inspect
import operator
import pprint
import re
from collections import defaultdict
from collections.abc import Callable
from typing import Any, TypeVar, cast

from . import dice

# Type variable for function decorators
_F = TypeVar('_F', bound=Callable[..., Any])  # Function type

__all__ = [
    'All',
    'Dice',
    'DiceTable',
    'Field',
    'FormatTemplate',
    'PickFrom',
    'PickOne',
    'Property',
    'RandomInt',
    'WithTags',
    'defer_to_end',
    'depends_on',
    'generator',
    'resolve',
]


class Field:
    """The base dynamic field class. Not very useful on its own.

    Subclasses of ``Field`` should define a ``__call__`` method::

        def __call__(self, parent): ...

    ``__call__`` should return the final, resolved value of the field.

    When mastering a blueprint, any callable field on the blueprint
    will be called with one argument, the parent blueprint itself.
    """

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self!s}>'

    def __str__(self) -> str:
        return ''

    def __add__(self, b: Any) -> Add:
        return Add(self, b)

    def __radd__(self, a: Any) -> Add:
        return Add(a, self)

    def __sub__(self, b: Any) -> Subtract:
        return Subtract(self, b)

    def __rsub__(self, a: Any) -> Subtract:
        return Subtract(a, self)

    def __mul__(self, b: Any) -> Multiply:
        return Multiply(self, b)

    def __rmul__(self, a: Any) -> Multiply:
        return Multiply(a, self)

    def __div__(self, b: Any) -> Divide:  # noqa: PLW3201
        return Divide(self, b)

    __truediv__ = __div__

    def __floordiv__(self, b: Any) -> FloorDivide:
        return FloorDivide(self, b)

    def __rdiv__(self, a: Any) -> Divide:  # noqa: PLW3201
        return Divide(a, self)

    __rtruediv__ = __rdiv__

    def __rfloordiv__(self, a: Any) -> FloorDivide:
        return FloorDivide(a, self)


class _Operator(Field):
    """Base class for all operator fields."""

    op: Callable[[Any, Any], Any] | None = None
    sym: str = ''
    items: tuple[Any, ...]

    def __init__(self, *items: Any) -> None:
        self.items = items

    def __repr__(self) -> str:
        return f'({self!s})'

    def __str__(self) -> str:
        return (f' {self.sym} ').join(repr(i) for i in self.items)

    def __call__(self, parent: Any) -> Any:
        result: Any = None
        for item in self.items:
            if result is None:
                result = self.resolve(parent, item)
            else:
                assert self.op is not None, 'op must be set in subclass'  # noqa: S101
                result = self.op(result, self.resolve(parent, item))
        return result

    def resolve(self, parent: Any, item: Any) -> Any:  # noqa: PLR6301
        if isinstance(item, _Operator):
            return item(parent)
        return resolve(parent, item)


class Add(_Operator):
    """When resolved, adds all the provided arguments and returns the result."""

    op: Callable[[Any, Any], Any] = operator.add
    sym: str = '+'


class Subtract(_Operator):
    """When resolved, subtracts all the provided arguments and returns the result."""

    op: Callable[[Any, Any], Any] = operator.sub
    sym: str = '-'


class Multiply(_Operator):
    """When resolved, multiplies all the provided arguments and returns the result."""

    op: Callable[[Any, Any], Any] = operator.mul
    sym: str = '*'


class Divide(_Operator):
    """When resolved, divides all the provided arguments and returns the result."""

    op: Callable[[Any, Any], Any] = operator.truediv
    sym: str = '/'


class FloorDivide(_Operator):
    """When resolved, divides-with-truncation all the provided arguments and returns the result."""

    op: Callable[[Any, Any], Any] = operator.floordiv
    sym: str = '//'


class RandomInt(Field):
    """When resolved, returns a random integer between ``start`` and ``end``."""

    start: int
    end: int

    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f'{self.start}...{self.end}'

    def __call__(self, parent: Any) -> int:  # noqa: D102
        return cast('int', parent.meta.random.randint(self.start, self.end))


class Dice(Field):
    """When resolved, returns a random roll of the dice defined in ``dice_expr``.

    A dice expression is simply an extended-format python expression,
    where a throw of the dice is represented as a string of the form
    ``NdS``, where ``N`` is the number of dice, and ``S`` is the
    number of sides on the dice. These dice expressions are expanded
    to a call to ``[random.randint(1, sides) for x in range(num)]``,
    which evaluates to a list of integer results.

    Within the expression, you have access to all python builtins, as
    well as ``parent``, ``random`` (taken from
    ``parent.meta.random``), and any keyword arguments passed in to
    the constructor.

    Example dice expressions::

        '3d6'                 # -> a list of 3 integer results from a six-sided die
        'sorted(3d6)          # -> a sorted list of 3 integer results
        '3d6 + [10]'          # -> a list of 4 integers, the last one being 10.
        'sum(3d6) + max(3d10) # -> an integer result from the given expression
        'random.choice(3d6)'  # -> a random integer result chosen from 3 rolls.
    """

    expr: str
    compiled_expr: Any
    local_kwargs: dict[str, Any]

    def __init__(self, dice_expr: str, **local_kwargs: Any) -> None:
        self.expr = dice_expr
        self.compiled_expr = dice.dcompile(dice_expr)  # type: ignore[no-untyped-call]
        self.local_kwargs = local_kwargs

    def __call__(self, parent: Any) -> Any:  # noqa: D102
        return dice.roll(self.compiled_expr, random_obj=parent.meta.random, parent=parent, **self.local_kwargs)  # type: ignore[no-untyped-call]

    def __str__(self) -> str:
        return str(self.expr)


class DiceTable(Dice):
    """Same as a Dice field, but the result of evaluating the dice expression is used to select a value from a table.

    The table maps dice results to values.
    """

    range_sep_cp: re.Pattern[str] = re.compile(r'(?:\.\.)|[:]')
    table: defaultdict[str | int, Any]

    def __init__(self, dice_expr: str, table: dict[str | int, Any], default: Any = None, **local_kwargs: Any) -> None:
        super().__init__(dice_expr, **local_kwargs)
        self.table = defaultdict(lambda: default)
        for key, value in table.items():
            if isinstance(key, str):
                if self.range_sep_cp.search(key):
                    start_end = self.range_sep_cp.split(key)
                    start, end = int(start_end[0]), int(start_end[-1])
                    for n in range(start, end + 1):
                        self.table[str(n)] = value
                else:
                    for i in key.split(','):
                        self.table[i.strip()] = value
            else:
                self.table[key] = value

    def __call__(self, parent: Any) -> Any:  # noqa: D102
        result = str(super().__call__(parent))
        result = self.table[result]
        return resolve(parent, result)

    def __str__(self) -> str:
        return f'{self.expr!s} for {pprint.pformat(self.table)}'


class PickOne(Field):
    """When resolved, returns a random item from the arguments provided."""

    choices: tuple[Any, ...]

    def __init__(self, *choices: Any) -> None:
        self.choices = choices

    def __str__(self) -> str:
        return str(self.choices)

    def __call__(self, parent: Any) -> Any:  # noqa: D102
        result = parent.meta.random.choice(self.choices)
        return resolve(parent, result)


class PickFrom(Field):
    """When resolved, returns a random item from the collection provided."""

    collection: Any

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def __str__(self) -> str:
        return str(self.collection)

    def __call__(self, parent: Any) -> Any:  # noqa: D102
        collection = resolve(parent, self.collection)
        return resolve(parent, parent.meta.random.choice(list(collection)))


class All(Field):
    """When resolved, returns a list of the provided items, themselves resolved."""

    items: tuple[Any, ...]

    def __init__(self, *items: Any) -> None:
        self.items = items

    def __str__(self) -> str:
        return str(self.items)

    def __call__(self, parent: Any) -> list[Any]:  # noqa: D102
        return [resolve(parent, i) if callable(i) else i for i in self.items]


class FormatTemplate(Field):
    """When resolved, returns a rendered string from the provided template.

    Uses the Python `format string syntax`_. All other fields are
    available to the template, as well as the parent ``meta`` options
    object.

    .. format string syntax: http://docs.python.org/library/string.html#formatstrings

    An example::

    >>> import blueprint as bp
    >>> class Item(bp.Blueprint):
    ...     bonus = 1
    ...     name = bp.FormatTemplate('Item +{bonus}')
    ...     joke = bp.FormatTemplate('Two men walked into a {meta.foo}')
    ...
    ...     class Meta:
    ...         foo = 'bar'

    >>> item = Item()
    >>> item.name
    "Item +1"
    >>> item.joke
    "Two men walked into a bar"
    """

    _defer_to_end: bool = True
    template: str

    def __init__(self, template: str) -> None:
        self.template = template

    def __str__(self) -> str:
        return str(self.template)

    def __get__(self, parent: Any, type_: type[Any] | None = None) -> str | FormatTemplate:
        if parent is None:
            return self

        fields: dict[str, Any] = {'meta': parent.meta, 'parent': parent}
        for name in parent.meta.fields:
            if getattr(parent.__class__, name) is not self:
                fields[name] = getattr(parent, name)
        template_str = cast('str', resolve(parent, self.template))
        return template_str.format(**fields)


class Property(Field):
    """A field that wraps a callable as a property-like descriptor."""

    func: Callable[[Any], Any]

    def __init__(self, func: Callable[[Any], Any]) -> None:
        self.func = func

    def __get__(self, parent: Any, type_: type[Any] | None = None) -> Any:
        if parent is None:
            return self

        return self.func(parent)


class WithTags(Field):
    r"""When resolved, returns the set of all blueprints selected by the given tags.

    Takes multiple arguments. Arguments may be individual tags, or
    space-separated strings with multiple tags. Tags begininng with
    ``!`` denote a NOT (or difference), that is, \"all blueprints
    *without* this tag\". Tags beginning with ``?`` denote an OR (or
    union), that is, \"all blueprints with this tag, but not required
    for others\". Tags without either prefix denote an AND (or
    interesction), that is, \"all blueprints must have this tag\".
    """

    with_tags: set[str]
    or_tags: set[str]
    not_tags: set[str]

    def __init__(self, *tags: str) -> None:
        all_tags: set[str] = set()
        for t in tags:
            all_tags.update(t.split())

        self.with_tags = set()
        self.or_tags = set()
        self.not_tags = set()

        for t in all_tags:
            if t.startswith('!'):
                self.not_tags.add(t)
            elif t.endswith('?'):
                self.or_tags.add(t)
            else:
                self.with_tags.add(t)

    def __call__(self, parent: Any) -> list[Any]:  # noqa: D102
        objects = parent.tag_repo.query_tags_intersection(*self.with_tags) if self.with_tags else parent.tag_repo
        if self.or_tags:
            objects = objects.query_tags_union(*self.or_tags)
        if self.not_tags:
            objects = objects.query_tags_difference(*self.not_tags)

        return [o for o in objects if not o.meta.abstract]


def generator(func: _F) -> _F:
    """Generator methods on a Blueprint don't get flagged as fields.

    Subsequently, they aren't subject to field treatment, and remain
    callable on a mastered Blueprint instance.
    """
    func.is_generator = True  # type: ignore[attr-defined]
    return func


def depends_on(*names: str) -> Callable[[_F], _F]:
    """Declare that the given method depends upon other members to be resolved first."""
    dependencies: set[str] = set()
    for name in names:
        dependencies.update(name.split())

    def wrap(func: _F) -> _F:
        func.depends_on = dependencies  # type: ignore[attr-defined]
        return func

    return wrap


def resolve(parent: Any, field: Any) -> Any:
    """Resolve a field with the given parent instance."""
    while callable(field):
        if inspect.ismethod(field):
            try:
                field = field(seed=parent.meta.random.random())
            except TypeError:
                field = field()
        else:
            try:
                field = field(parent=parent, seed=parent.meta.random.random())
            except TypeError:
                field = field(parent)
    if field.__class__.__name__ == 'generator':
        field = [resolve(parent, i) for i in field]
    return field


def defer_to_end(field: _F) -> _F:
    """Mark a field to be deferred to the end of resolution."""
    field._defer_to_end = True  # type: ignore[attr-defined]  # noqa: SLF001
    return field
