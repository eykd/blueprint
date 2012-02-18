# -*- coding: utf-8 -*-
"""blueprint.base -- base metaclasses and other junk for blueprints.
"""
import re
import inspect
import copy
from collections import deque
import random
from . import taggables

__all__ = ['Blueprint']


class Meta(object):
    def __init__(self):
        self.fields = set()
        self.mastered = False
        self.abstract = False
        self.source = None
        self.parent = None
        
        self.random = random.Random()
        self.seed = random.random()
        self.random.seed(self.seed)

    def __deepcopy__(self, memo):
        not_there = []
        existing = memo.get(self, not_there)
        if existing is not not_there:
            return existing

        meta = Meta()
        for name, value in self.__dict__.iteritems():
            if name == 'source' or name == 'parent':
                setattr(meta, name, value)
            else:
                setattr(meta, name, copy.deepcopy(value, memo))
        memo[self] = meta
        return meta

camelcase_cp = re.compile(r'[A-Z][^A-Z]+')


class BlueprintMeta(type):
    def __init__(cls, name, bases, attrs):
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
            cls.tags = set(cls.tags.split())
            cls.tags.add(cls.__name__)
            cls.tags.update(t.lower() for t in camelcase_cp.findall(cls.__name__))
            cls.last_picked = 0.0
            if 'name' not in attrs:
                cls.name = ' '.join(camelcase_cp.findall(cls.__name__))
            for base in bases:
                if hasattr(base, 'tags'):
                    cls.tags.update(base.tags)
            cls.tag_repo.addObject(cls)

    def __new__(cls, name, bases, attrs):
        _new = attrs.pop('__new__', None)
        new_attrs = {'__new__': _new} if _new is not None else {}
        new_class = super(BlueprintMeta, cls).__new__(cls, name, bases, new_attrs)
        new_class.tags = attrs.pop('tags', '')

        # Set up Meta options
        meta = new_class.meta = Meta()
        if 'Meta' in attrs:
            usermeta = attrs.pop('Meta')
            for key, value in usermeta.__dict__.iteritems():
                if not key.startswith('_'):
                    setattr(meta, key, value)
        meta.fields.update(a for a in attrs.keys() if not a.startswith('_') and not hasattr(attrs[a], 'is_generator'))
        for base in bases:
            if hasattr(base, 'meta'):
                meta.fields.update(base.meta.fields)

        # Transfer the rest of the attributes.
        for name, value in attrs.iteritems():
            new_class.add_to_class(name, value)

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Blueprint(taggables.TaggableClass):
    __metaclass__ = BlueprintMeta

    def __repr__(self):
        return '<%s:\n    %s\n    >' % (
            self.__class__.__name__,
            '\n    '.join(
                '%s -- %s' % (
                    n,
                    '\n'.join(
                        '    %s' % i
                        for i in repr(getattr(self, n)).splitlines()
                        ).strip()
                    )
                for n in sorted(self.meta.fields)
                )
            )

    def __init__(self, parent=None, seed=None, **kwargs):
        self.meta = copy.deepcopy(self.meta)
        if parent is not None:
            self.meta.parent = parent
        self.meta.mastered = True
        if seed is not None:
            self.meta.seed = seed
        else:
            self.meta.seed = random.random()
        self.meta.random.seed(self.meta.seed)
        self.meta.kwargs = kwargs
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

        # Resolve any unresolved fields.
        resolved = set()
        deferred = deque()
        deferred_to_end = deque()

        def resolve(name, field):
            if callable(field):
                if hasattr(field, 'depends_on') and not field.depends_on.issubset(resolved):
                    deferred.appendleft((name, field))
                else:
                    if inspect.ismethod(field):
                        setattr(self, name, field())
                    else:
                        setattr(self, name, field(self))
                    resolved.add(name)
            else:
                resolved.add(name)
            
        for name in self.meta.fields:
            class_field = getattr(self.__class__, name)
            if hasattr(class_field, 'defer_to_end'):
                deferred_to_end.appendleft(name)
            else:
                field = getattr(self, name)
                resolve(name, field)

        while deferred:
            name, field = deferred.pop()
            resolve(name, field)

        while deferred_to_end:
            name = deferred_to_end.pop()
            field = getattr(self, name)
            resolve(name, field)
