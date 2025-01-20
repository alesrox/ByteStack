from syntax_tree import *
from utils import literals
from tools import module
from lexer import keywords
from error import ParserError
from semantic_analyzer import Semantic

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.semantic = Semantic()
        self.next_token()
    
    def next_token(self):
        self.current_token = self.lexer.token()
    
    def throw_error(self, msg: str = None):
        token = self.current_token
        raise ParserError(f"SyntaxError: {msg} at line {token.lineno}.")
    
    def get_token_info(self):
        if '_LITERAL' in self.current_token.type:
            return self.current_token.type.replace('_', ' ').lower()
        elif self.current_token.type in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MOD', 'POW']:
            return self.current_token.type.lower() + ' symbol'
        elif self.current_token.type in ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'ASSIGN', 'START_LIST', 'END_LIST', 'EMPTY_ARR', 'POINT', 'RET']:
            return self.current_token.value
        elif self.current_token.type in ['EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE']:
            return 'logic operator'
        elif self.current_token.type in keywords:
            return f"{self.current_token.type.lower()} keyword"

        return self.current_token.type.lower()
    
    def get_program(self) -> BlockNode:
        statements = []
        while self.current_token:
            item = self.statements()
            if item:
                statements.append(item)
        
        return BlockNode(statements)

    def statements(self) -> ASTNode:
        if self.semantic.is_a_type(self.current_token.type) or self.semantic.is_a_type(self.current_token.value):
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
            case 'CONTINUE':
                self.next_token()
                self.next_token() # Consume ';'
                return ContinueStatement()
            case 'BREAK':
                self.next_token()
                self.next_token() # Consume ';'
                return BreakStatement()
            case _:
                self.throw_error(f"Unexpected '{self.get_token_info()}' token found")

    def block(self, new_context: bool = True):
        if new_context: self.semantic.new_no_named_context()
        if self.current_token.type != 'LBRACE':
            brace_str = '{'
            self.throw_error(f"Expected a '{brace_str}' to start a block, but got '{self.get_token_info()}' instead")

        self.next_token() # Consume '{'

        statements = []
        while self.current_token.type != 'RBRACE':
            statements.append(self.statements())
        
        self.next_token() # Consume '}'
        
        if new_context: self.semantic.return_context()
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

        self.semantic.lineno = self.current_token.lineno
        if self.current_token.type == 'START_LIST':
            new_list = []
            while self.current_token.type != 'END_LIST':
                self.next_token() # Consume '[' or ','
                new_list.append(self.expression())

            self.next_token() # Consume ']'
            return Literal(self.semantic.get_list_type(new_list), new_list)

        if self.current_token.type == 'LPAREN':
            self.next_token()  # Consume '('
            expr = self.binary_expression()
            if not self.current_token or self.current_token.type != 'RPAREN':
                self.throw_error(f"Expected a ')' to close the expression, but found '{self.get_token_info()}' instead")

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
            self.semantic.lineno = self.current_token.lineno
            self.semantic.get_var_type(identifier) # Throws an error if identifier doesn't exits
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
            if self.current_token.type == 'RPAREN': break # No struct args
            if self.current_token.type == 'COMMA': 
                self.throw_error("Unexpected ',' found. Expected a valid expression or operator before the comma")
            arguments.append(self.expression())
        
        self.next_token() # Consume ')'

        return NewCall(struct_name, arguments)
    
    def function_call(self, func_id, from_obj = 'System'):
        self.semantic.lineno = self.current_token.lineno
        arguments = []

        while self.current_token.type != 'RPAREN':
            self.next_token() # Consume '(' or ','
            if self.current_token.type == 'RPAREN': break # No args funcs
            if self.current_token.type == 'COMMA': 
                self.throw_error("Unexpected ',' found. Expected a valid expression or operator before the comma")
            arguments.append(self.expression())
        
        self.next_token() # Consume ')'
        # if self.current_token.type == 'SEMICOLON': self.next_token()
        arguments =  self.semantic.check_function_call(func_id, arguments)
        return FunctionCall(func_id, arguments, from_obj)

    def variable_declaration(self):
        var_type = self.current_token.type
        if var_type == 'IDENTIFIER': var_type = self.current_token.value
        if var_type == 'EMPTY_ARR': var_type = '[]'
        
        self.semantic.lineno = self.current_token.lineno
        self.next_token() # Consume VAR_TYPE_INFO
        while self.current_token.type == 'EMPTY_ARR': 
            self.next_token() # Consume '[]'
            var_type += '[]'

        var_name = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO
        
        self.semantic.add_table_type(var_name, var_type)
        if self.current_token.type == 'SEMICOLON':
            self.next_token() # Consume ';'
            return VariableDeclaration(var_name, var_type)
        
        if self.current_token.type != 'ASSIGN':
            self.throw_error(f"Expected an assignment operator '=', but got '{self.get_token_info()}' instead")
        
        self.next_token() # Consume '='
        value = self.expression()
        self.next_token() # Consume ';'
        value = self.semantic.check_types_assigment(var_name, value)
        return VariableDeclaration(var_name, var_type, value)
    
    def function_declaration(self):
        self.next_token() # Consume 'FUNC'
        func_name = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO
        self.semantic.lineno = self.current_token.lineno

        arguments = []
        if self.current_token.type != 'LPAREN':
            self.throw_error(f"Expected a '(' symbol, but found '{self.get_token_info()}' instead")
        
        while self.current_token.type != 'RPAREN':
            self.next_token() # Consume '(' o ','
            
            arg_type = self.current_token.type
            if arg_type == 'IDENTIFIER': arg_type = self.current_token.value
            if arg_type == 'EMPTY_ARR': arg_type = '[]'
            self.next_token() # LITERAL_TYPE_INFO
            while self.current_token.type == 'EMPTY_ARR': 
                self.next_token() # Consume '[]'
                var_type += '[]'

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
        
        self.semantic.add_new_func(func_name, return_type, arguments)
        self.semantic.change_context(func_name)
        func_body = self.block(False)
        func_body = module(func_name, [arg.identifier for arg in arguments], func_body)
        self.semantic.return_context()
        return FunctionDeclaration(func_name, return_type, arguments, func_body)
    
    def struct_declaration(self):
        self.next_token() # Consume 'struct'
        struct_name = self.current_token.value
        self.next_token() # Consume STRUCT_INFO_NAME

        if self.current_token.type != "LBRACE":
            self.throw_error(f"Expected a '(' symbol, but found '{self.get_token_info()}' instead")
        self.next_token()
        self.semantic.lineno = self.current_token.lineno

        struct_elements = []
        while self.current_token.type != "RBRACE":
            _type = self.current_token.value if self.current_token.type == 'IDENTIFIER' else self.current_token.type
            self.next_token() # Consume TYPE_VAR_INFO
            while self.current_token.type == 'EMPTY_ARR': 
                self.next_token() # Consume '[]'
                var_type += '[]'

            if self.current_token.type != 'IDENTIFIER':
                self.throw_error(f"Expected an identifier, but found '{self.get_token_info()}' instead")
            identifier = self.current_token.value
            self.next_token()

            if self.current_token.type != "SEMICOLON":
                self.throw_error(f"Expected a semicolon ';', but found '{self.get_token_info()}' instead")
            self.next_token() # Consume ';'
            struct_elements.append(ParameterNode(_type, identifier))
        
        self.next_token() # Consume '}'
        self.semantic.add_new_type(struct_name, struct_elements)
        return ClassDeclaration(struct_name, struct_elements)
    
    def assign_statement(self):
        identifier = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO
        self.semantic.lineno = self.current_token.lineno

        if self.current_token.type == 'START_LIST':
            self.next_token() # Consume '['

            index = self.expression()

            if self.current_token.type != 'END_LIST':
                self.throw_error(f"Expected a ']' symbol, but found '{self.get_token_info()}' instead")
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
                value = self.semantic.check_types_assigment(identifier, value)
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
            self.throw_error(f"Expected an assignment operator '=', but got '{self.get_token_info()}' instead.")
        self.next_token() # Consume '='

        value = self.expression()
        self.next_token() # Consume ';'
        value = self.semantic.check_types_assigment(identifier, value)
        return AssignmentNode(identifier, value)
    
    def if_statement(self):
        self.next_token() # Consume 'if'

        if self.current_token.type != 'LPAREN':
            self.throw_error(f"Expected a ']' symbol, but found '{self.get_token_info()}' instead")
        
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
            self.throw_error(f"Expected a ']' symbol, but found '{self.get_token_info()}' instead")

        self.next_token() # Consume '('
        while_condition = self.expression()
        self.next_token() # Consume ')'

        while_body = self.block()
        return WhileStatement(while_condition, while_body)

    def for_statement(self):
        self.next_token() # Consume 'for'

        if self.current_token.type != 'LPAREN':
            self.throw_error(f"Expected a ']' symbol, but found '{self.get_token_info()}' instead")

        self.next_token() # Consume '('
        for_var = None
        if self.semantic.is_a_type(self.current_token.type) or self.semantic.is_a_type(self.current_token.value):
            self.semantic.new_no_named_context()
            for_var = self.variable_declaration()
        elif self.current_token.type == 'IDENTIFIER':
            for_var = self.identifier()
            self.semantic.new_no_named_context()
        else:
            self.throw_error(f"Expected a variable identifier for the 'for' loop, but found '{self.get_token_info()}' instead")

        for_condition = self.expression()
        self.next_token() # Consume ')'

        for_body = self.block(False)
        self.semantic.return_context()
        return ForStatement(for_var, for_condition, None, for_body)

    def return_statement(self):
        self.next_token() # Consume 'return'
        expression = self.expression()
        self.next_token() # Consume ';'
        return ReturnStatement(expression)
