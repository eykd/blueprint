# -*- coding: utf-8 -*-
"""blueprint.mods -- blueprint modifiers.
"""
from . import base
import copy

__all__ = ['Mod']


class Mod(base.Blueprint):
    """A Blueprint Mod modifies other blueprints (or mastered blueprints).

    The mod itself can be mastered first, or applied directly.
    """
    def __new__(cls, source=None, *args, **kwargs):
        base_mod = super(Mod, cls).__new__(cls, *args, **kwargs)
        if source is None:
            return base_mod
        else:
            base_mod.meta.source = source
            base_mod.__init__(*args, **kwargs)
            return base_mod(source)

    def __call__(self, source):
        if isinstance(source, type):
            # If the source isn't mastered yet, subclass and mod it.
            mod = base.BlueprintMeta(source.__name__ + self.__class__.__name__,
                                     (source, ),
                                     dict((n, self.__dict__.get(n, getattr(self.__class__, n)))
                                          for n in self.meta.fields))
            mod.meta.source = source

            return mod
        else:
            # If the source is mastered, copy and mod it.
            mod = copy.deepcopy(source)
            mod.meta.source = source

            for name in self.meta.fields:
                setattr(mod, name, getattr(self, name))

            return mod
