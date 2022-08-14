# -*- coding: utf-8 -*-

class Result:
    def __init__(self, value, pos):
        self.value = value
        self.pos = pos

    def __repr__(self) -> str:
        return f"Result({self.value}, {self.pos})"
