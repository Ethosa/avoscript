# -*- coding: utf-8 -*-
from enum import Enum
from typing import Tuple, NewType


class TokenType(Enum):
    EOF = 0
    NEW_LINE = 1
    SPACE = 2
    RESERVED = 3
    OPERATOR = 4
    INT = 5
    FLOAT = 6
    BOOL = 7
    STRING = 8
    ID = 9


class Type(Enum):
    INT = 0
    FLOAT = 1
    BOOL = 2
    STRING = 3
    ARRAY = 4


Token = NewType('Token', Tuple[str, TokenType])
