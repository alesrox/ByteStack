from syntax_tree import *
from tools import string_to_list
from utils import opcodes, built_in_funcs, operations, built_in_obj_funcs

class ByteCodeCompiler:
    def __init__(self):
        self.length = 0
        self.bytecode = []

        self.identifiers = {}
        self.heap = []
        self.structs = {}
        self.table_type = {}

        self.b_c_statement = [0, '']
        self.in_loop = True

    def append_bytecode(self, instruction: tuple):
        self.bytecode.append(instruction)
        self.length += 1
    
    def generate_bytecode(self, ast: BlockNode):
        for statement in ast.statements:
            self.add_instructions(statement)

    def get_bytecode(self):
        return self.bytecode.copy()
    
    def get_heap_relative_location(self, from_object: str, attribute: str) -> int:
        _info = from_object
        info = self.structs[self.table_type[_info]]

        i = 1 # STRUCT_POS_HEAP
        for attr in info[2][::-1]:
            if attr == attribute: break
            i += 1

        return i

    def add_instructions(self, node: ASTNode):
        if isinstance(node, BinaryExpression):
            self.add_instructions(node.right)
            self.add_instructions(node.left)
            self.append_bytecode((opcodes[operations[node.operator]], 0))
        elif isinstance(node, UnaryExpressionNode):
            if isinstance(node, Literal):
                if node.value_type == 'INT_LITERAL':
                    self.append_bytecode((opcodes["STORE"],  int(node.value)))
                elif node.value_type == 'FLOAT_LITERAL':
                    self.append_bytecode((opcodes["STORE_FLOAT"], node.value))
                elif node.value_type == 'BOOL_LITERAL':
                    self.append_bytecode((opcodes["STORE"], 1 if node.value else 0))
                elif node.value_type == 'STRING_LITERAL':
                    string = string_to_list(node.value)
                    for char in string[::-1]:
                        self.append_bytecode((opcodes["STORE_CHAR"], char))
                    
                    self.append_bytecode((opcodes["BUILD_STR"], len(string)))
                elif '[]' in node.value_type:
                    for item in node.value[::-1]:
                        self.add_instructions(item)
                    
                    self.append_bytecode((opcodes["BUILD_LIST"], len(node.value)))
                elif node.value_type == 'VARIABLE':
                    self.append_bytecode((opcodes["LOAD"], self.identifiers[node.value]))
                else:
                    raise Exception(f"Literal Node uncontrolled: {node.to_dict()}")

            elif isinstance(node, FunctionCall):
                for arg in node.args:
                    self.add_instructions(arg)

                if node.from_obj in self.table_type:
                    self.append_bytecode((opcodes["LOAD"], self.identifiers[node.from_obj]))

                    self.append_bytecode((opcodes["LOAD_HEAP"], self.get_heap_relative_location(node.from_obj, node.identifier)))
                    self.append_bytecode((opcodes["CALL"], -1))
                else:
                    if node.from_obj != 'System':
                        self.append_bytecode((opcodes["LOAD"], self.identifiers[node.from_obj]))

                    if node.identifier in built_in_funcs:
                        opcode = opcodes["SYSCALL"]
                        input_funcs = built_in_funcs
                    else:
                        opcode = opcodes["OBJCALL"]
                        input_funcs = built_in_obj_funcs

                    if node.identifier in input_funcs:
                        self.append_bytecode((opcode, input_funcs[node.identifier]))
                    elif node.identifier in self.identifiers:
                        self.append_bytecode((opcodes["CALL"], self.identifiers[node.identifier]))
                    else: 
                        raise Exception(f"Unfound identifier '{node.identifier}'\nIdentifiers: {self.identifiers}")
            elif isinstance(node, NewCall):
                for arg in node.args:
                    self.heap.append(f"DATA-{node.struct}")
                    self.add_instructions(arg)

                self.append_bytecode((opcodes["NEW"], self.structs[node.struct][0]))
            elif isinstance(node, MemberAccess):
                if not node.list_access:
                    self.append_bytecode((opcodes["LOAD"], self.identifiers[node.object]))
                    self.append_bytecode((opcodes["LOAD_HEAP"], self.get_heap_relative_location(node.object, node.attribute)))
                else:
                    self.append_bytecode((opcodes["LOAD"], self.identifiers[node.object]))
                    self.append_bytecode((opcodes["LIST_ACCESS"], node.attribute))
            elif isinstance(node, CastingExpression):
                cast_argument = 0 if node.new_type == 'BOOL' else 1 if node.new_type == 'INT' else 2
                self.add_instructions(node.expression)
                self.append_bytecode((opcodes['CAST'], cast_argument))
            else:
                raise Exception(f"UnaryExpressionNode uncontrolled: {node.to_dict()}")

        elif isinstance(node, DeclarationNode):
            if isinstance(node, VariableDeclaration):
                self.identifiers[node.identifier] = len(self.identifiers)
                
                if isinstance(node.initializer, NewCall):
                    self.table_type[node.identifier] = node.initializer.struct
                
                if node.initializer == None:
                    instruction = 'BUILD_STR' if node.var_type == 'STRING' else 'STORE'
                    if '[]' in node.var_type: instruction = 'BUILD_LIST'
                    
                    self.append_bytecode((opcodes[instruction], 0))
                else:
                    self.add_instructions(node.initializer)

                self.append_bytecode((opcodes["STORE_MEM"], -1))
            elif isinstance(node, FunctionDeclaration):
                func_pos = self.length
                self.identifiers[node.identifier] = len(self.identifiers)
                self.append_bytecode((0, 0)) # STORE func_start_pos
                self.append_bytecode((opcodes["STORE_MEM"], -1))

                for arg in node.parameters:
                    if arg.type in self.structs: 
                        self.table_type[f'{node.identifier}.{arg.identifier}'] = arg.type

                    self.identifiers[f'{node.identifier}.{arg.identifier}'] = len(self.identifiers)
                    self.append_bytecode((opcodes["STORE"], 0))
                    self.append_bytecode((opcodes["STORE_MEM"], -1))
                
                jump_pos = self.length
                self.append_bytecode((0, 0)) # JUMP x

                self.bytecode[func_pos] = (opcodes["STORE"], self.length)

                for arg in node.parameters:
                    self.append_bytecode((opcodes["STORE_MEM"], self.identifiers[f'{node.identifier}.{arg.identifier}']))

                self.generate_bytecode(node.body)

                if self.bytecode[-1][0] != opcodes["RETURN"]:
                    self.append_bytecode((opcodes["RETURN"], 0))

                self.bytecode[jump_pos] = ((opcodes["JUMP"], self.length))
            elif isinstance(node, ClassDeclaration):
                self.structs[node.identifier] = [
                    len(self.heap), len(node.attributes), [arg.identifier for arg in node.attributes]
                ]

                self.heap.append(f"OBJ-{node.identifier}")

                aux = {"INT" : 1, "FLOAT" : 2, "ARRAY" : 4, "OBJ": 5}
                for arg in node.attributes:
                    if arg.type == "BOOL":
                        arg.type = "INT"
                    elif arg.type == "STRING" or "[]" in arg.type:
                        arg.type = "ARRAY"
                    
                    if arg.type not in aux:
                        arg.type = "OBJ"
                    
                    self.heap.append(f"PARAM-{aux[arg.type]}-{node.identifier}")
                    self.append_bytecode((opcodes["STORE"], aux[arg.type]))
                
                self.append_bytecode((opcodes["DEFINE_TYPE"], len(node.attributes)))
            else:
                raise Exception(f'DeclarationNode uncontrolled: {node.to_dict()}')
        
        elif isinstance(node, AssignmentNode):
            self.add_instructions(node.value)

            if isinstance(node.identifier, MemberAccess):
                if not node.identifier.list_access: # Struct
                    self.append_bytecode((opcodes["LOAD"], self.identifiers[node.identifier.object]))
                    self.append_bytecode((opcodes["STORE_HEAP"], self.get_heap_relative_location(node.identifier.object, node.identifier.attribute)))
                else: # List access
                    list_set = []
                    identifier = node.identifier.object
                    while isinstance(identifier, MemberAccess) and identifier.list_access:
                        list_set.append(identifier.attribute)
                        identifier = identifier.object

                    self.append_bytecode((opcodes["LOAD"], self.identifiers[identifier]))
                    
                    for setter in list_set:
                        if isinstance(setter, Literal) and setter.value_type != 'VARIABLE':
                            self.append_bytecode((opcodes["LIST_ACCESS"], setter.value))
                        else:
                            self.add_instructions(setter)
                            self.append_bytecode((opcodes["LIST_ACCESS"], -1))
                    
                    if isinstance(node.identifier.attribute, Literal) and node.identifier.attribute.value_type != "VARIABLE":
                        self.append_bytecode((opcodes["LIST_SET"], node.identifier.attribute.value))
                    else:
                        self.add_instructions(node.identifier.attribute)
                        self.append_bytecode((opcodes["LIST_SET"], -1))
            else:
                self.append_bytecode((opcodes["STORE_MEM"], self.identifiers[node.identifier]))
        
        elif isinstance(node, IfStatement):
            self.add_instructions(node.condition)
            # self.append_bytecode((opcodes["CREATE_SCOPE"], 0))
            if_instruction = self.length
            self.append_bytecode(["To replace IF"])

            elif_instructions = []
            for elif_statement in node.elif_statements:
                self.add_instructions(elif_statement.condition)
                elif_instructions.append(self.length)
                self.append_bytecode(["To replace ELIF START"])
            
            if node.else_block:
                self.generate_bytecode(node.else_block)

            self.append_bytecode(["To replace ELSE"])
    
            else_instruction = self.length - 1
            for i in range(len(elif_instructions)):
                self.generate_bytecode(node.elif_statements[i].then_block)
                ins = self.length
                self.bytecode[elif_instructions[i]] = (opcodes["JUMP_IF"], ins)
                elif_instructions[i] = self.length
                self.append_bytecode(["To replace ELIF END"])
    
            self.bytecode[if_instruction] = (opcodes["JUMP_IF"], self.length)
            self.generate_bytecode(node.then_block)
            end_if_pos = self.length
            
            self.bytecode[else_instruction] = (opcodes["JUMP"], end_if_pos)

            for elif_instruction in elif_instructions:
                self.bytecode[elif_instruction] = (opcodes["JUMP"], end_if_pos)

        elif isinstance(node, WhileStatement):
            self.in_loop = True
            # self.append_bytecode((opcodes["CREATE_SCOPE"], 0))
            while_condition = self.length
            self.loop_condition = while_condition
            self.add_instructions(node.condition)
            self.append_bytecode((opcodes["NOT"], 0))
            while_check = self.length
            self.append_bytecode((opcodes["JUMP_IF"]))
            self.generate_bytecode(node.body)

            if 'Continue' in self.b_c_statement: 
                self.bytecode[self.b_c_statement[0]] = (opcodes["JUMP"], self.length)
                self.b_c_statement = [0, '']

            self.append_bytecode((opcodes["JUMP"], while_condition))
            self.bytecode[while_check] = (self.bytecode[while_check], self.length)

            if 'Break' in self.b_c_statement: 
                self.bytecode[self.b_c_statement[0]] = (opcodes["JUMP"], self.length)
                self.b_c_statement = [0, '']

            self.in_loop = False

        elif isinstance(node, ForStatement):
            self.in_loop = True
            # self.append_bytecode((opcodes["CREATE_SCOPE"], 0))
            self.add_instructions(node.variable)
            for_condition = self.length
            self.loop_condition = for_condition
            self.add_instructions(node.condition)
            self.append_bytecode((opcodes["NOT"], 0))
            for_check = self.length
            self.append_bytecode((opcodes["JUMP_IF"]))
            self.generate_bytecode(node.body)

            if 'Continue' in self.b_c_statement: 
                self.bytecode[self.b_c_statement[0]] = (opcodes["JUMP"], self.length)
                self.b_c_statement = [0, '']

            self.append_bytecode((opcodes["LOAD"], self.identifiers[node.variable.identifier]))
            self.append_bytecode((opcodes["STORE"], 1))
            self.append_bytecode((opcodes["ADD"], 0))
            self.append_bytecode((opcodes["STORE_MEM"], self.identifiers[node.variable.identifier]))
            self.append_bytecode((opcodes["JUMP"], for_condition))
            self.bytecode[for_check] = (self.bytecode[for_check], self.length)

            if 'Break' in self.b_c_statement: 
                self.bytecode[self.b_c_statement[0]] = (opcodes["JUMP"], self.length)
                self.b_c_statement = [0, '']

            self.in_loop = False
        
        elif isinstance(node, ReturnStatement):
            self.add_instructions(node.expression)
            self.append_bytecode((opcodes["RETURN"], 0))

        elif isinstance(node, BreakStatement):
            if self.in_loop:
                self.b_c_statement = [self.length, 'Break']
                self.append_bytecode(0)

        elif isinstance(node, ContinueStatement):
            if self.in_loop:
                self.b_c_statement = [self.length, 'Continue']
                self.append_bytecode(0)
        else:
            raise Exception(f"ASTNode uncontrolled: {self.node.to_dict()}")
