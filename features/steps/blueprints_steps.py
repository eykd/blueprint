# -*- coding: utf-8 -*-
"""blueprints_steps -- behavior steps for blueprint features.
"""
from behave import given, when, then


@given(u'I have imported the blueprints module')
def step(context):
    import blueprint
    context.blueprint = blueprint


@when(u'I subclass Blueprint')
def step(context):
    class Item(context.blueprint.Blueprint):
        value = 1
        tags = 'foo bar'

        class Meta:
            abstract = True

    context.Item = Item

@then(u'my blueprint subclass will have a tag repository')
def step(context):
    hasattr(context.Item, 'tag_repo')


@then(u'my blueprint subclass will be tagged with its class name')
def step(context):
    assert 'Item' in context.Item.tags


@then(u'my blueprint subclass will have any other defined tags.')
def step(context):
    assert 'foo' in context.Item.tags
    assert 'bar' in context.Item.tags


@when(u'I subclass Item')
def step(context):
    class Weapon(context.Item):
        name = 'Some Weapon'
        tags = 'dangerous'
        damage = context.blueprint.RandomInt(1, 5)

        class Meta:
            abstract = True
    context.Weapon = Weapon


@then(u'my item subclass will have a tag repository')
def step(context):
    hasattr(context.Weapon, 'tag_repo')


@then(u"my item subclass tag repository will be the same as Item's")
def step(context):
    assert context.Weapon.tag_repo is context.Item.tag_repo


@then(u'my item subclass will be tagged with its class name')
def step(context):
    assert 'Weapon' in context.Weapon.tags


@then(u'my item subclass will inherit tags from Item')
def step(context):
    assert 'Item' in context.Weapon.tags
    assert 'foo' in context.Weapon.tags
    assert 'bar' in context.Weapon.tags


@then(u'my item subclass will have any other defined tags.')
def step(context):
    assert 'dangerous' in context.Weapon.tags


@when(u'I subclass Weapon several times')
def step(context):
    class Spear(context.Weapon):
        tags = 'primitive piercing'
        name = 'Worn Spear'
        damage = context.blueprint.RandomInt(10, 15)
        value = context.blueprint.RandomInt(4, 6)
    context.Spear = Spear

    class PointedStick(context.Weapon):
        tags = 'primitive piercing'
        name = 'Pointed Stick'
        damage = 6
        value = 2
    context.PointedStick = PointedStick

    class Club(context.Weapon):
        tags = 'primitive crushing'
        name = 'Big Club'
        damage = context.blueprint.RandomInt(10, 15)
        value = 2
    context.Club = Club


@then(u'I can query Weapon subclasses by tag.')
def step(context):
    repo = context.Item.tag_repo
    q = repo.queryTagsUnion('Weapon', 'primitive')
    assert context.Spear in q
    assert context.PointedStick in q
    assert context.Club in q
    

@then(u'I can select a Weapon subclass by tag.')
def step(context):
    repo = context.Item.tag_repo
    q = repo.queryTagsUnion('Weapon', 'primitive')
    assert context.Spear in q
    assert context.PointedStick in q
    assert context.Club in q

    old_weapon = None
    for x in range(10):
        weapon = repo.select(with_tags=('Weapon', 'primitive'))
        assert weapon in (context.Spear, context.PointedStick, context.Club)
        assert weapon is not old_weapon
        old_weapon = weapon
