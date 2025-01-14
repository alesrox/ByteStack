import sys
from syntax_tree import *

class Semantic:
    def __init__(self):
        self.types_register = [
            'INT', 'FLOAT', 'BOOL', 'STRING', '[]'
        ]

        self.table_type = {}

    def throw_error(self, result_type: str, expected_type: str):
        raise Exception(f'Cannot assign a {result_type} value to a {expected_type} Variable')

    def add_type(self, new_type):
        self.types_register.append(new_type)

    def add_table_type(self, key_name, value_type):
        if key_name in self.table_type:
            print(self.table_type)
            raise Exception(f'Variable {key_name} is already declareted')

        self.table_type[key_name] = value_type

    def check_declaration(self, variable, result_type: ExpressionNode):
        # expected_type = self.table_type[variable]
        # if isinstance(result_type, Literal):
        #     result_type = result_type.value_type.replace('_LITERAL', '')
        # elif isinstance(result_type, FunctionCall):
        #     result_type = self.table_type[result_type.identifier]
        # elif isinstance(result_type, NewCall):
        #     pass
        # elif isinstance(result_type, MemberAccess):
        #     pass
        # else: # BinaryExpression
        #     pass
        
        # if self.table_type[variable] != result_type: 
        #     self.throw_error(result_type, expected_type)

        return # TODO


    def check_assigment(self, expected_type, result_type):
        pass # TODO