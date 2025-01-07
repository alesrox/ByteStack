from utils import *
from syntax_tree import *
from tools import string_to_list

class ByteCodeCompiler:
    def __init__(self):
        self.length = 0
        self.bytecode = []
        self.identifiers = {}
        self.locals = {}
        self.structs = {}
        self.table_type = {}

    def append_bytecode(self, instruction: tuple):
        self.bytecode.append(instruction)
        self.length += 1

    def generate_bytecode(self, ast, scope: bool = False):
        if isinstance(ast, Program):
            for statement in ast.statements:
                self.add_instruction(statement, scope)

    def throw_error(self, msg: str):
        print(f"Compilation Error: {msg}")
        exit()

    def add_instruction(self, node, scope: bool = False):
        if isinstance(node, Declaration):
            if node.identifier not in self.identifiers:
                if scope:
                    self.locals[node.identifier] = len(self.locals)
                else:
                    self.identifiers[node.identifier] = len(self.identifiers)

            if isinstance(node.value, NewStatement):
                self.identifiers[node.identifier] += self.structs[node.value.obj][1]
                self.table_type[node.identifier] = node.value.obj

            self.add_instruction(node.value, scope)
            self.append_bytecode((bytecode_instructions["STORE_LOCAL" if scope else "STORE_MEM"], -1))
        elif isinstance(node, Assignment):
            self.add_instruction(node.value, scope)

            if isinstance(node.identifier, Attribute):
                _info = node.identifier.from_obj
                info = self.structs[self.table_type[_info]]
                i = 1
                for attr in info[2]:
                    if attr == node.identifier.identifier: break
                    i += 1
                
                self.append_bytecode((bytecode_instructions["STORE_MEM"], self.identifiers[_info] - i))
            elif isinstance(node.identifier, ListNode):
                list_set = []
                identifier = node.identifier.identifier
                while isinstance(identifier, ListNode):
                    list_set.append(identifier.index)
                    identifier = identifier.identifier

                if scope and identifier in self.locals:
                    self.append_bytecode((bytecode_instructions["LOAD_LOCAL"], self.locals[identifier]))
                else:
                    self.append_bytecode((bytecode_instructions["LOAD"], self.identifiers[identifier]))
                
                for setter in list_set:
                    if isinstance(setter, Expression) and setter.value_type != "IDENTIFIER":
                        self.append_bytecode((bytecode_instructions["LIST_ACCESS"], setter.value))
                    else:
                        self.add_instruction(setter, scope)
                        self.append_bytecode((bytecode_instructions["LIST_ACCESS"], -1))
                
                if isinstance(node.identifier.index, Expression) and node.identifier.index.value_type != "IDENTIFIER":
                    self.append_bytecode((bytecode_instructions["LIST_SET"], node.identifier.index.value))
                else:
                    self.add_instruction(node.identifier.index, scope)
                    self.append_bytecode((bytecode_instructions["LIST_SET"], -1))
            elif scope and node.identifier in self.locals: 
                self.append_bytecode((bytecode_instructions["STORE_LOCAL"], self.locals[node.identifier]))
            else:
                self.append_bytecode((bytecode_instructions["STORE_MEM"], self.identifiers[node.identifier]))
        elif isinstance(node, BinaryExpression):
            self.add_instruction(node.left, scope)
            self.add_instruction(node.right, scope)
            self.append_bytecode((bytecode_instructions[operations[node.operator]], 0))
        elif isinstance(node, Expression):
            if node.value_type == 'NUMBER':
                self.append_bytecode((bytecode_instructions["STORE"],  int(node.value)))
            if node.value_type == 'FLOAT_LITERAL':
                self.append_bytecode((bytecode_instructions["STORE_FLOAT"], node.value))
            elif node.value_type == 'BOOL_LITERAL':
                self.append_bytecode((bytecode_instructions["STORE"], 1 if node.value else 0))
            elif node.value_type == 'STRING_LITERAL':
                string = string_to_list(node.value)
                for char in string[::-1]:
                    self.append_bytecode((bytecode_instructions["STORE_CHAR"], char))

                self.append_bytecode((bytecode_instructions["BUILD_STR"], len(string)))
            elif node.value_type == 'IDENTIFIER':
                if isinstance(node.value, FunctionCall):
                    self.add_instruction(node.value, scope)
                elif isinstance(node.value, Attribute):
                    info = node.value.from_obj
                    info = self.structs[self.table_type[info]]
                    i = 0
                    for attr in info[2]:
                        if attr == node.value.identifier: break
                        i += 1

                    self.append_bytecode((bytecode_instructions["LOAD"], self.identifiers[node.value.from_obj]))
                    self.append_bytecode((bytecode_instructions["OBJCALL"], i))
                elif node.value in self.identifiers:
                    self.append_bytecode((bytecode_instructions["LOAD"], self.identifiers[node.value]))
                elif node.value in self.locals and scope:
                    self.append_bytecode((bytecode_instructions["LOAD_LOCAL"], self.locals[node.value]))
                else:
                    self.throw_error(f"Undefined identifier: {node.value}")
        elif isinstance(node, IfStatement):
            self.append_bytecode((bytecode_instructions["CREATE_SCOPE"], 0))
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
                self.generate_bytecode(node.elif_statements[i].true_block)
                ins = self.length
                self.bytecode[elif_instructions[i]] = (bytecode_instructions["JUMP_IF"], ins)
                elif_instructions[i] = self.length
                self.append_bytecode(["To replace ELIF END"])
    
            self.bytecode[if_instruction] = (bytecode_instructions["JUMP_IF"], self.length)
            self.generate_bytecode(node.true_block)
            end_if_pos = self.length
            
            if node.else_block:
                self.bytecode[else_instruction] = (bytecode_instructions["JUMP"], end_if_pos)

            for elif_instruction in elif_instructions:
                self.bytecode[elif_instruction] = (bytecode_instructions["JUMP"], end_if_pos)
            
            self.append_bytecode((bytecode_instructions["DEL_SCOPE"], 0))
            self.locals.clear()
        elif isinstance(node, ForStatement):
            self.append_bytecode((bytecode_instructions["CREATE_SCOPE"], 0))
            self.add_instruction(node.var, True)
            for_condition = self.length
            self.add_instruction(node.condition, True)
            self.append_bytecode((bytecode_instructions["NOT"], 0))
            for_check = self.length
            self.append_bytecode((bytecode_instructions["JUMP_IF"]))
            self.generate_bytecode(node.block, True)
            self.append_bytecode((bytecode_instructions["LOAD_LOCAL"], self.locals[node.var.identifier]))
            self.append_bytecode((bytecode_instructions["STORE"], 1))
            self.append_bytecode((bytecode_instructions["ADD"], 0))
            self.append_bytecode((bytecode_instructions["STORE_LOCAL"], self.locals[node.var.identifier]))
            self.append_bytecode((bytecode_instructions["JUMP"], for_condition))
            self.bytecode[for_check] = (self.bytecode[for_check], self.length)
            self.append_bytecode((bytecode_instructions["DEL_SCOPE"], 0))
            self.locals.clear()
        elif isinstance(node, WhileStatement):
            self.append_bytecode((bytecode_instructions["CREATE_SCOPE"], 0))
            while_condition = self.length
            self.add_instruction(node.condition, True)
            self.append_bytecode((bytecode_instructions["NOT"], 0))
            while_check = self.length
            self.append_bytecode((bytecode_instructions["JUMP_IF"]))
            self.generate_bytecode(node.block, True)
            self.append_bytecode((bytecode_instructions["JUMP"], while_condition))
            self.bytecode[while_check] = (self.bytecode[while_check], self.length)
            self.append_bytecode((bytecode_instructions["DEL_SCOPE"], 0))
            self.locals.clear()
        elif isinstance(node, FunctionDeclaration):
            self.append_bytecode((bytecode_instructions["STORE"], self.length+3))
            self.append_bytecode((bytecode_instructions["STORE_MEM"], -1))
            func_pos = self.length
            self.identifiers[node.identifier] = len(self.identifiers)
            self.append_bytecode((0, 0)) # JUMP x

            for arg in node.args:
                self.locals[arg.identifier] = len(self.locals)
                self.append_bytecode((bytecode_instructions["STORE_LOCAL"], -1))
            
            self.generate_bytecode(node.block, True)
            self.locals = {}
            if self.bytecode[-1] != (bytecode_instructions["RETURN"], 0):
                self.append_bytecode((bytecode_instructions["RETURN"], 0))
            self.bytecode[func_pos] = ((bytecode_instructions["JUMP"], self.length))
        elif isinstance(node, ReturnStatement):
            self.add_instruction(node.value, True)
            self.append_bytecode((bytecode_instructions["RETURN"], 0))
            self.locals.clear()
        elif isinstance(node, FunctionCall):
            for arg in node.args:
                self.add_instruction(arg, scope)

            if node.from_obj != 'System':
                if scope and node.from_obj in self.locals:
                    self.append_bytecode((bytecode_instructions["LOAD_LOCAL"], self.locals[node.from_obj]))
                else:
                    self.append_bytecode((bytecode_instructions["LOAD"], self.identifiers[node.from_obj]))
            
            if node.identifier in built_in_funcs:
                opcode = bytecode_instructions["SYSCALL"]
                in_funcs = built_in_funcs
            else:
                opcode = bytecode_instructions["OBJCALL"]
                in_funcs = built_in_obj_funcs

            if node.identifier in in_funcs:
                self.append_bytecode((opcode, in_funcs[node.identifier]))
            else:
                self.append_bytecode((bytecode_instructions["CALL"], self.identifiers[node.identifier]))
        elif isinstance(node, list):
            for item in node[::-1]:
                self.add_instruction(item)
            
            self.append_bytecode((bytecode_instructions["BUILD_LIST"], len(node)))
        elif isinstance(node, ListNode):
            list_access = []
            identifier = node.identifier
            while isinstance(identifier, ListNode):
                list_access.append(identifier.index)
                identifier = identifier.identifier

            if scope and identifier in self.locals:
                self.append_bytecode((bytecode_instructions["LOAD_LOCAL"], self.locals[identifier]))
            else:
                self.append_bytecode((bytecode_instructions["LOAD"], self.identifiers[identifier]))

            list_access.append(node.index)
            for access in list_access:
                if isinstance(access, Expression) and access.value_type != "IDENTIFIER":
                    self.append_bytecode((bytecode_instructions["LIST_ACCESS"], access.value))
                else:
                    self.add_instruction(access, scope)
                    self.append_bytecode((bytecode_instructions["LIST_ACCESS"], -1))
        elif isinstance(node, StructStatement):
            self.structs[node.name] = [
                len(self.structs), len(node.args), [arg.identifier for arg in node.args]
            ]

            aux = {"int" : 1, "float" : 2, "array" : 4, "obj": 5}
            for arg in node.args:
                if arg.var_type == "bool":
                    arg.var_type = "int"
                elif arg.var_type == "string" or "[]" in arg.var_type:
                    arg.var_type = "array"
                
                if arg.var_type not in aux:
                    arg.var_type = "obj"
                
                self.append_bytecode((bytecode_instructions["DEFINE_ATTR"], aux[arg.var_type]))
            
            self.append_bytecode((bytecode_instructions["DEFINE_TYPE"], self.structs[node.name][0]))

        elif isinstance(node, NewStatement):
            for arg in node.args:
                self.identifiers[f"QWEMNB{len(self.identifiers)}"] = 0
                self.add_instruction(arg)
            
            self.append_bytecode((bytecode_instructions["NEW"], self.structs[node.obj][0]))

    def get_bytecode(self):
        return self.bytecode.copy()

