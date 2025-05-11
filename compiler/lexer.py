import ply.lex as lex

tokens = [
    'INT_LITERAL', 'FLOAT_LITERAL', 'STRING_LITERAL', 'BOOL_LITERAL',
    'IDENTIFIER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MOD', 'POW',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'ASSIGN', 'SEMICOLON',
    'COMMA', 'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE',
    'START_LIST', 'END_LIST', 'EMPTY_ARR', 'POINT', 'RET'
]

keywords = {
    'if'        : 'IF',
    'else'      : 'ELSE',
    'elif'      : 'ELIF',
    'while'     : 'WHILE',
    'for'       : 'FOR',
    'return'    : 'RETURN',
    'func'      : 'FUNC',
    'try'       : 'TRY',
    'catch'     : 'CATCH',
    'throw'     : 'THROW',
    'new'       : 'NEW',
    'object'    : 'OBJECT',
    'extends'   : 'EXTENDS',
    'int'       : 'INT',
    'byte'      : 'BYTE',
    'float'     : 'FLOAT',
    'bool'      : 'BOOL',
    'string'    : 'STRING',
    'true'      : 'TRUE',
    'false'     : 'FALSE',
    'and'       : 'AND',
    'or'        : 'OR',
    'not'       : 'NOT',
    'Array'     : 'ARRAY',
    'struct'    : 'STRUCT',
    'continue'  : 'CONTINUE',
    'break'     : 'BREAK',
}

tokens += list(keywords.values())

t_CONTINUE = r'continue'
t_BREAK = r'break'
t_RET = r'->'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MOD = r'\%'
t_POW = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EMPTY_ARR = r'\[\]'
t_START_LIST = r'\['
t_END_LIST = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_ASSIGN = r'='
t_SEMICOLON = r';'
t_COMMA = r','

t_EQ = r'=='
t_NEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='
t_POINT = r'.'

def t_FLOAT_LITERAL(t):
    r'-?\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT_LITERAL(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

def t_STRING_LITERAL(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_BOOL_LITERAL(t):
    r'\b(true|false)\b'
    t.value = True if t.value == 'true' else False
    return t

def t_comment_singleline(t):
    r'//.*'
    pass

def t_comment_multiline(t):
    r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
    pass

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, 'IDENTIFIER')
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()