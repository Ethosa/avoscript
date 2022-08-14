# -*- coding: utf-8 -*-
from os.path import exists, isfile
from typing import Union, Tuple, List, Any
from pprint import pprint
from copy import deepcopy

from equality import AnyBase


ENV = []
ENV_CONSTS = []
STATEMENT_LIST_LEVEL = -1
MODULES = {
    # module_name: statement_list_level
}


def has_variable(name: str) -> Tuple[bool, int, bool]:
    """
    Finds variable or constant in environments
    :param name: var/const name
    :return: (contains, level index, is constant)
    """
    for level in range(len(ENV) - 1, -1, -1):
        if name in ENV[level]:
            return True, level, False
        elif name in ENV_CONSTS[level]:
            return True, level, True
    return False, 0, False


class Signal:
    IN_CYCLE = False
    IN_FOR_CYCLE = False
    IN_FUNCTION = False
    IN_CLASS = False
    IN_TRY = False
    IN_MAIN = False
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
    NEED_FREE = True

    @staticmethod
    def refresh():
        Signal.IN_CYCLE = False
        Signal.IN_FOR_CYCLE = False
        Signal.IN_FUNCTION = False
        Signal.IN_CLASS = False
        Signal.IN_TRY = False
        Signal.IN_MAIN = False
        Signal.BREAK = False
        Signal.CONTINUE = False
        Signal.RETURN = False
        Signal.NO_CREATE_LEVEL = False
        Signal.CREATE_BACK_LEVEL = False
        Signal.BACK_LEVEL = None
        Signal.RETURN_VALUE = None
        Signal.ARGUMENTS = None
        Signal.KW_ARGUMENTS = None
        Signal.CURRENT_CLASS = None
        Signal.ERROR = None


# --== AST ==-- #
class ASTExpr(AnyBase):
    def __repr__(self) -> str:
        return "AST expression"

    def eval(self):
        raise RuntimeError('nothing to eval')


class IntAST(ASTExpr):
    def __init__(self, i: int):
        self.i = i

    def __repr__(self) -> str:
        return f"IntAST({self.i})"

    def eval(self):
        return self.i


class FloatAST(ASTExpr):
    def __init__(self, f: float):
        self.f = f

    def __repr__(self) -> str:
        return f"FloatAST({self.f})"

    def eval(self):
        return self.f


class BoolAST(ASTExpr):
    def __init__(self, b: bool):
        self.b = b

    def __repr__(self) -> str:
        return f"BoolAST({self.b})"

    def eval(self):
        return self.b


class StringAST(ASTExpr):
    def __init__(self, s: str):
        self.s = s

    def __repr__(self) -> str:
        return f'StringAST("{self.s}")'

    def eval(self):
        return self.s


class ArrayAST(ASTExpr):
    def __init__(self, arr: List[Any]):
        self.arr = [i.value[0] for i in arr]

    def __repr__(self) -> str:
        return f"ArrayAST({self.arr})"

    def eval(self):
        return [i.eval() for i in self.arr]


class VarAST(ASTExpr):
    def __init__(self, var_name):
        self.var_name = var_name

    def __repr__(self) -> str:
        return f"VarAST({self.var_name})"

    def eval(self):
        has_var, level, is_const = has_variable(self.var_name)
        if has_var:
            if is_const:
                return ENV_CONSTS[level][self.var_name]
            else:
                return ENV[level][self.var_name]
        Signal.ERROR = f'{self.var_name} was used before assign'


class ModuleCallAST(ASTExpr):
    def __init__(self, module_name, module_obj):
        self.name = module_name
        self.obj = module_obj

    def __repr__(self) -> str:
        return f"ModuleCallAST({self.name}, {self.obj})"

    def eval(self):
        if self.name in MODULES:
            if self.obj not in ENV[MODULES[self.name]]:
                Signal.ERROR = f"unknown module object {self.obj}"
                return
            return ENV[MODULES[self.name]][self.obj]
        Signal.ERROR = f"unknown module {self.obj}"


class ClassPropAST(ASTExpr):
    def __init__(self, name, prop, is_super):
        self.name = name
        self.prop = prop
        self.is_super = is_super

    def __repr__(self) -> str:
        return f"ClassPropAST({self.name}, {self.prop})"

    def eval(self):
        if Signal.IN_CLASS and Signal.CURRENT_CLASS and self.name == 'this':
            self.name = Signal.CURRENT_CLASS
        has_var, level, is_const = has_variable(self.name)
        if has_var:
            obj = ENV[level][self.name]
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
            Signal.ERROR = f"unknown property {self.prop} of {self.name}"
        else:
            Signal.ERROR = f"unknown class {self.name}"


class ArgumentAST(ASTExpr):
    """serves FuncStmt/CallStmt arguments"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"ArgumentAST({self.name}, {self.value})"

    def eval(self):
        return self.name, self.value


class BraceAST(ASTExpr):
    """serves array[index]"""

    def __init__(self, obj, v):
        self.obj = obj
        self.v = v

    def __repr__(self) -> str:
        return f"BraceAST({self.v})"

    def eval(self):
        result = None
        if isinstance(self.obj, str):
            result = VarAST(self.obj).eval()
        elif isinstance(self.obj, (ArrayAST, StringAST, CallStmt, ModuleCallAST, ClassPropAST)):
            result = self.obj.eval()
        if result is not None:
            for i in self.v:
                result = result[i.eval()]
        if result is not None:
            return result
        Signal.ERROR = f"{self.obj.eval()} isn't indexed"


class BinOpAST(ASTExpr):
    def __init__(self, op, l, r):
        self.op = op
        self.l = l
        self.r = r

    def __repr__(self) -> str:
        return f"BinOpAST({self.op}, {self.l}, {self.r})"

    def eval(self):
        rval = self.r.eval()
        lval = self.l.eval()
        match self.op:
            case '*':
                return lval * rval
            case '/':
                return lval / rval
            case '-':
                return lval - rval
            case '+':
                return lval + rval
            case '%':
                return lval % rval
            case _:
                Signal.ERROR = f'unknown operation {self.op}'


class UnaryOpAST(ASTExpr):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __repr__(self) -> str:
        return f"UnaryOpAST({self.op}, {self.expr})"

    def eval(self):
        match self.op:
            case '++':
                binop = BinOpAST('+', self.expr, IntAST(1))
                if isinstance(self.expr, VarAST):
                    assign_stmt = AssignStmt(self.expr.var_name, binop)
                    assign_stmt.eval()
                    return self.expr.eval()
                return binop.eval()
            case '--':
                binop = BinOpAST('-', self.expr, IntAST(1))
                if isinstance(self.expr, VarAST):
                    assign_stmt = AssignStmt(self.expr.var_name, binop)
                    assign_stmt.eval()
                    return self.expr.eval()
                return binop.eval()
            case '-':
                return -(self.expr.eval())
            case _:
                Signal.ERROR = f"unknown unary operation: {self.op}"


class TernaryOpAST(ASTExpr):
    def __init__(self, first, op1, second, op2, third):
        self.first = first
        self.second = second
        self.third = third
        self.op1 = op1
        self.op2 = op2

    def __repr__(self) -> str:
        return f"TernaryOpAST({self.first}, {self.op1}, {self.second}, {self.op2}, {self.third})"

    def eval(self):
        if self.op1 == '?' and self.op2 == ':':
            if self.first.eval():
                return self.second.eval()
            return self.third.eval()
        elif self.op1 == 'if' and self.op2 == 'else':
            if self.second.eval():
                return self.first.eval()
            return self.third.eval()
        Signal.ERROR = f"unknown ternary operator {self.op1}, {self.op2}"


# --== Binary operations ==-- #
class BinOpExpr(AnyBase):
    def eval(self):
        raise RuntimeError('unknown binary operaion')


class RelativeOp(BinOpExpr):
    def __init__(self, op, l, r):
        self.op = op
        self.l = l
        self.r = r

    def __repr__(self) -> str:
        return f"RelOp({self.l}, {self.op}, {self.r})"

    def eval(self):
        rval = self.r.eval()
        lval = self.l.eval()
        match self.op:
            case '==':
                return lval == rval
            case '!=':
                return lval != rval
            case '>':
                return lval > rval
            case '<':
                return lval < rval
            case '>=':
                return lval >= rval
            case '<=':
                return lval <= rval
            case _:
                Signal.ERROR = f'unknown operation {self.op}'


class AndOp(BinOpExpr):
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def __repr__(self) -> str:
        return f"AndOp({self.l}, {self.r})"

    def eval(self):
        return self.l.eval() and self.r.eval()


class OrOp(BinOpExpr):
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def __repr__(self) -> str:
        return f"OrOp({self.l}, {self.r})"

    def eval(self):
        return self.l.eval() or self.r.eval()


class InOp(BinOpExpr):
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def __repr__(self) -> str:
        return f"InOp({self.l}, {self.r})"

    def eval(self):
        return self.l.eval() in self.r.eval()


class NotOp(BinOpExpr):
    def __init__(self, expr):
        self.expr = expr

    def eval(self):
        return not self.expr.eval()


class Stmt(AnyBase):
    def eval(self):
        raise RuntimeError("unknown statement")


class StmtList(Stmt):
    def __init__(self, statements):
        self.statements = [i.value for i in statements]

    def __repr__(self) -> str:
        return f"StmtList({', '.join([repr(i) for i in self.statements])})"

    def __iter__(self):
        for stmt in self.statements:
            yield stmt

    def eval(self):
        global STATEMENT_LIST_LEVEL
        in_main = False
        if not Signal.IN_MAIN:
            Signal.IN_MAIN = True
            in_main = True
        if not Signal.NO_CREATE_LEVEL:
            STATEMENT_LIST_LEVEL += 1
            ENV.append({})
            ENV_CONSTS.append({})
        if Signal.CREATE_BACK_LEVEL and Signal.BACK_LEVEL is None:
            Signal.BACK_LEVEL = STATEMENT_LIST_LEVEL-1
        # Arguments (if in function)
        if Signal.IN_FUNCTION and Signal.ARGUMENTS:
            for n, v in Signal.ARGUMENTS.items():
                ENV[STATEMENT_LIST_LEVEL][n.name] = v.value.eval()
            Signal.ARGUMENTS = None
        if Signal.IN_FUNCTION and Signal.KW_ARGUMENTS:
            for v in Signal.KW_ARGUMENTS:
                ENV[STATEMENT_LIST_LEVEL][v.name] = v.value.eval()
            Signal.KW_ARGUMENTS = None
        # Statements
        result = None
        for stmt in self.statements:
            try:
                result = stmt.eval()
            except Exception as e:
                Signal.ERROR = e
            if Signal.ERROR is not None:
                if not Signal.IN_TRY:
                    print(f'RuntimeError: {Signal.ERROR}')
                    exit(0)
                break
            if (Signal.BREAK or Signal.CONTINUE) and Signal.IN_CYCLE:
                break
            if Signal.RETURN and Signal.IN_FUNCTION:
                break
        if not Signal.NO_CREATE_LEVEL and STATEMENT_LIST_LEVEL not in MODULES.values():
            if not Signal.CREATE_BACK_LEVEL or Signal.BACK_LEVEL != STATEMENT_LIST_LEVEL:
                STATEMENT_LIST_LEVEL -= 1
                ENV.pop()
                ENV_CONSTS.pop()
        if Signal.CREATE_BACK_LEVEL and Signal.BACK_LEVEL == STATEMENT_LIST_LEVEL:
            Signal.CREATE_BACK_LEVEL = False
            Signal.BACK_LEVEL = None
            STATEMENT_LIST_LEVEL += 1
            ENV.append({})
            ENV_CONSTS.append({})
        if Signal.IN_MAIN and in_main:
            Signal.IN_MAIN = False
            if isinstance(self.statements[-1], EOFStmt):
                self.statements[-1].eval()
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

    def __assign_operation(self, val):
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
                    Signal.ERROR = f"unknown operator {self.assign_op}"
        return val

    def eval(self):
        has_var, level, is_const = has_variable(self.name)
        val = self.__assign_operation(self.a_expr)
        if self.is_assign:
            # Assign var/const
            if self.assign_op != '=':
                Signal.ERROR = f"{self.name} isn't assigned"
                return
            if has_var and level == STATEMENT_LIST_LEVEL:
                Signal.ERROR = f"{self.name} is assigned"
                return
            if self.is_const:
                ENV_CONSTS[STATEMENT_LIST_LEVEL][self.name] = val.eval()
            else:
                ENV[STATEMENT_LIST_LEVEL][self.name] = val.eval()
        elif has_var:
            # Reassign
            if is_const:
                ENV_CONSTS[level][self.name] = val.eval()
            else:
                ENV[level][self.name] = val.eval()
        elif isinstance(self.name, BraceAST):
            result = None
            obj = self.name
            if isinstance(obj.obj, str):
                result = VarAST(obj.obj).eval()
            elif isinstance(obj.obj, (ArrayAST, StringAST, CallStmt, ModuleCallAST, ClassPropAST)):
                result = obj.obj.eval()
            if result is not None:
                for i in obj.v[:-1]:
                    result = result[i.eval()]
            if result is not None:
                result[obj.v[-1].eval()] = val.eval()
        elif isinstance(self.name, ModuleCallAST):
            module = self.name
            if module.name not in MODULES:
                Signal.ERROR = f"unknown module {module.name}"
                return
            if module.obj in ENV[MODULES[module.name]]:
                ENV[MODULES[module.name]][module.obj] = val.eval()
            elif module.obj in ENV_CONSTS[MODULES[module.name]]:
                ENV_CONSTS[MODULES[module.name]][module.obj] = val.eval()
            else:
                Signal.ERROR = f"unknown module property {module.obj}"
                return
        elif isinstance(self.name, ClassPropAST):
            obj = self.name
            if Signal.IN_CLASS and Signal.CURRENT_CLASS and obj.name == 'this':
                obj.name = Signal.CURRENT_CLASS
            has_var, level, is_const = has_variable(obj.name)
            if has_var and not is_const:
                var = ENV[level][obj.name]
                if obj.is_super and var['parent'] is not None:
                    var = var['parent']
                if obj.prop in var['env']:
                    var['env'][obj.prop] = val.eval()
                    return
                if obj.prop in var['consts_env']:
                    var['consts_env'][obj.prop] = val.eval()
                    return
                while var['parent']:
                    var = var['parent']
                    if obj.prop in var['env']:
                        var['env'][obj.prop] = val.eval()
                        return
                    if obj.prop in var['consts_env']:
                        var['consts_env'][obj.prop] = val.eval()
                        return
                Signal.ERROR = f"unknown property {obj.prop} in class {obj.name}"
            else:
                Signal.ERROR = f"unknown class {obj.name}"
        else:
            Signal.ERROR = f"{self.name} isn't assigned"


class AssignClassStmt(Stmt):
    def __init__(self, name, body, inherit, prefix, interfaces):
        self.name = name
        self.body = body
        self.inherit = inherit
        self.prefix = prefix
        self.interfaces = interfaces

    def __repr__(self) -> str:
        return f"AssignClassStmt({self.prefix + ' ' if self.prefix else ''}{self.name}, {self.inherit}, {self.body})"

    def eval(self):
        global STATEMENT_LIST_LEVEL
        has_var, level, is_const = has_variable(self.name)
        if not has_var:
            Signal.NO_CREATE_LEVEL = True
            ENV.append({})
            ENV_CONSTS.append({})
            STATEMENT_LIST_LEVEL += 1
            self.body.eval()
            if self.inherit:
                has_var, level, is_const = has_variable(self.inherit)
                if has_var:
                    self.inherit = ENV[level][self.inherit]
                else:
                    Signal.ERROR = f"unknown inherit class {self.inherit}"
                    return
            must_have_data = []
            # implemented interfaces
            for interface in self.interfaces:
                h, l, c = has_variable(interface)
                if h:
                    interface = ENV[l][interface]
                    must_have_data += [i for i in interface['env'].keys() if i not in must_have_data]
                    must_have_data += [i for i in interface['consts_env'].keys() if i not in must_have_data]
                else:
                    Signal.ERROR = f"unknown interface {interface} of class {self.name}"
                    return
            ENV[STATEMENT_LIST_LEVEL - 1][self.name] = {
                'parent': self.inherit,
                'env': deepcopy(ENV[STATEMENT_LIST_LEVEL]),
                'consts_env': deepcopy(ENV_CONSTS[STATEMENT_LIST_LEVEL]),
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
                obj = ENV[STATEMENT_LIST_LEVEL - 1][self.name]
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
            STATEMENT_LIST_LEVEL -= 1
            ENV.pop()
            ENV_CONSTS.pop()
            Signal.NO_CREATE_LEVEL = False
            if len(must_have_data) > 0:
                print(f"[WARNING]: {', '.join(must_have_data)} isn't implemented in {self.name}")
        else:
            print(has_var, level, ENV[level][self.name])
            Signal.ERROR = f"class {self.name} is assigned"


class InterfaceStmt(Stmt):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self) -> str:
        return f"InterfaceStmt({self.name}, {self.body})"

    def eval(self):
        global STATEMENT_LIST_LEVEL
        has_var, level, is_const = has_variable(self.name)
        if not has_var:
            Signal.NO_CREATE_LEVEL = True
            ENV.append({})
            ENV_CONSTS.append({})
            STATEMENT_LIST_LEVEL += 1
            self.body.eval()
            ENV[STATEMENT_LIST_LEVEL - 1][self.name] = {
                'env': deepcopy(ENV[STATEMENT_LIST_LEVEL]),
                'consts_env': deepcopy(ENV_CONSTS[STATEMENT_LIST_LEVEL]),
                'name': self.name,
            }
            STATEMENT_LIST_LEVEL -= 1
            ENV.pop()
            ENV_CONSTS.pop()
            Signal.NO_CREATE_LEVEL = False
        else:
            Signal.ERROR = f"{self.name} is assigned"


class InitClassStmt(Stmt):
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        return f"InitClassStmt({self.args})"

    def eval(self):
        if None in ENV[STATEMENT_LIST_LEVEL]:
            Signal.ERROR = "this class equals init function"
            return
        ENV[STATEMENT_LIST_LEVEL][None] = (self.args, self.body)


class IfStmt(Stmt):
    def __init__(self, condition, body, elif_array, else_body):
        self.condition = condition
        self.body = body
        self.elif_array = elif_array
        self.else_body = else_body

    def __repr__(self) -> str:
        return f"IfStmt({self.condition}, {self.body}, {self.else_body})"

    def eval(self):
        condition = self.condition.eval()
        else_statement = True
        if condition:
            self.body.eval()
        else:
            for i in self.elif_array:
                (((_, condition), _), stmt_list), _ = i
                if condition.eval():
                    stmt_list.eval()
                    else_statement = False
                    break
        if self.else_body and else_statement:
            self.else_body.eval()


class SwitchCaseStmt(Stmt):
    def __init__(self, var, cases):
        self.var = var
        self.cases = cases

    def __repr__(self) -> str:
        return f"SwitchCaseStmt({self.var}, {self.cases})"

    def eval(self):
        var = self.var.eval()
        result = None
        for c in self.cases:
            if isinstance(c, CaseStmt):
                if c.condition:
                    val = c.condition.eval()
                    if val == var:
                        result = c.body.eval()
                        break
                    elif isinstance(val, (tuple, list)) and var in val:
                        result = c.body.eval()
                        break
                else:
                    result = c.body.eval()
                    break
        return result


class CaseStmt(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"CaseStmt({self.condition}, {self.body})"

    def eval(self):
        pass


class WhileStmt(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"WhileStmt({self.condition}, {self.body})"

    def eval(self):
        condition = self.condition.eval()
        while condition:
            self.body.eval()
            Signal.IN_CYCLE = True
            if Signal.IN_CYCLE:
                if Signal.CONTINUE:
                    Signal.CONTINUE = False
                    continue
                elif Signal.BREAK:
                    break
            if Signal.RETURN and Signal.IN_FUNCTION:
                break
            condition = self.condition.eval()
        Signal.IN_CYCLE = False
        Signal.BREAK = False
        Signal.CONTINUE = False


class ForStmt(Stmt):
    def __init__(self, var, cond, action, body):
        self.var = var  # VarAST or AssignStmt
        self.cond = cond  # BinOpExpr or VarAst/ArrayAST/CallStmt
        self.action = action  # AssignStmt(is_assign=False) or StmtList
        self.body = body  # StmtList or None

    def __repr__(self) -> str:
        return f"ForStmt({self.var}, {self.cond}, {self.action}, {self.body})"

    def eval(self):
        global STATEMENT_LIST_LEVEL
        ENV.append({})
        ENV_CONSTS.append({})
        STATEMENT_LIST_LEVEL += 1
        if self.body:  # for i = 0; i < 10; ++i; {}
            self.var.eval()
            condition = self.cond.eval()
            while condition:
                self.body.eval()
                Signal.IN_CYCLE = True
                if Signal.IN_CYCLE:
                    if Signal.CONTINUE:
                        Signal.CONTINUE = False
                        continue
                    if Signal.BREAK:
                        break
                if Signal.IN_FUNCTION and Signal.RETURN:
                    break
                self.action.eval()
                condition = self.cond.eval()
        else:  # for i in arr {}
            for i in self.cond.eval():
                ENV[STATEMENT_LIST_LEVEL][self.var] = i
                Signal.IN_CYCLE = True
                self.action.eval()
        STATEMENT_LIST_LEVEL -= 1
        ENV.pop()
        ENV_CONSTS.pop()
        Signal.IN_CYCLE = False
        Signal.BREAK = False
        Signal.CONTINUE = False


class BreakStmt(Stmt):
    def __repr__(self) -> str:
        return "BreakStmt"

    def eval(self):
        Signal.BREAK = True


class ContinueStmt(Stmt):
    def __repr__(self) -> str:
        return "ContinueStmt"

    def eval(self):
        Signal.CONTINUE = True


class TryCatchStmt(Stmt):
    def __init__(self, try_body, e_name, catch_body):
        self.try_body = try_body
        self.e_name = e_name
        self.catch_body = catch_body

    def __repr__(self) -> str:
        return f"TryCatchStmt({self.try_body}, {self.e_name}, {self.catch_body})"

    def eval(self):
        global STATEMENT_LIST_LEVEL
        Signal.IN_TRY = True
        self.try_body.eval()
        Signal.IN_TRY = False
        if Signal.ERROR is not None:
            Signal.NO_CREATE_LEVEL = True
            ENV.append({})
            ENV_CONSTS.append({})
            STATEMENT_LIST_LEVEL += 1
            ENV[STATEMENT_LIST_LEVEL][self.e_name] = Signal.ERROR
            Signal.ERROR = None
            self.catch_body.eval()
            STATEMENT_LIST_LEVEL -= 1
            ENV.pop()
            ENV_CONSTS.pop()


class EchoStmt(Stmt):
    def __init__(self, data):
        self.data = data

    def __repr__(self) -> str:
        return f"EchoStmt({self.data})"

    def eval(self):
        if isinstance(self.data, (Stmt, ASTExpr, BinOpExpr)):
            val = self.data.eval()
            if isinstance(val, tuple) and len(val) == 4:
                print(f"class {val[3]}")
            else:
                print(val)
        elif isinstance(self.data, (list, tuple)):
            for i in self.data:
                val = i.eval()
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

    def eval(self):
        if isinstance(self.text, ASTExpr):
            return input(self.text.eval())
        elif isinstance(self.text, str):
            return self.text


class BuiltInFuncStmt(Stmt):
    def __init__(self, name, arg):
        self.name = name
        self.arg = arg

    def __repr__(self) -> str:
        return f"BuiltInFuncStmt({self.name}, {self.arg})"

    def eval(self):
        val = None
        match self.name:
            case 'int':
                val = int(self.arg[0].eval())
            case 'float':
                val = float(self.arg[0].eval())
            case 'string':
                val = str(self.arg[0].eval())
            case 'length':
                val = len(self.arg[0].eval())
            case 'range':
                val = range(*[i.eval() for i in self.arg])
        return val


class FuncStmt(Stmt):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        return f"FuncStmt({self.name}, {self.args}, {self.body})"

    def eval(self):
        has_var, level, is_const = has_variable(self.name)
        if has_var and not is_const and level == STATEMENT_LIST_LEVEL:
            raise RuntimeError(f"Function {self.name} is exists")
        else:
            ENV[STATEMENT_LIST_LEVEL][self.name] = (self.args, self.body)


class LambdaStmt(Stmt):
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self) -> str:
        return f"LambdaStmt({self.args}, {self.body})"

    def eval(self):
        return self.args, self.body


class CallStmt(Stmt):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return f"CallStmt({self.name}, {self.args})"

    def eval(self):
        has_var, level, is_const = has_variable(self.name)
        f = None
        init_obj = None
        if has_var and not is_const:
            f = ENV[level][self.name]
            if isinstance(f, dict):  # class
                if not Signal.IN_CLASS:
                    Signal.CURRENT_CLASS = self.name
                Signal.IN_CLASS = True
                init_obj = f
                if None in f['env']:
                    f = f['env'][None]
                else:
                    f = ([], StmtList([]))
        elif isinstance(self.name, ModuleCallAST):
            f = self.name.eval()
        elif isinstance(self.name, ClassPropAST):
            f = self.name.eval()
            if not Signal.IN_CLASS:
                Signal.CURRENT_CLASS = self.name.name
            Signal.IN_CLASS = True
        if f:
            args = [i for i in self.args if i.name is None]
            fargs = [i for i in f[0] if i.value is None]
            kwargs = [i for i in self.args if i.name is not None]
            fkwargs = [i for i in f[0] if i.value is not None]
            if len(args) != len(fargs):
                raise RuntimeError(
                    f"function {self.name} waited for {len(fargs)}, but got {len(args)} arguments"
                )
            Signal.ARGUMENTS = {n: v for n, v in zip(fargs, args)}
            Signal.KW_ARGUMENTS = fkwargs + kwargs
            if not Signal.IN_FUNCTION:
                Signal.IN_FUNCTION = True
                f[1].eval()
                Signal.IN_FUNCTION = False
            else:
                f[1].eval()
            if init_obj:  # initialized class
                val = deepcopy(init_obj)
                val['initialized'] = True
                Signal.RETURN_VALUE = val
            Signal.RETURN = False

            returned = Signal.RETURN_VALUE
            Signal.RETURN_VALUE = None
            Signal.IN_CLASS = False
            Signal.CURRENT_CLASS = None
            return returned
        raise RuntimeError(f"function {self.name} isn't available")


class ReturnStmt(Stmt):
    def __init__(self, val):
        self.val = val

    def __repr__(self) -> str:
        return f"ReturnStmt({self.val})"

    def eval(self):
        Signal.RETURN = True
        Signal.RETURN_VALUE = self.val.eval()


class ImportStmt(Stmt):
    def __init__(self, module_name, objects):
        self.module_name = module_name
        self.objects = objects

    def __repr__(self) -> str:
        return f"ImportStmt({self.module_name}, {self.objects})"

    def eval(self):
        from .parser import stmt_list
        from . import Lexer
        module_name = self.module_name + '.avo'
        if not exists(module_name) or not isfile(module_name):
            raise RuntimeError(f"can't find module {module_name}")
        statements = stmt_list()(Lexer.lex_file(module_name), 0)
        if statements:
            Signal.CREATE_BACK_LEVEL = True
            MODULES[self.module_name] = STATEMENT_LIST_LEVEL + 1
            statements.value.eval()
        if self.objects is not None:
            env = [i for i in ENV[MODULES[self.module_name]].keys()]
            env_c = [i for i in ENV_CONSTS[MODULES[self.module_name]].keys()]
            for k in env + env_c:
                if k not in self.objects:
                    del ENV[MODULES[self.module_name]][k]


class EOFStmt(Stmt):
    def __repr__(self) -> str:
        return "EOFStmt()"

    def eval(self):
        global ENV, ENV_CONSTS, MODULES, STATEMENT_LIST_LEVEL
        if Signal.IN_MAIN or not Signal.NEED_FREE:
            return
        ENV = []
        ENV_CONSTS = []
        MODULES = {}
        STATEMENT_LIST_LEVEL = -1
        Signal.refresh()
