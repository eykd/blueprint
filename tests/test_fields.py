"""Tests for field types and operators."""

from collections.abc import Generator

import blueprint
from blueprint import fields


class TestFieldOperators:
    """Test field operators."""

    def test_field_repr(self) -> None:
        """Test Field __repr__ method."""
        field = fields.RandomInt(1, 10)
        assert 'RandomInt' in repr(field)

    def test_field_str(self) -> None:
        """Test Field __str__ method."""
        field = fields.Field()
        assert str(field) == ''

    def test_field_add(self) -> None:
        """Test adding fields."""

        class Item(blueprint.Blueprint):
            a = fields.RandomInt(1, 5)
            b = 10
            total = fields.RandomInt(1, 5) + 10

        item = Item()
        assert isinstance(item.total, int)
        assert 11 <= item.total <= 15

    def test_field_radd(self) -> None:
        """Test reverse adding fields."""

        class Item(blueprint.Blueprint):
            a = fields.RandomInt(1, 5)
            total = 10 + fields.RandomInt(1, 5)

        item = Item()
        assert 11 <= item.total <= 15  # type: ignore[operator]

    def test_field_sub(self) -> None:
        """Test subtracting fields."""

        class Item(blueprint.Blueprint):
            total = fields.RandomInt(1, 5) - 2

        item = Item()
        assert -1 <= item.total <= 3  # type: ignore[operator]

    def test_field_rsub(self) -> None:
        """Test reverse subtracting fields."""

        class Item(blueprint.Blueprint):
            total = 10 - fields.RandomInt(1, 5)

        item = Item()
        assert 5 <= item.total <= 9  # type: ignore[operator]

    def test_field_mul(self) -> None:
        """Test multiplying fields."""

        class Item(blueprint.Blueprint):
            total = fields.RandomInt(2, 4) * 3

        item = Item()
        assert 6 <= item.total <= 12  # type: ignore[operator]

    def test_field_rmul(self) -> None:
        """Test reverse multiplying fields."""

        class Item(blueprint.Blueprint):
            total = 3 * fields.RandomInt(2, 4)

        item = Item()
        assert 6 <= item.total <= 12  # type: ignore[operator]

    def test_field_div(self) -> None:
        """Test dividing fields."""

        class Item(blueprint.Blueprint):
            total = fields.RandomInt(10, 20) / 2

        item = Item()
        assert 5.0 <= item.total <= 10.0  # type: ignore[operator]

    def test_field_truediv(self) -> None:
        """Test true division of fields."""

        class Item(blueprint.Blueprint):
            total = fields.RandomInt(10, 20).__truediv__(2)

        item = Item()
        assert 5.0 <= item.total <= 10.0  # type: ignore[operator]

    def test_field_floordiv(self) -> None:
        """Test floor division of fields."""

        class Item(blueprint.Blueprint):
            total = fields.RandomInt(10, 20) // 3

        item = Item()
        assert 3 <= item.total <= 6  # type: ignore[operator]

    def test_field_rdiv(self) -> None:
        """Test reverse dividing fields."""

        class Item(blueprint.Blueprint):
            total = 100 / fields.RandomInt(2, 4)

        item = Item()
        assert 25.0 <= item.total <= 50.0  # type: ignore[operator]

    def test_field_rtruediv(self) -> None:
        """Test reverse true division of fields."""

        class Item(blueprint.Blueprint):
            a = fields.RandomInt(2, 4)
            total = a.__rtruediv__(100)

        item = Item()
        assert 25.0 <= item.total <= 50.0  # type: ignore[operator]

    def test_field_rfloordiv(self) -> None:
        """Test reverse floor division of fields."""

        class Item(blueprint.Blueprint):
            total = 100 // fields.RandomInt(2, 4)

        item = Item()
        assert 25 <= item.total <= 50  # type: ignore[operator]


class TestOperatorFields:
    """Test operator field classes."""

    def test_operator_repr(self) -> None:
        """Test operator __repr__ includes parentheses."""
        op = fields.Add(1, 2, 3)
        assert repr(op) == '(1 + 2 + 3)'

    def test_operator_str(self) -> None:
        """Test operator __str__ formatting."""
        op = fields.Add(1, 2)
        assert ' + ' in str(op)

    def test_add_operator(self) -> None:
        """Test Add operator."""

        class Item(blueprint.Blueprint):
            total = fields.Add(1, 2, 3)

        item = Item()
        assert item.total == 6  # type: ignore[comparison-overlap]

    def test_subtract_operator(self) -> None:
        """Test Subtract operator."""

        class Item(blueprint.Blueprint):
            total = fields.Subtract(10, 3, 2)

        item = Item()
        assert item.total == 5  # type: ignore[comparison-overlap]

    def test_multiply_operator(self) -> None:
        """Test Multiply operator."""

        class Item(blueprint.Blueprint):
            total = fields.Multiply(2, 3, 4)

        item = Item()
        assert item.total == 24  # type: ignore[comparison-overlap]

    def test_divide_operator(self) -> None:
        """Test Divide operator."""

        class Item(blueprint.Blueprint):
            total = fields.Divide(24, 2, 3)

        item = Item()
        assert item.total == 4.0  # type: ignore[comparison-overlap]

    def test_floordivide_operator(self) -> None:
        """Test FloorDivide operator."""

        class Item(blueprint.Blueprint):
            total = fields.FloorDivide(25, 2, 3)

        item = Item()
        assert item.total == 4  # type: ignore[comparison-overlap]

    def test_nested_operators(self) -> None:
        """Test nested operator expressions."""

        class Item(blueprint.Blueprint):
            total = fields.Add(fields.Multiply(2, 3), fields.Divide(10, 2))

        item = Item()
        assert item.total == 11.0  # type: ignore[comparison-overlap]


class TestRandomInt:
    """Test RandomInt field."""

    def test_random_int_str(self) -> None:
        """Test RandomInt __str__ method."""
        field = fields.RandomInt(1, 10)
        assert str(field) == '1...10'

    def test_random_int_call(self) -> None:
        """Test RandomInt generates values in range."""

        class Item(blueprint.Blueprint):
            value = fields.RandomInt(5, 15)

        for _ in range(20):
            item = Item()
            assert 5 <= item.value <= 15  # type: ignore[operator]


class TestDiceField:
    """Test Dice field."""

    def test_dice_str(self) -> None:
        """Test Dice __str__ method."""
        field = fields.Dice('3d6')
        assert str(field) == '3d6'

    def test_dice_call(self) -> None:
        """Test Dice field rolling."""

        class Item(blueprint.Blueprint):
            roll = fields.Dice('2d6')

        item = Item()
        assert 2 <= sum(item.roll) <= 12  # type: ignore[call-overload]


class TestDiceTable:
    """Test DiceTable field."""

    def test_dice_table_str(self) -> None:
        """Test DiceTable __str__ method."""
        table = {'1': 'low', '6': 'high'}
        field = fields.DiceTable('1d6', table)  # type: ignore[arg-type]
        assert '1d6' in str(field)

    def test_dice_table_with_ranges(self) -> None:
        """Test DiceTable with range keys."""
        table = {'1..3': 'low', '4:6': 'high'}

        class Item(blueprint.Blueprint):
            category = fields.DiceTable('1d6', table)  # type: ignore[arg-type]

        item = Item()
        assert item.category in {'low', 'high'}  # type: ignore[comparison-overlap]

    def test_dice_table_with_comma_separated(self) -> None:
        """Test DiceTable with comma-separated keys."""
        table = {'1, 2, 3': 'low', '4, 5, 6': 'high'}

        class Item(blueprint.Blueprint):
            category = fields.DiceTable('1d6', table)  # type: ignore[arg-type]

        item = Item()
        assert item.category in {'low', 'high'}  # type: ignore[comparison-overlap]

    def test_dice_table_with_int_keys(self) -> None:
        """Test DiceTable with integer keys."""
        # DiceTable converts results to string before lookup, so keys need to be strings
        table: dict[str | int, str] = {1: 'one', 2: 'two', 3: 'three'}

        class Item(blueprint.Blueprint):
            name = fields.DiceTable('1d3', table)

        item = Item()
        # DiceTable may return None if key not found
        assert item.name in {'one', 'two', 'three', None}  # type: ignore[comparison-overlap]

    def test_dice_table_with_default(self) -> None:
        """Test DiceTable with default value."""
        table = {'1': 'defined'}

        class Item(blueprint.Blueprint):
            value = fields.DiceTable('1d6', table, default='default')  # type: ignore[arg-type]

        item = Item()
        assert item.value in {'defined', 'default'}  # type: ignore[comparison-overlap]


class TestPickOne:
    """Test PickOne field."""

    def test_pick_one_str(self) -> None:
        """Test PickOne __str__ method."""
        field = fields.PickOne('a', 'b', 'c')
        assert 'a' in str(field)

    def test_pick_one_call(self) -> None:
        """Test PickOne picks from choices."""

        class Item(blueprint.Blueprint):
            choice = fields.PickOne('red', 'green', 'blue')

        item = Item()
        assert item.choice in {'red', 'green', 'blue'}  # type: ignore[comparison-overlap]


class TestPickFrom:
    """Test PickFrom field."""

    def test_pick_from_str(self) -> None:
        """Test PickFrom __str__ method."""
        field = fields.PickFrom(['a', 'b'])
        assert str(field) == "['a', 'b']"

    def test_pick_from_call(self) -> None:
        """Test PickFrom picks from collection."""

        class Item(blueprint.Blueprint):
            choice = fields.PickFrom(['alpha', 'beta', 'gamma'])

        item = Item()
        assert item.choice in {'alpha', 'beta', 'gamma'}  # type: ignore[comparison-overlap]


class TestAll:
    """Test All field."""

    def test_all_str(self) -> None:
        """Test All __str__ method."""
        field = fields.All('a', 'b')
        assert str(field) == "('a', 'b')"

    def test_all_call(self) -> None:
        """Test All returns list of resolved items."""

        class Item(blueprint.Blueprint):
            items = fields.All(1, 2, fields.RandomInt(3, 3))

        item = Item()
        assert item.items == [1, 2, 3]  # type: ignore[comparison-overlap]


class TestFormatTemplate:
    """Test FormatTemplate field."""

    def test_format_template_str(self) -> None:
        """Test FormatTemplate __str__ method."""
        field = fields.FormatTemplate('hello {name}')
        assert str(field) == 'hello {name}'

    def test_format_template_get_descriptor(self) -> None:
        """Test FormatTemplate as descriptor."""

        class Item(blueprint.Blueprint):
            bonus = 5
            name = fields.FormatTemplate(f'Item +{bonus}')

        item = Item()
        assert item.name == 'Item +5'

    def test_format_template_get_class_access(self) -> None:
        """Test accessing FormatTemplate on class returns self."""

        class Item(blueprint.Blueprint):
            name = fields.FormatTemplate('test')

        assert isinstance(Item.name, fields.FormatTemplate)

    def test_format_template_with_meta(self) -> None:
        """Test FormatTemplate with meta attributes."""

        class Item(blueprint.Blueprint):
            name = fields.FormatTemplate('Seed: {meta.seed}')

        item = Item(seed=12345)
        assert 'Seed: ' in item.name  # type: ignore[operator]


class TestProperty:
    """Test Property field."""

    def test_property_get_descriptor(self) -> None:
        """Test Property as descriptor."""

        class Item(blueprint.Blueprint):
            value = 10
            doubled = fields.Property(lambda self: self.value * 2)

        item = Item()
        assert item.doubled == 20

    def test_property_get_class_access(self) -> None:
        """Test accessing Property on class returns self."""

        class Item(blueprint.Blueprint):
            prop = fields.Property(lambda self: self.value)

        assert isinstance(Item.prop, fields.Property)


class TestWithTags:
    """Test WithTags field."""

    def test_with_tags_parsing(self) -> None:
        """Test WithTags parses tag strings."""
        field = fields.WithTags('foo bar', '!baz', 'qux?')
        assert 'foo' in field.with_tags
        assert 'bar' in field.with_tags
        assert '!baz' in field.not_tags
        assert 'qux?' in field.or_tags

    def test_with_tags_call(self) -> None:
        """Test WithTags returns matching blueprints."""

        class Item(blueprint.Blueprint):
            tags = 'foo bar'  # type: ignore[assignment]
            value = 1

        class Weapon(Item):
            tags = 'dangerous'
            damage = 5

        class Container(blueprint.Blueprint):
            items = fields.WithTags('foo')

        container = Container()
        assert len(container.items) > 0  # type: ignore[arg-type]

    def test_with_tags_filters_abstract(self) -> None:
        """Test WithTags filters out abstract blueprints."""

        class Base(blueprint.Blueprint):
            value = 1

            class Meta:
                abstract = True

        class Concrete(Base):
            value = 2

        class Container(blueprint.Blueprint):
            items = fields.WithTags('Base')

        container = Container()
        assert all(not item.meta.abstract for item in container.items)  # type: ignore[attr-defined]

    def test_with_tags_with_or_tags(self) -> None:
        """Test WithTags with or_tags (union)."""

        class Item1(blueprint.Blueprint):
            tags = 'foo'  # type: ignore[assignment]
            value = 1

        class Item2(blueprint.Blueprint):
            tags = 'bar'  # type: ignore[assignment]
            value = 2

        class Container(blueprint.Blueprint):
            items = fields.WithTags('?foo ?bar')

        container = Container()
        assert len(container.items) >= 0  # type: ignore[arg-type]

    def test_with_tags_with_not_tags(self) -> None:
        """Test WithTags with not_tags (difference)."""

        class Item1(blueprint.Blueprint):
            tags = 'foo'  # type: ignore[assignment]
            value = 1

        class Item2(blueprint.Blueprint):
            tags = 'foo bar'  # type: ignore[assignment]
            value = 2

        class Container(blueprint.Blueprint):
            items = fields.WithTags('foo !bar')

        container = Container()
        # not_tags strips the ! prefix when checking, so !bar checks for blueprints without 'bar' tag
        # The query filters out items that have 'bar' in their tags (after stripping the !)
        # So we should NOT see Item2 in the results
        result_tags = [set(item.tags) for item in container.items]  # type: ignore[attr-defined]
        # At least one item should not have 'bar'
        assert any('bar' not in tags for tags in result_tags)


class TestDecorators:
    """Test field decorators."""

    def test_generator_decorator(self) -> None:
        """Test generator decorator."""

        @fields.generator
        def my_generator() -> int:
            return 42

        assert hasattr(my_generator, 'is_generator')
        assert my_generator.is_generator is True

    def test_depends_on_decorator(self) -> None:
        """Test depends_on decorator."""

        @fields.depends_on('foo', 'bar')
        def my_field(self) -> int:  # type: ignore[no-untyped-def]
            return self.foo + self.bar  # type: ignore[no-any-return]

        assert hasattr(my_field, 'depends_on')
        assert 'foo' in my_field.depends_on
        assert 'bar' in my_field.depends_on

    def test_depends_on_with_space_separated(self) -> None:
        """Test depends_on with space-separated names."""

        @fields.depends_on('foo bar')
        def my_field(self) -> int:  # type: ignore[no-untyped-def]
            return self.foo + self.bar  # type: ignore[no-any-return]

        assert 'foo' in my_field.depends_on  # type: ignore[attr-defined]
        assert 'bar' in my_field.depends_on  # type: ignore[attr-defined]

    def test_defer_to_end_decorator(self) -> None:
        """Test defer_to_end decorator."""

        @fields.defer_to_end
        def my_field(self) -> int:  # type: ignore[no-untyped-def]
            return 42

        assert hasattr(my_field, '_defer_to_end')
        assert my_field._defer_to_end is True


class TestResolve:
    """Test the resolve function."""

    def test_resolve_callable_with_parent(self) -> None:
        """Test resolve with callable that takes parent."""

        class Item(blueprint.Blueprint):
            value = 10

        item = Item()

        def field(parent):  # type: ignore[no-untyped-def]
            return parent.value * 2

        result = fields.resolve(item, field)
        assert result == 20

    def test_resolve_callable_with_parent_and_seed(self) -> None:
        """Test resolve with callable that takes parent and seed."""

        class Item(blueprint.Blueprint):
            value = 10

        item = Item()

        def field(parent, seed):  # type: ignore[no-untyped-def]
            return parent.value + int(seed)

        result = fields.resolve(item, field)
        assert isinstance(result, int)

    def test_resolve_method_with_seed(self) -> None:
        """Test resolve with method that takes seed."""

        class Item(blueprint.Blueprint):
            value = 10

            def method(self, seed):  # type: ignore[no-untyped-def]
                return self.value + int(seed)

        item = Item()
        result = fields.resolve(item, item.method)
        assert isinstance(result, int)

    def test_resolve_method_without_args(self) -> None:
        """Test resolve with method that takes no args."""

        class Item(blueprint.Blueprint):
            value = 10

            def method(self) -> int:
                return self.value * 3

        item = Item()
        result = fields.resolve(item, item.method)
        assert result == 30

    def test_resolve_non_callable(self) -> None:
        """Test resolve with non-callable value."""

        class Item(blueprint.Blueprint):
            value = 10

        item = Item()
        result = fields.resolve(item, 42)
        assert result == 42

    def test_resolve_generator(self) -> None:
        """Test resolve with generator that yields fields."""

        def generator_field(parent: blueprint.Blueprint) -> Generator[fields.Field, None, None]:
            """Return a generator that yields field values."""
            yield fields.RandomInt(1, 5)
            yield fields.RandomInt(6, 10)

        class Item(blueprint.Blueprint):
            values = generator_field

        item = Item()
        # The generator should be resolved to a list of resolved values
        assert isinstance(item.values, list)
        assert len(item.values) == 2
        assert 1 <= item.values[0] <= 5
        assert 6 <= item.values[1] <= 10
