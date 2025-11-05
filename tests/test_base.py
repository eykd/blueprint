"""Tests for base blueprint functionality."""

import copy

import blueprint


class TestMeta:
    """Test Meta class."""

    def test_meta_initialization(self) -> None:
        """Test Meta initialization."""
        from blueprint.base import Meta

        meta = Meta()
        assert meta.fields == set()
        assert meta.mastered is False
        assert meta.abstract is False
        assert meta.source is None
        assert meta.parent is None
        assert meta.random is not None
        assert isinstance(meta.seed, float)

    def test_meta_deepcopy(self) -> None:
        """Test Meta __deepcopy__ method."""
        from blueprint.base import Meta

        meta1 = Meta()
        meta1.fields.add('test_field')
        meta1.mastered = True
        meta1.abstract = True

        memo: dict[int, object] = {}
        meta2 = copy.deepcopy(meta1, memo)

        assert meta2.fields == meta1.fields
        assert meta2.mastered == meta1.mastered
        assert meta2.abstract == meta1.abstract
        # Random should be a new instance
        assert meta2.random is not meta1.random

    def test_meta_deepcopy_with_memo(self) -> None:
        """Test Meta __deepcopy__ with existing memo."""
        from blueprint.base import Meta

        meta1 = Meta()
        memo: dict[int, object] = {}

        # First copy
        meta2 = copy.deepcopy(meta1, memo)
        # Second copy with same memo should return same object
        meta3 = copy.deepcopy(meta1, memo)

        assert meta2 is meta3

    def test_meta_deepcopy_preserves_source_and_parent(self) -> None:
        """Test that deepcopy preserves source and parent without copying."""
        from blueprint.base import Meta

        class Item(blueprint.Blueprint):
            value = 1

        parent = Item()
        source = Item

        meta1 = Meta()
        meta1.parent = parent
        meta1.source = source

        meta2 = copy.deepcopy(meta1)

        # Source and parent should be same objects
        assert meta2.parent is parent
        assert meta2.source is source


class TestBlueprintMeta:
    """Test BlueprintMeta metaclass."""

    def test_blueprint_meta_tags_string_conversion(self) -> None:
        """Test that string tags are converted to set."""

        class TestItem(blueprint.Blueprint):
            tags = 'foo bar baz'  # type: ignore[assignment]
            value = 1

        assert isinstance(TestItem.tags, set)
        assert 'foo' in TestItem.tags

    def test_blueprint_meta_inherits_base_tags(self, item: type[blueprint.Blueprint]) -> None:
        """Test that blueprint inherits tags from base class."""

        class ExtendedItem(item):  # type: ignore[misc, valid-type]
            tags = 'extra'

        assert 'foo' in ExtendedItem.tags
        assert 'bar' in ExtendedItem.tags
        assert 'extra' in ExtendedItem.tags

    def test_blueprint_meta_auto_name(self) -> None:
        """Test that name is auto-generated from class name."""

        class MySpecialItem(blueprint.Blueprint):
            value = 1

        assert MySpecialItem.name == 'My Special Item'

    def test_blueprint_meta_custom_name(self) -> None:
        """Test that custom name overrides auto-generated name."""

        class MyItem(blueprint.Blueprint):
            name = 'Custom Name'
            value = 1

        assert MyItem.name == 'Custom Name'

    def test_blueprint_meta_repr(self) -> None:
        """Test BlueprintMeta __repr__ method."""

        class Item(blueprint.Blueprint):
            value = 1
            name = 'test'

        r = repr(Item)
        assert 'Item' in r
        assert 'value' in r or 'name' in r

    def test_blueprint_meta_add_to_class(self) -> None:
        """Test add_to_class method."""
        from blueprint.base import BlueprintMeta

        class TestClass:
            pass

        # Create a mock metaclass instance
        class TestMeta(BlueprintMeta):
            pass

        class TestBlueprint(blueprint.Blueprint, metaclass=TestMeta):
            pass

        # Test with regular value
        TestMeta.add_to_class(TestBlueprint, 'test_attr', 42)
        assert TestBlueprint.test_attr == 42  # type: ignore[attr-defined]

    def test_blueprint_meta_add_to_class_with_contribute(self) -> None:
        """Test add_to_class with object that has contribute_to_class."""

        class ContributingField:
            def contribute_to_class(self, cls: type, name: str) -> None:
                setattr(cls, name, f'contributed_{name}')

        class TestBlueprint(blueprint.Blueprint):
            pass

        field = ContributingField()
        TestBlueprint.add_to_class('test_field', field)
        assert TestBlueprint.test_field == 'contributed_test_field'  # type: ignore[attr-defined]


class TestBlueprint:
    """Test Blueprint class."""

    def test_blueprint_repr(self) -> None:
        """Test Blueprint __repr__ method."""

        class Item(blueprint.Blueprint):
            value = 10
            name = 'Test Item'

        item = Item()
        r = repr(item)
        assert 'Item' in r
        assert 'value' in r or 'name' in r

    def test_blueprint_init_with_parent(self) -> None:
        """Test Blueprint initialization with parent."""

        class Container(blueprint.Blueprint):
            name = 'Container'

        class Item(blueprint.Blueprint):
            value = 10

        container = Container()
        item = Item(parent=container)

        assert item.meta.parent == container

    def test_blueprint_init_with_seed(self) -> None:
        """Test Blueprint initialization with custom seed."""

        class Item(blueprint.Blueprint):
            value = blueprint.RandomInt(1, 100)

        item1 = Item(seed=12345)
        item2 = Item(seed=12345)

        assert item1.value == item2.value

    def test_blueprint_init_with_parent_inherits_seed(self) -> None:
        """Test Blueprint inherits seed from parent."""

        class Container(blueprint.Blueprint):
            pass

        class Item(blueprint.Blueprint):
            value = blueprint.RandomInt(1, 100)

        container = Container(seed=99999)
        item = Item(parent=container)

        assert item.meta.seed == container.meta.seed

    def test_blueprint_init_with_kwargs(self) -> None:
        """Test Blueprint initialization with kwargs."""

        class Item(blueprint.Blueprint):
            value = 10

        item = Item(value=20, extra='test')

        assert item.value == 20
        assert item.extra == 'test'  # type: ignore[attr-defined]

    def test_blueprint_field_resolution_order(self) -> None:
        """Test that fields are resolved in correct order."""

        class Item(blueprint.Blueprint):
            a = 10
            b = blueprint.depends_on('a')(lambda self: self.a * 2)
            c = blueprint.depends_on('b')(lambda self: self.b + 5)

        item = Item()
        assert item.a == 10
        assert item.b == 20  # type: ignore[comparison-overlap]
        assert item.c == 25  # type: ignore[comparison-overlap]

    def test_blueprint_defer_to_end_fields(self) -> None:
        """Test that defer_to_end fields are resolved last."""

        class Item(blueprint.Blueprint):
            a = 10
            b = blueprint.defer_to_end(lambda self: self.a + self.c)
            c = 20

        item = Item()
        assert item.b == 30  # type: ignore[comparison-overlap]

    def test_blueprint_as_dict_generator(self) -> None:
        """Test as_dict generator method."""

        class Item(blueprint.Blueprint):
            value = 10
            name = 'Test'

        item = Item()
        d = item.as_dict()

        assert isinstance(d, dict)
        assert d['value'] == 10
        assert d['name'] == 'Test'

    def test_blueprint_meta_fields_inheritance(self, item: type[blueprint.Blueprint]) -> None:
        """Test that meta fields are inherited from base classes."""

        class ExtendedItem(item):  # type: ignore[misc, valid-type]
            extra = 100

        # Check that fields from base class are included
        assert 'value' in ExtendedItem.meta.fields
        assert 'extra' in ExtendedItem.meta.fields

    def test_blueprint_generator_methods_not_treated_as_fields(self) -> None:
        """Test that generator methods are not treated as fields."""

        class Item(blueprint.Blueprint):
            value = 10

            @blueprint.generator
            def make_items(self) -> list[int]:
                return [self.value] * 3

        item = Item()
        # make_items should be callable, not resolved
        assert callable(item.make_items)
        result = item.make_items()
        assert result == [10, 10, 10]

    def test_blueprint_deferred_dependency_resolution(self) -> None:
        """Test that fields with dependencies are deferred and resolved correctly."""

        class Item(blueprint.Blueprint):
            # b depends on a, but b is listed first in meta.fields due to declaration order
            b = blueprint.depends_on('a')(lambda self: self.a * 2)
            a = 5

        item = Item()
        # a should be resolved first, then b from the deferred queue
        assert item.a == 5
        assert item.b == 10  # type: ignore[comparison-overlap]

    def test_blueprint_with_user_meta_options(self) -> None:
        """Test Blueprint with custom Meta options."""

        class Item(blueprint.Blueprint):
            value = 10

            class Meta:
                abstract = True
                custom_option = 'test'

        assert Item.meta.abstract is True
        assert Item.meta.custom_option == 'test'  # type: ignore[attr-defined]
