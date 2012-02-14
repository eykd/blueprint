# -*- coding: utf-8 -*-
"""blueprint -- magical blueprints for procedural generation of content.

Based roughly on http://www.squidi.net/mapmaker/musings/m100402.php
"""
import base
import fields
import taggables

from base import *
from fields import *

__all__ = list(base.__all__) + fields.__all__ + ['base', 'fields']
