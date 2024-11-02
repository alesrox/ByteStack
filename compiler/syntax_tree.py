class ASTNode:
    def to_dict(self):
        return {"type": self.__class__.__name__}

class Program(ASTNode):
    def __init__(self, statements: list):
        self.statements : list = statements

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "statements": [statement.to_dict() if statement else None for statement in self.statements]
        }

class ListNode(ASTNode):
    def __init__(self, identifier, index):
        self.identifier = identifier
        self.index = index

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "identifier": self.identifier,
            "index": self.index
        }

class Expression(ASTNode):
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = value

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "value_type": self.value_type,
            "value": self.value
        }

class BinaryExpression(ASTNode):
    def __init__(self, operator: str, left, right):
        self.operator: str = operator
        self.left = left
        self.right = right

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "operator": self.operator,
            "left": self.left.to_dict() if isinstance(self.left, ASTNode) else self.left,
            "right": self.right.to_dict() if isinstance(self.right, ASTNode) else self.right
        }

class Declaration(ASTNode):
    def __init__(self, var_type: str, identifier: str, value):
        self.var_type: str = var_type
        self.identifier: str = identifier
        self.value = value

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "var_type": self.var_type,
            "identifier": self.identifier,
            "value": self.value.to_dict() if isinstance(self.value, ASTNode) else self.value
        }

class Assignment(ASTNode):
    def __init__(self, identifier, value: ASTNode):
        self.identifier: str = identifier
        self.value: ASTNode = value

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "identifier": 
                self.identifier.to_dict() if isinstance(self.identifier, ASTNode) else self.identifier,
            "value": self.value.to_dict() if isinstance(self.value, ASTNode) else self.value
        }

class IfStatement(ASTNode):
    def __init__(self, condition: Expression, true_block: Program, else_if_statements: list=None, else_block: Program=None):
        self.condition: Expression = condition
        self.true_block: Program = true_block
        self.elif_statements: list[IfStatement] = else_if_statements or []
        self.else_block: Program = else_block

    def to_dict(self) -> dict:
        new_dict = { 
            **super().to_dict(),
            "condition": self.condition.to_dict(),
            "true_block": self.true_block.to_dict(),
        }

        if self.elif_statements:
            new_dict["elif_statements"] = [elif_stmt.to_dict() for elif_stmt in self.elif_statements]

        if self.else_block:
            new_dict["else_block"] = self.else_block.to_dict()
        
        return new_dict
    
class ForStatement(ASTNode):
    def __init__(self, var, condition: Expression, block: Program):
        self.var = var
        self.condition: Expression = condition
        self.block: Program = block

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "var": self.var.to_dict(),
            "condition": self.condition.to_dict(),
            "statements": self.block.to_dict()
        }

class WhileStatement(ASTNode):
    def __init__(self, condition: Expression, block: Program, is_a_do_while: bool = False):
        self.is_a_do_while: bool = is_a_do_while
        self.condition: Expression = condition
        self.block: Program = block

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "do_while": self.is_a_do_while,
            "condition": self.condition.to_dict(),
            "statements": self.block.to_dict()
        }

class Argument(ASTNode):
    def __init__(self, arg_type, identifier):
        self.arg_type = arg_type
        self.identifier = identifier
    
    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "type": self.arg_type,
            "identifier": self.identifier
        }

class FunctionDeclaration(ASTNode):
    def __init__(self, identifier, args: Argument, block: Program):
        self.identifier = identifier
        self.args = args
        self.block = block

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "identifier" : self.identifier,
            "args" : [arg.to_dict() for arg in self.args],
            "body" : self.block.to_dict()
        }

class FunctionCall(ASTNode):
    def __init__(self, identifier, args, from_obj):
        self.identifier = identifier
        self.args = args
        self.from_obj = from_obj

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "from" : self.from_obj,
            "identifier" : self.identifier,
            "args" : [arg.to_dict() for arg in self.args],
        }
    
class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "value" : self.value.to_dict()
        }

class NewStatement(ASTNode):
    def __init__(self, obj):
        self.obj = obj

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "obj" : self.obj
        }