"""Tests for blueprint factory functionality.

Converted from features/factory.feature
"""

import blueprint


def test_factory_produces_magical_weapon(
    magical_item_prefix: type[blueprint.Mod], of_doom: type[blueprint.Mod]
) -> None:
    """Test that factories can produce mastered, modded blueprints.

    Scenario: Producing a mastered, modded blueprint
    - Create a MagicalItemFactory
    - Produce an item from the factory
    - Verify the item has been modified correctly
    """

    class MagicalItemFactory(blueprint.Factory):
        product = blueprint.PickFrom(blueprint.WithTags('weapon'))
        mods = [magical_item_prefix, of_doom]

    item = MagicalItemFactory()

    # FIXME: item is *sometimes* a subclass of a Doppelganger Weapon.
    # assert isinstance(item, Weapon)
    assert item.name.endswith('of DOOM')
    assert item.damage >= 20, f'Expected damage >= 20, got {item.damage} for {item}'
