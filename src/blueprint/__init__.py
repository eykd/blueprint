"""blueprint -- magical blueprints for procedural generation of content.

Based roughly on http://www.squidi.net/mapmaker/musings/m100402.php
"""

import blueprint.taggables as mods
from blueprint import base, collection, dice, factories, fields, mods
from blueprint._version import VERSION
from blueprint.base import *
from blueprint.collection import *
from blueprint.factories import *
from blueprint.fields import *
from blueprint.markov import *
from blueprint.mods import *

__all__ = (
    list(base.__all__)
    + fields.__all__
    + mods.__all__
    + factories.__all__
    + collection.__all__
    + ['base', 'fields', 'taggables', 'factories', 'mods', 'dice']
)
