# -*- coding: utf-8 -*-
"""blueprint.fields
"""
import random
import operator

__all__ = ['Field', 'RandomInt', 'PickOne', 'PickFrom', 'All',
           'FormatTemplate', 'WithTags',
           'generator', 'depends_on', 'resolve']


class Field(object):
    """The base dynamic field class. Not very useful on its own.

    Subclasses of ``Field`` should define a ``__call__`` method::

        def __call__(self, parent):
            ...

    ``__call__`` should return the final, resolved value of the field.

    When mastering a blueprint, any callable field on the blueprint
    will be called with one argument, the parent blueprint itself.
    """
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

    def __str__(self):
        return ''

    def __add__(self, b):
        return Add(self, b)

    def __radd__(self, a):
        return Add(a, self)

    def __sub__(self, b):
        return Subtract(self, b)

    def __rsub__(self, a):
        return Subtract(a, self)

    def __mul__(self, b):
        return Multiply(self, b)

    def __rmul__(self, a):
        return Multiply(a, self)

    def __div__(self, b):
        return Divide(self, b)

    def __rdiv__(self, a):
        return Divide(a, self)


class _Operator(object):
    """Base class for all operator fields.
    """
    op = None
    sym = ''
    
    def __init__(self, *items):
        self.items = items

    def __repr__(self):
        return '(%s)' % (str(self))

    def __str__(self):
        return (' %s ' % self.sym).join(repr(i) for i in self.items)

    def __call__(self, parent):
        result = None
        for item in self.items:
            if result is None:
                result = resolve(parent, item)
            else:
                result = self.op(result, resolve(parent, item))
        return result


class Add(_Operator):
    """When resolved, adds all the provided arguments and returns the result.
    """
    op = operator.add
    sym = '+'


class Subtract(_Operator):
    """When resolved, subtracts all the provided arguments and returns the result.
    """
    op = operator.sub
    sym = '-'


class Multiply(_Operator):
    """When resolved, multiplies all the provided arguments and returns the result.
    """
    op = operator.mul
    sym = '*'


class Divide(_Operator):
    """When resolved, divides all the provided arguments and returns the result.
    """
    op = operator.div
    sym = '/'


class RandomInt(Field):
    """When resolved, returns a random integer between ``start`` and ``end``.
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return '%s...%s' % (self.start, self.end)

    def __call__(self, parent):
        return random.randint(self.start, self.end)


class PickOne(Field):
    """When resolved, returns a random item from the arguments provided.
    """
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
    """When resolved, returns a random item from the collection provided.
    """
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
    """When resolved, returns a list of the provided items, themselves resolved.
    """
    def __init__(self, *items):
        self.items = items

    def __str__(self):
        return str(self.items)

    def __call__(self, parent):
        return [i(parent) if callable(i) else i for i in self.items]


class FormatTemplate(Field):
    """When resolved, returns a rendered string from the provided template.

    Uses the Python `format string syntax`_. All other fields are
    available to the template, as well as the parent ``meta`` options
    object. 

    .. format string syntax: http://docs.python.org/library/string.html#formatstrings

    An example::

    >>> import blueprint as bp
    >>> class Item(bp.Blueprint):
    ...     bonus = 1
    ...     name = bp.FormatTemplate('Item +{bonus}')
    ...     joke = bp.FormatTemplate('Two men walked into a {meta.foo}')
    ...
    ...     class Meta:
    ...         foo = 'bar'

    >>> item = Item()
    >>> item.name
    "Item +1"
    >>> item.joke
    "Two men walked into a bar"
    """
    defer_to_end = True
    
    def __init__(self, template):
        self.template = template

    def __str__(self):
        return str(self.template)

    def __get__(self, parent, type=None):
        if parent is None:
            return self
        
        fields = {'meta': parent.meta,
                  'parent': parent}
        for name in parent.meta.fields:
            if getattr(parent.__class__, name) is not self:
                fields[name] = getattr(parent, name)
        return self.template.format(**fields)


class WithTags(Field):
    """When resolved, returns the set of all blueprints selected by the given tags.

    Takes multiple arguments. Arguments may be individual tags, or
    space-separated strings with multiple tags. Tags begininng with
    ``!`` denote a NOT (or difference), that is, \"all blueprints
    *without* this tag\". Tags beginning with ``?`` denote an OR (or
    union), that is, \"all blueprints with this tag, but not required
    for others\". Tags without either prefix denote an AND (or
    interesction), that is, \"all blueprints must have this tag\".
    """
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

        return list(o for o in objects if not o.meta.abstract)


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


def resolve(parent, field):
    """Resolve a field with the given parent instance.
    """
    if callable(field):
        return field(parent)
    else:
        return field
