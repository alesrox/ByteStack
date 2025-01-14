from syntax_tree import *
from tools import string_to_list
from utils import opcodes, built_in_funcs, operations, built_in_obj_funcs

class ByteCodeCompiler:
    def __init__(self):
        self.length = 0
        self.bytecode = []
        self.identifiers = {}
        self.locals = {}
        self.heap = []
        self.structs = {}
        self.table_type = {}

    def append_bytecode(self, instruction: tuple):
        self.bytecode.append(instruction)
        self.length += 1
    
    def generate_bytecode(self, ast, scope: bool = False):
        if isinstance(ast, BlockNode):
            for statement in ast.statements:
                self.add_instruction(statement, scope)

    def get_bytecode(self):
        return self.bytecode.copy()
    
    def throw_error(self, msg: str = None):
        raise Exception(f"Compilation Error: {msg}")
    
    def get_heap_location(self, node: MemberAccess) -> int:
        _info = node.identifier.object
        info = self.structs[self.table_type[_info][0]]

        i = self.table_type[_info][1] + 1 # STRUCT_POS_HEAP
        for attr in info[2][::-1]:
            if attr == node.identifier.attribute: break
            i += 1

        return i+1

    def add_instruction(self, node, scope: bool = False):
        if isinstance(node, BinaryExpression):
            self.add_instruction(node.left, scope)
            self.add_instruction(node.right, scope)
            self.append_bytecode((opcodes[operations[node.operator]], 0))
        elif isinstance(node, UnaryExpressionNode):
            if isinstance(node, Literal):
                if node.value_type == 'INT_LITERAL':
                    self.append_bytecode((opcodes["STORE"],  int(node.value)))
                if node.value_type == 'FLOAT_LITERAL':
                    self.append_bytecode((opcodes["STORE_FLOAT"], node.value))
                elif node.value_type == 'BOOL_LITERAL':
                    self.append_bytecode((opcodes["STORE"], 1 if node.value else 0))
                elif node.value_type == 'STRING_LITERAL':
                    string = string_to_list(node.value)
                    for char in string[::-1]:
                        self.append_bytecode((opcodes["STORE_CHAR"], char))
                elif node.value_type == '[]':
                    for item in node.value[::-1]:
                        self.add_instruction(item)
                    
                    self.append_bytecode((opcodes["BUILD_LIST"], len(node.value)))
                elif node.value_type == 'VARIABLE':
                    if node.value in self.identifiers:
                        self.append_bytecode((opcodes["LOAD"], self.identifiers[node.value]))
                    elif node.value in self.locals and scope:
                        self.append_bytecode((opcodes["LOAD_LOCAL"], self.locals[node.value]))
                    else:
                        self.throw_error(f"Undefined identifier: {node.value}")
            elif isinstance(node, FunctionCall):
                for arg in node.args:
                    self.add_instruction(arg, scope)

                if node.from_obj != 'System':
                    if scope and node.from_obj in self.locals:
                        self.append_bytecode((opcodes["LOAD_LOCAL"], self.locals[node.from_obj]))
                    else:
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
                    self.throw_error(node.identifier) # TODO: msg
            elif isinstance(node, NewCall):
                for arg in node.args:
                    self.heap.append(f"DATA-{node.struct}")
                    self.add_instruction(arg)

                self.append_bytecode((opcodes["NEW"], self.structs[node.struct][0]))
            elif isinstance(node, MemberAccess):
                if not node.list_access:
                    self.append_bytecode((opcodes["LOAD_HEAP"], self.get_heap_location(node)))
                else:
                    self.append_bytecode((opcodes["LOAD"], self.identifiers[node.object]))
                    self.append_bytecode((opcodes["LIST_ACCESS"], node.attribute))
            else:
                self.throw_error('UnaryExpressionNode') # TODO: msg

        elif isinstance(node, DeclarationNode):
            if isinstance(node, VariableDeclaration):
                if node.identifier not in self.identifiers:
                    if scope:
                        self.locals[node.identifier] = len(self.locals)
                    else:
                        self.identifiers[node.identifier] = len(self.identifiers)
                else:
                    self.throw_error() # TODO: msg
                
                if isinstance(node.initializer, NewCall):
                    self.table_type[node.identifier] = [node.initializer.struct, len(self.heap)]
                
                self.add_instruction(node.initializer, scope)
                self.append_bytecode((opcodes["STORE_LOCAL" if scope else "STORE_MEM"], -1))
            elif isinstance(node, FunctionDeclaration):
                func_pos = self.length + 2
                self.identifiers[node.identifier] = len(self.identifiers)
                self.append_bytecode((opcodes["STORE"], func_pos + 1))
                self.append_bytecode((opcodes["STORE_MEM"], -1))
                self.append_bytecode((0, 0)) # JUMP x

                for arg in node.parameters:
                    self.locals[arg.identifier] = len(self.locals)
                    self.append_bytecode((opcodes["STORE_LOCAL"], -1))
                
                self.generate_bytecode(node.body, True)

                self.locals = {}
                if self.bytecode[-1][0] != opcodes["RETURN"]:
                    self.append_bytecode((opcodes["RETURN"], 0))

                self.bytecode[func_pos] = ((opcodes["JUMP"], self.length))
            elif isinstance(node, ClassDeclaration):
                self.structs[node.identifier] = [
                    len(self.heap), len(node.attributes), [arg.identifier for arg in node.attributes]
                ]

                self.heap.append(f"OBJ-{node.identifier}")

                aux = {"int" : 1, "float" : 2, "array" : 4, "obj": 5}
                for arg in node.attributes:
                    if arg.type == "bool":
                        arg.type = "int"
                    elif arg.type == "string" or "[]" in arg.type:
                        arg.type = "array"
                    
                    if arg.type not in aux:
                        arg.type = "obj"
                    
                    self.heap.append(f"PARAM-{aux[arg.type]}-{node.identifier}")
                    self.append_bytecode((opcodes["STORE"], aux[arg.type]))
                
                self.append_bytecode((opcodes["DEFINE_TYPE"], len(node.attributes)))
            else:
                self.throw_error('DeclarationNode') # TODO: msg
        
        elif isinstance(node, AssignmentNode):
            self.add_instruction(node.value, scope)

            if isinstance(node.identifier, MemberAccess):
                if not node.identifier.list_access: # Struct
                    _info = node.identifier.object
                    info = self.structs[self.table_type[_info][0]]

                    i = self.table_type[_info][1] + 1 # STRUCT_POS_HEAP
                    for attr in info[2][::-1]:
                        if attr == node.identifier.attribute: break
                        i += 1
                    
                    self.append_bytecode((opcodes["STORE_HEAP"], i+1))
                else: # List access
                    list_set = []
                    identifier = node.identifier.object
                    while isinstance(identifier, MemberAccess) and identifier.list_access:
                        list_set.append(identifier.attribute)
                        identifier = identifier.object

                    if scope and identifier in self.locals:
                        self.append_bytecode((opcodes["LOAD_LOCAL"], self.locals[identifier]))
                    else:
                        self.append_bytecode((opcodes["LOAD"], self.identifiers[identifier]))
                    
                    for setter in list_set:
                        if isinstance(setter, Literal) and setter.value_type != 'VARIABLE':
                            self.append_bytecode((opcodes["LIST_ACCESS"], setter.value))
                        else:
                            self.add_instruction(setter, scope)
                            self.append_bytecode((opcodes["LIST_ACCESS"], -1))
                    
                    if isinstance(node.identifier.attribute, Literal) and node.identifier.attribute.value_type != "VARIABLE":
                        self.append_bytecode((opcodes["LIST_SET"], node.identifier.attribute.value))
                    else:
                        self.add_instruction(node.identifier.attribute, scope)
                        self.append_bytecode((opcodes["LIST_SET"], -1))
            elif scope and node.identifier in self.locals: 
                self.append_bytecode((opcodes["STORE_LOCAL"], self.locals[node.identifier]))
            else:
                self.append_bytecode((opcodes["STORE_MEM"], self.identifiers[node.identifier]))
        
        elif isinstance(node, IfStatement):
            self.append_bytecode((opcodes["CREATE_SCOPE"], 0))
            self.add_instruction(node.condition, True)
            if_instruction = self.length
            self.append_bytecode(["To replace IF"])

            elif_instructions = []
            for elif_statement in node.elif_statements:
                self.add_instruction(elif_statement.condition, True)
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
            
            if node.else_block:
                self.bytecode[else_instruction] = (opcodes["JUMP"], end_if_pos)

            for elif_instruction in elif_instructions:
                self.bytecode[elif_instruction] = (opcodes["JUMP"], end_if_pos)
            
            self.append_bytecode((opcodes["DEL_SCOPE"], 0))
            self.locals.clear()

        elif isinstance(node, WhileStatement):
            self.append_bytecode((opcodes["CREATE_SCOPE"], 0))
            while_condition = self.length
            self.add_instruction(node.condition, True)
            self.append_bytecode((opcodes["NOT"], 0))
            while_check = self.length
            self.append_bytecode((opcodes["JUMP_IF"]))
            self.generate_bytecode(node.body, True)
            self.append_bytecode((opcodes["JUMP"], while_condition))
            self.bytecode[while_check] = (self.bytecode[while_check], self.length)
            self.append_bytecode((opcodes["DEL_SCOPE"], 0))
            self.locals.clear()

        elif isinstance(node, ForStatement):
            self.append_bytecode((opcodes["CREATE_SCOPE"], 0))
            self.add_instruction(node.variable, True)
            for_condition = self.length
            self.add_instruction(node.condition, True)
            self.append_bytecode((opcodes["NOT"], 0))
            for_check = self.length
            self.append_bytecode((opcodes["JUMP_IF"]))
            self.generate_bytecode(node.body, True)
            self.append_bytecode((opcodes["LOAD_LOCAL"], self.locals[node.variable.identifier]))
            self.append_bytecode((opcodes["STORE"], 1))
            self.append_bytecode((opcodes["ADD"], 0))
            self.append_bytecode((opcodes["STORE_LOCAL"], self.locals[node.variable.identifier]))
            self.append_bytecode((opcodes["JUMP"], for_condition))
            self.bytecode[for_check] = (self.bytecode[for_check], self.length)
            self.append_bytecode((opcodes["DEL_SCOPE"], 0))
            self.locals.clear()
        
        elif isinstance(node, ReturnStatement):
            self.add_instruction(node.expression, True)
            self.append_bytecode((opcodes["RETURN"], 0))
            self.locals.clear()

        elif isinstance(node, BreakStatement):
            pass # TODO

        elif isinstance(node, ContinueStatement):
            pass # TODO
