# -*- coding: utf-8 -*-
from re import compile

from .types import Type, Token
from .parser import *
from .result import Result


TOKEN_EXPRESSIONS = [
    (r'"[^\n"]*"', Type.STRING),
    (r'\'[^\n\']*\'', Type.STRING),
    (r'\#[^\n]+', None),
    (r'\#\[[\s\S]+?\]\#', None),
    (r'\s', None),
    (r'\b(if|elif|else|while|for|break|continue|echo|var|const|func|return|import)\b', Type.RESERVED),
    (r'[\(\)\{\}\[\];,]', Type.RESERVED),
    (r'(\bin\b|\bor\b|\band\b|&&|\|\||\+\=|\-\=|\*\=|\/\=|\+\+|\-\-)', Type.OPERATOR),
    (r'>=', Type.OPERATOR),
    (r'<=', Type.OPERATOR),
    (r'==', Type.OPERATOR),
    (r'::', Type.OPERATOR),
    (r'!=', Type.OPERATOR),
    (r'\-?[0-9]+\.[0-9]+', Type.FLOAT),
    (r'\-?[0-9]+', Type.INT),
    (r'[\+\-\/\*\=<>~!@$%^&:\.]', Type.OPERATOR),
    (r'\b(true|on|enable|false|off|disable)\b', Type.BOOL),
    (r'[a-zA-Z_][a-zA-Z0-9_]*', Type.ID),
    (r'\Z', Type.EOF),
]


def lex(src: str) -> List[Token]:
    """
    Splits source string to tokens
    :param src: source string
    :return: list of tokens
    """
    res: List[Token] = []
    i = 0
    while i < len(src):
        match = None
        for pattern, token_type in TOKEN_EXPRESSIONS:
            regex = compile(pattern)
            match = regex.match(src, i)
            if match:
                if token_type:
                    res.append((match.group(0), token_type))
                break
        if match:
            i = match.end(0)
        else:
            print(f"error at {i} ({src[i]})")
            exit(-1)
    return res
