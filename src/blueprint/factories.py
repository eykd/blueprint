"""blueprint.factories -- blueprint factories."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from . import base

if TYPE_CHECKING:
    from collections.abc import Sequence

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

    product: ClassVar[Any] = None
    mods: ClassVar[Sequence[Any]] = []

    def __new__(cls, *args: Any, **kwargs: Any) -> base.Blueprint:  # type: ignore[misc]  # noqa: ANN401
        """Create a new Factory instance and immediately return the product.

        Args:
            *args: Additional positional arguments passed to Blueprint.__init__.
            **kwargs: Additional keyword arguments passed to Blueprint.__init__.

        Returns:
            A mastered blueprint with mods applied.

        Raises:
            ValueError: If the Factory subclass doesn't define a product field.
            TypeError: If the product field doesn't resolve to a Blueprint.

        """
        if cls.product is None:
            raise ValueError('Factory subclasses must define a `product` field in order to be used.')

        factory = super().__new__(cls, *args, **kwargs)
        factory.__init__(*args, **kwargs)  # type: ignore[misc]

        if not isinstance(factory.product, base.Blueprint) and not isinstance(factory.product, base.BlueprintMeta):
            msg = f'The `Factory.product` field must resolve to a single blueprint when mastered.\n{factory.product!r}'
            raise TypeError(msg)

        return factory()

    def __call__(
        self,
        parent: base.Blueprint | None = None,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> base.Blueprint:
        """Apply mods to the product and return the result.

        Args:
            parent: Optional parent blueprint for nested blueprint context.
            *args: Additional positional arguments passed to product instantiation.
            **kwargs: Additional keyword arguments passed to product instantiation.

        Returns:
            A mastered blueprint with all mods applied and factory fields transferred.

        """
        product: type[base.Blueprint] | base.Blueprint = self.product
        for mod in self.mods:
            product = mod(product)

        if isinstance(product, type):
            # If the product isn't mastered yet, master it.
            # Ensure parent is passed correctly by putting it in kwargs
            call_kwargs = {**kwargs, 'parent': parent}
            product = product(*args, **call_kwargs)

        for name in self.meta.fields:
            if name in {'product', 'mods'}:
                continue
            setattr(product, name, getattr(self, name))

        return product
