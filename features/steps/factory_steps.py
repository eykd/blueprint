# -*- coding: utf-8 -*-
"""factory_steps -- behavior steps for Factory features.
"""
from behave import given, when, then


@when(u'I subclass Factory')
def step(context):
    class MagicalItemFactory(context.blueprint.Factory):
        product = context.blueprint.PickFrom(
            context.blueprint.WithTags('weapon'))
        mods = [context.MagicalItemPrefix, context.OfDoom]

    context.MagicalItemFactory = MagicalItemFactory


@then(u'I can produce a magical weapon of DOOM')
def step(context):
    item = context.MagicalItemFactory()
    # FIXME: item is *sometimes* a subclass of a Doppelganger Weapon.
    # assert isinstance(item, context.Weapon)
    assert item.name.endswith('of DOOM')
    assert item.damage >= 20, (item.damage, item)
