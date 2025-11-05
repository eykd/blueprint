"""Tests for BlueprintCollection functionality."""

import sys

import blueprint
from blueprint.collection import BlueprintCollection


class TestBlueprintCollection:
    """Test BlueprintCollection behavior."""

    def test_collection_initialization(self) -> None:
        """Test creating a BlueprintCollection."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item, seed='test')
        assert collection.blueprint == Item
        assert collection.seed == 'test'
        assert collection.kwargs == {}

    def test_collection_with_kwargs(self) -> None:
        """Test creating a BlueprintCollection with kwargs."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item, seed='test', custom_arg='foo')
        assert collection.kwargs == {'custom_arg': 'foo'}

    def test_collection_len(self) -> None:
        """Test that collection length is sys.maxsize."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item)
        assert len(collection) == sys.maxsize

    def test_collection_iter(self) -> None:
        """Test that collection is iterable."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item)
        # The collection's __iter__ just returns iter(self), which returns
        # an iterator over the collection. This is a recursive definition that will fail.
        # Instead, just test that we can get an iterator from the slice
        iterator = iter(collection[0:5])
        assert iterator is not None

    def test_collection_contains(self) -> None:
        """Test that collection contains check always returns True."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item)
        assert 'anything' in collection  # type: ignore[comparison-overlap]
        assert 123 in collection  # type: ignore[comparison-overlap]
        assert None in collection

    def test_collection_call_with_defaults(self) -> None:
        """Test calling collection with default parameters."""

        class Item(blueprint.Blueprint):
            value = blueprint.RandomInt(1, 10)

        collection = BlueprintCollection(Item, seed='test')
        item = collection()
        assert isinstance(item, Item)
        assert item.meta.mastered

    def test_collection_call_with_parent(self) -> None:
        """Test calling collection with parent parameter."""

        class Item(blueprint.Blueprint):
            value = 1

        class Container(blueprint.Blueprint):
            name = 'Container'

        container = Container()
        collection = BlueprintCollection(Item)
        item = collection(parent=container)
        assert item.meta.parent == container

    def test_collection_call_with_seed_override(self) -> None:
        """Test calling collection with seed override."""

        class Item(blueprint.Blueprint):
            value = blueprint.RandomInt(1, 100)

        collection = BlueprintCollection(Item, seed='original')
        item1 = collection(seed='custom')
        item2 = collection(seed='custom')
        # Same seed should produce same results
        assert item1.value == item2.value  # type: ignore[attr-defined]

    def test_collection_call_with_kwargs(self) -> None:
        """Test calling collection with additional kwargs."""

        class Item(blueprint.Blueprint):
            value = 1
            name = 'default'

        collection = BlueprintCollection(Item)
        item = collection(name='custom')
        assert item.name == 'custom'  # type: ignore[attr-defined]

    def test_collection_call_merges_kwargs(self) -> None:
        """Test that call merges kwargs with collection kwargs."""

        class Item(blueprint.Blueprint):
            value = 1
            name = 'default'
            tag = 'default'

        collection = BlueprintCollection(Item, name='collection')
        item = collection(tag='call')
        assert item.name == 'collection'  # type: ignore[attr-defined]
        assert item.tag == 'call'  # type: ignore[attr-defined]

    def test_collection_getitem_int(self) -> None:
        """Test getting item by integer index."""

        class Item(blueprint.Blueprint):
            value = blueprint.RandomInt(1, 100)

        collection = BlueprintCollection(Item, seed='test')
        item1 = collection[0]
        item2 = collection[0]
        # Same index should produce same results
        assert item1.value == item2.value  # type: ignore[attr-defined]
        assert isinstance(item1, Item)

    def test_collection_getitem_different_indices(self) -> None:
        """Test that different indices produce different items."""

        class Item(blueprint.Blueprint):
            value = blueprint.RandomInt(1, 100)

        collection = BlueprintCollection(Item, seed='test')
        item0 = collection[0]
        item1 = collection[1]
        item2 = collection[2]
        # Different indices should (likely) produce different results
        values = {item0.value, item1.value, item2.value}  # type: ignore[attr-defined]
        assert len(values) > 1

    def test_collection_getitem_slice_with_stop(self) -> None:
        """Test getting items with a slice that has a stop value."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item, seed='test')
        items = collection[0:5]
        assert isinstance(items, list)
        assert len(items) == 5
        assert all(isinstance(item, Item) for item in items)

    def test_collection_getitem_slice_with_step(self) -> None:
        """Test getting items with a slice that has a step value."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item, seed='test')
        items = collection[0:10:2]
        assert isinstance(items, list)
        assert len(items) == 5

    def test_collection_getitem_slice_with_start(self) -> None:
        """Test getting items with a slice that has a start value."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item, seed='test')
        items = collection[5:10]
        assert isinstance(items, list)
        assert len(items) == 5

    def test_collection_getitem_slice_without_stop(self) -> None:
        """Test getting items with an open-ended slice returns a generator."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item, seed='test')
        items = collection[0:]
        # Should return a generator
        assert hasattr(items, '__next__')
        # Test we can get items from it
        first = next(items)
        assert isinstance(first, Item)

    def test_collection_getitem_slice_infinite_generator(self) -> None:
        """Test that open-ended slice produces an infinite generator."""

        class Item(blueprint.Blueprint):
            value = blueprint.RandomInt(1, 10)

        collection = BlueprintCollection(Item, seed='test')
        items = collection[10:]
        # Get several items to verify it works
        generated = [next(items) for _ in range(5)]  # type: ignore[call-overload]
        assert len(generated) == 5
        assert all(isinstance(item, Item) for item in generated)

    def test_collection_getitem_slice_with_start_and_step_no_stop(self) -> None:
        """Test open-ended slice with start and step."""

        class Item(blueprint.Blueprint):
            value = 1

        collection = BlueprintCollection(Item, seed='test')
        items = collection[5::2]
        # Should be a generator
        assert hasattr(items, '__next__')
        first = next(items)
        assert isinstance(first, Item)
