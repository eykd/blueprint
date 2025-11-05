"""Base metaclasses and core Blueprint implementation.

This module provides the foundational classes for the Blueprint system:
- Meta: Configuration and metadata container for Blueprint instances
- BlueprintMeta: Metaclass that handles Blueprint class creation and tag registration
- Blueprint: Base class for all blueprint templates with field resolution
"""

from __future__ import annotations

import copy
import random
import re
from collections import deque
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from . import fields, taggables

__all__ = ['Blueprint']


class Meta:
    """Metadata container for Blueprint configuration and state.

    This class stores metadata about Blueprint instances, including field tracking,
    mastering state, hierarchy relationships, and random number generation settings.

    Attributes:
        fields: Set of field names present on the blueprint.
        mastered: Flag indicating whether the blueprint has been mastered (instantiated
            with all dynamic fields resolved to concrete values).
        abstract: Flag indicating whether the blueprint is abstract. Abstract blueprints
            are not added to the tag repository and won't appear in tag queries.
        source: When a blueprint is modified (modded), this references the original
            source blueprint or blueprint class.
        parent: When a blueprint is nested inside another blueprint, this references
            the parent blueprint instance.
        random: Random number generator instance used for all random field resolution.
        seed: Seed value used to initialize the random number generator. Can be a
            string or float for reproducible generation.
        kwargs: Additional keyword arguments passed during blueprint instantiation.

    """

    fields: set[str]
    mastered: bool
    abstract: bool
    source: type[Blueprint] | Blueprint | None
    parent: Blueprint | None
    random: random.Random
    seed: str | float
    kwargs: dict[str, Any]

    def __init__(self) -> None:
        """Initialize Meta with default values.

        Sets up default metadata state including empty field set, unmastered status,
        concrete (non-abstract) type, no parent/source relationships, and a new
        random number generator with a random seed.
        """
        self.fields = set()
        self.mastered = False
        self.abstract = False
        self.source = None
        self.parent = None

        self.random = random.Random()  # noqa: S311
        self.seed = random.random()  # noqa: S311
        self.random.seed(self.seed)

    def __deepcopy__(self, memo: dict[int, Any]) -> Meta:
        """Create a deep copy of this Meta instance.

        Special handling for certain attributes:
        - source and parent are shallow-copied to preserve relationships
        - random gets a new Random() instance to avoid shared state
        - All other attributes are deep-copied

        Args:
            memo: Dictionary tracking already-copied objects to handle circular references.

        Returns:
            A new Meta instance with copied values.

        """
        self_id = id(self)
        existing: Meta | None = memo.get(self_id)
        if existing is not None:  # pragma: no cover
            return existing

        meta = Meta()
        for name, value in self.__dict__.items():
            if name in {'source', 'parent'}:
                setattr(meta, name, value)
            elif name == 'random':
                meta.random = random.Random()  # noqa: S311
            else:
                setattr(meta, name, copy.deepcopy(value, memo))
        memo[self_id] = meta
        return meta


camelcase_cp: re.Pattern[str] = re.compile(r'[A-Z][^A-Z]+')


class BlueprintMeta(type):
    """Metaclass that handles Blueprint class creation and tag registration.

    This metaclass provides the declarative magic for Blueprint classes:
    - Initializes tag repositories for direct Blueprint subclasses
    - Auto-generates tags from CamelCase class names
    - Inherits tags from parent blueprint classes
    - Collects and tracks field definitions across the inheritance hierarchy
    - Registers blueprint classes in their appropriate tag repository

    The first direct subclass of Blueprint creates a new TagRepository, while
    subsequent subclasses of that lineage share the same repository.
    """

    tag_repo: taggables.TagRepository | None
    tags: set[str] | str
    name: str
    last_picked: float
    meta: Meta

    def __init__(
        cls,
        _name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> None:
        """Initialize a new Blueprint class with tag repository and tag processing.

        This method implements the mount point pattern for tag repositories:
        - Direct Blueprint subclasses create a new TagRepository
        - Indirect subclasses register themselves in their ancestor's repository

        For registered blueprints, this method:
        - Converts string tags to sets and adds the class name as a tag
        - Extracts additional tags from CamelCase class names
        - Inherits tags from parent blueprint classes
        - Generates a human-readable name from the class name
        - Registers the class in the appropriate tag repository

        Args:
            _name: Name of the class being created.
            bases: Tuple of base classes.
            attrs: Dictionary of class attributes.

        """
        if not hasattr(cls, 'tag_repo'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.tag_repo = taggables.TagRepository()
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            if isinstance(cls.tags, str):  # pragma: no branch
                cls.tags = set(cls.tags.split())
            cls.tags.add(cls.__name__)
            cls.tags.update(t.lower() for t in camelcase_cp.findall(cls.__name__))
            cls.last_picked = 0.0
            if 'name' not in attrs:
                cls.name = ' '.join(camelcase_cp.findall(cls.__name__))
            for base in bases:
                if hasattr(base, 'tags'):  # pragma: no branch
                    base_tags = base.tags
                    if isinstance(base_tags, set):
                        cls.tags.update(base_tags)
            if cls.tag_repo is not None and not cls.meta.abstract:  # pragma: no branch
                cls.tag_repo.add_object(cls)  # type: ignore[arg-type]

    def __new__(
        cls: type[BlueprintMeta],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> BlueprintMeta:
        """Create a new Blueprint class with field tracking and metadata setup.

        This method creates the blueprint class structure by:
        - Preserving special Python attributes (__new__, __classcell__)
        - Processing the tags attribute
        - Setting up Meta configuration from the user's Meta class
        - Collecting field definitions (non-private, non-generator attributes)
        - Inheriting field definitions from parent blueprints
        - Contributing attributes to the class via add_to_class protocol

        Args:
            cls: The metaclass being used to create the new class.
            name: Name of the new Blueprint class.
            bases: Tuple of base classes.
            attrs: Dictionary of class attributes being defined.

        Returns:
            The newly created Blueprint class.

        """
        new = attrs.pop('__new__', None)
        classcell = attrs.pop('__classcell__', None)
        new_attrs: dict[str, Any] = {}
        if new is not None:
            new_attrs['__new__'] = new
        if classcell is not None:
            new_attrs['__classcell__'] = classcell
        new_class = super().__new__(cls, name, bases, new_attrs)
        new_class.tags = attrs.pop('tags', '')

        # Set up Meta options
        meta = new_class.meta = Meta()
        if 'Meta' in attrs:
            usermeta = attrs.pop('Meta')
            for key, value in usermeta.__dict__.items():
                if not key.startswith('_'):
                    setattr(meta, key, value)
        meta.fields.update(a for a in attrs if not a.startswith('_') and not hasattr(attrs[a], 'is_generator'))
        for base in bases:
            if hasattr(base, 'meta'):
                meta.fields.update(base.meta.fields)

        # Transfer the rest of the attributes.
        for attr_name, value in attrs.items():
            new_class.add_to_class(attr_name, value)

        return new_class

    def add_to_class(cls, name: str, value: Any) -> None:  # noqa: ANN401
        """Add an attribute to the Blueprint class with optional special handling.

        If the value has a 'contribute_to_class' method, that method is called
        to allow the value to customize how it's added to the class. Otherwise,
        the value is set as a standard class attribute.

        Args:
            cls: The Blueprint class being modified.
            name: The attribute name.
            value: The value to add to the class.

        """
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def __repr__(cls) -> str:
        """Return a detailed string representation of the Blueprint class.

        Returns:
            A multi-line string showing the class name and all its fields with
            their current values, formatted for readability.

        """
        return '<{}:\n    {}\n    >'.format(
            cls.__name__,
            '\n    '.join(
                '{} -- {}'.format(n, '\n'.join(f'    {i}' for i in repr(getattr(cls, n)).splitlines()).strip())
                for n in sorted(cls.meta.fields)
            ),
        )


class Blueprint(taggables.TaggableClass, metaclass=BlueprintMeta):
    """Base class for creating procedural generation templates with dynamic fields.

    Blueprints are template classes that combine static and dynamic field definitions.
    When instantiated, all dynamic fields (callables) are resolved to produce a
    "mastered" blueprint with concrete values. This enables procedural generation
    of game content, characters, items, and other structured data.

    Key features:
        - Automatic tagging from CamelCase class names (e.g., CaveMan → ['cave', 'man'])
        - Tag inheritance from parent blueprint classes
        - Field resolution with dependency tracking
        - Reproducible generation via seeding
        - Support for nested blueprints with parent relationships

    To create a blueprint, subclass Blueprint and define fields:
        - Static fields: assign plain values (strings, numbers, etc.)
        - Dynamic fields: assign callable objects (functions, Field instances)
        - Generator methods: use @generator decorator for methods that build final objects

    Attributes:
        meta: Metadata container with configuration and state information.

    Example:
        >>> import blueprint as bp

        >>> class Item(bp.Blueprint):
        ...     # Tags are space-separated
        ...     tags = 'foo bar'
        ...     # Simple fields are static values
        ...     name = 'generic item'
        ...     value = 1
        ...     # Dynamic field values use any callable object
        ...     quality = bp.RandomInt(1, 6)
        ...     price = bp.depends_on('value', 'quality')(lambda _: _.value * _.quality)

        >>> sorted(Item.tags)
        ['Item', 'bar', 'foo', 'item']
        >>> item = Item()  # Instantiate a "mastered" blueprint.

        >>> item.value
        1
        >>> 1 <= item.quality <= 6
        True

    """

    meta: Meta

    def __repr__(self) -> str:
        """Return a detailed string representation of the mastered blueprint.

        Returns:
            A multi-line string showing the class name and all resolved field values,
            formatted for readability.

        """
        return '<{}:\n    {}\n    >'.format(
            self.__class__.__name__,
            '\n    '.join(
                '{} -- {}'.format(n, '\n'.join(f'    {i}' for i in repr(getattr(self, n)).splitlines()).strip())
                for n in sorted(self.meta.fields)
            ),
        )

    def __init__(
        self,
        parent: Blueprint | None = None,
        seed: str | float | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Initialize and master a blueprint instance.

        Creates a "mastered" blueprint by:
        - Deep copying the class metadata to create instance-specific metadata
        - Setting up parent relationships if this is a nested blueprint
        - Initializing the random number generator with a seed
        - Applying any keyword argument overrides
        - Resolving all dynamic fields to concrete values

        Args:
            parent: Optional parent blueprint for nested blueprints. If provided,
                inherits the parent's seed unless explicitly overridden.
            seed: Optional seed for reproducible random generation. If not provided,
                uses parent's seed (if parent exists) or generates a random seed.
            **kwargs: Additional keyword arguments to override field values. These
                are set as instance attributes before field resolution.

        """
        self.meta = copy.deepcopy(self.meta)
        if parent is not None:
            self.meta.parent = parent
        self.meta.mastered = True
        if seed is not None:
            self.meta.seed = seed
        elif parent is not None:
            self.meta.seed = parent.meta.seed
        else:
            self.meta.seed = random.random()  # noqa: S311
        self.meta.random.seed(self.meta.seed)
        self.meta.kwargs = kwargs
        for name, value in kwargs.items():
            setattr(self, name, value)

        self._resolve_fields()

    def _resolve_fields(self) -> None:
        """Resolve all blueprint fields in dependency order.

        This method processes fields in three passes:
        1. Regular fields: Resolved in order, with deferred resolution for fields
           with unmet dependencies (via @depends_on decorator).
        2. Deferred fields: Fields with dependencies are resolved once their
           dependencies are met, using a work queue approach.
        3. End-deferred fields: Fields marked with @defer_to_end are resolved
           last, after all other fields.

        Static fields (non-callables) are marked as resolved immediately.
        Dynamic fields (callables) are invoked via fields.resolve() to produce
        concrete values.
        """
        resolved: set[str] = set()
        deferred: deque[tuple[str, Callable[[Any], Any]]] = deque()
        deferred_to_end: deque[str] = deque()
        deferred_to_end_names: set[str] = set()

        def resolve(name: str, field: Any) -> None:  # noqa: ANN401
            # print "Can we resolve", name
            if callable(field):
                if hasattr(field, 'depends_on') and not field.depends_on.issubset(resolved):
                    if field.depends_on.intersection(deferred_to_end_names):  # pragma: no cover
                        deferred_to_end.append(name)
                    else:
                        deferred.appendleft((name, field))
                else:
                    setattr(self, name, fields.resolve(self, field))
                    resolved.add(name)
            else:
                resolved.add(name)

        for name in self.meta.fields:
            class_field = getattr(self.__class__, name)
            if hasattr(class_field, '_defer_to_end'):
                deferred_to_end.appendleft(name)
                deferred_to_end_names.add(name)
            else:
                field = getattr(self, name)
                resolve(name, field)

        while deferred:
            name, field = deferred.pop()
            resolve(name, field)

        deferred_to_end_names.clear()
        while deferred_to_end:
            name = deferred_to_end.pop()
            field = getattr(self, name)
            resolve(name, field)

    @fields.generator
    def as_dict(self) -> dict[str, Any]:
        """Return a dictionary of all mastered field values.

        This is a generator method (marked with @generator decorator) and is not
        automatically called during blueprint instantiation. It must be explicitly
        invoked to produce the dictionary output.

        Returns:
            A dictionary mapping field names to their resolved values for this
            mastered blueprint instance.

        """
        return {n: getattr(self, n) for n in self.meta.fields}
