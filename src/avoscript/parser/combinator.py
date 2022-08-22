# -*- coding: utf-8 -*-
from typing import List, Callable

from src.avoscript.lexer.types import Token
from src.avoscript.lexer.result import Result


class Combinator:
    def __call__(self, tokens: List[Token], i: int) -> Result:
        pass

    def __add__(self, other) -> 'Combinator':
        return Concat(self, other)

    def __mul__(self, other) -> 'Combinator':
        return Exp(self, other)

    def __or__(self, other) -> 'Combinator':
        return Alt(self, other)

    def __xor__(self, other) -> 'Combinator':
        return Process(self, other)


class Reserved(Combinator):
    def __init__(self, value, token: Token):
        self.value = value
        self.token = token

    def __call__(self, tokens: List[Token], i: int) -> Result:
        if (
                i < len(tokens) and
                tokens[i][0] == self.value and
                tokens[i][1] == self.token
        ):
            return Result(tokens[i][0], i+1)

    def __repr__(self) -> str:
        return f"Reserved({self.value}, {self.token})"


class Tag(Combinator):
    def __init__(self, token: Token):
        self.token = token

    def __call__(self, tokens, i) -> Result:
        if i < len(tokens) and tokens[i][1] == self.token:
            return Result(tokens[i][0], i+1)

    def __repr__(self) -> str:
        return f"Tag({self.token})"


class Concat(Combinator):
    def __init__(self, left: Combinator, r: Combinator):
        self.left = left
        self.r = r

    def __call__(self, tokens: List[Token], i: int) -> Result:
        l_res = self.left(tokens, i)
        if l_res:
            r_res = self.r(tokens, l_res.pos)
            if r_res:
                res = (l_res.value, r_res.value)
                return Result(res, r_res.pos)

    def __repr__(self) -> str:
        return f"Concat({self.left}, {self.r})"


class Alt(Combinator):
    def __init__(self, left: Combinator, r: Combinator):
        self.left = left
        self.r = r

    def __call__(self, tokens: List[Token], i: int) -> Result:
        l_res = self.left(tokens, i)
        if l_res:
            return l_res
        else:
            return self.r(tokens, i)

    def __repr__(self) -> str:
        return f"Alt({self.left}, {self.r})"


class Opt(Combinator):
    def __init__(self, c: Combinator):
        self.c = c

    def __call__(self, tokens: List[Token], i: int) -> Result:
        res = self.c(tokens, i)
        if res:
            return res
        return Result(None, i)

    def __repr__(self) -> str:
        return f"Opt({self.c})"


class Rep(Combinator):
    def __init__(self, c: Combinator):
        self.c = c

    def __call__(self, tokens: List[Token], i: int) -> Result:
        res = self.c(tokens, i)
        result = []
        while res:
            result.append(res)
            i = res.pos
            res = self.c(tokens, i)
        return Result(result, i)

    def __repr__(self) -> str:
        return f"Rep({self.c})"


class Process(Combinator):
    def __init__(self, c: Combinator, f: Callable):
        self.c = c
        self.f = f

    def __call__(self, tokens: List[Token], i: int) -> Result:
        res = self.c(tokens, i)
        if res:
            res.value = self.f(res.value)
            return res

    def __repr__(self) -> str:
        return f"Process({self.c}, {self.f})"


class Exp(Combinator):
    def __init__(self, c: Combinator, sep: Combinator):
        self.c = c
        self.sep = sep

    def __call__(self, tokens: List[Token], i: int) -> Result:
        res = self.c(tokens, i)

        def process_next(result):
            sep_func, r = result
            return sep_func(res.value, r)
        if self.sep:
            next_c = self.sep + self.c ^ process_next
        else:
            next_c = self.c ^ process_next
        next_res = res
        while next_res:
            next_res = next_c(tokens, res.pos)
            if next_res:
                res = next_res
        return res

    def __repr__(self) -> str:
        return f"Exp({self.c}, {self.sep})"


class Lazy(Combinator):
    def __init__(self, c_func: Callable):
        self.c = None
        self.c_func = c_func

    def __call__(self, tokens: List[Token], i: int) -> Result:
        if not self.c:
            self.c = self.c_func()
        return self.c(tokens, i)

    def __repr__(self) -> str:
        return f"Lazy({self.c}, {self.c_func})"


class Phrase(Combinator):
    def __init__(self, c: Combinator):
        self.c = c

    def __call__(self, tokens: List[Token], i: int) -> Result:
        res = self.c(tokens, i)
        if res and res.pos == len(tokens):
            return res
        else:
            raise RuntimeError(f"error at {res.pos} token. {res.value}")

    def __repr__(self) -> str:
        return f"Phrase({self.c})"
