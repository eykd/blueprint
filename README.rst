=========
Blueprint
=========

Magical blueprints for procedural generation of content. Based roughly
on a `series of articles`_ by Sean Howard. `Overview here`_.

.. _series of articles: http://www.squidi.net/mapmaker/index.php
.. _Overview here: http://www.squidi.net/mapmaker/musings/m100402.php

- `Introduction`_
- `Fields and Generators`_
- `Tags`_
- `Mods`_
- `Factories`_
- `TODO`_
- `HELP`_
- `DEVELOPMENT`_
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


===========
DEVELOPMENT
===========

Itching to hack on blueprint? Fork the repository on `on github`_ and
submit a pull request. If you're not sure what you're doing, follow
`these guidelines`_.

.. _on github: http://github.com/eykd/blueprint/
.. _these guidelines: https://gun.io/blog/how-to-github-fork-branch-and-pull-request/

On github, bleeding-edge development works should be done on feature
branches. ``master`` *should* always remain stable.

Setup
-----

Blueprint uses `uv`_ for dependency management. To set up your
development environment::

    # Install dependencies (dev + test groups)
    uv sync --group dev --group test

    # Install pre-commit hooks
    uv run pre-commit install

.. _uv: https://docs.astral.sh/uv/

Testing
-------

Tests are written using `pytest`_ and are located in the ``tests/``
folder. Blueprint maintains **100% test coverage** (including branch
coverage) and validates test independence with randomized execution
order.

To run the test suite::

    # Run all tests with coverage
    uv run pytest

    # Run tests with randomized order (validates test independence)
    uv run pytest --random-order

    # Run the comprehensive test script (format, lint, type-check, test)
    ./runtests.sh

.. _pytest: https://docs.pytest.org/

Code Quality
------------

Blueprint enforces strict code quality standards:

- **Type checking**: All code is fully type-annotated and checked with
  `mypy`_ in strict mode
- **Linting**: Comprehensive linting with `ruff`_ (50+ rule groups enabled)
- **Formatting**: Consistent code formatting with ruff
- **Documentation**: Google-style docstrings with executable doctests

To check code quality::

    # Run type checker
    uv run mypy src tests

    # Run linter
    uv run ruff check .

    # Auto-fix linting issues
    uv run ruff check --fix .

    # Run formatter
    uv run ruff format .

    # Run all pre-commit hooks manually
    uv run pre-commit run --all-files

.. _mypy: https://www.mypy-lang.org/
.. _ruff: https://docs.astral.sh/ruff/


=========
CHANGELOG
=========

- **0.7**: Major modernization release with comprehensive quality improvements:

  - **Breaking changes:**

    - **Dropped Python 2.7 support**: Minimum Python version is now 3.11+.

    - **Method naming convention**: Changed from camelCase to snake_case for
      internal methods (e.g., ``_getMaster()`` → ``_get_master()``). Public
      API field classes (``PickOne``, ``PickFrom``, etc.) remain unchanged.

    - **Comparison methods**: Replaced ``__cmp__`` with total ordering
      (``__lt__``, ``__le__``, ``__eq__``, ``__ge__``, ``__gt__``) for
      Python 3 compatibility.

  - **Quality improvements:**

    - **100% test coverage**: Achieved complete branch coverage with
      comprehensive test suite.

    - **Full type annotations**: All code is now fully type-annotated and
      validated with mypy in strict mode. Package includes ``py.typed``
      marker for downstream type checking.

    - **Comprehensive linting**: Enforced via ruff with 50+ rule groups
      enabled, ensuring consistent code style and catching potential issues.

    - **Doctest integration**: All code examples in docstrings are now
      executable and validated during testing.

    - **Test independence**: Validated with pytest-random-order to ensure
      tests can run in any order without dependencies.

  - **Infrastructure improvements:**

    - **Modern tooling**: Migrated from setuptools to uv + hatchling for
      faster, more reliable builds.

    - **Src layout**: Adopted modern src/ layout for better packaging
      practices.

    - **Pre-commit hooks**: Added automated formatting, linting, and type
      checking before commits.

    - **GitHub Actions CI**: Automated testing on Python 3.11, 3.12, and
      3.13.

    - **Dynamic versioning**: Improved version handling with
      uv-dynamic-versioning.

  - **Bug fixes:**

    - Fixed abstract blueprints being incorrectly included in tag
      repositories.

    - Removed test ordering dependencies that could cause flaky test
      failures.

    - Improved dice compilation and random number generation consistency.

  - **Testing framework**: Migrated from behave (BDD) to pytest with modern
    fixtures and parametrization.

- **0.6.1**: Fixed Python 3 compatibility in dice roller.

- **0.6**: Experimental Python 3 compatibility, and bug-fixes:

  - **Feature:** Experimental Python 3 compatibility, thanks to `0ion9`_.

  - **Major bug fix:** Fixed bug in dice compilation.

- **0.5**: A couple new features, some interfaces and many bug-fixes:

  - **Feature:** Added Property descriptor which acts like a field. May not actually be useful.

  - **Feature:** Dice rolls now return a results list, which auto-sums
    when doing integer or floating point arithmetic. No more mandatory
    ``sum()`` in your dice expressions.

  - **Major bug fix:** Fixed bug where Dice fields did not use the
    correct random object, with nondeterministic results.

  - **Bug fix/Interface change:** Improved (though not yet perfect)
    field resolution mechanics. Fields that depend on other, deferred
    fields now have a fighting chance at resolving.

  - **Bug fix/Interface change:** DiceTable no longer accepts `-` or
    arbitrary numbers of `.` or `:` as a range separator. Only `..` or
    `:` work now.

  - **Interface change:** Operators are now Fields in their own right,
    with all resulting rights and privileges.

- **0.4**: Added a dice roller through ``blueprint.dice.roll``, and a
  corresponding ``Dice`` and ``DiceTable`` fields. Blueprint
  subclasses now have a better ``__repr__`` through the
  metaclass. **METACLASSES ROCK.**

  Modified the behavior of field resolution. All fields now use
  ``fields.resolve`` to consistently handle nested callables.

- **0.3.4**: Learned how to read. Corrected Sean Howard's name in the
  intro copy. Three micro-releases in 1 hour!

- **0.3.3**: Learned how to use distutils. :P (Fixed a unicode string
  in ``setup([packages=[...]])``.)

- **0.3.2**: Added the LICENSE file to the source distribution, so pip
  won't fail.

- **0.3.1**: Radically improved docstrings, with relevant
  examples. Added a changelog!

- **0.3**: Added Factories. Bugfixes.

- **0.2**: Added Mods. Bugfixes.

- **0.1**: Initial release.


.. _0ion9: https://github.com/0ion9
