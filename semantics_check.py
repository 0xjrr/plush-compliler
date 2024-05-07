from ast_nodes import *

class TypeChecker:
    def __init__(self):
        self.symbol_table = {}  # To store variable names and their types
        self.errors = []

    def check_program(self, program):
        for declaration in program.declarations:
            self.check_declaration(declaration)

    def check_declaration(self, declaration):
        if isinstance(declaration, FunctionDeclaration):
            self.check_function_declaration(declaration)
        elif isinstance(declaration, MainFunctionDeclaration):
            self.check_main_function_declaration(declaration)
        elif isinstance(declaration, VariableDeclaration):
            self.check_variable_declaration(declaration)
        else:
            self.errors.append(f"Unknown declaration type: {type(declaration)}")

    def check_function_declaration(self, function_decl):
        # Add function parameters to symbol table
        for param in function_decl.parameters:
            self.symbol_table[param.name] = param.type

        # Check function body
        self.check_statement_block(function_decl.body)

    def check_main_function_declaration(self, main_func_decl):
        # Main function has no parameters
        # Check function body
        self.check_statement_block(main_func_decl.body)

    def check_variable_declaration(self, var_decl):
        # Check if variable already declared
        if var_decl.name in self.symbol_table:
            self.errors.append(f"Variable '{var_decl.name}' already declared")
            return

        # Add variable to symbol table
        self.symbol_table[var_decl.name] = var_decl.data_type

        # Check variable initialization expression
        self.check_expression(var_decl.value)

    def check_statement_block(self, statement_block):
        for statement in statement_block.statements:
            self.check_statement(statement)

    def check_statement(self, statement):
        if isinstance(statement, VariableDeclaration):
            self.check_variable_declaration(statement)
        elif isinstance(statement, IfStatement):
            self.check_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            self.check_while_statement(statement)
        elif isinstance(statement, DoWhileStatement):
            self.check_do_while_statement(statement)
        elif isinstance(statement, AssignmentStatement):
            self.check_assignment_statement(statement)
        elif isinstance(statement, ReturnStatement):
            self.check_return_statement(statement)
        elif isinstance(statement, ExpressionStatement):
            self.check_expression(statement.expression)
        else:
            self.errors.append(f"Unknown statement type: {type(statement)}")

    def check_if_statement(self, if_stmt):
        self.check_expression(if_stmt.condition)
        self.check_statement_block(if_stmt.then_block)
        if if_stmt.else_block:
            self.check_statement_block(if_stmt.else_block)

    def check_while_statement(self, while_stmt):
        self.check_expression(while_stmt.condition)
        self.check_statement_block(while_stmt.body)

    def check_do_while_statement(self, do_while_stmt):
        self.check_statement_block(do_while_stmt.body)
        self.check_expression(do_while_stmt.condition)

    def check_assignment_statement(self, assign_stmt):
        if assign_stmt.target not in self.symbol_table:
            self.errors.append(f"Variable '{assign_stmt.target}' not declared")
            return
        expected_type = self.symbol_table[assign_stmt.target]
        self.check_expression(assign_stmt.value)
        actual_type = self.get_expression_type(assign_stmt.value)
        if expected_type != actual_type:
            self.errors.append(f"Type mismatch in assignment for variable '{assign_stmt.target}'")

    def check_return_statement(self, return_stmt):
        if return_stmt.value:
            self.check_expression(return_stmt.value)

    def check_expression(self, expression):
        if isinstance(expression, BinaryExpression):
            self.check_binary_expression(expression)
        elif isinstance(expression, UnaryExpression):
            self.check_unary_expression(expression)
        elif isinstance(expression, Literal):
            pass  # Literals have correct type
        elif isinstance(expression, FunctionCall):
            self.check_function_call(expression)
        else:
            self.errors.append(f"Unknown expression type: {type(expression)}")

    def check_binary_expression(self, binary_expr):
        self.check_expression(binary_expr.left)
        self.check_expression(binary_expr.right)

    def check_unary_expression(self, unary_expr):
        self.check_expression(unary_expr.operand)

    def check_function_call(self, func_call):
        # Check if function exists
        # Check if arguments match parameters in type and number
        pass

    def get_expression_type(self, expression):
        if isinstance(expression, Literal):
            return type(expression.value).__name__.lower()
        elif isinstance(expression, BinaryExpression):
            return self.get_expression_type(expression.left)
        elif isinstance(expression, UnaryExpression):
            return self.get_expression_type(expression.operand)
        elif isinstance(expression, FunctionCall):
            # Determine return type of function call
            pass
        elif isinstance(expression, Identifier):
            return self.symbol_table.get(expression.name, None)
        return None

if __name__ == "__main__":
    # Test type checking
    from grammar import parser

    type_checker = TypeChecker()

    test_input = """
    function compute(x: int, y: float): float {
        val z : float := 0.0;
        return x + y;
    }
    """
    result = parser.parse(test_input)
    type_checker.check_program(result)
    print("Errors:", type_checker.errors)

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
    type_checker.check_program(result)
    print("Errors:", type_checker.errors)

    # Additional test cases can be added here
