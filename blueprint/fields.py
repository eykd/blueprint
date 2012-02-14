# -*- coding: utf-8 -*-
"""blueprint.fields
"""
import random

__all__ = ['Field', 'RandomInt', 'PickOne', 'PickFrom', 'All',
           'FormatTemplate', 'WithTags', 'generator', 'depends_on']


class Field(object):
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

    def __str__(self):
        return ''


class RandomInt(Field):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return '%s...%s' % (self.start, self.end)

    def __call__(self, parent):
        return random.randint(self.start, self.end)


class PickOne(Field):
    def __init__(self, *choices):
        self.choices = choices

    def __str__(self):
        return str(self.choices)

    def __call__(self, parent):
        result = random.choice(self.choices)
        if callable(result):
            result = result(parent)
        return result


class PickFrom(Field):
    def __init__(self, collection):
        self.collection = collection

    def __str__(self):
        return str(self.collection)

    def __call__(self, parent):
        collection = self.collection
        if callable(collection):
            collection = collection(parent)
        result = random.choice(list(collection))
        if callable(result):
            result = result(parent)
        return result


class All(Field):
    def __init__(self, *items):
        self.items = items

    def __str__(self):
        return str(self.items)

    def __call__(self, parent):
        return [i(parent) if callable(i) else i for i in self.items]


class FormatTemplate(Field):
    defer_to_end = True
    
    def __init__(self, template):
        self.template = template

    def __str__(self):
        return str(self.template)

    def __get__(self, parent, type=None):
        if parent is None:
            return self
        
        fields = {}
        for name in parent.meta.fields:
            if getattr(parent.__class__, name) is not self:
                fields[name] = getattr(parent, name)
        return self.template.format(**fields)


class WithTags(Field):
    def __init__(self, *tags):
        all_tags = set()
        for t in tags:
            all_tags.update(t.split())
        
        self.with_tags = set()
        self.or_tags = set()
        self.not_tags = set()

        for t in all_tags:
            if t.startswith('!'):
                self.not_tags.add(t)
            elif t.endswith('?'):
                self.or_tags.add(t)
            else:
                self.with_tags.add(t)

    def __call__(self, parent):
        if self.with_tags:
            objects = parent.tag_repo.queryTagsIntersection(*self.with_tags)
        else:
            objects = parent.tag_repo
        if self.or_tags:
            objects = objects.queryTagsUnion(*self.or_tags)
        if self.not_tags:
            objects = objects.queryTagsDifference(*self.not_tags)

        return list(objects)


def generator(func):
    """Generator methods on a Blueprint don't get flagged as fields.

    Subsequently, they aren't subject to field treatment, and remain
    callable on a mastered Blueprint instance.
    """
    func.is_generator = True
    return func


def depends_on(*names):
    """Declare that the given method depends upon other members to be resolved first.
    """
    dependencies = set()
    for name in names:
        dependencies.update(name.split())

    def wrap(func):
        func.depends_on = dependencies
        return func

    return wrap
