"""blueprint.mods -- blueprint modifiers."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, overload

from . import base

if TYPE_CHECKING:
    from typing import Self

__all__ = ['Mod']


class Mod(base.Blueprint):
    """A Blueprint Mod modifies other blueprints (or mastered blueprints).

    The mod itself can be mastered first, or applied directly. Mods
    always return mastered items. An example::

        >>> import blueprint as bp
        >>> class Item(bp.Blueprint):
        ...     name = 'generic item'
        ...     quality = bp.RandomInt(1, 6)
        ...     value = 1

        >>> class Magical(bp.Mod):
        ...     name = bp.FormatTemplate('magical {meta.source.name}')
        ...     quality = lambda _: _.meta.source.quality * 1.2
        ...     value = bp.RandomInt(2, 10)

        >>> item = Magical(Item)
        >>> item.name
        'magical generic item'
        >>> 1.2 <= item.quality <= (6*1.2)
        True
        >>> 2 <= item.value <= 10
        True
    """

    @overload
    def __new__(
        cls,
        source: None = None,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> Self: ...

    @overload
    def __new__(  # type: ignore[misc]
        cls,
        source: type[base.Blueprint] | base.Blueprint,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> base.Blueprint: ...

    def __new__(  # type: ignore[misc]
        cls,
        source: type[base.Blueprint] | base.Blueprint | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Self | base.Blueprint:
        """Create a new Mod instance, optionally applying it to a source blueprint.

        Args:
            source: The blueprint class or instance to modify, or None to create an unbound mod.
            *args: Additional positional arguments passed to Blueprint.__init__.
            **kwargs: Additional keyword arguments passed to Blueprint.__init__.

        Returns:
            If source is None, returns the Mod instance itself.
            If source is provided, returns a mastered blueprint with modifications applied.

        """
        base_mod = super().__new__(cls, *args, **kwargs)
        if source is None:
            return base_mod
        base_mod.meta.source = source
        base_mod.__init__(*args, **kwargs)  # type: ignore[misc]
        return base_mod(source)

    def __call__(self, source: type[base.Blueprint] | base.Blueprint) -> base.Blueprint:
        """Apply this mod to a source blueprint.

        Args:
            source: The blueprint class or instance to modify.

        Returns:
            A mastered blueprint with this mod's field values applied.

        """
        if isinstance(source, type):
            # If the source isn't mastered yet, do so now.
            mod: base.Blueprint = source()
        else:
            mod = copy.deepcopy(source)
        mod.meta.source = source

        for name in self.meta.fields:
            setattr(mod, name, getattr(self, name))

        return mod
