# -*- coding: utf-8 -*-
"""blueprint -- magical blueprints for procedural generation of content.

Based roughly on http://www.squidi.net/mapmaker/musings/m100402.php
"""
import blueprint.base as base
import blueprint.fields as fields
import blueprint.taggables as mods
import blueprint.factories as factories
import blueprint.mods as mods
import blueprint.dice as dice
import blueprint.collection as collection
from blueprint.base import *
from blueprint.fields import *
from blueprint.mods import *
from blueprint.factories import *
from blueprint.markov import *
from blueprint.collection import *

__all__ = list(base.__all__) \
          + fields.__all__ \
          + mods.__all__ \
          + factories.__all__ \
          + collection.__all__ \
          + ['base', 'fields', 'taggables', 'factories', 'mods', 'dice']
