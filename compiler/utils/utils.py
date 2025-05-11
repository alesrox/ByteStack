opcodes = {
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
    "STORE_BYTE"    : 0x10,
    "STORE_FLOAT"   : 0x11,
    "STORE_CHAR"    : 0x12,
    "STORE_MEM"     : 0x13,
    "LOAD"          : 0x14,
    "JUMP"          : 0x15,
    "JUMP_IF"       : 0x16,
    "CALL"          : 0x17,
    "RETURN"        : 0x18,
    "BUILD_LIST"    : 0x19,
    "LIST_ACCESS"   : 0x1A,
    "LIST_SET"      : 0x1B,
    "DEFINE_TYPE"   : 0x1C,
    "NEW"           : 0x1D,
    "CAST"          : 0x1E,
    "SYSCALL"       : 0xFF
}

operations = {
    '+': "ADD", '-': "SUB", '*': "MUL", '/': "DIV", '%': "MOD",
    'and': "AND", 'or': "OR", 'not': "NOT",
    '==': "EQ", '!=': "NEQ", 
    '<': "LT", '<=': "LE", '>': "GT", '>=': "GE",
}

literals = ['INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL', 'BOOL_LITERAL']

built_in_funcs = {
    'exit'      : 0,    
    'print'     : 1, 
    'input'     : 2,
    'getf'      : 3,
    'scan'      : 4,
    'type'      : 5,
    'read'      : 6,
    'write'     : 7,
    'size'      : 8,
    'append'    : 9,
    'remove_at' : 10,
    'is_empty'  : 11,
    'slice'     : 12,
    'map'       : 13,
    'filter'    : 14,
    'min'       : 15,
    'max'       : 16,
    'lower'     : 17,
    'upper'     : 18,
    'toString'  : 19,
}

TYPE_IDS = {
    "BOOL": 1,
    "BYTE": 1,
    "INT": 2,
    "FLOAT": 3,
    "CHAR": 4,
    "STRING": 5,
}

def get_type_info(type_str):
    depth = type_str.count("[]")
    base_type = type_str.replace("[]", "")

    if base_type == "STRING":
        return TYPE_IDS["CHAR"], depth + 1
    else:
        return TYPE_IDS[base_type], depth

def encode_cast_arg(from_type_str, to_type_str):
    from_id, from_depth = get_type_info(from_type_str)
    to_id, to_depth = get_type_info(to_type_str)

    max_depth = max(from_depth, to_depth)
    encoded = (max_depth << 16) | (from_id << 8) | to_id
    return encoded