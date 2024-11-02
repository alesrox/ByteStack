from syntax_tree import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.next_token()
    
    def next_token(self):
        self.current_token = self.lexer.token()
    
    def parser(self) -> Program:
        if not self.lexer:
            raise Exception()

        return self.program()
    
    def throw_error(self, msg: str):
        token = self.current_token
        raise Exception(f"Compilation Error on line {token.lineno} and lexpos {token.lexpos}: {msg}")
        exit()
    
    def program(self) -> Program:
        statements = []
        while self.current_token:
            item = self.statements()
            if item:
                statements.append(item)
        
        return Program(statements)

    def statements(self) -> ASTNode:
        match self.current_token.type:
            case 'LET':
                return self.declaration()
            case 'IDENTIFIER':
                return self.identifier()
            case 'IF':
                return self.if_statement()
            case 'FOR':
                return self.for_statement()
            case 'WHILE':
                return self.while_statement()
            case 'DO':
                return self.while_statement()
            case 'LBRACE':
                return self.block()
            case 'FUNC':
                return self.function_declaration()
            case 'RETURN':
                return self.return_statement()
            case _:
                self.throw_error(f"Unexpected Token: {self.current_token}")

    def block(self):
        if self.current_token.type != 'LBRACE':
            self.throw_error(f"Expected a '{'{'}' symbol: {self.current_token}")

        self.next_token()  # Consume '{'

        statements = []
        while self.current_token and self.current_token.type != 'RBRACE':
            statements.append(self.statements())

        self.next_token()  # Consume '}'
        return Program(statements)
        
    def list_expresion(self):
        if self.current_token.type == 'EMPTY_ARR':
            self.next_token() # Consume '[]'
            return []
        
        items = []
        while self.current_token.type != 'END_LIST':
            self.next_token() # Consume '[' or ','
            items.append(self.expression())
        
        self.next_token() # Consume ']'
        return items

    def expression(self):
        if self.current_token.type in ('START_LIST', 'EMPTY_ARR'):
            return self.list_expresion()

        if self.current_token.type == "LPAREN":
            self.next_token() # Consume ')'
            expr = self.binary_expression()
            if self.current_token.type != 'RPAREN':
                self.throw_error(f"Expected a ')' symbol: {self.current_token}")

            self.next_token() # Consume ')'
            return expr

        if self.current_token.type in ['NUMBER', 'FLOAT_LITERAL', 'BOOL_LITERAL', 'STRING_LITERAL', 'IDENTIFIER']:
            token = self.lexer.clone().token()
            if token.type in ('SEMICOLON', 'COMMA', 'END_LIST', 'RPAREN'):
                literal_type, value = self.current_token.type, self.current_token.value
                self.next_token()
                return Expression(literal_type, value)
            elif self.current_token.type == 'IDENTIFIER' and token.type == 'LPAREN':
                token = self.current_token
                self.next_token()
                return self.function_call(token.value)
            elif self.current_token.type == 'IDENTIFIER' and token.type == 'START_LIST':
                token = self.current_token
                self.next_token() # Consume VAR_NAME_INFO
                self.next_token() # Consume '['
                index = self.expression()
                self.next_token() # Consume ']'
                return ListNode(token.value, index)

            expr = self.binary_expression()
            return expr
        
        self.throw_error(f"Unexpected Token: {self.current_token}")

    def binary_expression(self, operator_group: int = 0):
        operators = (
            ('AND', 'OR'),
            ('EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'),
            ('PLUS', 'MINUS'),
            ('MULTIPLY', 'DIVIDE'),
        )

        if operator_group == len(operators):
            return self.literal_expression()

        left = self.binary_expression(operator_group + 1)

        while self.current_token and self.current_token.type in operators[operator_group]:
            operator = self.current_token.value
            self.next_token()
            right = self.binary_expression(operator_group + 1)
            left = BinaryExpression(operator, left, right)

        return left
    
    def literal_expression(self):
        if self.current_token.type in ['NUMBER', 'FLOAT_LITERAL', 'STRING_LITERAL', 'BOOL_LITERAL', 'IDENTIFIER']:
            token = self.current_token
            self.next_token()
            return Expression(token.type, token.value) 

        self.throw_error(f"Unexpected expresion: {self.current_token}")

    def declaration(self):
        self.next_token() # Consume 'LET'
        var_type = self.current_token.value
        self.next_token() # Consume VAR_TYPE_INFO
        if self.current_token.type == 'EMPTY_ARR': 
            self.next_token() # Consume '[]'
            var_type += '[]'
        
        if self.current_token.type != 'IDENTIFIER':
            self.throw_error(f"An Identifier was expected: {self.current_token}")
        
        identifier = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO

        if self.current_token.type != 'ASSIGN':
            self.throw_error("Expected an equal symbol")
        
        self.next_token() # Consume '='

        value = self.expression()
        if ('[]' in var_type) and not isinstance(value, list):
            self.throw_error("An array was expected")

        self.next_token() # Consume ';'
        return Declaration(var_type, identifier, value)
    
    def identifier(self):
        identifier = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO

        if self.current_token.type == 'START_LIST':
            self.next_token() # Consume '['
            index = self.expression()

            if self.current_token.type != 'END_LIST':
                self.throw_error(f"Expected an ']' symbol: {self.current_token}")

            self.next_token() # Consume ']'
            identifier = ListNode(identifier, index)

            if self.current_token.type == 'ASSIGN':
                self.next_token() # Consume '='
                value = self.expression()
                self.next_token() # Consume ';'
                return Assignment(identifier, value)
            
        if self.current_token.type == 'POINT':
            self.next_token() # Consume '.'
            func_id = self.current_token.value
            self.next_token() # Consume FUNC_NAME_TYPE
            result = self.function_call(func_id, identifier)
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
        return Assignment(identifier, value)
    
    def if_statement(self):
        self.next_token() # Consume 'if'

        if self.current_token.type != 'LPAREN':
            self.throw_error("Expected a '(' symbol")
        
        self.next_token() # Consume '('
        condition = self.expression()
        self.next_token() # Consume ')'

        true_block = self.block()
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

        return IfStatement(condition, true_block, elif_statements, else_block)

    def for_statement(self):
        self.next_token() # Consume 'for'

        if self.current_token.type != 'LPAREN':
            self.throw_error("Expected a '(' symbol")
        self.next_token() # Consume '('
        
        for_var = None
        if self.current_token.type == 'LET':
            for_var = self.declaration()
        elif self.current_token.type == 'IDENTIFIER':
            for_var = self.identifier()
        else:
            self.throw_error(f'Expected a For Identifier Var: {self.current_token}')

        for_condition = self.expression()
        self.next_token() # Consume ')'

        for_body = self.block()
        return ForStatement(for_var, for_condition, for_body)

    def while_statement(self):
        while_condition = None
        is_a_do_while = self.current_token.type == 'DO'
        self.next_token() # Consume 'While' or 'Do'

        if not is_a_do_while:
            if self.current_token.type != 'LPAREN':
                self.throw_error(f"Expected a '(' symbol: {self.current_token}")
            self.next_token() # Consume '('
            while_condition = self.expression()
            self.next_token() # Consume ')'

        while_body = self.block()

        if is_a_do_while:
            if self.current_token.type != 'WHILE':
                self.throw_error('Expected a while condition')

            self.next_token() # Consume 'While'
            self.next_token() # Consume '('
            while_condition = self.expression()
            self.next_token() # Consume ')'

            if self.current_token.type != 'SEMICOLON': 
                self.throw_error("Expected a ';' symbol")
            
            self.next_token()
        return WhileStatement(while_condition, while_body, is_a_do_while)
    
    def return_statement(self):
        self.next_token() # Consume 'Return'
        expression = self.expression()
        self.next_token() # Consume ';'
        return ReturnStatement(expression)

    def function_declaration(self):
        self.next_token() # Consume 'func'
        identifier = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO

        arguments = []
        if self.current_token.type != 'LPAREN':
            self.throw_error(f"Excpected a '(' symbol: {self.current_token}")

        while self.current_token.type != 'RPAREN':
            self.next_token() # Consume '(' o ','
            
            arg_type = self.current_token.type
            self.next_token() # LITERAL_TYPE_INFO
            arguments.append(
                Argument(arg_type, self.current_token.value)
            )
    
            self.next_token() # VAR_NAME_INFO

        self.next_token() # Consume ')'
        return FunctionDeclaration(identifier, arguments, self.block())
    
    def function_call(self, identifier, from_obj = 'System'):
        arguments = []

        while self.current_token.type != 'RPAREN':
            self.next_token() # Consume '(' or ','
            if self.current_token.type == 'RPAREN': break
            arguments.append(self.expression())
        
        self.next_token() # Consume ')'
        # if self.current_token.type == 'SEMICOLON': self.next_token()
        return FunctionCall(identifier, arguments, from_obj)