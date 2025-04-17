from utils.syntax_tree import *

def pretty_print(data, indent=0):
    spaces = ' ' * indent
    if isinstance(data, dict):
        if data == '{}':
            print('{}')
        else:
            print("{")
            for key, value in data.items():
                print(f"{spaces}    {key}: ", end="")
                if isinstance(value, ASTNode):
                    pretty_print(value.to_dict(), indent + 4)
                else:
                    pretty_print(value, indent + 4)
            print(f"{spaces}}}")
    elif isinstance(data, list):
        if data != []:
            print("[")
            for item in data:
                print(f"{spaces}    ", end="")
                if isinstance(item, ASTNode):
                    pretty_print(item.to_dict(), indent + 4)
                else:
                    pretty_print(item, indent + 4)
            print(f"{spaces}]")
        else:
            print("[]")
    else:
        print(data)

def get_key(obj_dict: dict, element):
    for key, value in obj_dict.items():
        if value == element:
            return key
    
    return None

# TODO: Deprecated, delete after checkout
# def string_to_list(string: str) -> list:
#     list_from_string = []
#     string = string.replace('\\n', '\n')
#     string = string.replace('\\t', '\t')

#     string += '\0' * (-len(string) % 4)

#     for i in range(0, len(string), 4):
#         block = string[i:i + 4]
#         packed = 0
#         for j, char in enumerate(reversed(block)):
#             packed |= ord(char) << (24 - j * 8)
#         list_from_string.append(packed)

#     return list_from_string

def name(func_name: str, args: list, original: str):
    if original in args:
        return f'{func_name}.{original}'

    return original

def module(func_name: str, arguments: list[ParameterNode], ast_node: ASTNode):
    if isinstance(ast_node, BlockNode):
        statements = []
        for ast in ast_node.statements:
            statements.append(module(func_name, arguments, ast))

        ast_node.statements = statements
    elif isinstance(ast_node, BinaryExpression):
        ast_node.left = module(func_name, arguments, ast_node.left)
        ast_node.right = module(func_name, arguments, ast_node.right)
    elif isinstance(ast_node, Literal):
        ast_node.value = name(func_name, arguments, ast_node.value)
    elif isinstance(ast_node, FunctionCall):
        ast_node.identifier = name(func_name, arguments, ast_node.identifier)
        ast_node.from_obj = name(func_name, arguments, ast_node.from_obj)
        args = []
        for arg in ast_node.args:
            args.append(module(func_name, arguments, arg))
        
        ast_node.args = args
    elif isinstance(ast_node, NewCall):
        args = []
        for arg in ast_node.args:
            args.append(module(func_name, arguments, arg))
        
        ast_node.args = args
    elif isinstance(ast_node, MemberAccess):
        ast_node.object = name(func_name, arguments, ast_node.object)
        ast_node.attribute = module(func_name, arguments, ast_node.attribute)
    elif isinstance(ast_node, CastingExpression):
        ast_node.expression = module(func_name, arguments, ast_node.expression)
    elif isinstance(ast_node, VariableDeclaration):
        ast_node.initializer = module(func_name, arguments, ast_node.initializer)
    elif isinstance(ast_node, AssignmentNode):
        ast_node.identifier = name(func_name, arguments, ast_node.identifier)
    elif isinstance(ast_node, IfStatement):
        ast_node.condition = module(func_name, arguments, ast_node.condition)
        ast_node.then_block = module(func_name, arguments, ast_node.then_block)
        ast_node.else_block = module(func_name, arguments, ast_node.else_block)
        elifs = []
        for item in ast_node.elif_statements:
            elifs.append(module(func_name, arguments, item))
        
        ast_node.elif_statements = elifs
    elif isinstance(ast_node, WhileStatement):
        ast_node.condition = module(func_name, arguments, ast_node.condition)
        ast_node.body = module(func_name, arguments, ast_node.body)
    elif isinstance(ast_node, ForStatement):
        ast_node.body = module(func_name, arguments, ast_node.body)
        ast_node.condition = module(func_name, arguments, ast_node.condition)
        ast_node.variable = name(func_name, arguments, ast_node.variable)
    elif isinstance(ast_node, ReturnStatement):
        ast_node.expression = module(func_name, arguments, ast_node.expression)

    return ast_node