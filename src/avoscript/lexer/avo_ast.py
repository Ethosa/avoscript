# -*- coding: utf-8 -*-
import traceback
from os.path import exists, isfile
from typing import Union, Tuple, List, Any
from pprint import pprint
from copy import deepcopy
from re import findall
from random import randint, random
import math
import sys

from colorama import Fore

from equality import AnyBase
from . import Lexer, parser


ENV = []
ENV_CONSTS = []
MODULES = {
    # module_name: statement_list_level
}
BUILTIN = {
    'round': round,
    'randf': random,
    'randi': randint,
    'range': range,
    'length': len,
    'string': str,
    'int': int,
    'float': float,
    'array': list,
}
BUILTIN_BUILD = False


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


class Signal:
    IN_CYCLE = False
    IN_FOR_CYCLE = False
    IN_FUNCTION = False
    IN_CLASS = False
    IN_TRY = False
    IN_MAIN = False
    IN_MODULE = False
    CURRENT_MODULE = 'main'
    BREAK = False
    CONTINUE = False
    RETURN = False
    NO_CREATE_LEVEL = False
    CREATE_BACK_LEVEL = False
    BACK_LEVEL = None
    RETURN_VALUE = None
    ARGUMENTS = None
    KW_ARGUMENTS = None
    CURRENT_CLASS = None
    ERROR = None
    # no refresh
    NEED_FREE = True
    VERBOSE = False

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


STATEMENT_LIST_LEVEL = LevelIndex()


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

    def __init__(self, s: str):
        self.s = s

    def __repr__(self) -> str:
        return f'StringAST({Fore.LIGHTGREEN_EX}"{self.s}"{Fore.RESET})'

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
        return result


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
        in_built_in = (self.name, self.obj) in BUILTIN
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
        elif isinstance(self.obj, (ArrayAST, StringAST, CallStmt, ModuleCallAST, ClassPropAST)):
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
                    assign_stmt = AssignStmt(self.expr.var_name, binop)
                    assign_stmt.eval(env, consts, lvl, modules, signal)
                    return self.expr.eval(env, consts, lvl, modules, signal)
                return binop.eval(env, consts, lvl, modules, signal)
            case '--':
                binop = BinOpAST('-', self.expr, IntAST(1))
                if isinstance(self.expr, VarAST):
                    assign_stmt = AssignStmt(self.expr.var_name, binop)
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


class Stmt(AnyBase):
    def eval(self, env, consts, lvl, modules, signal):
        raise RuntimeError("unknown statement")


class StmtList(Stmt):
    def __init__(self, statements):
        self.statements = [i.value for i in statements]

    def __repr__(self) -> str:
        return f"StmtList({', '.join([repr(i) for i in self.statements])})"

    def __iter__(self):
        for stmt in self.statements:
            yield stmt

    def eval(self, env, consts, lvl, modules, signal):
        global BUILTIN_BUILD
        if not BUILTIN_BUILD:
            BUILTIN_BUILD = True
            for attr in dir(math):
                a = getattr(math, attr)
                if callable(a) and not attr.startswith('_'):
                    BUILTIN[('math', attr)] = a
        in_main = False
        in_module = signal.IN_MODULE
        if in_module:
            signal.IN_MODULE = False
        if not signal.IN_MAIN:
            signal.IN_MAIN = True
            in_main = True
        if not signal.NO_CREATE_LEVEL:
            lvl.inc()
            env.append({})
            consts.append({})
        # Arguments (if in function)
        if signal.IN_FUNCTION and signal.ARGUMENTS:
            for n, v in signal.ARGUMENTS.items():
                env[lvl][n.name] = v.value.eval(env, consts, lvl, modules, signal)
            signal.ARGUMENTS = None
        if signal.IN_FUNCTION and signal.KW_ARGUMENTS:
            for v in signal.KW_ARGUMENTS:
                env[lvl][v.name] = v.value.eval(env, consts, lvl, modules, signal)
            signal.KW_ARGUMENTS = None
        # Statements
        result = None
        for stmt in self.statements:
            if signal.VERBOSE:
                print(f'{Fore.CYAN}[STATEMENT]{Fore.RESET}: {stmt}')
            try:
                result = stmt.eval(env, consts, lvl, modules, signal)
            except Exception as e:
                traceback.print_exc()
                signal.ERROR = e
            if signal.ERROR is not None:
                if not signal.IN_TRY:
                    print(f'RuntimeError: {signal.ERROR} in module "{signal.CURRENT_MODULE}"')
                    exit(0)
                break
            if (signal.BREAK or signal.CONTINUE) and signal.IN_CYCLE:
                break
            if signal.RETURN and signal.IN_FUNCTION:
                break
        if not signal.NO_CREATE_LEVEL and lvl not in modules.values() and not in_module:
            lvl.dec()
            env.pop()
            consts.pop()
        if signal.IN_MAIN and in_main:
            signal.IN_MAIN = False
            if isinstance(self.statements[-1], EOFStmt):
                self.statements[-1].eval(env, consts, lvl, modules, signal)
            return
        return result


class AssignStmt(Stmt):
    def __init__(
            self,
            name: str,
            a_expr: Union[Stmt, ASTExpr, BinOpExpr],
            is_const: bool = False,
            is_assign: bool = False,
            assign_op: str = '='
    ):
        self.name = name
        self.a_expr = a_expr
        self.is_const = is_const
        self.is_assign = is_assign
        self.assign_op = assign_op

    def __repr__(self) -> str:
        return f"AssignStmt({self.name}, {self.a_expr})"

    def __assign_operation(self, val, signal):
        if not self.is_assign:
            name = self.name
            if isinstance(name, str):
                name = VarAST(name)
            match self.assign_op:
                case '*=':
                    val = BinOpAST('*', name, val)
                case '/=':
                    val = BinOpAST('/', name, val)
                case '+=':
                    val = BinOpAST('+', name, val)
                case '-=':
                    val = BinOpAST('-', name, val)
                case '=':
                    pass
                case _:
                    signal.ERROR = f"unknown operator {self.assign_op}"
        return val

    def eval(self, env, consts, lvl, modules, signal):
        has_var, level, is_const = has_variable(self.name, env, consts)
        val = self.__assign_operation(self.a_expr, signal)
        if self.is_assign:
            # Assign var/const
            if self.assign_op != '=':
                signal.ERROR = f"{self.name} isn't assigned"
                return
            if has_var and level == lvl:
                signal.ERROR = f"{self.name} is assigned"
                return
            if self.is_const:
                consts[lvl][self.name] = val.eval(env, consts, lvl, modules, signal)
            else:
                env[lvl][self.name] = val.eval(env, consts, lvl, modules, signal)
        elif has_var:
            # Reassign
            if is_const:
                consts[level][self.name] = val.eval(env, consts, lvl, modules, signal)
            else:
                env[level][self.name] = val.eval(env, consts, lvl, modules, signal)
        elif isinstance(self.name, BraceAST):
            result = None
            obj = self.name
            if isinstance(obj.obj, str):
                result = VarAST(obj.obj).eval(env, consts, lvl, modules, signal)
            elif isinstance(obj.obj, (ArrayAST, StringAST, CallStmt, ModuleCallAST, ClassPropAST)):
                result = obj.obj.eval(env, consts, lvl, modules, signal)
            if result is not None:
                for i in obj.v[:-1]:
                    i = i.eval(env, consts, lvl, modules, signal)
                    result = result[i.eval(env, consts, lvl, modules, signal)]
            if result is not None:
                i = obj.v[-1].eval(env, consts, lvl, modules, signal)
                if i == len(result):
                    result.append(val.eval(env, consts, lvl, modules, signal))
                else:
                    result[i] = val.eval(env, consts, lvl, modules, signal)
        elif isinstance(self.name, ModuleCallAST):
            module = self.name
            if module.name not in modules:
                signal.ERROR = f"unknown module {module.name}"
                return
            if module.obj in env[modules[module.name]]:
                env[modules[module.name]][module.obj] = val.eval(env, consts, lvl, modules, signal)
            elif module.obj in consts[modules[module.name]]:
                consts[modules[module.name]][module.obj] = val.eval(env, consts, lvl, modules, signal)
            else:
                signal.ERROR = f"unknown module property {module.obj}"
                return
        elif isinstance(self.name, ClassPropAST):
            obj = self.name
            if signal.IN_CLASS and signal.CURRENT_CLASS and obj.name == 'this':
                obj.name = signal.CURRENT_CLASS
            has_var, level, is_const = has_variable(obj.name, env, consts)
            if has_var and not is_const:
                var = env[level][obj.name]
                if obj.is_super and var['parent'] is not None:
                    var = var['parent']
                if obj.prop in var['env']:
                    var['env'][obj.prop] = val.eval(env, consts, lvl, modules, signal)
                    return
                if obj.prop in var['consts_env']:
                    var['consts_env'][obj.prop] = val.eval(env, consts, lvl, modules, signal)
                    return
                while var['parent']:
                    var = var['parent']
                    if obj.prop in var['env']:
                        var['env'][obj.prop] = val.eval(env, consts, lvl, modules, signal)
                        return
                    if obj.prop in var['consts_env']:
                        var['consts_env'][obj.prop] = val.eval(env, consts, lvl, modules, signal)
                        return
                signal.ERROR = f"unknown property {obj.prop} in class {obj.name}"
            else:
                signal.ERROR = f"unknown class {obj.name}"
        else:
            signal.ERROR = f"{self.name} isn't assigned"


class AssignClassStmt(Stmt):
    def __init__(self, name, body, inherit, prefix, interfaces):
        self.name = name
        self.body = body
        self.inherit = inherit
        self.prefix = prefix
        self.interfaces = interfaces

    def __repr__(self) -> str:
        return f"AssignClassStmt({self.prefix + ' ' if self.prefix else ''}{self.name}, {self.inherit}, {self.body})"

    def eval(self, env, consts, lvl, modules, signal):
        has_var, level, is_const = has_variable(self.name, env, consts)
        if not has_var:
            signal.NO_CREATE_LEVEL = True
            env.append({})
            consts.append({})
            lvl.inc()
            self.body.eval(env, consts, lvl, modules, signal)
            if self.inherit:
                has_var, level, is_const = has_variable(self.inherit, env, consts)
                if has_var:
                    self.inherit = env[level][self.inherit]
                else:
                    signal.ERROR = f"unknown inherit class {self.inherit}"
                    return
            must_have_data = []
            # implemented interfaces
            for interface in self.interfaces:
                h, l, c = has_variable(interface, env, consts)
                if h:
                    interface = env[l][interface]
                    must_have_data += [i for i in interface['env'].keys() if i not in must_have_data]
                    must_have_data += [i for i in interface['consts_env'].keys() if i not in must_have_data]
                else:
                    signal.ERROR = f"unknown interface {interface} of class {self.name}"
                    return
            env[lvl - 1][self.name] = {
                'parent': self.inherit,
                'env': deepcopy(env[lvl]),
                'consts_env': deepcopy(consts[lvl]),
                'name': self.name,
                'prefix': self.prefix,
                'must_have_data': must_have_data
            }
            parent = self.inherit
            if parent:
                # what should be implemented?
                prefix = parent['prefix']
                must_have_data += [i for i in parent['must_have_data'] if i not in must_have_data]
                if prefix == 'abstract':
                    must_have_data += [i for i in parent['env'].keys() if i not in must_have_data]
                    must_have_data += [i for i in parent['consts_env'].keys() if i not in must_have_data]
                while parent['parent']:
                    parent = parent['parent']
                    must_have_data += [i for i in parent['must_have_data'] if i not in must_have_data]
                    if prefix == 'abstract':
                        must_have_data += [i for i in parent['env'].keys() if i not in must_have_data]
                        must_have_data += [i for i in parent['consts_env'].keys() if i not in must_have_data]
            # what is implemented
            for data in must_have_data:
                obj = env[lvl - 1][self.name]
                prefix = obj['prefix']
                if (data in obj['env'] or data in obj['consts_env']) and prefix != 'abstract':
                    must_have_data.remove(data)
                    continue
                while obj['parent']:
                    obj = obj['parent']
                    prefix = obj['prefix']
                    if (data in obj['env'] or data in obj['consts_env']) and prefix != 'abstract':
                        must_have_data.remove(data)
                        break
            lvl.dec()
            env.pop()
            consts.pop()
            signal.NO_CREATE_LEVEL = False
            if len(must_have_data) > 0:
                print(f"[WARNING]: {', '.join(must_have_data)} isn't implemented in {self.name}")
        else:
            print(has_var, level, env[level][self.name])
            signal.ERROR = f"class {self.name} is assigned"


class InterfaceStmt(Stmt):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self) -> str:
        return f"InterfaceStmt({self.name}, {self.body})"

    def eval(self, env, consts, lvl, modules, signal):
        has_var, level, is_const = has_variable(self.name, env, consts)
        if not has_var:
            signal.NO_CREATE_LEVEL = True
            env.append({})
            consts.append({})
            lvl.inc()
            self.body.eval(env, consts, lvl, modules, signal)
            env[lvl - 1][self.name] = {
                'env': deepcopy(env[lvl]),
                'consts_env': deepcopy(consts[lvl]),
                'name': self.name,
            }
            lvl.dec()
            env.pop()
            consts.pop()
            signal.NO_CREATE_LEVEL = False
        else:
            signal.ERROR = f"{self.name} is assigned"


class InitClassStmt(Stmt):
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        return f"InitClassStmt({self.args})"

    def eval(self, env, consts, lvl, modules, signal):
        if None in env[lvl]:
            signal.ERROR = "this class equals init function"
            return
        env[lvl][None] = (self.args, self.body)


class IfStmt(Stmt):
    def __init__(self, condition, body, elif_array, else_body):
        self.condition = condition
        self.body = body
        self.elif_array = elif_array
        self.else_body = else_body

    def __repr__(self) -> str:
        return f"IfStmt({self.condition}, {self.body}, {self.else_body})"

    def eval(self, env, consts, lvl, modules, signal):
        condition = self.condition.eval(env, consts, lvl, modules, signal)
        else_statement = True
        if condition:
            self.body.eval(env, consts, lvl, modules, signal)
        else:
            for i in self.elif_array:
                (((_, condition), _), stmt_list), _ = i
                if condition.eval(env, consts, lvl, modules, signal):
                    stmt_list.eval(env, consts, lvl, modules, signal)
                    else_statement = False
                    break
        if self.else_body and else_statement:
            self.else_body.eval(env, consts, lvl, modules, signal)


class SwitchCaseStmt(Stmt):
    def __init__(self, var, cases):
        self.var = var
        self.cases = cases

    def __repr__(self) -> str:
        return f"SwitchCaseStmt({self.var}, {self.cases})"

    def eval(self, env, consts, lvl, modules, signal):
        var = self.var.eval(env, consts, lvl, modules, signal)
        result = None
        for c in self.cases:
            if isinstance(c, CaseStmt):
                if c.condition:
                    val = c.condition.eval(env, consts, lvl, modules, signal)
                    if val == var:
                        result = c.body.eval(env, consts, lvl, modules, signal)
                        break
                    elif isinstance(val, (tuple, list)) and var in val:
                        result = c.body.eval(env, consts, lvl, modules, signal)
                        break
                else:
                    result = c.body.eval(env, consts, lvl, modules, signal)
                    break
        return result


class CaseStmt(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"CaseStmt({self.condition}, {self.body})"

    def eval(self, env, consts, lvl, modules, signal):
        pass


class WhileStmt(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"WhileStmt({self.condition}, {self.body})"

    def eval(self, env, consts, lvl, modules, signal):
        condition = self.condition.eval(env, consts, lvl, modules, signal)
        while condition:
            self.body.eval(env, consts, lvl, modules, signal)
            signal.IN_CYCLE = True
            if signal.IN_CYCLE:
                if signal.CONTINUE:
                    signal.CONTINUE = False
                    continue
                elif signal.BREAK:
                    break
            if signal.RETURN and signal.IN_FUNCTION:
                break
            condition = self.condition.eval(env, consts, lvl, modules, signal)
        signal.IN_CYCLE = False
        signal.BREAK = False
        signal.CONTINUE = False


class ForStmt(Stmt):
    def __init__(self, var, cond, action, body):
        self.var = var  # VarAST or AssignStmt
        self.cond = cond  # BinOpExpr or VarAst/ArrayAST/CallStmt
        self.action = action  # AssignStmt(is_assign=False) or StmtList
        self.body = body  # StmtList or None

    def __repr__(self) -> str:
        return f"ForStmt({self.var}, {self.cond}, {self.action}, {self.body})"

    def eval(self, env, consts, lvl, modules, signal):
        env.append({})
        consts.append({})
        lvl.inc()
        if self.body:  # for i = 0; i < 10; ++i; {}
            self.var.eval(env, consts, lvl, modules, signal)
            condition = self.cond.eval(env, consts, lvl, modules, signal)
            while condition:
                self.body.eval(env, consts, lvl, modules, signal)
                signal.IN_CYCLE = True
                if signal.IN_CYCLE:
                    if signal.CONTINUE:
                        signal.CONTINUE = False
                        continue
                    if signal.BREAK:
                        break
                if signal.IN_FUNCTION and signal.RETURN:
                    break
                self.action.eval(env, consts, lvl, modules, signal)
                condition = self.cond.eval(env, consts, lvl, modules, signal)
        else:  # for i in arr {}
            for i in self.cond.eval(env, consts, lvl, modules, signal):
                env[lvl][self.var] = i
                signal.IN_CYCLE = True
                self.action.eval(env, consts, lvl, modules, signal)
        lvl.dec()
        env.pop()
        consts.pop()
        signal.IN_CYCLE = False
        signal.BREAK = False
        signal.CONTINUE = False


class BreakStmt(Stmt):
    def __repr__(self) -> str:
        return "BreakStmt"

    def eval(self, env, consts, lvl, modules, signal):
        signal.BREAK = True


class ContinueStmt(Stmt):
    def __repr__(self) -> str:
        return "ContinueStmt"

    def eval(self, env, consts, lvl, modules, signal):
        signal.CONTINUE = True


class TryCatchStmt(Stmt):
    def __init__(self, try_body, e_name, catch_body):
        self.try_body = try_body
        self.e_name = e_name
        self.catch_body = catch_body

    def __repr__(self) -> str:
        return f"TryCatchStmt({self.try_body}, {self.e_name}, {self.catch_body})"

    def eval(self, env, consts, lvl, modules, signal):
        signal.IN_TRY = True
        self.try_body.eval(env, consts, lvl, modules, signal)
        signal.IN_TRY = False
        if signal.ERROR is not None:
            signal.NO_CREATE_LEVEL = True
            env.append({})
            consts.append({})
            lvl.inc()
            env[lvl][self.e_name] = signal.ERROR
            signal.ERROR = None
            self.catch_body.eval(env, consts, lvl, modules, signal)
            lvl.dec()
            env.pop()
            consts.pop()


class EchoStmt(Stmt):
    def __init__(self, data):
        self.data = data

    def __repr__(self) -> str:
        return f"EchoStmt({self.data})"

    def eval(self, env, consts, lvl, modules, signal):
        if isinstance(self.data, (Stmt, ASTExpr, BinOpExpr)):
            val = self.data.eval(env, consts, lvl, modules, signal)
            if isinstance(val, tuple) and len(val) == 4:
                print(f"class {val[3]}")
            else:
                print(val)
        elif isinstance(self.data, (list, tuple)):
            for i in self.data:
                val = i.eval(env, consts, lvl, modules, signal)
                if isinstance(val, tuple) and len(val) == 4:
                    print(f"class {val[3]}", end=" ")
                else:
                    print(val, end=" ")
            print()
        else:
            print(self.data)


class ReadStmt(Stmt):
    def __init__(self, text):
        self.text = text

    def __repr__(self) -> str:
        return f"ReadStmt({self.text})"

    def eval(self, env, consts, lvl, modules, signal):
        if isinstance(self.text, ASTExpr):
            return input(self.text.eval(env, consts, lvl, modules, signal))
        elif isinstance(self.text, str):
            return self.text


class FuncStmt(Stmt):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        return f"FuncStmt({self.name}, {self.args}, {self.body})"

    def eval(self, env, consts, lvl, modules, signal):
        has_var, level, is_const = has_variable(self.name, env, consts)
        if has_var and not is_const and level == lvl:
            signal.ERROR = f"Function {self.name} is exists"
            return
        env[lvl][self.name] = (self.args, self.body)


class LambdaStmt(Stmt):
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        return f"LambdaStmt({self.args}, {self.body})"

    def eval(self, env, consts, lvl, modules, signal):
        return self.args, self.body


class CallStmt(Stmt):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return f"CallStmt({self.name}, {self.args})"

    def eval(self, env, consts, lvl, modules, signal):
        has_var, level, is_const = has_variable(self.name, env, consts)
        f = None
        init_obj = None
        if has_var and not is_const:
            f = env[level][self.name]
            if isinstance(f, dict):  # class
                if not signal.IN_CLASS:
                    signal.CURRENT_CLASS = self.name
                signal.IN_CLASS = True
                init_obj = f
                if None in f['env']:
                    f = f['env'][None]
                else:
                    f = ([], StmtList([]))
        elif isinstance(self.name, ModuleCallAST):
            f = self.name.eval(env, consts, lvl, modules, signal)
        elif isinstance(self.name, ClassPropAST):
            f = self.name.eval(env, consts, lvl, modules, signal)
            if not signal.IN_CLASS:
                signal.CURRENT_CLASS = self.name.name
            signal.IN_CLASS = True
        if f is not None:
            args = [i for i in self.args if i.name is None]
            fargs = [i for i in f[0] if i.value is None]
            kwargs = [i for i in self.args if i.name is not None]
            fkwargs = [i for i in f[0] if i.value is not None]
            if len(args) != len(fargs):
                signal.ERROR = (
                    f"function {self.name} waited for {len(fargs)}, but got {len(args)} arguments"
                )
                return
            signal.ARGUMENTS = {n: v for n, v in zip(fargs, args)}
            signal.KW_ARGUMENTS = fkwargs + kwargs
            if not signal.IN_FUNCTION:
                signal.IN_FUNCTION = True
                f[1].eval(env, consts, lvl, modules, signal)
                signal.IN_FUNCTION = False
            else:
                f[1].eval(env, consts, lvl, modules, signal)
            if init_obj:  # initialized class
                val = deepcopy(init_obj)
                signal.RETURN_VALUE = val
            signal.RETURN = False

            returned = signal.RETURN_VALUE
            signal.RETURN_VALUE = None
            signal.IN_CLASS = False
            signal.CURRENT_CLASS = None
            return returned
        else:
            args = [
                i.value.eval(env, consts, lvl, modules, signal)
                for i in self.args if i.name is None
            ]
            kwargs = {
                i.name: i.value.eval(env, consts, lvl, modules, signal)
                for i in self.args if i.name is not None
            }
            if isinstance(self.name, str):
                if self.name in BUILTIN:
                    returned = BUILTIN[self.name](*args, **kwargs)
                    return returned
            elif isinstance(self.name, ModuleCallAST):
                val = (self.name.name, self.name.obj)
                if val in BUILTIN:
                    returned = BUILTIN[val](*args, **kwargs)
                    return returned
        signal.ERROR = f"function {self.name} isn't available"


class ReturnStmt(Stmt):
    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return f"ReturnStmt({self.val})"

    def eval(self, env, consts, lvl, modules, signal):
        signal.RETURN = True
        signal.RETURN_VALUE = self.val.eval(env, consts, lvl, modules, signal)


class ImportStmt(Stmt):
    def __init__(self, module_name, objects, from_import):
        self.module_name = module_name
        self.objects = objects
        self.from_import = from_import

    def __repr__(self) -> str:
        return f"ImportStmt({self.module_name}, {self.objects}, {self.from_import})"

    def eval(self, env, consts, lvl, modules, signal):
        current_module = signal.CURRENT_MODULE
        if self.module_name is not None:
            module_name = self.module_name + '.avo'
            if not exists(module_name) or not isfile(module_name):
                signal.ERROR = f"can't find module {module_name}"
                return
            statements = parser.stmt_list()(Lexer.lex_file(module_name), 0)
            if statements:
                signal.CURRENT_MODULE = module_name
                signal.IN_MODULE = True
                modules[self.module_name] = lvl+1
                statements.value.eval(env, consts, lvl, modules, signal)
        if self.from_import:
            environment = [i for i in env[modules[self.module_name]].keys()]
            constants = [i for i in consts[modules[self.module_name]].keys()]
            for k in environment + constants:
                if k not in self.objects:
                    del env[modules[self.module_name]][k]
        else:
            while len(self.objects) > 0:
                self.module_name = self.objects.pop(0)
                self.eval(env, consts, lvl, modules, signal)
        signal.CURRENT_MODULE = current_module


class EOFStmt(Stmt):
    def __repr__(self) -> str:
        return "EOFStmt()"

    def eval(self, env, consts, lvl, modules, signal):
        if signal.IN_MAIN or not signal.NEED_FREE:
            return
        env.clear()
        consts.clear()
        modules.clear()
        lvl.i = 0
        signal.refresh()
