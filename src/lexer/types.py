# -*- coding: utf-8 -*-
from enum import Enum
from typing import Tuple, NewType


class TokenType(Enum):
    EOF = 0
    RESERVED = 1
    OPERATOR = 2
    INT = 3
    FLOAT = 4
    BOOL = 5
    STRING = 6
    BUILT_IN = 7
    ID = 8


class Type(Enum):
    INT = 0
    FLOAT = 1
    BOOL = 2
    STRING = 3
    ARRAY = 4


Token = NewType('Token', Tuple[str, TokenType])
