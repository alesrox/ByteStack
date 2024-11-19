bytecode_instructions = {
    "ADD"           : 0x01,
    "SUB"           : 0x02,
    "MUL"           : 0x03,
    "DIV"           : 0x04,
    "MOD"           : 0x05,
    "AND"           : 0x06,
    "OR"            : 0x07,
    "NOT"           : 0x08,
    "EQ"            : 0x09,
    "NEQ"           : 0x0A,
    "LT"            : 0x0B,
    "GT"            : 0x0C,
    "LE"            : 0x0D,
    "GE"            : 0x0E,
    "STORE"         : 0x0F,
    "STORE_FLOAT"   : 0x10,
    "STORE_MEM"     : 0x11,
    "LOAD"          : 0x12,
    "JUMP"          : 0x13,
    "JUMP_IF"       : 0x14,
    "CREATE_SCOPE"  : 0x15,
    "DEL_SCOPE"     : 0x16,
    "CALL"          : 0x17,
    "STORE_LOCAL"   : 0x18,
    "LOAD_LOCAL"    : 0x19,
    "RETURN"        : 0x1A,
    "BUILD_LIST"    : 0x1B,
    "LIST_ACCESS"   : 0x1C,
    "LIST_SET"      : 0x1D,
    "BUILD_STR"     : 0x1E,
    "OBJCALL"       : 0xFE,
    "SYSCALL"       : 0xFF
}

operations = {
    '+': "ADD", '-': "SUB", '*': "MUL", '/': "DIV", '%': "MOD",
    'and': "AND", 'or': "OR", 'not': "NOT",
    '==': "EQ", '!=': "NEQ", 
    '<': "LT", '<=': "LE", '>': "GT", '>=': "GE",
}

built_in_funcs = {
    'exit'  : 0,    
    'print' : 1, 
    'input' : 2,
    'getf'  : 3,
    'scan'  : 4,
}

built_in_obj_funcs = {
    'append'    : 0,
    'size'      : 1,
    'remove'    : 2,
    'pop'       : 3,
    'is_empty'  : 4,
    'slice'     : 5,
    'map'       : 6,
    'filter'    : 7,
    'min'       : 8,
    'max'       : 9,
    'lower'     : 10,
    'upper'     : 11,
}