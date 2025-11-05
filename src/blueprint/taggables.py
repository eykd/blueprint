"""blueprint.taggables -- tag repositories and query interface for selecting contained items."""

import contextlib
import itertools
import operator
import time
from collections import defaultdict

__all__ = ['AbstractTagSet', 'TagRepository', 'TagSet', 'Taggable', 'TaggableClass', 'resolve_tags']


def resolve_tags(*tags):
    all_tags = set()
    for t in tags:
        all_tags.update(t.split())
    return all_tags


class AbstractTagSet:
    """Define methods for interacting with a local tag set."""

    def __iter__(self):
        return iter(self.all())

    def query_tags_intersection(self, *tags):
        objects = None
        for tag in resolve_tags(*tags):
            tag_query = self.query_tag(tag)
            if objects is None:
                objects = tag_query
            objects.intersection_update(tag_query)
        return objects

    def query_tags_union(self, *tags):
        objs = TagSet()
        for tag in resolve_tags(*tags):
            objs.update(self.query_tag(tag))
        return objs

    def query_tags_difference(self, *tags):
        objs = TagSet(self.all())
        for tag in resolve_tags(*tags):
            for obj in list(objs):
                if tag in obj.tags:
                    objs.remove(obj)

        return objs

    def query(self, with_tags=(), or_tags=(), not_tags=()):
        objects = self.query_tags_intersection(*with_tags) if with_tags else self.all()
        if or_tags:
            objects = objects.query_tags_union(*or_tags)
        if not_tags:
            objects = objects.query_tags_difference(*not_tags)

        return objects

    def select(self, with_tags=(), or_tags=(), not_tags=()):
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
        """
        with_tags = resolve_tags(*with_tags)
        or_tags = resolve_tags(*or_tags)
        not_tags = resolve_tags(*not_tags)

        objects = self.query_tags_intersection(*with_tags)
        if not_tags:
            objects = objects.query_tags_difference(*not_tags)

        rankings = []
        for obj in objects:
            rank = 0
            for tag in obj.tags:
                if tag in or_tags:
                    rank += 1
                elif tag not in with_tags:
                    rank -= 1
            rankings.append(rank)
        # Python 3 zip is an iterator, ergo no itertools.izip available.)
        ranks_objs = sorted(zip(rankings, objects), reverse=True, key=operator.itemgetter(0))
        toprank = ranks_objs[0][0]
        how_many = rankings.count(toprank)
        top_contenders = [robj[1] for robj in ranks_objs[:how_many]]

        if how_many == 1:
            winner = top_contenders[0]
        else:
            by_access = [(getattr(cntndr, 'last_picked', 0), cntndr) for cntndr in top_contenders]
            by_access.sort(key=operator.itemgetter(0))
            winner = by_access[0][1]

        winner.last_picked = time.time()

        return winner


class Taggable:
    """A taggable object."""

    def __init__(self, tag_repo, *tags) -> None:
        super().__init__()
        self.tags = set(tags)
        self._tag_repo = None
        self.tag_repo = tag_repo
        self.last_picked = 0.0

    def __repr__(self) -> str:
        return '<{}: {}>'.format(self.__class__.__name__, ' '.join(self.tags))

    @property
    def tag_repo(self):
        return self._tag_repo

    @tag_repo.setter
    def tag_repo(self, repo) -> None:
        if self._tag_repo is not None and repo is not self._tag_repo:
            self._tag_repo.remove_object(self)

        if repo is not None and repo is not self._tag_repo:
            repo.add_object(self, check_repo=False)

        self._tag_repo = repo

    def add_tag(self, *tags) -> None:
        self.tag_repo.tag_object(self, *tags)

    def remove_tag(self, *tags) -> None:
        self.tag_repo.untagObject(self, *tags)

    def __cmp__(self, other):
        result = 1
        if hasattr(other, 'tags'):
            result = cmp(self.tags, other.tags)
        return result


class TaggableClass:
    """A taggable class object.

    Instances of such a class will not be tagged.
    """

    @classmethod
    def add_tag(cls, *tags) -> None:
        cls.tag_repo.tag_object(cls, *tags)

    @classmethod
    def remove_tag(cls, *tags) -> None:
        cls.tag_repo.untag_object(cls, *tags)

    last_picked = 0.0


class TagRepository(AbstractTagSet):
    """An example implementation for storing and querying tags."""

    def __init__(self, *objs) -> None:
        self.tag_objs = defaultdict(TagSet)
        self.add_object(*objs)

    def add_object(self, *objs, **kwargs) -> None:
        for obj in objs:
            if kwargs.get('check_repo', True) and obj.tag_repo is not self:
                obj.tag_repo = self
            else:
                for tag in resolve_tags(*obj.tags):
                    self.tag_objs[tag].add(obj)

    def remove_object(self, *objs) -> None:
        for obj in objs:
            for tag in resolve_tags(*obj.tags):
                with contextlib.suppress(KeyError):
                    self.tag_objs[tag].remove(obj)

    def add_tags(self, *tags) -> None:
        """Add tags to the db."""
        for tag in resolve_tags(*tags):
            self.tag_objs[tag]

    def tag_object(self, obj, *tags) -> None:
        """Tag an object."""
        for tag in resolve_tags(*tags):
            self.tag_objs[tag].add(obj)
        obj.tags.update(tags)

    def untag_object(self, obj, *tags) -> None:
        """Untag an object."""
        for tag in resolve_tags(*tags):
            with contextlib.suppress(KeyError):
                self.tag_objs[tag].remove(obj)
        obj.tags.difference_update(tags)

    def all(self):
        """Return the set of all objects in the repository."""
        return TagSet(itertools.chain.from_iterable(self.tag_objs.values()))

    def query_tag(self, tag):
        """Return the set of objects referenced by the given tag."""
        return TagSet(self.tag_objs[tag])


class TagSet(set, AbstractTagSet):
    """An object for collecting taggables and running tag queries on them.

    Not nearly as efficient as querying taggables stored in a
    TagRepository, but useful.
    """

    def all(self):
        return self

    def query_tag(self, tag):
        """Return all objects in the set that have the given tag."""
        objs = TagSet()
        for obj in self:
            if tag in obj.tags:
                objs.add(obj)
        return objs
