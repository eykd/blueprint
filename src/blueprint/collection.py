"""blueprint.collections -- a collection class for blueprints."""

import itertools as it
import sys
from collections.abc import Generator, Iterator, Sequence
from typing import Any, overload

from blueprint.base import Blueprint

__all__ = ['BlueprintCollection']


class BlueprintCollection(Sequence[Blueprint]):
    """A collection that generates blueprint instances on demand.

    This class implements both Sequence and Callable protocols to provide
    flexible access to blueprint instances. It can be called to generate
    blueprints with custom parameters, or indexed/sliced to generate
    blueprints with deterministic seeds.
    """

    blueprint: type[Blueprint]
    seed: str
    kwargs: dict[str, Any]

    def __init__(self, blueprint: type[Blueprint], seed: str = '', **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize a blueprint collection.

        Args:
            blueprint: The Blueprint class to instantiate
            seed: Base seed string for deterministic generation
            **kwargs: Additional keyword arguments to pass to blueprint instances

        """
        self.blueprint = blueprint
        self.seed = seed
        self.kwargs = kwargs

    def __len__(self) -> int:
        """Return the theoretical maximum size of the collection."""
        return sys.maxsize

    def __iter__(self) -> Iterator[Blueprint]:
        """Return an iterator over the collection."""
        return iter(self)

    def __contains__(self, item: object) -> bool:
        """Check if an item is in the collection (always True)."""
        return True

    def __call__(
        self,
        parent: Blueprint | None = None,
        seed: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Blueprint:
        """Generate a blueprint instance with the given parameters.

        Args:
            parent: Optional parent blueprint
            seed: Optional seed override (uses collection's seed if not provided)
            **kwargs: Additional keyword arguments merged with collection's kwargs

        Returns:
            A mastered blueprint instance

        """
        options: dict[str, Any] = {}
        options.update(self.kwargs)
        options.update(kwargs)
        return self.blueprint(parent=parent, seed=seed if seed is not None else self.seed, **options)

    @overload
    def __getitem__(self, idx: int) -> Blueprint: ...

    @overload
    def __getitem__(self, idx: slice) -> Sequence[Blueprint]: ...

    def __getitem__(self, idx: int | slice) -> Blueprint | Sequence[Blueprint] | Generator[Blueprint, None, None]:
        """Get blueprint(s) by index or slice.

        Args:
            idx: Integer index or slice object

        Returns:
            - For integer index: Single blueprint with deterministic seed
            - For slice with stop: List of blueprints
            - For slice without stop: Infinite generator of blueprints

        """
        if isinstance(idx, slice):
            seed = f'{self.seed}%s'
            if idx.stop is None:
                return (self(seed=seed % i, **self.kwargs) for i in it.count(idx.start or 0, idx.step or 1))
            return [self(seed=seed % i) for i in range(idx.start or 0, idx.stop, idx.step or 1)]
        seed = f'{self.seed}{idx}'
        return self(seed=seed)
