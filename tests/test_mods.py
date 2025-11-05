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
