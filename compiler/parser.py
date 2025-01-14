from syntax_tree import *
from utils import literals
from semantic_analyzer import Semantic

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.semantic = Semantic()
        self.next_token()
    
    def next_token(self):
        self.current_token = self.lexer.token()
    
    def throw_error(self, msg: str=None):
        token = self.current_token
        raise Exception(f"Compilation Error on line {token.lineno} and lexpos {token.lexpos}: {msg}")
    
    def get_program(self) -> BlockNode:
        statements = []
        while self.current_token:
            item = self.statements()
            if item:
                statements.append(item)
        
        return BlockNode(statements)

    def statements(self) -> ASTNode:
        if self.current_token.type in self.semantic.types_register or self.current_token.value in self.semantic.types_register:
            return self.variable_declaration()

        match self.current_token.type:
            case 'LBRACE':
                return self.block()
            case 'FUNC':
                return self.function_declaration()
            case 'STRUCT':
                return self.struct_declaration()
            case 'IDENTIFIER':
                return self.assign_statement()
            case 'IF':
                return self.if_statement()
            case 'FOR':
                return self.for_statement()
            case 'WHILE':
                return self.while_statement()
            case 'RETURN':
                return self.return_statement()
            case _:
                self.throw_error(f"Unexpected Token: {self.current_token}")

    def block(self):
        self.next_token() # Consume '{'

        statements = []
        while self.current_token.type != 'RBRACE':
            statements.append(self.statements())
        
        self.next_token() # Consume '}'
        return BlockNode(statements)

    def expression(self):
        if self.current_token and self.current_token.type == 'NOT':
            operator = self.current_token.value
            self.next_token()
            operand = self.binary_expression()
            return BinaryExpression(operator, operand, None)
        
        return self.binary_expression()

    def binary_expression(self, operator_group: int = 0):
        operators = (
            ('AND', 'OR'),
            ('EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'),
            ('PLUS', 'MINUS'),
            ('MULTIPLY', 'DIVIDE', 'MOD'),
            ('POW'),
        )

        if operator_group == len(operators):
            return self.unary_expression()

        left = self.binary_expression(operator_group + 1)

        while self.current_token and self.current_token.type in operators[operator_group]:
            operator = self.current_token.value
            self.next_token()
            right = self.binary_expression(operator_group + 1)
            left = BinaryExpression(operator, left, right)

        return left
    
    def unary_expression(self):
        if self.current_token.type == 'EMPTY_ARR':
            self.next_token() # Consume '[]'
            return Literal('[]', [])

        if self.current_token.type == 'START_LIST':
            new_list = []
            while self.current_token.type != 'END_LIST':
                self.next_token() # Consume '[' or ','
                new_list.append(self.expression())

            self.next_token() # Consume ']'
            return Literal('[]', new_list)

        if self.current_token.type == 'LPAREN':
            self.next_token()  # Consume '('
            expr = self.binary_expression()
            if not self.current_token or self.current_token.type != 'RPAREN':
                self.throw_error("Expected a ')'")

            self.next_token() # Consume ')'
            return expr
        
        if self.current_token.type == 'NEW':
            self.next_token() # Consume 'new'
            return self.new_call()

        if self.current_token.type in literals:
            token = self.current_token
            self.next_token()
            return Literal(token.type, token.value)
        
        identifier = self.current_token.value
        self.next_token() # Consume VAR_INFO_NAME
        if self.current_token.type == 'LPAREN':
            return self.function_call(identifier)
        elif self.current_token.type != 'POINT':
            return Literal('VARIABLE', identifier)
        
        self.next_token() # Consume '.'
        access_attr = self.current_token.value
        self.next_token()

        if self.current_token.type != 'LPAREN':
            return MemberAccess(identifier, access_attr)
        
        return self.function_call(access_attr, identifier)

    def new_call(self):
        struct_name = self.current_token.value
        self.next_token() # Consume STRUCT_NAME_INFO

        arguments = []

        while self.current_token.type != 'RPAREN':
            self.next_token() # Consume '(' or ','
            if self.current_token.type == 'COMMA': self.throw_error('Wrong argmuents') # TODO: Improve error msg
            arguments.append(self.expression())
        
        self.next_token() # Consume ')'

        return NewCall(struct_name, arguments)
    
    def function_call(self, func_id, from_obj = 'System'):
        arguments = []

        while self.current_token.type != 'RPAREN':
            self.next_token() # Consume '(' or ','
            if self.current_token.type == 'RPAREN': break # No args funcs
            if self.current_token.type == 'COMMA': self.throw_error('Wrong argmuents') # TODO: Improve error msg
            arguments.append(self.expression())
        
        self.next_token() # Consume ')'
        # if self.current_token.type == 'SEMICOLON': self.next_token()
        return FunctionCall(func_id, arguments, from_obj)

    def variable_declaration(self):
        var_type = self.current_token.type
        if var_type == 'EMPTY_ARR': var_type = '[]'
        self.next_token() # Consume VAR_TYPE_INFO
        if self.current_token.type == 'EMPTY_ARR': 
            self.next_token() # Consume '[]'
            var_type += '[]'

        var_name = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO
        
        self.semantic.add_table_type(var_name, var_type)
        if self.current_token.type == 'SEMICOLON':
            self.next_token() # Consume ';'
            return VariableDeclaration(var_name, var_type)
        
        if self.current_token.type != 'ASSIGN':
            self.throw_error(f'{self.current_token}')
        
        self.next_token() # Consume '='
        value = self.expression()
        self.next_token() # Consume ';'
        self.semantic.check_declaration(var_name, value)
        return VariableDeclaration(var_name, var_type, value)
    
    def function_declaration(self):
        self.next_token() # Consume 'FUNC'
        func_name = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO

        arguments = []
        if self.current_token.type != 'LPAREN':
            self.throw_error(f"Excpected a '(' symbol: {self.current_token}")
        
        while self.current_token.type != 'RPAREN':
            self.next_token() # Consume '(' o ','
            
            arg_type = self.current_token.type
            self.next_token() # LITERAL_TYPE_INFO
            arguments.append(
                ParameterNode(arg_type, self.current_token.value)
            )
    
            self.next_token() # VAR_NAME_INFO

        self.next_token() # Consume ')'
        return_type = 'VOID'
        if self.current_token.type == 'RET':
            self.next_token() # Consume '->'
            return_type = self.current_token.type
            self.next_token() # Conseume RETURN_TYPE_INFO
        
        self.semantic.add_table_type(func_name, return_type)
        return FunctionDeclaration(func_name, return_type, arguments, self.block())
    
    def struct_declaration(self):
        self.next_token() # Consume 'struct'
        struct_name = self.current_token.value
        self.semantic.add_type(struct_name)
        self.next_token() # Consume STRUCT_INFO_NAME

        if self.current_token.type != "LBRACE":
            self.throw_error(f"Expected a '{'{'}' symbol but recived: {self.current_token}")
        self.next_token()

        struct_elements = []
        while self.current_token.type != "RBRACE":
            _type = self.current_token.value
            self.next_token() # Consume TYPE_VAR_INFO
            if self.current_token.type == 'EMPTY_ARR': 
                self.next_token() # Consume '[]'
                var_type += '[]'

            if self.current_token.type != 'IDENTIFIER':
                self.throw_error(f"An Identifier was expected: {self.current_token}")
            identifier = self.current_token.value
            self.next_token()

            if self.current_token.type != "SEMICOLON":
                self.throw_error(f"A semicolon ';' was expected")
            self.next_token() # Consume ';'
            struct_elements.append(ParameterNode(_type, identifier))
        
        self.next_token() # Consume '}'
        return ClassDeclaration(struct_name, struct_elements)
    
    def assign_statement(self):
        identifier = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO

        if self.current_token.type == 'START_LIST':
            self.next_token() # Consume '['

            index = self.expression()

            if self.current_token.type != 'END_LIST':
                self.throw_error(f"Expected an ']' symbol: {self.current_token}")
            self.next_token() # Consume ']'

            identifier = MemberAccess(identifier, index, True)

            while self.current_token.type == 'START_LIST':
                self.next_token() # Consume '['
                index = self.expression()
                self.next_token() # Conusme ']'
                identifier = MemberAccess(identifier, index, True)

            if self.current_token.type == 'ASSIGN':
                self.next_token() # Consume '='
                value = self.expression()
                self.next_token() # Consume ';'
                self.semantic.check_assigment(identifier, value)
                return AssignmentNode(identifier, value)
            
        if self.current_token.type == 'POINT':
            self.next_token() # Consume '.'
            access_attr = self.current_token.value
            self.next_token()

            if self.current_token.type != 'LPAREN':
                identifier = MemberAccess(identifier, access_attr)
            else:
                result = self.function_call(access_attr, identifier)
                self.next_token() # Consume ';'
                return result
        
        if self.current_token.type == 'LPAREN':
            function_call = self.function_call(identifier)
            self.next_token() # Consume ';'
            return function_call
        
        if self.current_token.type != 'ASSIGN':
            self.throw_error("Expected an equal symbol")
        self.next_token() # Consume '='

        value = self.expression()
        self.next_token() # Consume ';'
        self.semantic.check_assigment(identifier, value)
        return AssignmentNode(identifier, value)
    
    def if_statement(self):
        self.next_token() # Consume 'if'

        if self.current_token.type != 'LPAREN':
            self.throw_error("Expected a '(' symbol")
        
        self.next_token() # Consume '('
        condition = self.expression()
        self.next_token() # Consume ')'

        then_block = self.block()
        elif_statements = []
        else_block = None

        while self.current_token and self.current_token.type == 'ELIF':
            self.next_token()  # Consume 'elif'
            elif_condition = self.expression()  # condition
            elif_block = self.block()  # block
            elif_statements.append(IfStatement(elif_condition, elif_block))

        if self.current_token and self.current_token.type == 'ELSE':
            self.next_token()  # Consume 'else'
            else_block = self.block()  # else block

        return IfStatement(condition, then_block, elif_statements, else_block)

    def while_statement(self):
        while_condition = None
        self.next_token() # Consume 'While'

        if self.current_token.type != 'LPAREN':
            self.throw_error(f"Expected a '(' symbol: {self.current_token}")

        self.next_token() # Consume '('
        while_condition = self.expression()
        self.next_token() # Consume ')'

        while_body = self.block()
        return WhileStatement(while_condition, while_body)

    def for_statement(self):
        self.next_token() # Consume 'for'

        if self.current_token.type != 'LPAREN':
            self.throw_error("Expected a '(' symbol")

        self.next_token() # Consume '('
        for_var = None
        if self.current_token.type in self.semantic.types_register:
            for_var = self.variable_declaration()
        elif self.current_token.type == 'IDENTIFIER':
            for_var = self.identifier()
        else:
            self.throw_error(f'Expected a For Identifier Variable: {self.current_token}')

        for_condition = self.expression()
        self.next_token() # Consume ')'

        for_body = self.block()
        return ForStatement(for_var, for_condition, None, for_body)

    def return_statement(self):
        self.next_token() # Consume 'return'
        expression = self.expression()
        self.next_token() # Consume ';'
        return ReturnStatement(expression)
