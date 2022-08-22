# -*- coding: utf-8 -*-
from enum import Enum
from typing import Tuple, NewType
import sys


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


class Signal:
    def __init__(self):
        self.IN_CYCLE = False
        self.IN_FOR_CYCLE = False
        self.IN_FUNCTION = False
        self.IN_CLASS = False
        self.IN_TRY = False
        self.IN_MAIN = False
        self.IN_MODULE = False
        self.BREAK = False
        self.CONTINUE = False
        self.RETURN = False
        self.NO_CREATE_LEVEL = False
        self.CREATE_BACK_LEVEL = False
        self.BACK_LEVEL = None
        self.RETURN_VALUE = None
        self.ARGUMENTS = None
        self.KW_ARGUMENTS = None
        self.CURRENT_CLASS = None
        self.ERROR = None
        self.CURRENT_MODULE = 'main'
        self.ENUM_COUNTER = 0
        # no refresh
        self.NEED_FREE = True
        self.VERBOSE = False

    def refresh(self):
        self.IN_CYCLE = False
        self.IN_FOR_CYCLE = False
        self.IN_FUNCTION = False
        self.IN_CLASS = False
        self.IN_TRY = False
        self.IN_MAIN = False
        self.IN_MODULE = False
        self.BREAK = False
        self.CONTINUE = False
        self.RETURN = False
        self.NO_CREATE_LEVEL = False
        self.CREATE_BACK_LEVEL = False
        self.BACK_LEVEL = None
        self.RETURN_VALUE = None
        self.ARGUMENTS = None
        self.KW_ARGUMENTS = None
        self.CURRENT_CLASS = None
        self.ERROR = None
        self.CURRENT_MODULE = 'main'
        self.ENUM_COUNTER = 0


class StdString:
    def __init__(self):
        self.out = ""

    def write(self, v):
        self.out += v

    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = sys.__stdout__


class LevelIndex:
    def __init__(self):
        self.i = -1

    def __index__(self):
        return self.i

    def __add__(self, other: int) -> int:
        return self.i + other

    def __sub__(self, other: int) -> int:
        return self.i - other

    def __repr__(self) -> str:
        return str(self.i)

    def inc(self):
        self.i += 1

    def dec(self):
        self.i -= 1


Token = NewType('Token', Tuple[str, TokenType])
