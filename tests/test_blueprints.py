"""Tests for blueprint class behavior.

Converted from features/blueprints.feature
"""

import blueprint


class TestBlueprintSubclassing:
    """Tests for subclassing Blueprint.

    Scenario: Subclassing Blueprint
    """

    def test_blueprint_has_tag_repository(self, item: type[blueprint.Blueprint]) -> None:
        """Blueprint subclass should have a tag repository."""
        assert hasattr(item, 'tag_repo')

    def test_blueprint_tagged_with_class_name(self, item: type[blueprint.Blueprint]) -> None:
        """Blueprint subclass should be tagged with its class name."""
        assert 'Item' in item.tags

    def test_blueprint_has_defined_tags(self, item: type[blueprint.Blueprint]) -> None:
        """Blueprint subclass should have any other defined tags."""
        assert 'foo' in item.tags
        assert 'bar' in item.tags


class TestItemSubclassing:
    """Tests for subclassing an Item.

    Scenario: Subclassing an Item
    """

    def test_item_has_tag_repository(self, weapon: type[blueprint.Blueprint]) -> None:
        """Item subclass should have a tag repository."""
        assert hasattr(weapon, 'tag_repo')

    def test_item_shares_tag_repository(
        self, item: type[blueprint.Blueprint], weapon: type[blueprint.Blueprint]
    ) -> None:
        """Item subclass tag repository should be the same as Item's."""
        assert weapon.tag_repo is item.tag_repo

    def test_item_tagged_with_class_name(self, weapon: type[blueprint.Blueprint]) -> None:
        """Item subclass should be tagged with its class name."""
        assert 'Weapon' in weapon.tags

    def test_item_inherits_tags(self, weapon: type[blueprint.Blueprint]) -> None:
        """Item subclass should inherit tags from Item."""
        assert 'Item' in weapon.tags
        assert 'foo' in weapon.tags
        assert 'bar' in weapon.tags

    def test_item_has_defined_tags(self, weapon: type[blueprint.Blueprint]) -> None:
        """Item subclass should have any other defined tags."""
        assert 'dangerous' in weapon.tags


class TestBlueprintSelection:
    """Tests for selecting blueprints by tag.

    Scenario: Selecting blueprints by tag
    """

    def test_query_weapon_subclasses_by_tag(
        self,
        item: type[blueprint.Blueprint],
        spear: type[blueprint.Blueprint],
        pointed_stick: type[blueprint.Blueprint],
        club: type[blueprint.Blueprint],
    ) -> None:
        """Should be able to query Weapon subclasses by tag."""
        repo = item.tag_repo
        assert repo is not None
        q = repo.query_tags_union('Weapon', 'primitive')

        assert spear in q  # type: ignore[comparison-overlap]
        assert pointed_stick in q  # type: ignore[comparison-overlap]
        assert club in q  # type: ignore[comparison-overlap]

    def test_select_weapon_subclass_by_tag(
        self,
        item: type[blueprint.Blueprint],
        spear: type[blueprint.Blueprint],
        pointed_stick: type[blueprint.Blueprint],
        club: type[blueprint.Blueprint],
    ) -> None:
        """Should be able to select a Weapon subclass by tag."""
        repo = item.tag_repo
        assert repo is not None
        q = repo.query_tags_union('Weapon', 'primitive')

        assert spear in q  # type: ignore[comparison-overlap]
        assert pointed_stick in q  # type: ignore[comparison-overlap]
        assert club in q  # type: ignore[comparison-overlap]

        old_weapon = None
        for _ in range(10):
            weapon = repo.select(with_tags=('Weapon', 'primitive'))
            assert weapon in {spear, pointed_stick, club}  # type: ignore[comparison-overlap]
            assert weapon is not old_weapon
            old_weapon = weapon
