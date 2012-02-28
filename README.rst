=========
Blueprint
=========

Magical blueprints for procedural generation of content. Based roughly
on a `series of articles`_ by Sean Norman. `Overview here`_.

.. _series of articles: http://www.squidi.net/mapmaker/index.php
.. _Overview here: http://www.squidi.net/mapmaker/musings/m100402.php

- `Introduction`_
- `Fields and Generators`_
- `Tags`_
- `Mods`_
- `Factories`_
- `TODO`_
- `HELP`_
- `Changelog`_


============
Introduction
============

Blueprints are data objects. The essential idea is that you write
subclasses of ``blueprint.Blueprint`` with fields that define the
general parameters of their values (e.g. an integer between 0 and
10). When you instantiate a blueprint, you get a "mastered" blueprint
with well-defined values for each field. Mastered blueprints may
define special "generator" instance methods that build final objects
from the master.

**Think of it as prototypal inheritance for Python!** (Yeah, I
probably don't know what I'm talking about.)

Most of the big moving parts have their documentation, often with
examples, in the docstring. Blueprint is best played with at the
command line, trying out how things work. For the impatient, an
example::

    import blueprint


    class Item(blueprint.Blueprint):
        value = 1
        tags = 'foo bar'

        class Meta:
            abstract = True


    class Weapon(Item):
        name = 'Some Weapon'
        tags = 'dangerous equippable'
        damage = blueprint.RandomInt(1, 5)

        class Meta:
            abstract = True


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
        weapon -- <Spear:
            damage -- 5
            name -- 'Spear'
            value -- 6
            >
        >
    >>> actor.weapon.name
    'Spear'


Now, we can take our reified master data object and do something with
it--use it as-is, or build another entity using the generated data.


=====================
Fields and Generators
=====================

Blueprints are data objects. By default, every member of a blueprint
is treated as a field, either static or dynamic. Static fields are
simple data attributes. Dynamic fields are callable objects that take
one positional argument, the blueprint on which they are being called.

Dynamic fields make blueprints quite useful. A few basic fields are
provided to get you started, and Blueprints themselves can be used as
fields. Fields are designed to be nestable. They can rely upon each
other too--use the ``blueprint.depends_on`` decorator to declare these
dependencies.

If you really must have a callable method on your mastered blueprint,
use the ``blueprint.generator`` decorator (or mark your callable
object with the ``is_generator`` flag). These are called "generators"
("contractors" in squidi's terminology) because they're intended to be
used to generate your final entity, whether it be a ``dict`` or a WAD
file.
   

====
Tags
====

Blueprints automatically organize themselves using tags (domains in
squidi's parlance). A direct descendant of Blueprint has its own tag
repository (``blueprint.taggables.TagRepository``), which all its
subclasses will share. So, in the above example, you can query
``Weapon.tag_repo.query(with_tags=('piercing'))`` and receive
``set([Spear, PointedStick])``.

Blueprints are also automatically tagged by their class name (and
their ancestor superclass names!), with camel-cased words separated
out. So ``CaveMan`` will automatically get the tags ``set(['cave', 'man',
'actor'])``.

This makes the following possible::

    class MammothHunter(CaveMan):
        weapon = blueprint.PickFrom(
            blueprint.WithTags('pointed weapon')
            )


====
Mods
====

Sometimes, you'll want to dynamically modify a blueprint. To do this,
create a subclass of ``Mod``. Mods are just special blueprints::
   
    class OfDoom(blueprint.Mod):
        name = blueprint.FormatTemplate('{meta.source.name} of DOOM')
        value = lambda _: _.meta.source.value * 5


Then, apply it to another blueprint::

    >>> club = OfDoom(Club)
    >>> club.name
    'Big Club of DOOM'

Mods always produce mastered blueprints.


=========
Factories
=========

Factories put all the pieces together--they're rather a blueprint
factory. Say that you want an item drop that selects from a few common
Weapon blueprints and adds a couple magical Mods to make it
cooler. Here's our second mod::

    class MagicalItemPrefix(blueprint.Mod):
        prefix = blueprint.PickOne(
            'Gnarled',
            'Inscribed',
            'Magnificent',
            )
        name = blueprint.depends_on('prefix')(
            blueprint.FormatTemplate('{parent.prefix} {meta.source.name}'))


Now, here's our Magical Item factory::

    class MagicalItemFactory(blueprint.Factory):
        product = blueprint.PickFrom(
            blueprint.WithTags('weapon'))
        mods = [MagicalItemPrefix, OfDoom]


Now, when we call the factory, we get a random Weapon with magical properties::

    >>> weapon = MagicalItemFactory()
    >>> weapon.name
    'Gnarled Worn Spear of DOOM'

Factories always produce mastered blueprints.


====
TODO
====

- Better documentation. :\)
- Support all operators on ``blueprint.Field``


====
HELP
====

If you run into trouble, or find a bug, file an issue in the `tracker
on github <https://github.com/eykd/blueprint/issues>`_.

On github, bleeding-edge development work is done on the ``develop``
branch. ``master`` *should* always be stable.


=========
CHANGELOG
=========

- **0.3.2**: Added the LICENSE file to the source distribution, so pip
  won't fail.

- **0.3.1**: Radically improved docstrings, with relevant
  examples. Added a changelog!

- **0.3**: Added Factories. Bugfixes.

- **0.2**: Added Mods. Bugfixes.

- **0.1**: Initial release.
