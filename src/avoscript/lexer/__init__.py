# -*- coding: utf-8 -*-
from typing import List
from re import compile

from .types import TokenType, Token


class Lexer:
    TOKEN_EXPRESSIONS = [
        (r'"[^\n"]*"', TokenType.STRING),
        (r'\'[^\n\']*\'', TokenType.STRING),
        (r'\#\[[\s\S]+\]\#', None),
        (r'\#[^\n]+', None),
        (r'\s', None),
        (r'\b(if|elif|else|switch|case|while|for|break|continue)\b', TokenType.RESERVED),
        (r'\b(echo|read|var|const|func|return|import|from)\b', TokenType.RESERVED),
        (r'\b(class|init|super|this|abstract|interface|of)\b', TokenType.RESERVED),
        (r'\b(try|catch)\b', TokenType.RESERVED),
        (r'[\(\)\{\}\[\];,]', TokenType.RESERVED),
        (r'(\bin\b|\bor\b|\band\b|&&|\|\||\+\=|\-\=|\*\=|\/\=|\+\+|\-\-)', TokenType.OPERATOR),
        (r'\b(int|float|string|range|length)\b', TokenType.BUILT_IN),
        (r'(=>|->)', TokenType.OPERATOR),
        (r'>=', TokenType.OPERATOR),
        (r'<=', TokenType.OPERATOR),
        (r'==', TokenType.OPERATOR),
        (r'::', TokenType.OPERATOR),
        (r'!=', TokenType.OPERATOR),
        (r'\`.+\`', TokenType.ID),
        (r'\-?[0-9]+\.[0-9]+', TokenType.FLOAT),
        (r'\-?[0-9]+', TokenType.INT),
        (r'[\+\-\/\*\=<>~!@$%^&:\.\?]', TokenType.OPERATOR),
        (r'\b(true|on|enable|false|off|disable)\b', TokenType.BOOL),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', TokenType.ID),
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
        return res + [(None, TokenType.EOF)]

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
