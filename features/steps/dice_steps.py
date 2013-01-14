# -*- coding: utf-8 -*-
"""dice_steps -- behavior steps for dice features.
"""
from behave import given, when, then

try:
    _ = xrange
except NameError:
    xrange = range # Python 3

@given(u'I have {dice_expr}')
def dice_step(context, dice_expr):
    context.dice_expr = dice_expr
    from blueprint import dice
    context.dice = dice


@when(u'I compile the dice expression')
def step(context):
    context.compiled_dice_expr = context.dice.dcompile(context.dice_expr)


@when(u'I roll the dice {N:d} times')
def roll_step(context, N):
    context.rolls = [
        context.dice.roll(context.compiled_dice_expr)
        for n in xrange(N)
        ]


@then(u'the sum should be less than {min_sum:d}')
def min_sum_step(context, min_sum):
    context.min_sum = min_sum
    for roll in context.rolls:
        assert sum(roll) >= min_sum


@then(u'the sum should not exceed {max_sum:d}')
def max_sum_step(context, max_sum):
    context.max_sum = max_sum
    for roll in context.rolls:
        assert sum(roll) <= max_sum


@then(u'the minimum individual roll should not be less than {min_roll:d}')
def min_roll_step(context, min_roll):
    context.min_roll = min_roll
    for roll in context.rolls:
        assert min(roll) >= min_roll, ("%r not >= %r" % (min(roll), min_roll))


@then(u'the maximum individual roll should not exceed {max_roll:d}')
def max_roll_step(context, max_roll):
    context.max_roll = max_roll
    for roll in context.rolls:
        assert max(roll) <= max_roll, ("%r not <= %r" % (max(roll), max_roll))
