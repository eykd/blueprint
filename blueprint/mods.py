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
            # If the source isn't mastered yet, do so now.
            mod = source()
        else:
            mod = copy.deepcopy(source)
        mod.meta.source = source

        for name in self.meta.fields:
            setattr(mod, name, getattr(self, name))

        return mod
