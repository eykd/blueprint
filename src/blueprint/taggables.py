"""blueprint.taggables -- tag repositories and query interface for selecting contained items."""

from __future__ import annotations

import contextlib
import functools
import itertools
import operator
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

__all__ = ['AbstractTagSet', 'TagRepository', 'TagSet', 'Taggable', 'TaggableClass', 'resolve_tags']


class TaggableProtocol(Protocol):
    """Protocol defining the interface for taggable objects."""

    tags: set[str]
    last_picked: float
    tag_repo: TagRepository | None


def resolve_tags(*tags: str) -> set[str]:
    """Resolve tags by splitting space-separated tag strings into individual tags.

    Args:
        *tags: Variable number of tag strings (may contain spaces)

    Returns:
        Set of individual tag strings

    """
    all_tags: set[str] = set()
    for t in tags:
        all_tags.update(t.split())
    return all_tags


class AbstractTagSet:
    """Define methods for interacting with a local tag set."""

    def __iter__(self) -> Iterator[TaggableProtocol]:
        """Iterate over all objects in the tag set."""
        return iter(self.all())

    def all(self) -> TagSet:
        """Return all objects in the tag set.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def query_tag(self, tag: str) -> TagSet:
        """Query for objects with a specific tag.

        This method must be implemented by subclasses.

        Args:
            tag: The tag to query for

        Returns:
            TagSet containing objects with the specified tag

        """
        raise NotImplementedError

    def query_tags_intersection(self, *tags: str) -> TagSet:
        """Query for objects that have ALL of the specified tags.

        Args:
            *tags: Variable number of tag strings (may contain spaces)

        Returns:
            TagSet containing objects that match all specified tags

        """
        objects: TagSet | None = None
        for tag in resolve_tags(*tags):
            tag_query = self.query_tag(tag)
            if objects is None:
                objects = tag_query
            objects.intersection_update(tag_query)
        return objects if objects is not None else TagSet()

    def query_tags_union(self, *tags: str) -> TagSet:
        """Query for objects that have ANY of the specified tags.

        Args:
            *tags: Variable number of tag strings (may contain spaces)

        Returns:
            TagSet containing objects that match any of the specified tags

        """
        objs = TagSet()
        for tag in resolve_tags(*tags):
            objs.update(self.query_tag(tag))
        return objs

    def query_tags_difference(self, *tags: str) -> TagSet:
        """Query for objects that do NOT have any of the specified tags.

        Args:
            *tags: Variable number of tag strings (may contain spaces)

        Returns:
            TagSet containing objects without any of the specified tags

        """
        objs = TagSet(self.all())
        for tag in resolve_tags(*tags):
            for obj in list(objs):
                if tag in obj.tags:
                    objs.remove(obj)

        return objs

    def query(
        self,
        with_tags: Iterable[str] = (),
        or_tags: Iterable[str] = (),
        not_tags: Iterable[str] = (),
    ) -> TagSet:
        """Query for objects matching the tag criteria.

        Args:
            with_tags: Objects must have ALL of these tags (intersection)
            or_tags: Objects must have ANY of these tags (union)
            not_tags: Objects must NOT have any of these tags (difference)

        Returns:
            TagSet containing objects matching the criteria

        """
        objects = self.query_tags_intersection(*with_tags) if with_tags else self.all()
        if or_tags:
            objects = objects.query_tags_union(*or_tags)
        if not_tags:
            objects = objects.query_tags_difference(*not_tags)

        return objects

    def select(
        self,
        with_tags: Iterable[str] = (),
        or_tags: Iterable[str] = (),
        not_tags: Iterable[str] = (),
    ) -> TaggableProtocol:
        """Select the best object for the given tags.

        1. Begin with the set of all available resources.

        2. Rule out any resources that do not include *all* of the
           required tags in the query set.

        3. Rank the remaining resources in terms of those that match
           the greatest number of optional tags.

        4. Rank the remaining resources from step 3 in terms of those
           with the least number of additional tags (that is, tags on
           the resource that are not specified as required or optional
           tags in the query).

        5. If more than one resource is ranked highest at this point,
           select the least recently used resource.  If there is more
           than one resource that has never been used, select Randomly
           from among the highest-ranked resources.

        Args:
            with_tags: Objects must have ALL of these tags (required)
            or_tags: Objects should have ANY of these tags (optional, for ranking)
            not_tags: Objects must NOT have any of these tags (excluded)

        Returns:
            The best matching taggable object based on the ranking criteria

        """
        with_tags_set = resolve_tags(*with_tags)
        or_tags_set = resolve_tags(*or_tags)
        not_tags_set = resolve_tags(*not_tags)

        objects = self.query_tags_intersection(*with_tags_set)
        if not_tags_set:
            objects = objects.query_tags_difference(*not_tags_set)

        rankings: list[int] = []
        for obj in objects:
            rank = 0
            for tag in obj.tags:
                if tag in or_tags_set:
                    rank += 1
                elif tag not in with_tags_set:
                    rank -= 1
            rankings.append(rank)
        ranks_objs = sorted(zip(rankings, objects, strict=False), reverse=True, key=operator.itemgetter(0))
        toprank: int = ranks_objs[0][0]
        how_many: int = rankings.count(toprank)
        top_contenders: list[TaggableProtocol] = [robj[1] for robj in ranks_objs[:how_many]]

        if how_many == 1:
            winner = top_contenders[0]
        else:
            by_access: list[tuple[float, TaggableProtocol]] = [
                (getattr(cntndr, 'last_picked', 0.0), cntndr) for cntndr in top_contenders
            ]
            by_access.sort(key=operator.itemgetter(0))
            winner = by_access[0][1]

        winner.last_picked = time.time()

        return winner


@functools.total_ordering
class Taggable:
    """A taggable object."""

    tags: set[str]
    last_picked: float
    _tag_repo: TagRepository | None

    def __init__(self, tag_repo: TagRepository | None, *tags: str) -> None:
        """Initialize a Taggable object.

        Args:
            tag_repo: The tag repository to register this object with
            *tags: Variable number of tag strings to apply to this object

        """
        super().__init__()
        self.tags = set(tags)
        self._tag_repo = None
        self.tag_repo = tag_repo
        self.last_picked = 0.0

    def __repr__(self) -> str:
        """Return a string representation of the taggable object."""
        return '<{}: {}>'.format(self.__class__.__name__, ' '.join(self.tags))

    @property
    def tag_repo(self) -> TagRepository | None:
        """Get the tag repository this object is registered with."""
        return self._tag_repo

    @tag_repo.setter
    def tag_repo(self, repo: TagRepository | None) -> None:
        """Set the tag repository, handling de/registration.

        Args:
            repo: The tag repository to register with, or None to unregister

        """
        if self._tag_repo is not None and repo is not self._tag_repo:
            self._tag_repo.remove_object(self)

        if repo is not None and repo is not self._tag_repo:
            repo.add_object(self, check_repo=False)

        self._tag_repo = repo

    def add_tag(self, *tags: str) -> None:
        """Add tags to this object.

        Args:
            *tags: Variable number of tag strings to add

        """
        if self.tag_repo is not None:
            self.tag_repo.tag_object(self, *tags)

    def remove_tag(self, *tags: str) -> None:
        """Remove tags from this object.

        Args:
            *tags: Variable number of tag strings to remove

        """
        if self.tag_repo is not None:
            self.tag_repo.untag_object(self, *tags)

    def __eq__(self, other: object) -> bool:
        """Check equality based on tags.

        Args:
            other: Object to compare with

        Returns:
            True if both objects have the same tags

        """
        if not isinstance(other, (Taggable, TaggableClass)):
            return NotImplemented
        return self.tags == other.tags

    def __lt__(self, other: object) -> bool:
        """Compare objects based on sorted tags.

        Args:
            other: Object to compare with

        Returns:
            True if this object's sorted tags are less than the other's

        """
        if not isinstance(other, (Taggable, TaggableClass)):
            return NotImplemented
        return sorted(self.tags) < sorted(other.tags)

    def __hash__(self) -> int:
        """Return hash based on tags.

        Returns:
            Hash value based on frozenset of tags

        """
        return hash(frozenset(self.tags))


class TaggableClass:
    """A taggable class object.

    Instances of such a class will not be tagged.
    Note: This class uses class-level attributes and methods, unlike Taggable
    which uses instance-level attributes.
    """

    tags: set[str]
    tag_repo: TagRepository
    last_picked: float = 0.0

    @classmethod
    def add_tag(cls, *tags: str) -> None:
        """Add tags to this class.

        Args:
            *tags: Variable number of tag strings to add

        """
        # TaggableClass uses class objects, not instances, so we ignore type checking here
        cls.tag_repo.tag_object(cls, *tags)  # type: ignore[arg-type]

    @classmethod
    def remove_tag(cls, *tags: str) -> None:
        """Remove tags from this class.

        Args:
            *tags: Variable number of tag strings to remove

        """
        # TaggableClass uses class objects, not instances, so we ignore type checking here
        cls.tag_repo.untag_object(cls, *tags)  # type: ignore[arg-type]


class TagRepository(AbstractTagSet):
    """An example implementation for storing and querying tags."""

    tag_objs: defaultdict[str, TagSet]

    def __init__(self, *objs: TaggableProtocol) -> None:
        """Initialize a TagRepository.

        Args:
            *objs: Variable number of taggable objects to add to the repository

        """
        self.tag_objs = defaultdict(TagSet)
        self.add_object(*objs)

    def add_object(self, *objs: TaggableProtocol, check_repo: bool = True) -> None:
        """Add objects to the repository.

        Args:
            *objs: Variable number of taggable objects to add
            check_repo: If True, update the object's tag_repo (default: True)

        """
        for obj in objs:
            if check_repo and obj.tag_repo is not self:
                obj.tag_repo = self
            else:
                for tag in resolve_tags(*obj.tags):
                    self.tag_objs[tag].add(obj)

    def remove_object(self, *objs: TaggableProtocol) -> None:
        """Remove objects from the repository.

        Args:
            *objs: Variable number of taggable objects to remove

        """
        for obj in objs:
            for tag in resolve_tags(*obj.tags):
                with contextlib.suppress(KeyError):
                    self.tag_objs[tag].remove(obj)

    def add_tags(self, *tags: str) -> None:
        """Add tags to the database (creates empty tag entries).

        Args:
            *tags: Variable number of tag strings to add

        """
        for tag in resolve_tags(*tags):
            self.tag_objs[tag]

    def tag_object(self, obj: TaggableProtocol, *tags: str) -> None:
        """Tag an object.

        Args:
            obj: The taggable object to tag
            *tags: Variable number of tag strings to apply

        """
        for tag in resolve_tags(*tags):
            self.tag_objs[tag].add(obj)
        obj.tags.update(tags)

    def untag_object(self, obj: TaggableProtocol, *tags: str) -> None:
        """Remove tags from an object.

        Args:
            obj: The taggable object to untag
            *tags: Variable number of tag strings to remove

        """
        for tag in resolve_tags(*tags):
            with contextlib.suppress(KeyError):
                self.tag_objs[tag].remove(obj)
        obj.tags.difference_update(tags)

    def all(self) -> TagSet:
        """Return the set of all objects in the repository.

        Returns:
            TagSet containing all objects across all tags

        """
        return TagSet(itertools.chain.from_iterable(self.tag_objs.values()))

    def query_tag(self, tag: str) -> TagSet:
        """Return the set of objects referenced by the given tag.

        Args:
            tag: The tag to query for

        Returns:
            TagSet containing objects with the specified tag

        """
        return TagSet(self.tag_objs[tag])


class TagSet(set[TaggableProtocol], AbstractTagSet):
    """An object for collecting taggables and running tag queries on them.

    Not nearly as efficient as querying taggables stored in a
    TagRepository, but useful.
    """

    def all(self) -> TagSet:
        """Return all objects in the set (returns self).

        Returns:
            This TagSet instance

        """
        return self

    def query_tag(self, tag: str) -> TagSet:
        """Return all objects in the set that have the given tag.

        Args:
            tag: The tag to query for

        Returns:
            TagSet containing objects with the specified tag

        """
        objs = TagSet()
        for obj in self:
            if tag in obj.tags:
                objs.add(obj)
        return objs
