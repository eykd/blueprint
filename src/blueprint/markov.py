# -*- coding: utf-8 -*-
"""blueprint.markov -- Markov Chain generator.
"""
import collections

from blueprint import fields

try:
    _ = xrange
    del _
except NameError:
    xrange = range  # Python 3

__all__ = ['MarkovChain']


class MarkovChain(fields.Field, collections.Mapping):
    """Uses a Markov Chain to generate random sequences.

    Derived from Peter Corbett's CGI random name generator, with input
    from the ElderLore object-oriented variation.

    http://www.pick.ucam.org/~ptc24/mchain.html
    """
    def __init__(self, source_list, chainlen=2, max_length=10):
        if 1 > chainlen > 10:
            raise ValueError("Chain length must be between 1 and 10, inclusive")
        self._dict = collections.defaultdict(list)
        self.chainlen = chainlen
        self.max_length = max_length
        self.readData(source_list)

    def next(self):
        return self.getRandomName()
        
    def readData(self, names, destroy=False):
        if destroy:
            self._dict.clear()

        oldnames = []
        chainlen = self.chainlen

        for name in names:
            oldnames.append(name)
            spacer = u''.join((u" " * chainlen, name))
            name_len = len(name)
            for num in xrange(name_len):
                self.add_key(spacer[num:num+chainlen], spacer[num+chainlen])
            self.add_key(spacer[name_len:name_len+chainlen], "\n")

    def getRandomName(self, parent):
        """Return a random name.
        """
        prefix = u" " * self.chainlen
        name = u""
        suffix = u""
        while 1:
            suffix = self.get_suffix(prefix, parent)
            if suffix == u"-":
                continue
            elif suffix == u"\n" or len(name) == self.max_length:
                break
            else:
                name = u''.join((name, suffix))
                prefix = u''.join((prefix[1:], suffix))
        return name

    def __call__(self, parent):
        return self.getRandomName(parent)

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def add_key(self, prefix, suffix):
        self._dict[prefix].append(suffix)

    def get_suffix(self, prefix, parent):
        return parent.meta.random.choice(self[prefix])
