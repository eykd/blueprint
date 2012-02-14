=========
Blueprint
=========

Magical blueprints for procedural generation of content. Based roughly
on http://www.squidi.net/mapmaker/musings/m100402.php

The essential idea is that you write subclasses of
`blueprint.Blueprint` with fields that define the general parameters
of their values (e.g. an integer between 0 and 10). When you
instantiate a blueprint, you get a "mastered" blueprint with
well-defined values for each field. Mastered blueprints may define
special "generator" instance methods that build final objects from the
master.

**Think of it as prototypal inheritance for Python!**

An example::

    import blueprint

    class Item(blueprint.Blueprint):
        value = 1
        tags = 'foo bar'


    class Weapon(Item):
        name = 'Some Weapon'
        tags = 'dangerous equippable'
        damage = blueprint.RandomInt(1, 5)


    class Spear(Weapon):
        tags = 'primitive piercing'
        name = 'Worn Spear'
        damage = blueprint.RandomInt(10, 15)
        value = blueprint.RandomInt(4, 6)


    class PointedStick(Weapon):
        tags = 'primitive piercing'
        name = 'Pointed Stick'
        damage = 6
        value = 2


    class Club(Weapon):
        tags = 'primitive crushing'
        name = 'Big Club'
        damage = blueprint.RandomInt(10, 15)
        value = 2


    class Actor(blueprint.Blueprint):
        tags = 'active'


    class CaveMan(Actor):
        name = 'Cave Man'
        weapon = blueprint.PickOne(
            Club, Spear, PointedStick
            )

And then:

    >>> actor = CaveMan()
    >>> actor
    <CaveMan:
        name -- 'Cave Man'
        weapon -- <PointedStick:
            damage -- 6
            name -- 'Pointed Stick'
            value -- 2
            >
        >
   

====
Tags
====

Blueprints automatically organize themselves using tags. A direct
descendant of Blueprint has its own tag repository
(`blueprint.taggables.TagRepository`), which all its subclasses will
share. So, in the above example, you can query
`Weapon.tag_repo.query(with_tags=('piercing'))` and receive
`set([Spear, PointedStick])`.

Blueprints are also automatically tagged by their class name (and
their ancestor superclass names!), with camel-cased words separated
out. So `CaveMan` will automatically get the tags `set(['cave', 'man',
'actor'])`.

This makes the following possible::

    class MammothHunter(CaveMan):
        weapon = blueprint.PickFrom(
            blueprint.WithTags('pointed weapon')
            )


====
TODO
====

- Better documentation. :\)

