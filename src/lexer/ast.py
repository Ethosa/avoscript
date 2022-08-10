# -*- coding: utf-8 -*-
from typing import Union, Tuple, List, Any

from equality import AnyBase


ENV = []
ENV_CONSTS = []
STATEMENT_LIST_LEVEL = -1


def has_variable(name: str) -> Tuple[bool, int, bool]:
    """
    Finds variable or constant in environments
    :param name: var/const name
    :return: (contains, level index, is constant)
    """
    for level in range(len(ENV)-1, -1, -1):
        if name in ENV[level]:
            return True, level, False
        elif name in ENV_CONSTS[level]:
            return True, level, True
    return False, 0, False


class Signal:
    IN_CYCLE = False
    IN_FOR_CYCLE = False
    IN_FUNCTION = False
    BREAK = False
    CONTINUE = False
    RETURN = False
    NO_CREATE_LEVEL = False
    RETURN_VALUE = None
    ARGUMENTS = None
    KW_ARGUMENTS = None


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
        raise RuntimeError(f'{self.var_name} was used before assign')


class BraceAST(ASTExpr):
    def __init__(self, obj, v):
        self.obj = obj
        self.v = v

    def __repr__(self) -> str:
        return f"BraceAST({self.v})"

    def eval(self):
        if isinstance(self.obj, str):
            return VarAST(self.obj).eval()[self.v.eval()]
        elif isinstance(self.obj, ArrayAST):
            return self.obj.eval()[self.v.eval()]
        elif isinstance(self.obj, StringAST):
            return self.obj.eval()[self.v.eval()]
        elif isinstance(self.obj, CallStmt):
            return self.obj.eval()[self.v.eval()]
        raise RuntimeError(f"{self.obj.eval()} isn't indexed")


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
            case _:
                raise RuntimeError('unknown operation')


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
                    return self.expr
                return binop.eval()
            case '--':
                binop = BinOpAST('-', self.expr, IntAST(1))
                if isinstance(self.expr, VarAST):
                    assign_stmt = AssignStmt(self.expr.var_name, binop)
                    assign_stmt.eval()
                    return self.expr
                return binop.eval()
            case _:
                raise RuntimeError(f"unknown unary operation: {self.op}")


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
                raise RuntimeError('unknown operation')


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
        if not Signal.NO_CREATE_LEVEL:
            STATEMENT_LIST_LEVEL += 1
            ENV.append({})
            ENV_CONSTS.append({})
        # Arguments (if in function)
        if Signal.IN_FUNCTION and Signal.ARGUMENTS:
            for n, v in Signal.ARGUMENTS.items():
                ENV[STATEMENT_LIST_LEVEL][n.value[0][0]] = v.value[0][1].eval()
            Signal.ARGUMENTS = None
        if Signal.IN_FUNCTION and Signal.KW_ARGUMENTS:
            for v in Signal.KW_ARGUMENTS:
                if isinstance(v.value[0][1], tuple):
                    ENV[STATEMENT_LIST_LEVEL][v.value[0][0]] = v.value[0][1][1].eval()
                else:
                    ENV[STATEMENT_LIST_LEVEL][v.value[0][0][0]] = v.value[0][1].eval()
            Signal.KW_ARGUMENTS = None
        # Statements
        for stmt in self.statements:
            stmt.eval()
            if (Signal.BREAK or Signal.CONTINUE) and Signal.IN_CYCLE:
                break
            if Signal.RETURN and Signal.IN_FUNCTION:
                break
        if not Signal.NO_CREATE_LEVEL:
            STATEMENT_LIST_LEVEL -= 1
            ENV.pop()
            ENV_CONSTS.pop()


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

    def eval(self):
        has_var, level, is_const = has_variable(self.name)
        if self.is_assign:
            # Assign var/const
            if self.assign_op != '=':
                raise RuntimeError(f"{self.name} isn't assigned")
            if has_var and level == STATEMENT_LIST_LEVEL:
                raise RuntimeError(f"{self.name} is assigned")
            if self.is_const:
                ENV_CONSTS[STATEMENT_LIST_LEVEL][self.name] = self.a_expr.eval()
            else:
                ENV[STATEMENT_LIST_LEVEL][self.name] = self.a_expr.eval()
        elif has_var:
            val = self.a_expr
            match self.assign_op:
                case '*=':
                    val = BinOpAST('*', VarAST(self.name), val)
                case '/=':
                    val = BinOpAST('/', VarAST(self.name), val)
                case '+=':
                    val = BinOpAST('+', VarAST(self.name), val)
                case '-=':
                    val = BinOpAST('-', VarAST(self.name), val)
                case '=':
                    pass
                case _:
                    raise RuntimeError(f"unknown operator {self.assign_op}")
            # Reassign
            if is_const:
                ENV_CONSTS[level][self.name] = val.eval()
            else:
                ENV[level][self.name] = val.eval()
        else:
            raise RuntimeError(f"{self.name} isn't assigned")


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
        if condition:
            self.body.eval()
        else:
            for i in self.elif_array:
                (((_, condition), _), stmt_list), _ = i
                if condition.eval():
                    stmt_list.eval()
            if self.else_body:
                self.else_body.eval()


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
        Signal.NO_CREATE_LEVEL = True
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
        Signal.NO_CREATE_LEVEL = False
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


class EchoStmt(Stmt):
    def __init__(self, data):
        self.data = data

    def __repr__(self) -> str:
        return f"EchoStmt({self.data})"

    def eval(self):
        if isinstance(self.data, (Stmt, ASTExpr, BinOpExpr)):
            print(self.data.eval())
        elif isinstance(self.data, (list, tuple)):
            print(*[i.eval() for i in self.data])
        else:
            print(self.data)


class FuncStmt(Stmt):
    def __init__(self, name, args, body):
        self.name = name
        self.args = args if args else []
        self.body = body

    def __repr__(self) -> str:
        return f"FuncStmt({self.name}, {self.args}, {self.body})"

    def eval(self):
        has_var, level, is_const = has_variable(self.name)
        if has_var and not is_const and level == STATEMENT_LIST_LEVEL:
            raise RuntimeError(f"Function {self.name} is exists")
        else:
            ENV[STATEMENT_LIST_LEVEL][self.name] = (self.args, self.body)


class CallStmt(Stmt):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return f"CallStmt({self.name}, {self.args})"

    def eval(self):
        has_var, level, is_const = has_variable(self.name)
        if has_var and self.name in ENV[level]:
            f = ENV[level][self.name]
            args = [i for i in self.args if i.value[0][0] is None]
            fargs = [i for i in f[0] if i.value[0][1] is None]
            kwargs = [i for i in self.args if not i.value[0][0] is None]
            fkwargs = [i for i in f[0] if not i.value[0][1] is None]
            if len(args) != len(fargs):
                raise RuntimeError(
                    f"function {self.name} waited for {len(fargs)}, but got {len(args)} arguments"
                )
            Signal.IN_FUNCTION = True
            Signal.ARGUMENTS = {n: v for n, v in zip(fargs, args)}
            Signal.KW_ARGUMENTS = fkwargs + kwargs
            f[1].eval()
            Signal.IN_FUNCTION = False
            Signal.RETURN = False

            returned = Signal.RETURN_VALUE
            Signal.RETURN_VALUE = None
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
