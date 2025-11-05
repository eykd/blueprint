"""Pytest fixtures for blueprint tests.

This module defines common fixtures used across multiple test files,
particularly those that correspond to common @given steps from the
original Behave test suite.
"""

from typing import Any

import pytest

import blueprint
from blueprint import taggables


@pytest.fixture(scope='module')
def item() -> type[blueprint.Blueprint]:
    """Create an Item blueprint class.

    Corresponds to: "When I subclass Blueprint"
    """

    class Item(blueprint.Blueprint):
        value = 1
        tags = 'foo bar'  # type: ignore[assignment]

        class Meta:
            abstract = True

    return Item


@pytest.fixture(scope='module')
def weapon(item: type[blueprint.Blueprint]) -> type[blueprint.Blueprint]:
    """Create a Weapon blueprint class.

    Corresponds to: "When I subclass Item"
    """

    class Weapon(item):  # type: ignore[misc, valid-type]
        name = 'Some Weapon'
        tags = 'dangerous'
        damage = blueprint.RandomInt(1, 5)

        class Meta:
            abstract = True

    return Weapon


@pytest.fixture(scope='module')
def spear(weapon: type[blueprint.Blueprint]) -> type[blueprint.Blueprint]:
    """Create a Spear weapon subclass.

    Corresponds to: "When I subclass Weapon several times"
    """

    class Spear(weapon):  # type: ignore[misc, valid-type]
        tags = 'primitive piercing'
        name = 'Worn Spear'
        damage = blueprint.RandomInt(10, 15)
        value = blueprint.RandomInt(4, 6)

    return Spear


@pytest.fixture(scope='module')
def pointed_stick(weapon: type[blueprint.Blueprint]) -> type[blueprint.Blueprint]:
    """Create a PointedStick weapon subclass.

    Corresponds to: "When I subclass Weapon several times"
    """

    class PointedStick(weapon):  # type: ignore[misc, valid-type]
        tags = 'primitive piercing'
        name = 'Pointed Stick'
        damage = 6
        value = 2

    return PointedStick


@pytest.fixture(scope='module')
def club(weapon: type[blueprint.Blueprint]) -> type[blueprint.Blueprint]:
    """Create a Club weapon subclass.

    Corresponds to: "When I subclass Weapon several times"
    """

    class Club(weapon):  # type: ignore[misc, valid-type]
        tags = 'primitive crushing'
        name = 'Big Club'
        damage = blueprint.RandomInt(10, 15)
        value = 2

    return Club


@pytest.fixture
def of_doom() -> type[blueprint.Mod]:
    """Create OfDoom mod class.

    Corresponds to: "When I subclass Mod"
    """

    class OfDoom(blueprint.Mod):
        name = blueprint.FormatTemplate('{meta.source.name} of DOOM')

        def value(self) -> int:
            return self.meta.source.value * 20  # type: ignore[union-attr, no-any-return]

        def damage(self) -> int:
            return self.meta.source.damage * 20  # type: ignore[union-attr, no-any-return]

    return OfDoom


@pytest.fixture
def magical_item_prefix() -> type[blueprint.Mod]:
    """Create MagicalItemPrefix mod class.

    Corresponds to: "When I subclass Mod"
    """

    class MagicalItemPrefix(blueprint.Mod):
        prefix = blueprint.PickOne(
            'Gnarled',
            'Inscribed',
            'Magnificent',
        )
        name = blueprint.depends_on('prefix')(blueprint.FormatTemplate('{parent.prefix} {meta.source.name}'))  # type: ignore[type-var]

    return MagicalItemPrefix


@pytest.fixture
def _tag_repo_setup() -> dict[str, Any]:
    """Internal fixture that creates a tag repository with test taggables.

    This is a private fixture used by the individual tag fixtures.
    Use the individual fixtures (repo, t1, t2, t3, t4) instead of this one.

    Corresponds to: "Given a tag repository with taggables in it"
    """
    repo = taggables.TagRepository()
    t1 = taggables.Taggable(repo, 't1', 'foo')
    t2 = taggables.Taggable(repo, 't2', 'foo', 'bar')
    t3 = taggables.Taggable(repo, 't3', 'foo', 'bar', 'baz')
    t4 = taggables.Taggable(repo, 't4', 'boo')

    return {
        'repo': repo,
        't1': t1,
        't2': t2,
        't3': t3,
        't4': t4,
    }


@pytest.fixture
def repo(_tag_repo_setup: dict[str, Any]) -> taggables.TagRepository:
    """Get the tag repository from the test setup."""
    return _tag_repo_setup['repo']  # type: ignore[no-any-return]


@pytest.fixture
def t1(_tag_repo_setup: dict[str, Any]) -> taggables.Taggable:
    """Get taggable t1 (tags: 'foo')."""
    return _tag_repo_setup['t1']  # type: ignore[no-any-return]


@pytest.fixture
def t2(_tag_repo_setup: dict[str, Any]) -> taggables.Taggable:
    """Get taggable t2 (tags: 'foo', 'bar')."""
    return _tag_repo_setup['t2']  # type: ignore[no-any-return]


@pytest.fixture
def t3(_tag_repo_setup: dict[str, Any]) -> taggables.Taggable:
    """Get taggable t3 (tags: 'foo', 'bar', 'baz')."""
    return _tag_repo_setup['t3']  # type: ignore[no-any-return]


@pytest.fixture
def t4(_tag_repo_setup: dict[str, Any]) -> taggables.Taggable:
    """Get taggable t4 (tags: 'boo')."""
    return _tag_repo_setup['t4']  # type: ignore[no-any-return]
