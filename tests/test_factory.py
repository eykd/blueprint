"""Tests for blueprint factory functionality.

Converted from features/factory.feature
"""

from typing import ClassVar

import blueprint


def test_factory_produces_magical_weapon(
    magical_item_prefix: type[blueprint.Mod], of_doom: type[blueprint.Mod], weapon: type[blueprint.Blueprint]
) -> None:
    """Test that factories can produce mastered, modded blueprints.

    Scenario: Producing a mastered, modded blueprint
    - Create a MagicalItemFactory
    - Produce an item from the factory
    - Verify the item has been modified correctly
    """

    class MagicalItemFactory(blueprint.Factory):
        product = blueprint.PickFrom(blueprint.WithTags('weapon'))
        mods: ClassVar[list[type[blueprint.Mod]]] = [magical_item_prefix, of_doom]

    item = MagicalItemFactory()

    # TODO: item is *sometimes* a subclass of a Doppelganger Weapon.
    assert item.name.endswith('of DOOM')  # type: ignore[attr-defined]
    assert item.damage >= 20, f'Expected damage >= 20, got {item.damage} for {item}'  # type: ignore[attr-defined]
