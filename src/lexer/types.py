# -*- coding: utf-8 -*-
from enum import Enum
from typing import Tuple, NewType


class Type(Enum):
    EOF = 0
    RESERVED = 1
    OPERATOR = 2
    INT = 3
    FLOAT = 4
    BOOL = 5
    STRING = 6
    ID = 7


Token = NewType('Token', Tuple[str, Type])
