# -*- coding: utf-8 -*-
from random import randint, random
from .types import LevelIndex


ENV = []
ENV_CONSTS = []
STATEMENT_LIST_LEVEL = LevelIndex()
MODULES = {
    # module_name: statement_list_level
}
BUILTIN = {
    'round': round,
    'randf': random,
    'randi': randint,
    'range': range,
    'length': len,
    'string': str,
    'int': int,
    'float': float,
    'array': list,
}
BUILTIN_BUILD = False
