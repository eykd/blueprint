"""Tests for taggables module."""

import blueprint
from blueprint import taggables


class TestResolveTagsFunction:
    """Test the resolve_tags function."""

    def test_resolve_tags_single_tag(self) -> None:
        """Test resolving a single tag."""
        result = taggables.resolve_tags('foo')
        assert result == {'foo'}

    def test_resolve_tags_space_separated(self) -> None:
        """Test resolving space-separated tags."""
        result = taggables.resolve_tags('foo bar baz')
        assert result == {'foo', 'bar', 'baz'}

    def test_resolve_tags_multiple_args(self) -> None:
        """Test resolving multiple tag arguments."""
        result = taggables.resolve_tags('foo bar', 'baz qux')
        assert result == {'foo', 'bar', 'baz', 'qux'}


class TestAbstractTagSet:
    """Test AbstractTagSet base class."""

    def test_abstract_tag_set_iter(self, repo: taggables.TagRepository) -> None:
        """Test that __iter__ calls all()."""
        result = list(repo)
        all_items = list(repo.all())
        assert len(result) == len(all_items)

    def test_abstract_tag_set_all_not_implemented(self) -> None:
        """Test that all() raises NotImplementedError in base class."""
        ts = taggables.AbstractTagSet()
        try:
            ts.all()
            raise AssertionError('Should have raised NotImplementedError')
        except NotImplementedError:
            pass

    def test_abstract_tag_set_query_tag_not_implemented(self) -> None:
        """Test that query_tag() raises NotImplementedError in base class."""
        ts = taggables.AbstractTagSet()
        try:
            ts.query_tag('foo')
            raise AssertionError('Should have raised NotImplementedError')
        except NotImplementedError:
            pass

    def test_query_tags_intersection_with_no_tags(self, repo: taggables.TagRepository) -> None:
        """Test intersection query with no tags returns empty TagSet."""
        result = repo.query_tags_intersection()
        assert isinstance(result, taggables.TagSet)

    def test_query_without_args_returns_all(self, repo: taggables.TagRepository) -> None:
        """Test query without args returns all objects."""
        result = repo.query()
        assert len(result) == len(repo.all())

    def test_query_with_or_tags_only(
        self, repo: taggables.TagRepository, t1: taggables.Taggable, t2: taggables.Taggable
    ) -> None:
        """Test query with only or_tags."""
        result = repo.query(or_tags=['foo'])
        assert t1 in result
        assert t2 in result

    def test_query_with_not_tags_only(
        self, repo: taggables.TagRepository, t1: taggables.Taggable, t4: taggables.Taggable
    ) -> None:
        """Test query with only not_tags."""
        result = repo.query(not_tags=['bar'])
        assert t1 in result
        assert t4 in result

    def test_select_single_match(self, repo: taggables.TagRepository, t4: taggables.Taggable) -> None:
        """Test select with single matching object."""
        result = repo.select(with_tags=['boo'])
        assert result == t4

    def test_select_with_or_tags(self, repo: taggables.TagRepository) -> None:
        """Test select with optional tags affects ranking."""
        result = repo.select(with_tags=['foo'], or_tags=['bar', 'baz'])
        assert result is not None
        assert 'foo' in result.tags

    def test_select_with_not_tags(self, repo: taggables.TagRepository) -> None:
        """Test select excludes objects with not_tags."""
        result = repo.select(with_tags=['foo'], not_tags=['baz'])
        assert result is not None
        assert 'baz' not in result.tags

    def test_select_updates_last_picked(self, repo: taggables.TagRepository) -> None:
        """Test select updates last_picked timestamp."""
        obj = repo.select(with_tags=['boo'])
        assert obj.last_picked > 0

    def test_select_prefers_least_recently_used(self, repo: taggables.TagRepository) -> None:
        """Test select prefers least recently used object."""
        # Mark one object as recently picked
        t2 = repo.query_tag('foo').query_tag('bar')
        next(iter(t2)).last_picked = 9999999999.0

        # Select should prefer other objects
        result = repo.select(with_tags=['foo', 'bar'])
        assert result.last_picked < 9999999999.0


class TestTaggable:
    """Test Taggable class."""

    def test_taggable_initialization(self) -> None:
        """Test creating a Taggable."""
        repo = taggables.TagRepository()
        t = taggables.Taggable(repo, 'foo', 'bar')
        assert 'foo' in t.tags
        assert 'bar' in t.tags
        assert t.tag_repo == repo

    def test_taggable_repr(self) -> None:
        """Test Taggable __repr__ method."""
        repo = taggables.TagRepository()
        t = taggables.Taggable(repo, 'foo', 'bar')
        r = repr(t)
        assert 'Taggable' in r
        assert 'foo' in r or 'bar' in r

    def test_taggable_tag_repo_property(self) -> None:
        """Test tag_repo property getter."""
        repo = taggables.TagRepository()
        t = taggables.Taggable(repo, 'foo')
        assert t.tag_repo == repo

    def test_taggable_tag_repo_setter_with_different_repo(self) -> None:
        """Test setting tag_repo to different repository."""
        repo1 = taggables.TagRepository()
        repo2 = taggables.TagRepository()
        t = taggables.Taggable(repo1, 'foo')

        # Change to different repo
        t.tag_repo = repo2

        assert t.tag_repo == repo2
        assert t in repo2.query_tag('foo')
        assert t not in repo1.query_tag('foo')

    def test_taggable_tag_repo_setter_with_none(self) -> None:
        """Test setting tag_repo to None."""
        repo = taggables.TagRepository()
        t = taggables.Taggable(repo, 'foo')

        # Set to None
        t.tag_repo = None

        assert t.tag_repo is None

    def test_taggable_tag_repo_setter_with_same_repo(self) -> None:
        """Test setting tag_repo to same repository."""
        repo = taggables.TagRepository()
        t = taggables.Taggable(repo, 'foo')

        # Set to same repo (should be no-op)
        t.tag_repo = repo

        assert t.tag_repo == repo

    def test_taggable_add_tag(self, t1: taggables.Taggable) -> None:
        """Test adding tags to a taggable."""
        t1.add_tag('new_tag')
        assert 'new_tag' in t1.tags

    def test_taggable_add_tag_without_repo(self) -> None:
        """Test adding tag without repo does nothing."""
        t = taggables.Taggable(None, 'foo')
        t.add_tag('bar')
        # Should not raise error but tag won't be added to repo

    def test_taggable_remove_tag(self, t2: taggables.Taggable) -> None:
        """Test removing tags from a taggable."""
        t2.remove_tag('bar')
        assert 'bar' not in t2.tags

    def test_taggable_remove_tag_without_repo(self) -> None:
        """Test removing tag without repo does nothing."""
        t = taggables.Taggable(None, 'foo', 'bar')
        t.remove_tag('bar')
        # Should not raise error

    def test_taggable_eq(self, repo: taggables.TagRepository) -> None:
        """Test Taggable equality based on tags."""
        t1 = taggables.Taggable(repo, 'foo', 'bar')
        t2 = taggables.Taggable(repo, 'bar', 'foo')
        assert t1 == t2

    def test_taggable_eq_with_non_taggable(self, t1: taggables.Taggable) -> None:
        """Test Taggable equality with non-taggable returns NotImplemented."""
        result = t1.__eq__('not a taggable')
        assert result == NotImplemented

    def test_taggable_lt(self, repo: taggables.TagRepository) -> None:
        """Test Taggable less than comparison."""
        t1 = taggables.Taggable(repo, 'aaa')
        t2 = taggables.Taggable(repo, 'bbb')
        assert t1 < t2

    def test_taggable_lt_with_non_taggable(self, t1: taggables.Taggable) -> None:
        """Test Taggable less than with non-taggable returns NotImplemented."""
        result = t1.__lt__('not a taggable')
        assert result == NotImplemented

    def test_taggable_hash(self, t1: taggables.Taggable) -> None:
        """Test Taggable hashing."""
        h = hash(t1)
        assert isinstance(h, int)


class TestTaggableClass:
    """Test TaggableClass."""

    def test_taggable_class_add_tag(self) -> None:
        """Test adding tags to a class."""

        class Item(blueprint.Blueprint):
            value = 1

        original_tags = Item.tags.copy()  # type: ignore[union-attr]
        Item.add_tag('custom_tag')
        assert 'custom_tag' in Item.tags
        assert len(Item.tags) == len(original_tags) + 1

    def test_taggable_class_remove_tag(self) -> None:
        """Test removing tags from a class."""

        class Item(blueprint.Blueprint):
            tags = 'foo bar'  # type: ignore[assignment]
            value = 1

        Item.remove_tag('foo')
        assert 'foo' not in Item.tags


class TestTagRepository:
    """Test TagRepository class."""

    def test_tag_repository_initialization_with_objects(self) -> None:
        """Test creating a TagRepository with initial objects."""
        t1 = taggables.Taggable(None, 'foo')
        t2 = taggables.Taggable(None, 'bar')
        repo = taggables.TagRepository(t1, t2)

        assert t1 in repo.all()
        assert t2 in repo.all()

    def test_tag_repository_add_object_with_check_repo_false(self) -> None:
        """Test add_object with check_repo=False."""
        repo = taggables.TagRepository()
        t = taggables.Taggable(None, 'foo')
        repo.add_object(t, check_repo=False)

        assert t in repo.query_tag('foo')
        assert t.tag_repo is None

    def test_tag_repository_remove_object(self, repo: taggables.TagRepository, t1: taggables.Taggable) -> None:
        """Test removing object from repository."""
        repo.remove_object(t1)
        assert t1 not in repo.all()

    def test_tag_repository_remove_nonexistent_object(self, repo: taggables.TagRepository) -> None:
        """Test removing non-existent object doesn't raise error."""
        t = taggables.Taggable(None, 'nonexistent')
        repo.remove_object(t)
        # Should not raise error

    def test_tag_repository_add_tags(self, repo: taggables.TagRepository) -> None:
        """Test adding tags to repository."""
        repo.add_tags('new_tag1', 'new_tag2')
        # Tags should exist in repo even if empty
        assert 'new_tag1' in repo.tag_objs
        assert 'new_tag2' in repo.tag_objs

    def test_tag_repository_tag_object(self, repo: taggables.TagRepository, t1: taggables.Taggable) -> None:
        """Test tagging an object."""
        repo.tag_object(t1, 'new_tag')
        assert 'new_tag' in t1.tags
        # Check that t1 is in the results by checking the set contains an item with matching tags
        results = repo.query_tag('new_tag')
        assert any(item.tags == t1.tags for item in results)

    def test_tag_repository_untag_object(self, repo: taggables.TagRepository, t2: taggables.Taggable) -> None:
        """Test untagging an object."""
        repo.untag_object(t2, 'bar')
        assert 'bar' not in t2.tags

    def test_tag_repository_untag_nonexistent_tag(self, repo: taggables.TagRepository, t1: taggables.Taggable) -> None:
        """Test untagging non-existent tag doesn't raise error."""
        repo.untag_object(t1, 'nonexistent')
        # Should not raise error

    def test_tag_repository_all(self, repo: taggables.TagRepository) -> None:
        """Test getting all objects from repository."""
        all_objs = repo.all()
        assert isinstance(all_objs, taggables.TagSet)
        assert len(all_objs) > 0

    def test_tag_repository_query_tag(self, repo: taggables.TagRepository, t1: taggables.Taggable) -> None:
        """Test querying by single tag."""
        result = repo.query_tag('foo')
        assert t1 in result


class TestTagSet:
    """Test TagSet class."""

    def test_tag_set_all(self, t1: taggables.Taggable, t2: taggables.Taggable) -> None:
        """Test TagSet all() returns self."""
        ts = taggables.TagSet([t1, t2])
        assert ts.all() is ts

    def test_tag_set_query_tag(self, t1: taggables.Taggable, t2: taggables.Taggable, t3: taggables.Taggable) -> None:
        """Test TagSet query_tag method."""
        ts = taggables.TagSet([t1, t2, t3])
        result = ts.query_tag('bar')
        assert t1 not in result
        assert t2 in result
        assert t3 in result

    def test_tag_set_query_tags_union(
        self, t1: taggables.Taggable, t2: taggables.Taggable, t4: taggables.Taggable
    ) -> None:
        """Test TagSet union query."""
        ts = taggables.TagSet([t1, t2, t4])
        result = ts.query_tags_union('foo', 'boo')
        assert len(result) == 3

    def test_tag_set_query_tags_difference(self, t1: taggables.Taggable, t2: taggables.Taggable) -> None:
        """Test TagSet difference query."""
        ts = taggables.TagSet([t1, t2])
        result = ts.query_tags_difference('bar')
        assert t1 in result
        assert t2 not in result
