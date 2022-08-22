# -*- coding: utf-8 -*-
from codecs import decode
from typing import Tuple, List, Any
from pprint import pprint
from re import findall, compile, UNICODE, VERBOSE

from colorama import Fore

from equality import AnyBase
from . import Lexer, parser, statements, default


def has_variable(name: str, env, consts) -> Tuple[bool, int, bool]:
    """
    Finds variable or constant in environments
    :param name: var/const name
    :param env: variable environment
    :param consts: constants environment
    :return: (contains, level index, is constant)
    """
    for level in range(len(env) - 1, -1, -1):
        if name in env[level]:
            return True, level, False
        elif name in consts[level]:
            return True, level, True
    return False, 0, False


# --== AST ==-- #
class ASTExpr(AnyBase):
    def __repr__(self) -> str:
        return "AST expression"

    def eval(self, env, consts, lvl, modules, signal):
        raise RuntimeError('nothing to eval')


class NullAST(ASTExpr):
    def __repr__(self) -> str:
        return "NullAST()"

    def eval(self, env, consts, lvl, modules, signal):
        return None


class IntAST(ASTExpr):
    def __init__(self, i: int):
        self.i = i

    def __repr__(self) -> str:
        return f"IntAST({Fore.LIGHTYELLOW_EX}{self.i}{Fore.RESET})"

    def eval(self, env, consts, lvl, modules, signal):
        return self.i


class FloatAST(ASTExpr):
    def __init__(self, f: float):
        self.f = f

    def __repr__(self) -> str:
        return f"FloatAST({Fore.LIGHTYELLOW_EX}{self.f}{Fore.RESET})"

    def eval(self, env, consts, lvl, modules, signal):
        return self.f


class BoolAST(ASTExpr):
    def __init__(self, b: bool):
        self.b = b

    def __repr__(self) -> str:
        return f"BoolAST({Fore.YELLOW}{self.b}{Fore.RESET})"

    def eval(self, env, consts, lvl, modules, signal):
        return self.b


class StringAST(ASTExpr):
    VARIABLE = r'\$[a-zA-Z][a-zA-Z0-9_]*'
    EXPRESSION = r'\$\{.*\}'
    ESCAPE_SEQUENCE_RE = compile(
        r'(\\U........|\\u....|\\x..|\\[0-7]{1,3}|\\N\{[^}]+\}|\\[\\\'"abfnrtv])', UNICODE | VERBOSE
    )

    def __init__(self, s: str):
        self.s = s

    def __repr__(self) -> str:
        return f'StringAST({Fore.LIGHTGREEN_EX}"{self.s}"{Fore.RESET})'

    def decode(self):
        def decode_match(match):
            return decode(match.group(0), 'unicode-escape')

        return StringAST.ESCAPE_SEQUENCE_RE.sub(decode_match, self.s)

    def eval(self, env, consts, lvl, modules, signal):
        result = self.s
        matched = findall(StringAST.VARIABLE, result)
        for m in matched:
            result = result.replace(m, str(VarAST(m[1:]).eval(env, consts, lvl, modules, signal)))
        matched = findall(StringAST.EXPRESSION, result)
        for m in matched:
            result = result.replace(
                m,
                str(parser.expression()(Lexer.lex(m[2:-1]), 0).value.eval(env, consts, lvl, modules, signal))
            )
        return self.decode()


class ArrayAST(ASTExpr):
    def __init__(self, arr: List[Any]):
        self.arr = [i.value[0] for i in arr]

    def __repr__(self) -> str:
        return f"ArrayAST({self.arr})"

    def eval(self, env, consts, lvl, modules, signal):
        return [i.eval(env, consts, lvl, modules, signal) for i in self.arr]


class GeneratorAST(ASTExpr):
    def __init__(self, val, var, obj, condition):
        self.val = val
        self.var = var
        self.obj = obj
        self.condition = condition

    def __repr__(self) -> str:
        return f"GeneratorAST({self.val}, {self.var}, {self.obj}, {self.condition})"

    def eval(self, env, consts, lvl, modules, signal):
        result = []
        env.append({})
        consts.append({})
        lvl.inc()
        for i in self.obj.eval(env, consts, lvl, modules, signal):
            env[lvl][self.var] = i
            if self.condition is not None:
                if self.condition.eval(env, consts, lvl, modules, signal):
                    result.append(self.val.eval(env, consts, lvl, modules, signal))
            else:
                result.append(self.val.eval(env, consts, lvl, modules, signal))
        lvl.dec()
        consts.pop()
        env.pop()
        return result


class VarAST(ASTExpr):
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self) -> str:
        return f"VarAST({self.var_name})"

    def eval(self, env, consts, lvl, modules, signal):
        has_var, level, is_const = has_variable(self.var_name, env, consts)
        if has_var:
            if is_const:
                return consts[level][self.var_name]
            else:
                return env[level][self.var_name]
        signal.ERROR = f'{self.var_name} was used before assign'


class ModuleCallAST(ASTExpr):
    def __init__(self, module_name, module_obj):
        self.name = module_name
        self.obj = module_obj

    def __repr__(self) -> str:
        return f"ModuleCallAST({self.name}, {self.obj})"

    def eval(self, env, consts, lvl, modules, signal):
        in_built_in = (self.name, self.obj) in default.BUILTIN
        if self.name in modules:
            if self.obj not in env[modules[self.name]]:
                signal.ERROR = f"unknown module object {self.obj}"
                return
            elif in_built_in:
                return None
            return env[modules[self.name]][self.obj]
        elif in_built_in:
            return None
        signal.ERROR = f"unknown module {self.obj}"


class ClassPropAST(ASTExpr):
    def __init__(self, name, prop, is_super):
        self.name = name
        self.prop = prop
        self.is_super = is_super

    def __repr__(self) -> str:
        return f"ClassPropAST({self.name}, {self.prop})"

    def eval(self, env, consts, lvl, modules, signal):
        if signal.IN_CLASS and signal.CURRENT_CLASS and self.name == 'this':
            self.name = signal.CURRENT_CLASS
        has_var, level, is_const = has_variable(self.name, env, consts)
        if has_var:
            obj = env[level][self.name]
            result = None
            if self.is_super and obj['parent'] is not None:
                obj = obj['parent']
            if self.prop in obj['env']:
                result = obj['env'][self.prop]
            if self.prop in obj['consts_env']:
                result = obj['consts_env'][self.prop]
            while obj['parent'] and result is None:
                obj = obj['parent']
                if self.prop in obj['env']:
                    result = obj['env'][self.prop]
                    break
                if self.prop in obj['env_consts']:
                    result = obj['env_consts'][self.prop]
                    break
            if result is not None:
                if obj['prefix'] == 'abstract':
                    print(f'[WARNING]: {self.prop} is abstract property')
                return result
            signal.ERROR = f"unknown property {self.prop} of {self.name}"
        else:
            signal.ERROR = f"unknown class {self.name}"


class ArgumentAST(ASTExpr):
    """serves FuncStmt/CallStmt arguments"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"ArgumentAST({self.name}, {self.value})"

    def eval(self, env, consts, lvl, modules, signal):
        return self.name, self.value


class BraceAST(ASTExpr):
    """serves array[index]"""

    def __init__(self, obj, v):
        self.obj = obj
        self.v = v

    def __repr__(self) -> str:
        return f"BraceAST({self.v})"

    def eval(self, env, consts, lvl, modules, signal):
        result = None
        if isinstance(self.obj, str):
            result = VarAST(self.obj).eval(env, consts, lvl, modules, signal)
        elif isinstance(self.obj, (ArrayAST, StringAST, statements.CallStmt, ModuleCallAST, ClassPropAST)):
            result = self.obj.eval(env, consts, lvl, modules, signal)
        if result is not None:
            for i in self.v:
                result = result[i.eval(env, consts, lvl, modules, signal)]
        if result is not None:
            return result
        signal.ERROR = f"{self.obj.eval(env, consts, lvl, modules, signal)} isn't indexed"


class BinOpAST(ASTExpr):
    def __init__(self, op, left, r):
        self.op = op
        self.left = left
        self.r = r

    def __repr__(self) -> str:
        return f"BinOpAST({self.op}, {self.left}, {self.r})"

    def eval(self, env, consts, lvl, modules, signal):
        r_val = self.r.eval(env, consts, lvl, modules, signal)
        l_val = self.left.eval(env, consts, lvl, modules, signal)
        match self.op:
            case '*':
                return l_val * r_val
            case '/':
                return l_val / r_val
            case '-':
                return l_val - r_val
            case '+':
                return l_val + r_val
            case '%':
                return l_val % r_val
            case _:
                signal.ERROR = f'unknown operation {self.op}'


class UnaryOpAST(ASTExpr):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __repr__(self) -> str:
        return f"UnaryOpAST({self.op}, {self.expr})"

    def eval(self, env, consts, lvl, modules, signal):
        match self.op:
            case '++':
                binop = BinOpAST('+', self.expr, IntAST(1))
                if isinstance(self.expr, VarAST):
                    assign_stmt = statements.AssignStmt(self.expr.var_name, binop)
                    assign_stmt.eval(env, consts, lvl, modules, signal)
                    return self.expr.eval(env, consts, lvl, modules, signal)
                return binop.eval(env, consts, lvl, modules, signal)
            case '--':
                binop = BinOpAST('-', self.expr, IntAST(1))
                if isinstance(self.expr, VarAST):
                    assign_stmt = statements.AssignStmt(self.expr.var_name, binop)
                    assign_stmt.eval(env, consts, lvl, modules, signal)
                    return self.expr.eval(env, consts, lvl, modules, signal)
                return binop.eval(env, consts, lvl, modules, signal)
            case '-':
                return -(self.expr.eval(env, consts, lvl, modules, signal))
            case _:
                signal.ERROR = f"unknown unary operation: {self.op}"


class TernaryOpAST(ASTExpr):
    def __init__(self, first, op1, second, op2, third):
        self.first = first
        self.second = second
        self.third = third
        self.op1 = op1
        self.op2 = op2

    def __repr__(self) -> str:
        return f"TernaryOpAST({self.first}, {self.op1}, {self.second}, {self.op2}, {self.third})"

    def eval(self, env, consts, lvl, modules, signal):
        if self.op1 == '?' and self.op2 == ':':
            if self.first.eval(env, consts, lvl, modules, signal):
                return self.second.eval(env, consts, lvl, modules, signal)
            return self.third.eval(env, consts, lvl, modules, signal)
        elif self.op1 == 'if' and self.op2 == 'else':
            if self.second.eval(env, consts, lvl, modules, signal):
                return self.first.eval(env, consts, lvl, modules, signal)
            return self.third.eval(env, consts, lvl, modules, signal)
        signal.ERROR = f"unknown ternary operator {self.op1}, {self.op2}"


# --== Binary operations ==-- #
class BinOpExpr(AnyBase):
    def eval(self, env, consts, lvl, modules, signal):
        raise RuntimeError('unknown binary operation')


class RelativeOp(BinOpExpr):
    def __init__(self, op, left, r):
        self.op = op
        self.left = left
        self.r = r

    def __repr__(self) -> str:
        return f"RelOp({self.left}, {self.op}, {self.r})"

    def eval(self, env, consts, lvl, modules, signal):
        r_val = self.r.eval(env, consts, lvl, modules, signal)
        l_val = self.left.eval(env, consts, lvl, modules, signal)
        match self.op:
            case '==':
                return l_val == r_val
            case '!=':
                return l_val != r_val
            case '>':
                return l_val > r_val
            case '<':
                return l_val < r_val
            case '>=':
                return l_val >= r_val
            case '<=':
                return l_val <= r_val
            case _:
                signal.ERROR = f'unknown operation {self.op}'


class AndOp(BinOpExpr):
    def __init__(self, left, r):
        self.left = left
        self.r = r

    def __repr__(self) -> str:
        return f"AndOp({self.left}, {self.r})"

    def eval(self, env, consts, lvl, modules, signal):
        return (
                self.left.eval(env, consts, lvl, modules, signal) and
                self.r.eval(env, consts, lvl, modules, signal)
        )


class OrOp(BinOpExpr):
    def __init__(self, left, r):
        self.left = left
        self.r = r

    def __repr__(self) -> str:
        return f"OrOp({self.left}, {self.r})"

    def eval(self, env, consts, lvl, modules, signal):
        return (
                self.left.eval(env, consts, lvl, modules, signal) or
                self.r.eval(env, consts, lvl, modules, signal)
        )


class InOp(BinOpExpr):
    def __init__(self, left, r):
        self.left = left
        self.r = r

    def __repr__(self) -> str:
        return f"InOp({self.left}, {self.r})"

    def eval(self, env, consts, lvl, modules, signal):
        return (
                self.left.eval(env, consts, lvl, modules, signal) in
                self.r.eval(env, consts, lvl, modules, signal)
        )


class NotOp(BinOpExpr):
    def __init__(self, expr):
        self.expr = expr

    def eval(self, env, consts, lvl, modules, signal):
        return not self.expr.eval(env, consts, lvl, modules, signal)