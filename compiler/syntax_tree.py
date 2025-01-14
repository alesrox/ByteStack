class ASTNode:
    def to_dict(self) -> dict:
        return {"type": self.__class__.__name__}

class BlockNode(ASTNode):
    def __init__(self, statements: list[ASTNode]):
        self.statements: list = statements

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "statements": [statement.to_dict() if statement else None for statement in self.statements]
        }

class TypeNode(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def to_dict(self) -> dict:
        return {
            # **super().to_dict(),
            "primitive type" : self.name
        }

class ExpressionNode(ASTNode):
    def __init__(self, expression_type: str):
        self.expression_type = expression_type

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
        }

class BinaryExpression(ExpressionNode):
    def __init__(self, operator: str, right: ExpressionNode, left: ExpressionNode):
        super().__init__('Binary Expression')
        self.operator = operator
        self.right = right
        self.left = left

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "operator": self.operator,
            "right": self.right.to_dict(),
            "left": self.left.to_dict()
        }

class UnaryExpressionNode(ExpressionNode):
    def __init__(self, unary_expression_type: str):
        super().__init__('Unary Expression')
        self.unary_expression_type = unary_expression_type

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
        }

class Literal(UnaryExpressionNode):
    def __init__(self, value_type: TypeNode, value):
        super().__init__('Literal')
        self.value_type = value_type
        self.value = value

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "value_type": self.value_type,
            "value": self.value
        }

class FunctionCall(UnaryExpressionNode):
    def __init__(self, identifier: str, args: list[ExpressionNode], from_obj: str = 'System'):
        super().__init__('Function Call')
        self.identifier = identifier
        self.args = args
        self.from_obj = from_obj

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "identifier": self.identifier,
            "args": [arg.to_dict() for arg in self.args],
            "from_obj": self.from_obj
        }

class NewCall(UnaryExpressionNode):
    def __init__(self, identifier: str, args: list[ExpressionNode]):
        super().__init__('Function Call')
        self.struct = identifier
        self.args = args

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "struct": self.struct,
            "args": [arg.to_dict() for arg in self.args],
        }

class MemberAccess(UnaryExpressionNode):
    def __init__(self, obj: str, attribute: any, list_access: bool = False):
        super().__init__('Member Access')
        self.object = obj
        self.attribute = attribute
        self.list_access = list_access

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "object": self.object,
            "attribute": self.attribute
        }

class DeclarationNode(ASTNode):
    def __init__(self, obj_declarated, identifier: str):
        self.obj_declarated = obj_declarated
        self.identifier = identifier

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "identifier": self.identifier,
        }

class VariableDeclaration(DeclarationNode):
    def __init__(self, identifier: str, var_type: TypeNode, initializer: ExpressionNode = None):
        super().__init__('Variable', identifier)
        self.var_type = var_type
        self.initializer = initializer

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "var_type": self.var_type,
            "initializer": self.initializer.to_dict() if isinstance(self.initializer, ASTNode) else self.initializer
        }

class ParameterNode(ASTNode):
    def __init__(self, p_type: TypeNode, identifier: str):
        self.type = p_type
        self.identifier = identifier

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "type": self.type,
            "identifier": self.identifier,
        }

class FunctionDeclaration(DeclarationNode):
    def __init__(self, identifier: str, return_type: TypeNode, parameters: list[ParameterNode], body: BlockNode):
        super().__init__('Function', identifier)
        self.return_type = return_type
        self.parameters = parameters
        self.body = body

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "return_type": self.return_type,
            "parameters": [param.to_dict() for param in self.parameters],
            "body": self.body.to_dict() if self.body else None
        }

class ClassDeclaration(DeclarationNode):
    def __init__(self, identifier: str, attr: list[ParameterNode]):
        super().__init__('Struct', identifier)
        self.attributes = attr

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "identifier": self.identifier,
            "attributes": [attr.to_dict() for attr in self.attributes]
        }

class StatementNode(ASTNode):
    def __init__(self, statement):
        super().__init__()
        self.statement = statement

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
        }

class AssignmentNode(StatementNode):
    def __init__(self, identifier: str, value: ExpressionNode):
        super().__init__("Assignment")
        self.identifier = identifier
        self.value = value
    
    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "identifier": self.identifier,
            "value": self.value
        }

class IfStatement(StatementNode):
    def __init__(self, condition: ExpressionNode, then_block: BlockNode, else_if_statements: list[StatementNode] = None, else_block: BlockNode = None):
        super().__init__("IfStatement")
        self.condition = condition
        self.then_block = then_block
        self.elif_statements: list[IfStatement] = else_if_statements or []
        self.else_block = else_block

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "condition": self.condition.to_dict(),
            "then_block": self.then_block.to_dict(),
            "elif_statements": [statement.to_dict() for statement in self.elif_statements],
            "else_block": self.else_block.to_dict() if self.else_block else None
        }

class WhileStatement(StatementNode):
    def __init__(self, condition: ExpressionNode, body: BlockNode):
        super().__init__("WhileStatement")
        self.condition = condition
        self.body = body

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "condition": self.condition.to_dict(),
            "body": self.body.to_dict()
        }

class ForStatement(StatementNode):
    def __init__(self, variable: str, condition: ExpressionNode, increment: ExpressionNode, body: BlockNode):
        super().__init__("ForStatement")
        self.variable = variable
        self.condition = condition
        self.increment = increment
        self.body = body

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "variable": self.variable,
            "condition": self.condition.to_dict(),
            # "increment": self.increment.to_dict(),
            "body": self.body.to_dict()
        }

class BreakStatement(StatementNode):
    def __init__(self):
        super().__init__("BreakStatement")

    def to_dict(self) -> dict:
        return {**super().to_dict()}

class ContinueStatement(StatementNode):
    def __init__(self):
        super().__init__("ContinueStatement")

    def to_dict(self) -> dict:
        return {**super().to_dict()}

class ReturnStatement(StatementNode):
    def __init__(self, expression: ExpressionNode):
        super().__init__("ReturnStatement")
        self.expression = expression

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "return": self.expression
        }