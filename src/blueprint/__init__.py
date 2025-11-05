"""blueprint -- magical blueprints for procedural generation of content.

Based roughly on http://www.squidi.net/mapmaker/musings/m100402.php
"""

from blueprint import base, collection, dice, factories, fields, mods, taggables
from blueprint._version import VERSION
from blueprint.base import Blueprint
from blueprint.collection import BlueprintCollection
from blueprint.factories import Factory
from blueprint.fields import (
    All,
    Dice,
    DiceTable,
    Field,
    FormatTemplate,
    PickFrom,
    PickOne,
    Property,
    RandomInt,
    WithTags,
    defer_to_end,
    depends_on,
    generator,
    resolve,
)
from blueprint.markov import MarkovChain
from blueprint.mods import Mod

__all__ = [
    'VERSION',
    'All',
    'Blueprint',
    'BlueprintCollection',
    'Dice',
    'DiceTable',
    'Factory',
    'Field',
    'FormatTemplate',
    'MarkovChain',
    'Mod',
    'PickFrom',
    'PickOne',
    'Property',
    'RandomInt',
    'WithTags',
    'base',
    'collection',
    'defer_to_end',
    'depends_on',
    'dice',
    'factories',
    'fields',
    'generator',
    'mods',
    'resolve',
    'taggables',
]
