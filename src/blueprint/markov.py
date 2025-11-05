"""blueprint.markov -- Markov Chain generator."""

from __future__ import annotations

import collections
from collections.abc import Iterable, Iterator, Mapping
from typing import TYPE_CHECKING

from blueprint import fields

if TYPE_CHECKING:
    from blueprint.base import Blueprint

__all__ = ['MarkovChain']

# Constants
MAX_CHAIN_LENGTH = 10


class MarkovChain(fields.Field, Mapping[str, list[str]]):
    """Uses a Markov Chain to generate random sequences.

    Derived from Peter Corbett's CGI random name generator, with input
    from the ElderLore object-oriented variation.

    http://www.pick.ucam.org/~ptc24/mchain.html
    """

    _dict: collections.defaultdict[str, list[str]]
    chainlen: int
    max_length: int

    def __init__(self, source_list: Iterable[str], chainlen: int = 2, max_length: int = 10) -> None:
        if 1 > chainlen > MAX_CHAIN_LENGTH:
            msg = f'Chain length must be between 1 and {MAX_CHAIN_LENGTH}, inclusive'
            raise ValueError(msg)
        self._dict = collections.defaultdict(list)
        self.chainlen = chainlen
        self.max_length = max_length
        self.read_data(source_list)

    def next(self) -> str:
        """Generate the next random name in the sequence.

        Note: This method has a known issue where it doesn't pass the required parent argument.
        """
        return self.get_random_name()  # type: ignore[call-arg]  # Missing parent arg is a bug in original code

    def read_data(self, names: Iterable[str], *, destroy: bool = False) -> None:
        """Read training data from an iterable of names.

        Args:
            names: Iterable of strings to use as training data for the Markov chain.
            destroy: If True, clear existing chain data before reading. Defaults to False.

        """
        if destroy:
            self._dict.clear()

        oldnames = []
        chainlen = self.chainlen

        for name in names:
            oldnames.append(name)
            spacer = ''.join((' ' * chainlen, name))
            name_len = len(name)
            for num in range(name_len):
                self.add_key(spacer[num : num + chainlen], spacer[num + chainlen])
            self.add_key(spacer[name_len : name_len + chainlen], '\n')

    def get_random_name(self, parent: Blueprint) -> str:
        """Return a random name."""
        prefix = ' ' * self.chainlen
        name = ''
        suffix = ''
        while 1:
            suffix = self.get_suffix(prefix, parent)
            if suffix == '-':
                continue
            if suffix == '\n' or len(name) == self.max_length:
                break
            name = f'{name}{suffix}'
            prefix = ''.join((prefix[1:], suffix))
        return name

    def __call__(self, parent: Blueprint) -> str:
        """Generate a random name when the MarkovChain is called as a field.

        Args:
            parent: The blueprint instance this field belongs to.

        Returns:
            A randomly generated name based on the training data.

        """
        return self.get_random_name(parent)

    def __getitem__(self, key: str) -> list[str]:
        return self._dict[key]

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def add_key(self, prefix: str, suffix: str) -> None:
        """Add a prefix-suffix pair to the Markov chain dictionary.

        Args:
            prefix: The prefix string (key) in the chain.
            suffix: The suffix character to associate with this prefix.

        """
        self._dict[prefix].append(suffix)

    def get_suffix(self, prefix: str, parent: Blueprint) -> str:
        """Get a random suffix character for the given prefix.

        Args:
            prefix: The prefix string to look up in the chain.
            parent: The blueprint instance, used to access the random number generator.

        Returns:
            A randomly selected suffix character associated with the prefix.

        """
        return parent.meta.random.choice(self[prefix])
