"""blueprint.collections -- a collection class for blueprints.
"""
import sys
from collections.abc import Callable, Sequence

__all__ = ['BlueprintCollection']


class BlueprintCollection(Sequence, Callable):
    def __init__(self, blueprint, seed='', **kwargs):
        self.blueprint = blueprint
        self.seed = seed
        self.kwargs = kwargs

    def __len__(self):
        return sys.maxsize

    def __iter__(self):
        return iter(self)

    def __contains__(self):
        return True

    def __call__(self, parent=None, seed=None, **kwargs):
        options = {}
        options.update(self.kwargs)
        options.update(kwargs)
        return self.blueprint(parent=parent,
                              seed=seed if seed is not None else self.seed,
                              **options)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            seed = '%s%%s' % self.seed
            if idx.stop is None:
                return (self(seed=seed % i, **self.kwargs)
                        for i in it.count(idx.start or 0, idx.step or 1))
            return [self(seed=seed % i)
                    for i in range(idx.start or 0,
                                   idx.stop, idx.step or 1)]
        seed = '%s%s' % (self.seed, idx)
        return self(seed=seed)
