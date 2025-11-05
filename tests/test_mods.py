"""Tests for blueprint modification functionality.

Converted from features/mods.feature
"""

import blueprint


def test_mod_creates_modified_blueprint(club: type[blueprint.Blueprint], of_doom: type[blueprint.Mod]) -> None:
    """Test that mods can modify other blueprints.

    Scenario: Modifying a blueprint
    - Apply OfDoom mod to Club
    - Verify modified blueprint is still a Club instance
    - Verify name has been modified
    - Verify damage has been scaled appropriately
    """
    club_instance = of_doom(club)

    assert isinstance(club_instance, club)
    assert club_instance.name == 'Big Club of DOOM'  # type: ignore[attr-defined]
    assert club_instance.damage >= 200, f'Expected damage >= 200, got {club_instance.damage}'  # type: ignore[attr-defined]


class TestMod:
    """Test Mod class functionality."""

    def test_mod_with_blueprint_class(self, club: type[blueprint.Blueprint]) -> None:
        """Test applying mod to a blueprint class."""

        class PowerMod(blueprint.Mod):
            def damage(self) -> int:
                return self.meta.source.damage * 10  # type: ignore[union-attr, no-any-return]

        modded = PowerMod(club)
        assert isinstance(modded, club)
        assert modded.damage >= 100  # type: ignore[operator]

    def test_mod_with_blueprint_instance(self, club: type[blueprint.Blueprint]) -> None:
        """Test applying mod to a blueprint instance."""

        class PowerMod(blueprint.Mod):
            def damage(self) -> int:
                return self.meta.source.damage * 10  # type: ignore[union-attr, no-any-return]

        club_instance = club()
        modded = PowerMod(club_instance)
        assert isinstance(modded, club)

    def test_mod_without_source_creates_unbound_mod(self) -> None:
        """Test creating a Mod without source creates unbound mod."""

        class PowerMod(blueprint.Mod):
            multiplier = 10

        mod = PowerMod()
        assert isinstance(mod, PowerMod)
        assert mod.multiplier == 10

    def test_mod_call_with_blueprint_class(self, spear: type[blueprint.Blueprint]) -> None:
        """Test calling mod as function with blueprint class."""

        class SharpMod(blueprint.Mod):
            prefix = 'Sharp'

        mod = SharpMod()
        modded = mod(spear)
        assert isinstance(modded, spear)
        assert modded.prefix == 'Sharp'  # type: ignore[attr-defined]

    def test_mod_call_with_blueprint_instance(self, spear: type[blueprint.Blueprint]) -> None:
        """Test calling mod as function with blueprint instance."""

        class SharpMod(blueprint.Mod):
            prefix = 'Sharp'

        spear_instance = spear()
        mod = SharpMod()
        modded = mod(spear_instance)
        assert isinstance(modded, spear)
        assert modded.prefix == 'Sharp'  # type: ignore[attr-defined]

    def test_mod_preserves_source(self, club: type[blueprint.Blueprint]) -> None:
        """Test that mod preserves source reference."""

        class TestMod(blueprint.Mod):
            bonus = 5

        modded = TestMod(club)
        assert modded.meta.source == club

    def test_mod_copies_all_fields(self, club: type[blueprint.Blueprint]) -> None:
        """Test that mod copies all its fields to the modded blueprint."""

        class MultiFieldMod(blueprint.Mod):
            bonus = 100
            special = 'magical'
            extra_damage = 50

        modded = MultiFieldMod(club)
        assert modded.bonus == 100

        assert modded.special == 'magical'

        assert modded.extra_damage == 50
