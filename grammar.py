import ply.yacc as yacc
from lexer import tokens  # Import the tokens from the lexer
import ast_nodes

precedence = (
    ('nonassoc', 'LT', 'GT', 'LE', 'GE', 'EQUALS', 'NE'),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'), # Left associative operators plus and minus
    ('left', 'TIMES', 'DIVIDE', 'MOD'), # Left associative operators times, divide, and mod
    ('right', 'NOT'),  # Right associative Unary
)

# Program structure
def p_program(p):
    "program : declaration_list"
    p[0] = ast_nodes.Program(p[1])

def p_declaration_list(p):
    """declaration_list : declaration_list declaration
                        | empty"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_declaration(p):
    """declaration : function_declaration
                   | statement"""
    p[0] = p[1]

# Variable declarations
def p_variable_declaration(p):
    """variable_declaration : VAL IDENTIFIER COLON TYPE ASSIGN expression SEMICOLON
                            | VAR IDENTIFIER COLON TYPE ASSIGN expression SEMICOLON"""
    p[0] = ast_nodes.VariableDeclaration(p[1], p[2], p[4], p[6])

# Function declarations
def p_function_declaration(p):
    """function_declaration : FUNCTION IDENTIFIER LPAREN parameter_list RPAREN COLON TYPE statement_block
                            | FUNCTION MAIN LPAREN parameter_list RPAREN COLON TYPE statement_block"""
    if p[2] == 'main':
        p[0] = ast_nodes.MainFunctionDeclaration(p[4], p[7], p[8])
    else:
        p[0] = ast_nodes.FunctionDeclaration(p[2], p[4], p[7], p[8])

def p_parameter_list(p):
    """parameter_list : parameter_list COMMA parameter
                      | parameter
                      | empty"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_parameter(p):
    "parameter : IDENTIFIER COLON TYPE"
    p[0] = (p[1], p[3])

def p_statement_block(p):
    "statement_block : LBRACE statement_list RBRACE"
    p[0] = p[2]

def p_statement_list(p):
    """statement_list : statement_list statement
                      | empty"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

# Statements
def p_statement(p):
    """statement : variable_declaration
                 | if_statement
                 | while_statement
                 | do_while_statement
                 | assignment_statement
                 | expression_statement
                 | return_statement"""
    p[0] = p[1]

def p_return_statement(p):
    """return_statement : RETURN expression SEMICOLON
                        | RETURN SEMICOLON"""
    if len(p) == 4:
        p[0] = ast_nodes.ReturnStatement(p[2])
    else:
        p[0] = ast_nodes.ReturnStatement(None)

def p_if_statement(p):
    """if_statement : IF LPAREN expression RPAREN statement_block ELSE statement_block
                    | IF LPAREN expression RPAREN statement_block"""
    if len(p) == 8:
        p[0] = ast_nodes.IfStatement(p[3], p[5], p[7])
    else:
        p[0] = ast_nodes.IfStatement(p[3], p[5], None)

def p_while_statement(p):
    "while_statement : WHILE LPAREN expression RPAREN statement_block SEMICOLON"
    p[0] = ast_nodes.WhileStatement(p[3], p[5])

def p_do_while_statement(p):
    "do_while_statement : DO statement_block WHILE LPAREN expression RPAREN SEMICOLON"
    p[0] = ast_nodes.DoWhileStatement(p[5], p[2])

def p_assignment_statement(p):
    "assignment_statement : IDENTIFIER ASSIGN expression SEMICOLON"
    p[0] = ast_nodes.AssignmentStatement(p[1], p[3])

def p_expression_statement(p):
    "expression_statement : expression SEMICOLON"
    p[0] = ast_nodes.ExpressionStatement(p[1])

def p_function_call(p):
    "function_call : IDENTIFIER LPAREN expression_list RPAREN"
    p[0] = ('func_call', p[1], p[3])

# Expressions
def p_expression_list(p):
    """expression_list : expression_list COMMA expression
                       | expression"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_expression(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQUALS expression
                  | expression NE expression
                  | expression AND expression
                  | expression OR expression
                  | LPAREN expression RPAREN
                  | NOT expression
                  | IDENTIFIER
                  | NUMBER
                  | FLOAT
                  | STRING
                  | TRUE
                  | FALSE
                  | function_call"""
    if len(p) == 4:
        if p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = (p[2], p[1], p[3])
    elif len(p) == 3:
        p[0] = ('not', p[2])
    else:
        p[0] = p[1]


def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc(debug=True, debugfile="parser.out")

# Example usage
if __name__ == "__main__":
    import print_tree
    print("Running parser tests...")

    print("Test 1")
    test_input = """
    function compute(x: int, y: float): float {
        val z : float := 0.0;
        return x + y;
    }
    """
    result = parser.parse(test_input)
    print(result)

    print("Test 2")
    s = """
    function test(x: int, y: float): string {
        var z : string := "hello";
        val a : int := 1;
        if (x > y) {
            z := "x is greater";
        } else {
            z := "y is greater or equal";
        }
        return z;
    }

    function main(): void {
        var x : int := 1;
        var y : float := 2.0;
        var z : string := test(x, y);
    }
    """
    result = parser.parse(s)
    print(result)

    print("Test 3")
    s = """
    function test(x: int, y: float): string {
        var z : string := "hello";
        while (x > 0) {
            x := x - 1;
            z := z + "!";
        }
        return z;
    }
    """
    result = parser.parse(s)
    print(result)

    print("Test 4")
    s = """
    function test(x: int, y: float): float {
        a :=   2 * x + y;
        b                := 3 * (x - y);
        return x + y * 2;
    }
    """
    result = parser.parse(s)
    print(result) 

    print("Test 5")
    s = """
    function test(x: int): void {
        a := 0;
        do {
            a := a + 1;
        } while (a < x);
       while (a > 0) {
            a := a - 1;
        };
        return;
    }
    """
    result = parser.parse(s)
    print(result) 

    print("Test 6")

    s = """
    function binary_operation(x: int, y: int): int {
        return y * 2 + x / 3; 
    }
    """
    result = parser.parse(s)
    print(result)
