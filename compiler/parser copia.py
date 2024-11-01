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
                return self.assignment()
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
            case 'SEMICOLON':
                pass
                #self.next_token()
                #return self.statements()
            case _:
                self.throw_error(f"Unexpected Token: {self.current_token}")

        self.next_token()
    
    def block(self):
        if self.current_token.type != 'LBRACE':
            self.throw_error(f"Expected a '{'{'}' symbol: {self.current_token}")
        self.next_token()  # Consume '{'

        statements = []
        while self.current_token and self.current_token.type != 'RBRACE':
            if self.current_token.type == 'SEMICOLON':
                self.next_token()
            else:
                statements.append(self.statements())

        self.next_token()  # Consume '}'
        return Program(statements)

    def expression(self):
        expr = None

        if self.current_token.type == "NEW":
            return self.new_obj()
        
        if self.current_token.type == "EMPTY_ARR":
            return []
        
        if self.current_token.type == "START_LIST":
            items = []
            while self.current_token and self.current_token.type != 'END_LIST':
                self.next_token() # Consume '[', ','
                items.append(self.expression())
            
            self.next_token() # Consume ']'
            return items

        if self.current_token.type == "LPAREN":
            self.next_token()
            expr = self.binary_expression()
            if self.current_token.type != 'RPAREN':
                self.throw_error(f"Expected a ')' symbol: {self.current_token}")

            self.next_token() # Consume ')'
            return expr

        if self.current_token.type in ['NUMBER', 'FLOAT_LITERAL', 'BOOL_LITERAL', 'IDENTIFIER']:
            token = self.current_token
            self.next_token()
            if self.current_token.type in ('SEMICOLON', 'COMMA', 'END_LIST'):
                literal_type, value = token.type, token.value
                return Expression(literal_type, value)
            elif self.current_token.type == 'LPAREN':
                return self.function_call(token.value)
            elif self.current_token.type == 'START_LIST':
                self.next_token() # Consume '['
                index = self.current_token.value
                self.next_token()

                if self.current_token.type != 'END_LIST':
                    self.throw_error(f"Expected an ']' symbol: {self.current_token}")

                self.next_token() # Consume ']'
                if self.current_token.type == 'RPAREN': self.next_token()
                return ListNode(token.value, index)

            expr = self.binary_expression()
            if self.current_token.type not in ('SEMICOLON', 'RPAREN', 'COMMA', 'END_LIST'):
                self.throw_error(f"Expected a ';' symbol: {self.current_token}")
        
        self.next_token() # Consume ';', ',', ')'
        return expr

    def binary_expression(self, operator_group: int = 0):
        operators = (
            ('AND', 'OR'),
            ('EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'),
            ('PLUS', 'MINUS'),
            ('MULTIPLY', 'DIVIDE'),
        )

        if operator_group == len(operators):
            return self.literal_expression()

        # if self.current_token and self.current_token.type == 'MINUS' and operator_group == 2:
        #     self.next_token()
        #     right = self.binary_expression(operator_group + 1)
        #     return BinaryExpression('-', Expression('NUMBER', 0), right)

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
        
        identifier = self.current_token.value
        self.next_token() # Consume VAR_NAME_INFO
        
        if self.current_token.type != 'ASSIGN':
            self.throw_error("Expected an equal symbol")
        
        self.next_token() # Consume '='

        value = self.expression()
        if '[]' in var_type and not isinstance(value, list):
            self.throw_error("An array was expected")
        return Declaration(var_type, identifier, value)
    
    def assignment(self):
        identifier = self.current_token.value
        index = None
        self.next_token() # Consume VAR_NAME_INFO

        if self.current_token.type == 'START_LIST':
            self.next_token() # Consume '['
            index = self.current_token.value
            self.next_token() 

            if self.current_token.type != 'END_LIST':
                self.throw_error(f"Expected an ']' symbol: {self.current_token}")

            self.next_token() # Consume ']'
            return Assignment(identifier, self.expression(), index)

        if self.current_token.type == 'POINT':
            self.next_token()
            return self.function_call(self.current_token.value, identifier)

        if self.current_token.type == 'LPAREN':
            return self.function_call(identifier)

        if self.current_token.type != 'ASSIGN':
            self.throw_error(f"Expected an equal symbol: {self.current_token}")
        self.next_token()
        
        value = self.expression()

        return Assignment(identifier, value, index)

    def if_statement(self):
        self.next_token() # Conseume 'if'

        if self.current_token.type != 'LPAREN':
            self.throw_error("Expected a '(' symbol")

        condition = self.expression()

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
        self.next_token()
        
        for_var = None
        if self.current_token.type == 'LET':
            for_var = self.declaration()
        elif self.current_token.type == 'IDENTIFIER':
            for_var = self.assignment()
        else:
            self.throw_error(f'Expected a For Identifier Var: {self.current_token}')
        
        self.next_token() # Consume ';'
        for_condition = self.expression()
        for_body = self.block()
        
        return ForStatement(for_var, for_condition, for_body)
    
    def while_statement(self):
        is_a_do_while = self.current_token.type == 'DO'
        self.next_token() # Consume 'While' o 'Do'

        if not is_a_do_while:
            while_condition = self.expression()

        while_body = self.block()

        if is_a_do_while:
            if self.current_token.type != 'WHILE':
                self.throw_error('Expected a while condition')

            self.next_token()
            while_condition = self.expression()

            if self.current_token.type == 'SEMICOLON': self.next_token()

        return WhileStatement(while_condition, while_body, is_a_do_while)
    
    def return_statement(self):
        self.next_token()
        return ReturnStatement(self.expression())

    def function_declaration(self):
        self.next_token() # Consume 'func'
        identifier = self.current_token.value
        self.next_token()

        arguments = []
        if self.current_token.type != 'LPAREN':
            self.throw_error(f"Excpected a '(' symbol: {self.current_token}")

        if self.lexer.clone().token() != 'RPAREN':
            while self.current_token.type != 'RPAREN':
                self.next_token() # Consume '(' o ','
                
                arg_type = self.current_token.type
                self.next_token()
                arguments.append(
                    Argument(arg_type, self.current_token.value)
                )
                self.next_token()

        self.next_token() # Consume ')'
        return FunctionDeclaration(identifier, arguments, self.block())
    
    def function_call(self, identifier, from_obj = 'System'):
        arguments = []

        self.next_token() # Consume '('
        if self.current_token != 'RPAREN':
            while self.current_token and self.current_token.type != 'SEMICOLON':
                arguments.append(self.expression())
        else:
            self.next_token() # Consume ')'
        
        return FunctionCall(identifier, arguments, from_obj)
    
    def new_obj(self):
        self.next_token() # Consume 'new'
        if self.current_token.type in ['INT', 'FLOAT', 'BOOL', 'STRING']:
            self.next_token()
            if self.current_token.type == 'EMPTY_ARR':
                self.next_token()
                return []