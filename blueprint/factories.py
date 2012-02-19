# -*- coding: utf-8 -*-
"""blueprint.factories -- blueprint factories.
"""
from . import base
import copy

__all__ = ['Factory']


class Factory(base.Blueprint):
    """A Factory assembles mastered blueprints made to order.

    A Factory subclass can define the following fields:

    - ``product``: A Factory subclass *must* define a ``product``
      field. The ``product`` field *must* resolve to a single
      Blueprint.

    - ``mods``: A list of mods to apply to the product field.

    Calling a factory will return the product with mods applied.
    """
    product = None
    mods = []
    
    def __new__(cls, *args, **kwargs):
        if cls.product is None:
            raise ValueError('Factory subclasses must define a `product` field in order to be used.')

        factory = super(Factory, cls).__new__(cls, *args, **kwargs)
        factory.__init__(*args, **kwargs)

        if not isinstance(factory.product, base.Blueprint) \
               and not isinstance(factory.product, base.BlueprintMeta):
            raise TypeError('The `Factory.product` field must resolve to a single blueprint when mastered.\n%r' \
                            % factory.product)

        return factory()

    def __call__(self, parent=None, *args, **kwargs):
        product = self.product
        for mod in self.mods:
            product = mod(product)
        
        if isinstance(product, type):
            # If the product isn't mastered yet, master it.
            product = product(parent=parent, *args, **kwargs)

        for name in self.meta.fields:
            if name in ('product', 'mods'):
                continue
            setattr(product, name, getattr(self, name))

        return product
