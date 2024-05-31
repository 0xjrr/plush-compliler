import ply.lex as lex

tokens = [
    "NUMBER",
    "FLOAT",
    "STRING",
    "IDENTIFIER",
    # Arithmetic operators
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "MOD",
    "SQUARE",  
    # Parentheses and braces
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    # Brackets
    "LBRACKET",  # Left square bracket
    "RBRACKET",  # Right square bracket
    # Comparison operators
    "EQUALS",
    "NE",
    "GE",
    "GT",
    "LE",
    "LT",
    # Logical operators
    "AND",
    "OR",
    "NOT",
    # Bitwise operators
    "BITWISE_AND",
    "BITWISE_OR",
    "BITWISE_XOR",
    "BITWISE_NOT",
    "BITWISE_LSHIFT",
    "BITWISE_RSHIFT",
    # Keywords
    "VAL",
    "VAR",
    "FUNCTION",
    "IF",
    "ELSE",
    "WHILE",
    "DO",
    "TRUE",
    "FALSE",
    # Break and Continue
    "BREAK",
    "CONTINUE",
    # Punctuation
    "SEMICOLON",
    "COLON",
    "COMMA",
    "ASSIGN",
    # Increment and decrement
    "PLUSPLUS",
    "MINUSMINUS",
    "INCREMENT",
    "DECREMENT",
    # Types
    "TYPE",
    # Main and return
    "MAIN",
    "RETURN",
    # Argstring
    "ARGSTRING",
    # Import
    "IMPORT",
    # Print
    "PRINTINT",
    "PRINTDOUBLE",
    "PRINTSTRING",
    "PRINTF",
]

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_MOD = r"%"
t_SQUARE = r"\^"

t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"

t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_EQUALS = r"=="
t_NE = r"!="
t_GE = r">="
t_GT = r">"
t_LE = r"<="
t_LT = r"<"

t_AND = r"&&"
t_OR = r"\|\|"
t_NOT = r"!"

t_SEMICOLON = r";"
t_COLON = r":"
t_COMMA = r","
t_ASSIGN = r":="

# Bitwise operators
t_BITWISE_AND = r"&"
t_BITWISE_OR = r"\|"
t_BITWISE_NOT = r"~"
t_BITWISE_LSHIFT = r"<<"
t_BITWISE_RSHIFT = r">>"

# Increment and decrement
t_PLUSPLUS = r"\+\+"
t_MINUSMINUS = r"--"
t_INCREMENT = r"\+="
t_DECREMENT = r"-="

# Argstring
def t_ARGSTRING(t):
    r"args:\[string\]"
    t.type = "ARGSTRING"
    return t

# Keywords
reserved = {
    "val": "VAL",
    "var": "VAR",
    "function": "FUNCTION",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "do": "DO",
    "break": "BREAK",
    "continue": "CONTINUE",
    "true": "TRUE",
    "false": "FALSE",
    "int": "TYPE",
    "float": "TYPE",
    "string": "TYPE",
    "double": "TYPE",
    "void": "TYPE",
    "bool": "TYPE",
    "main": "MAIN",
    "return": "RETURN",
    "import": "IMPORT",
    "print_int": "PRINTINT",
    "print_double": "PRINTDOUBLE",
    "print_string": "PRINTSTRING",
    "printf": "PRINTF",
}


# Identifiers
def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(t.value, "IDENTIFIER")  # Check for reserved words
    return t


# Float literals
def t_FLOAT(t):
    r"\d+\.\d*|\.\d+"
    t.value = float(t.value)
    return t


# Number literals
def t_NUMBER(t):
    r"\d+[\d_]*"
    t.value = int(t.value.replace('_', ''))
    return t


# String literals
def t_STRING(t):
    r"\".*?\" "
    t.value = t.value[1:-1]  # Remove quotes
    return t


# Comments
def t_COMMENT(t):
    r"\#.*"
    pass  # Token is discarded


# Whitespace (spaces and tabs)
t_ignore = " \t"


# Newlines
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Error handling
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()

if __name__ == "__main__":
        
    # Test
    test_small = """
    val x : int := 1;
    var y : float := 1.2;
    # This is a comment
    if (x > y) {
        var result : string := "x is greater";
    } else {
        val result : string := "y is greater or equal";
    }
    """



    test_large = """
    # Define a function to calculate the square of a number
    function square(val num : int) : int {
        square := num * num;
    }

    # Define a function to check if a number is positive, negative, or zero
    function checkNumber(val x : int) : string {
        if (x > 0) {
            checkNumber := "positive";
        } else if (x < 0) {
            checkNumber := "negative";
        } else {
            checkNumber := "zero";
        }
    }

    # Main program starts here
    val pi : double := 3.14159;
    var radius : double := 2.5;
    val area : double := pi * square(radius); # Calculate the area of a circle

    # Using a loop to count down from 5
    var counter : int := 5;
    while (counter > 0) {
        println("Counting down: " + counter);
        counter := counter - 1;
    }

    # Checking if area is greater than a threshold
    if (area > 10) {
        println("Large circle");
    } else {
        println("Small circle");
    }

    # Checking number sign
    var number : int := -42;
    val sign : string := checkNumber(number);
    println("The number is " + sign);

    """

    # Give the lexer some input
    lexer.input(test_small)

    print("\n --- Small test ---\n")

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)

    # Give the lexer some input
    lexer.input(test_large)

    print("\n --- Large test ---\n")

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)
