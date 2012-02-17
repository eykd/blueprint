# -*- coding: utf-8 -*-
"""blueprints_steps -- behavior steps for blueprint features.
"""
from behave import given, when, then


@when(u'I subclass Mod')
def step(context):
    class OfDoom(context.blueprint.Mod):
        name = context.blueprint.FormatTemplate('{meta.source.name} of DOOM')
        value = lambda _: _.meta.source.value * 20
        damage = lambda _: _.meta.source.damage * 20

    context.OfDoom = OfDoom


@then(u'I can mod a Club to create a modified Club of DOOM')
def step(context):
    context.ClubOfDoom = cod = context.OfDoom(context.Club)
    club = cod()
    assert club.name == 'Big Club of DOOM'
    assert club.damage > 200, club.damage
