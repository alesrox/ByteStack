import copy
import utils.utils as utils
from utils.syntax_tree import *
from utils.error import SemanticError

operations = {
    '+': "add", '-': "substract", '*': "multiply", '/': "divide", '%': "modulize",
}

class Semantic:
    def __init__(self):
        self.lineno = 0
        self.context = 'MAIN'
        self.context_history = []
        self.non_named_contexts = 0

        self.primitive_types = [
            'INT', 'BYTE', 'FLOAT', 'BOOL', 'STRING',
        ]

        self.non_primitive_types = ['[]']
        self.table_type = {
            'exit'      : 'VOID',
            'print'     : 'VOID',
            'input'     : 'INT',
            'getf'      : 'FLOAT',
            'type'      : 'STRING',
            'scan'      : 'STRING',
            'read'      : '[]',
            'write'     : 'VOID',
            'append'    : 'VOID',
            'size'      : 'INT',
            'remove'    : 'VOID',
            'pop'       : 'VOID',
            'is_empty'  : 'BOOL',
            'slice'     : '[]',
            'map'       : '[]',
            'filter'    : '[]',
            'min'       : 'FLOAT',
            'max'       : 'FLOAT',
            'lower'     : 'STRING',
            'upper'     : 'STRING',
            'toString'  : 'STRING',
        }
        self.functions = {}
        self.structs = {}

    def clone(self):
        return copy.deepcopy(self)
    
    def new_no_named_context(self):
        self.non_named_contexts += 1
        self.context_history.insert(0, self.context)
        self.context = f'{self.context}.{self.non_named_contexts}'
    
    def change_context(self, context_name):
        self.context_history.insert(0, self.context)
        self.context = context_name
    
    def return_context(self):
        self.context = 'MAIN' if not self.context_history else self.context_history.pop(0)

    def throw_error(self, result_type: str, expected_type: str):
        raise SemanticError(f'Type mismatch: Cannot assign a {result_type} value to a {expected_type} variable', self.lineno)
    
    def is_a_type(self, to_check_type: str) -> bool:
        return to_check_type in self.primitive_types or to_check_type in self.non_primitive_types

    def add_new_type(self, new_type, args_type):
        if new_type in self.structs:
            raise SemanticError(f'TypeError: Struct {new_type} is already declared', self.lineno)

        self.non_primitive_types.append(new_type)
        self.structs[new_type] = {}

        for arg_type in args_type: 
            self.structs[new_type][arg_type.identifier] = arg_type.type

    def add_new_func(self, func_name, return_type, args):
        if func_name in self.table_type:
            raise SemanticError(f'NameError: Variable {func_name} is already declared', self.lineno)

        self.table_type[func_name] = return_type
        self.functions[func_name] = [arg.type for arg in args]

        func_context = func_name + '.'
        for arg in args:
            self.table_type[func_context + arg.identifier] = arg.type

    def add_table_type(self, key_name, value_type):
        complete_name = self.context + '.' + key_name if self.context != 'MAIN' else key_name
        if complete_name in self.table_type:
            raise SemanticError(f'NameError: Variable {key_name} is already declared', self.lineno)

        self.table_type[complete_name] = value_type
    
    def literal_casting(self, expected_type: str, result: Literal) -> any:
        match expected_type:
            case 'BOOL':
                return bool(result.value)
            case 'INT':
                return int(result.value)
            case 'BYTE':
                return max(-128, min(127, result.value))
            case 'FLOAT':
                return float(result.value)
            case 'STRING':
                return str(result.value)

        raise TypeError(f"Expected a {expected_type} but {result.value_type} given")
    
    def implicit_casting(self, expected_type: str, result_type: str) -> bool:
        same_type = expected_type == result_type
        expected_primitive = expected_type in self.primitive_types
        result_primitive = result_type in self.primitive_types[0:-1]
        
        return not same_type and expected_primitive and result_primitive
    
    def get_unary_type(self, expr: UnaryExpressionNode):
        if isinstance(expr, Literal):
            if expr.value_type != 'VARIABLE':
                return expr.value_type.replace('_LITERAL', '')
            
            return self.get_var_type(expr.value)
        elif isinstance(expr, FunctionCall):
            return self.table_type[expr.identifier]
        elif isinstance(expr, MemberAccess):
            if expr.list_access:
                list_id = expr.object
                num_access = 1
                while True:
                    if isinstance(list_id, MemberAccess):
                        list_id = list_id.object
                        num_access += 1
                    else:
                        return self.get_var_type(list_id).replace('[]', '', num_access)
            else:
                return self.structs[self.get_var_type(expr.object)][expr.attribute]
        elif isinstance(expr, NewCall):
            return expr.struct

        return None

    def get_binary_type(self, operation: BinaryExpression):
        left = self.get_type(operation.left)
        right = self.get_type(operation.right)
        operator = operation.operator

        op_verb = 'make logic operations with a' if operator not in operations else operations[operator]
        if left not in self.primitive_types: 
            raise SemanticError(
                f'TypeError: Cannot {op_verb} {left} struct with {right} {"type" if right in self.primitive_types else "struct"}',
                self.lineno
            )
        elif right not in self.primitive_types: 
            raise SemanticError(
                f'TypeError: Cannot {op_verb} {left} {"type" if left in self.primitive_types else "struct"} with {right} struct', 
                self.lineno
            )

        if left == right: return left

        if (left == 'STRING') ^ (right == 'STRING'):
            if operator == '+':
                return 'STRING'
            else:
                raise SemanticError(f'TypeError: Cannot {op_verb} {left} type with {right} type', self.lineno)
        
        if operator == '/': return 'FLOAT'

        if operator in ['+', '-', '*', '%', '^']:
            if (left == 'FLOAT') ^ (right == 'LEFT'):
                return 'FLOAT'
            else:
                return 'INT'
        else:
            return 'BOOL'
        
    def get_var_type(self, var_name):
        if var_name in self.table_type: return self.table_type[var_name]

        complete_name = self.context + '.' + var_name
        if complete_name in self.table_type:
            return self.table_type[complete_name]
        else:
            scopes = self.context.split('.')[::-1]
            for scope in scopes:
                complete_name = complete_name.replace(scope + '.', '', 1)
                if complete_name in self.table_type:
                    return self.table_type[complete_name]
            
            raise SemanticError(f"NameError: Undefined variable '{var_name}'", self.lineno)
        
    def get_type(self, expression: ExpressionNode):
        if isinstance(expression, UnaryExpressionNode):
            return self.get_unary_type(expression)
        elif isinstance(expression, BinaryExpression):
            return self.get_binary_type(expression)
        
        return None
    
    def get_list_type(self, literal_list: list):
        sub_type = None
        matrix_order = ''

        if literal_list == []: return '[]'
        first_element = True
        for element in literal_list:
            pre_sub_type = sub_type
            if isinstance(element, BinaryExpression):
                sub_type = self.get_binary_type(element)
            elif isinstance(element.value, list):
                if first_element: matrix_order += '[]'
                sub_type = self.get_list_type(element.value)
            else:
                sub_type = self.get_type(element)

            if pre_sub_type == '[]': pre_sub_type = sub_type
            if pre_sub_type != None and pre_sub_type != sub_type:
                raise SemanticError(f'Type mismatch: Cannot insert a value of type {sub_type} into a {pre_sub_type} list', self.lineno)

            first_element = False
        
        if matrix_order == '': matrix_order = '[]'
        return f'{sub_type}{matrix_order}'
    
    def check_list_types(self, expected_type, list_type):
        if '[]' not in expected_type and expected_type != 'STRING':
            self.throw_error(list_type, expected_type)
        
        # list_type = self.get_list_type(list_value)
        is_empty_list = '[]' * list_type.count('[]') == list_type
        if is_empty_list: return expected_type
        if expected_type != list_type:
            self.throw_error(list_type, expected_type)
        
        return expected_type

    def check_types_assigment(self, variable, result: ExpressionNode): # JEJE
        expected_type = self.get_var_type(variable) if isinstance(variable, str) else self.get_type(variable)
        result_type = self.get_type(result)
        
        if '[]' in result_type:
            list_type = None
            if isinstance(result, FunctionCall):
                list_type = result_type
            else:
                list_type = self.get_list_type(result.value)

            result_type = self.check_list_types(expected_type, list_type)
        elif isinstance(result, Literal):
            if self.implicit_casting(expected_type, result_type):
                new_value = self.literal_casting(expected_type, result)
                result = Literal(expected_type + '_LITERAL', new_value)
            elif expected_type != result_type:
                self.throw_error(result_type, expected_type)
        
        if self.implicit_casting(expected_type, result_type):
            return CastingExpression(expected_type, result)
        elif expected_type != result_type:
            self.throw_error(result_type, expected_type)
    
        return result
    
    def check_function_call(self, func_name, arguments):
        if func_name in utils.built_in_funcs or func_name in utils.built_in_obj_funcs:
            return arguments # TODO

        expected_num_args = len(self.functions[func_name])
        if len(arguments) > expected_num_args:
            raise SemanticError(f"TypeError: Too many arguments provided. Expected {expected_num_args}, but got {len(arguments)}", self.lineno)
        elif len(arguments) < expected_num_args:
            raise SemanticError(f"TypeError: Too few arguments provided. Expected {expected_num_args}, but got {len(arguments)}", self.lineno)

        new_arguments = []
        for i in range(expected_num_args):
            arg_type = self.get_type(arguments[i])
            if self.functions[func_name][i] != arg_type:
                if self.implicit_casting(self.functions[func_name][i], arg_type):
                    arguments[i] = CastingExpression(self.functions[func_name][i], arguments[i])
                else:
                    msg_part1 = f"TypeError: Argument of '{func_name}' function has an invalid type. "
                    msg_part2 = f"Expected {self.functions[func_name][i]} value, but got {arg_type} value"
                    raise SemanticError(msg_part1 + msg_part2, self.lineno)
            
            new_arguments.append(arguments[i])
        
        return new_arguments
