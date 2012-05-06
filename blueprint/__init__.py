# -*- coding: utf-8 -*-
"""blueprint -- magical blueprints for procedural generation of content.

Based roughly on http://www.squidi.net/mapmaker/musings/m100402.php
"""
import base
import fields
import taggables
import factories
import mods
import dice

from base import *
from fields import *
from mods import *
from factories import *
from markov import *
from collection import *

__all__ = list(base.__all__) \
          + fields.__all__ \
          + mods.__all__ \
          + factories.__all__ \
          + collection.__all__ \
          + ['base', 'fields', 'taggables', 'factories', 'mods', 'dice']
