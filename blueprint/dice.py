# -*- coding: utf-8 -*-
"""blueprint.dice -- a magic bag of dice.
"""
import re
import random

__all__ = ['roll', 'dcompile']

dice_cp = re.compile(r'(?P<num>\d+)d(?P<sides>\d+)')


def dcompile(dice_expr):
    """Compile the given dice expression into a code object.

    This expands all ``NdS``-style dice expressions into valid python
    code (list comprehensions), and compiles the rest for a future
    ``eval``.
    """
    expr = dice_cp.sub('[random.randint(1, \g<sides>) for x in xrange(\g<num>)]', dice_expr)
    return compile(expr, 'dice_expression', 'eval')


def roll(dice_expr, random_obj=None, **kwargs):
    """Return the result of evaluating the given dice expression.

    ``dice_expr`` may be either a dice expression as a string, or a
    code object as returned by ``dcompile``.
    """
    if random_obj is None:
        random_obj = random
    if isinstance(dice_expr, basestring):
        dice_expr = dcompile(dice_expr)

    return eval(dice_expr, globals(), dict(
        random = random_obj,
        **kwargs
        ))
