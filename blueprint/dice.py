# -*- coding: utf-8 -*-
"""blueprint.dice -- a magic bag of dice.
"""
import re

__all__ = ['roll', 'dcompile']

try:
    _ = xrange
except NameError:
    # Python 3
    xrange = range
    basestring = str

dice_cp = re.compile(r'(?P<num>\d+)d(?P<sides>\d+)')
fudge_cp = re.compile(r'(?P<num>\d+)d[fF]')

safe_cp = re.compile(r"""
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
""", re.VERBOSE)


class results(list):
    def __int__(self):
        return int(sum(self))

    def __str__(self):
        return str(int(self))

    def __unicode__(self):
        return unicode(int(self))

    def __hash__(self):
        return hash(int(self))

    def __float__(self):
        return float(sum(self))

    def _convert(self, other):
        return type(other)(self)

    def __add__(self, b):
        return self._convert(b) + b

    def __radd__(self, a):
        return a + self._convert(a)

    def __sub__(self, b):
        return self._convert(b) - b

    def __rsub__(self, a):
        return a - self._convert(a)

    def __mul__(self, b):
        return self._convert(b) * b

    def __rmul__(self, a):
        return a * self._convert(a)

    def __div__(self, b):
        return self._convert(b) / b

    __truediv__ = __div__
    def __floordiv__(self, b):
        return self._convert(b) // b

    def __rdiv__(self, a):
        return a / self._convert(a)

    __rtruediv__ = __rdiv__

    def __rfloordiv__(self, a):
        return a // self._convert(a)

    def __eq__(self, b):
        return b == self._convert(b)

    def __ne__(self, b):
        return b != self._convert(b)


def dcompile(dice_expr):
    """Compile the given dice expression into a code object.

    This expands all ``NdS``-style dice expressions into valid python
    code (list comprehensions), and compiles the rest for a future
    ``eval``.
    """
    assert safe_cp.match(dice_expr), 'Invalid dice expression: %s' % dice_expr
    expr = dice_cp.sub('results(random.randint(1, \g<sides>) '
                       'for x in xrange(\g<num>))',
                       dice_expr)
    expr = fudge_cp.sub(('results(random.choice([-1, -1, 0, 0, 1, 1]) '
                         'for x in xrange(\g<num>))'),
                        expr)
    return compile(expr, 'dice_expression: (%s)' % dice_expr, 'eval')


def roll(dice_expr, random_obj=None, **kwargs):
    """Return the result of evaluating the given dice expression.

    ``dice_expr`` may be either a dice expression as a string, or a
    code object as returned by ``dcompile``.
    """
    if random_obj is None:
        import random
        random_obj = random
    if isinstance(dice_expr, basestring):
        dice_expr = dcompile(dice_expr)

    local_vars = dict(**kwargs)
    local_vars['random'] = random_obj
    local_vars['results'] = results
    local_vars['xrange'] = xrange

    return eval(dice_expr, local_vars)
