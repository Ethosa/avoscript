# -*- coding: utf-8 -*-
import math
import traceback
from typing import Union
from copy import deepcopy
from os.path import exists, isfile

from equality import AnyBase
from colorama import Fore

from . import Lexer, default, expressions, parser


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
        if not default.BUILTIN_BUILD:
            default.BUILTIN_BUILD = True
            for attr in dir(math):
                a = getattr(math, attr)
                if callable(a) and not attr.startswith('_'):
                    default.BUILTIN[('math', attr)] = a
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
            a_expr: Union[Stmt, 'expressions.ASTExpr', 'expressions.BinOpExpr'],
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
                name = expressions.VarAST(name)
            match self.assign_op:
                case '*=':
                    val = expressions.BinOpAST('*', name, val)
                case '/=':
                    val = expressions.BinOpAST('/', name, val)
                case '+=':
                    val = expressions.BinOpAST('+', name, val)
                case '-=':
                    val = expressions.BinOpAST('-', name, val)
                case '=':
                    pass
                case _:
                    signal.ERROR = f"unknown operator {self.assign_op}"
        return val

    def eval(self, env, consts, lvl, modules, signal):
        has_var, level, is_const = expressions.has_variable(self.name, env, consts)
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
        elif isinstance(self.name, expressions.BraceAST):
            result = None
            obj = self.name
            if isinstance(obj.obj, str):
                result = expressions.VarAST(obj.obj).eval(env, consts, lvl, modules, signal)
            elif isinstance(
                    obj.obj,
                    (expressions.ArrayAST, expressions.StringAST, CallStmt,
                     expressions.ModuleCallAST, expressions.ClassPropAST)
            ):
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
        elif isinstance(self.name, expressions.ModuleCallAST):
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
        elif isinstance(self.name, expressions.ClassPropAST):
            obj = self.name
            if signal.IN_CLASS and signal.CURRENT_CLASS and obj.name == 'this':
                obj.name = signal.CURRENT_CLASS
            has_var, level, is_const = expressions.has_variable(obj.name, env, consts)
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
        has_var, level, is_const = expressions.has_variable(self.name, env, consts)
        if not has_var:
            signal.NO_CREATE_LEVEL = True
            env.append({})
            consts.append({})
            lvl.inc()
            self.body.eval(env, consts, lvl, modules, signal)
            if self.inherit:
                has_var, level, is_const = expressions.has_variable(self.inherit, env, consts)
                if has_var:
                    self.inherit = env[level][self.inherit]
                else:
                    signal.ERROR = f"unknown inherit class {self.inherit}"
                    return
            must_have_data = []
            # implemented interfaces
            for interface in self.interfaces:
                h, l, c = expressions.has_variable(interface, env, consts)
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
        has_var, level, is_const = expressions.has_variable(self.name, env, consts)
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
        if isinstance(self.data, (Stmt, expressions.ASTExpr, expressions.BinOpExpr)):
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
        if isinstance(self.text, expressions.ASTExpr):
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
        has_var, level, is_const = expressions.has_variable(self.name, env, consts)
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
        has_var, level, is_const = expressions.has_variable(self.name, env, consts)
        f = None
        init_obj = None
        current_class = signal.CURRENT_CLASS
        in_class = signal.IN_CLASS
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
        elif isinstance(self.name, expressions.ModuleCallAST):
            f = self.name.eval(env, consts, lvl, modules, signal)
        elif isinstance(self.name, expressions.ClassPropAST):
            if not signal.IN_CLASS and self.name.name != 'this':
                signal.CURRENT_CLASS = self.name.name
            signal.IN_CLASS = True
            f = self.name.eval(env, consts, lvl, modules, signal)
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
            if in_class:
                signal.IN_CLASS = True
            if current_class is not None:
                signal.CURRENT_CLASS = current_class
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
                if self.name in default.BUILTIN:
                    returned = default.BUILTIN[self.name](*args, **kwargs)
                    return returned
            elif isinstance(self.name, expressions.ModuleCallAST):
                val = (self.name.name, self.name.obj)
                if val in default.BUILTIN:
                    returned = default.BUILTIN[val](*args, **kwargs)
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
