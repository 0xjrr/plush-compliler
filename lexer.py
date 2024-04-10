import ply.lex as lex

tokens = [
    'NUMBER', 'FLOAT', 'STRING', 'IDENTIFIER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'EQUALS', 'NE', 'GE', 'GT', 'LE', 'LT',
    'AND', 'OR', 'NOT',
    'VAL', 'VAR', 'FUNCTION', 'IF', 'ELSE', 'WHILE',
    'TRUE', 'FALSE', 'SEMICOLON', 'COLON', 'COMMA', 'ASSIGN'
]

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_EQUALS = r'=='
t_NE = r'!='
t_GE = r'>='
t_GT = r'>'
t_LE = r'<='
t_LT = r'<'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r','
t_ASSIGN = r':='

# Keywords
reserved = {
    'val': 'VAL',
    'var': 'VAR',
    'function': 'FUNCTION',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'true': 'TRUE',
    'false': 'FALSE'
}

# Identifiers
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Check for reserved words
    return t

# Float literals
def t_FLOAT(t):
    r'\d+\.\d*|\.\d+'
    t.value = float(t.value)
    return t

# Number literals
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# String literals
def t_STRING(t):
    r'\".*?\"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

# Comments
def t_COMMENT(t):
    r'\#.*'
    pass  # Token is discarded

# Whitespace (spaces and tabs)
t_ignore = ' \t'

# Newlines
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()


# Test it out
data = '''
val x : int := 1;
var y : float := 1.2;
# This is a comment
if (x > y) {
    var result : string := "x is greater";
} else {
    val result : string := "y is greater or equal";
}
'''

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break  # No more input
    print(tok)
