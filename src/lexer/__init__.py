# -*- coding: utf-8 -*-
from re import compile

from .types import Type, Token
from .parser import *
from .result import Result


class Lexer:
    TOKEN_EXPRESSIONS = [
        (r'"[^\n"]*"', Type.STRING),
        (r'\'[^\n\']*\'', Type.STRING),
        (r'\#\[[\s\S]+\]\#', None),
        (r'\#[^\n]+', None),
        (r'\s', None),
        (r'\b(if|elif|else|switch|case|while|for|break|continue|echo|var|const|func|return|import)\b', Type.RESERVED),
        (r'[\(\)\{\}\[\];,]', Type.RESERVED),
        (r'(\bin\b|\bor\b|\band\b|&&|\|\||\+\=|\-\=|\*\=|\/\=|\+\+|\-\-)', Type.OPERATOR),
        (r'>=', Type.OPERATOR),
        (r'<=', Type.OPERATOR),
        (r'==', Type.OPERATOR),
        (r'::', Type.OPERATOR),
        (r'!=', Type.OPERATOR),
        (r'\`.+\`', Type.ID),
        (r'\-?[0-9]+\.[0-9]+', Type.FLOAT),
        (r'\-?[0-9]+', Type.INT),
        (r'[\+\-\/\*\=<>~!@$%^&:\.\?]', Type.OPERATOR),
        (r'\b(true|on|enable|false|off|disable)\b', Type.BOOL),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', Type.ID),
        (r'\Z', Type.EOF),
    ]

    @staticmethod
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
            for pattern, token_type in Lexer.TOKEN_EXPRESSIONS:
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

    @staticmethod
    def lex_file(path_to_file: str) -> List[Token]:
        """
        Read and splits source file to tokens
        :param path_to_file: path to file
        :return: list of tokens
        """
        src: str
        with open(path_to_file, 'r', encoding='utf-8') as f:
            src = f.read()
        return Lexer.lex(src)
