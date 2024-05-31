import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tree.ast_nodes import *
class TypeChecker:
    def __init__(self):
        self.symbol_table_stack = [{'immutable_vars': []}]  # A stack of dictionaries for scoping
        self.functions = {}  # Function name to function return type
        self.current_function = None
        self.errors = []
        # validation result is a dictionary that maps expressions with their types
        self.validation_result = {}

    def check_program(self, program):
        self.check_global_variables(program.global_variables)
        for declaration in program.declarations:
            self.check_declaration(declaration)

    def check_global_variables(self, globals):
        if globals:
            for var_decl in globals.declarations:
                if isinstance(var_decl, ArrayDeclaration):
                    self.check_array_declaration(var_decl)
                else:
                    self.check_global_variable_declaration(var_decl)
    
    def check_global_variable_declaration(self, var_decl):
        # Check if variable already declared in global scope
        if var_decl.name in self.symbol_table_stack[0]:
            self.errors.append(f"Variable '{var_decl.name}' already declared in global scope")
            return
        # Add variable to global scope
        self.symbol_table_stack[0][var_decl.name] = var_decl.data_type
        # Check variable initialization kind
        if var_decl.var_kind == "val":
            if not var_decl.value:
                self.errors.append(f"Constant variable '{var_decl.name}' must be initialized")
                return
            self.check_expression(var_decl.value)
            self.symbol_table_stack[0].get("immutable_vars", []).append(var_decl.name)
        else:
            if var_decl.value:
                self.check_expression(var_decl.value)
        
    def check_array_declaration(self, array_decl):
        # Check if array already declared in global scope
        if array_decl.name in self.symbol_table_stack[0]:
            self.errors.append(f"Array '{array_decl.name}' already declared in global scope")
            return
        # Add array to global scope
        self.symbol_table_stack[0][array_decl.name] = array_decl.data_type
        for value in array_decl.value:
            self.check_expression(value)

    def check_declaration(self, declaration):
        if isinstance(declaration, FunctionStatement):
            self.check_function_declaration(declaration)
        elif isinstance(declaration, MainFunctionStatement):
            self.check_main_function_declaration(declaration)
        elif isinstance(declaration, VariableDeclaration):
            self.check_variable_declaration(declaration)
        elif isinstance(declaration, ArrayDeclaration):
            self.check_array_declaration(declaration)
        else:
            self.errors.append(f"Unknown declaration type: {type(declaration)}")

    def check_function_declaration(self, function_decl):
        self.symbol_table_stack.append({'immutable_vars': []})  # New scope for function
        self.current_function = function_decl.name
        # Add function parameters to symbol table
        if function_decl.parameters and any(function_decl.parameters):
            for param_name, param_type in function_decl.parameters:
                self.symbol_table_stack[-1][param_name] = param_type

        # Add function to functions dictionary
        self.functions[function_decl.name] = function_decl.return_type

        # Check function body
        self.check_statement_block(function_decl.body)
        self.current_function = None
        self.symbol_table_stack.pop()  # End of function scope

    def check_main_function_declaration(self, main_func_decl):
        self.symbol_table_stack.append({'immutable_vars': []})  # New scope for main function
        self.current_function = "main"
        # Main function has no parameters
        # Check function body
        self.check_statement_block(main_func_decl.body)
        self.current_function = None
        self.symbol_table_stack.pop()  # End of main function scope

    def check_variable_declaration(self, var_decl):
        # Check if variable already declared in global scope
        global_scope = self.symbol_table_stack[0]
        if var_decl.name in global_scope:
            self.errors.append(f"Variable '{var_decl.name}' already declared in global scope")
            return
        
        # Check if variable already declared in current scope
        current_scope = self.symbol_table_stack[-1]
        if var_decl.name in current_scope:
            self.errors.append(f"Variable '{var_decl.name}' already declared in current scope")
            return

        # Add variable to symbol table
        self.symbol_table_stack[-1][var_decl.name] = var_decl.data_type

        # Check variable initialization kind
        if var_decl.var_kind == "val":
            if not var_decl.value:
                self.errors.append(f"Constant variable '{var_decl.name}' must be initialized")
                return
            self.check_expression(var_decl.value)
            self.symbol_table_stack[-1].get("immutable_vars", []).append(var_decl.name)
        
        # Check variable initialization expression
        self.check_expression(var_decl.value)

    def check_statement_block(self, statement_block):
        for statement in statement_block:
            self.check_statement(statement)

    def check_statement(self, statement):
        if isinstance(statement, VariableDeclaration):
            self.check_variable_declaration(statement)
        elif isinstance(statement, ArrayDeclaration):
            self.check_array_declaration(statement)
        elif isinstance(statement, IfStatement):
            self.check_if_statement(statement)
        elif isinstance(statement, WhileStatement):
            self.check_while_statement(statement)
        elif isinstance(statement, DoWhileStatement):
            self.check_do_while_statement(statement)
        elif isinstance(statement, AssignmentStatement):
            self.check_assignment_statement(statement)
        elif isinstance(statement, ArrayAssignmentStatement):
            self.check_array_assignment_statement(statement)
        elif isinstance(statement, ReturnStatement):
            self.check_return_statement(statement)
        elif isinstance(statement, ExpressionStatement):
            self.check_expression(statement.expression)
        elif isinstance(statement, PrintStatement):
            self.check_print_statement(statement)
        elif isinstance(statement, ArrayAllocation):
            pass
        else:
            self.errors.append(f"Unknown statement type: {type(statement)}")

    def check_variable_reference(self, name):
        # Check variable in the nearest scope
        for scope in reversed(self.symbol_table_stack):
            if name in scope:
                return
        self.errors.append(f"Variable '{name}' not declared")
    
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
        variable_type = None
        # Check if variable is declared
        for scope in reversed(self.symbol_table_stack):
            if assign_stmt.target in scope:
                # Check variable kind
                if assign_stmt.target in scope.get("immutable_vars", []):
                    self.errors.append(f"Cannot assign to constant variable '{assign_stmt.target}'")
                    return
                variable_type = scope[assign_stmt.target]
                break
        if not variable_type:
            self.errors.append(f"Variable '{assign_stmt.target}' not declared")
            return
        
        self.check_expression(assign_stmt.value)
        # Assume get_expression_type() can determine the expression's type
        actual_type = self.get_expression_type(assign_stmt.value)
        if actual_type == "str":
            actual_type = "string"
        
        # Store result in validation_result
        self.validation_result[f"Assignment: {assign_stmt.value}"] = actual_type
        if variable_type != actual_type:
            self.errors.append(f"Type mismatch in assignment for variable '{assign_stmt.target}'")

    def check_array_assignment_statement(self, assign_stmt):
        array_type = None
        # Check if array is declared
        for scope in reversed(self.symbol_table_stack):
            if assign_stmt.target in scope:
                # Check array kind
                if assign_stmt.target in scope.get("immutable_vars", []):
                    self.errors.append(f"Cannot assign to constant array '{assign_stmt.target}'")
                    return
                array_type = scope[assign_stmt.target]
                break
        if not array_type:
            self.errors.append(f"Array '{assign_stmt.target}' not declared")
            return
        
        self.check_expression(assign_stmt.index)
        self.check_expression(assign_stmt.value)
        # Assume get_expression_type() can determine the expression's type
        actual_type = self.get_expression_type(assign_stmt.value)
        if actual_type == "str":
            actual_type = "string"
        
        # Store result in validation_result
        self.validation_result[f"ArrayAssignment: {assign_stmt.value}"] = actual_type
        if array_type[0] != actual_type:
            self.errors.append(f"Type mismatch in array assignment for array '{assign_stmt.target}'")

    def check_return_statement(self, return_stmt):
        if return_stmt.value:
            self.check_expression(return_stmt.value)
            # Assume get_expression_type() can determine the expression's type
            actual_type = self.get_expression_type(return_stmt.value)
            if actual_type == "str":
                actual_type = "string"
            # Store result in validation_result
            self.validation_result[f"Return: {return_stmt.value}"] = actual_type
            
            if self.current_function:
                if actual_type != self.functions.get(self.current_function, None):
                    self.errors.append(f"Return type mismatch in {self.current_function} function")
            else:
                self.errors.append(f"Return statement outside of function")

    def check_expression(self, expression):
        if isinstance(expression, BinaryExpression):
            self.check_binary_expression(expression)
        elif isinstance(expression, UnaryExpression):
            self.check_unary_expression(expression)
        elif isinstance(expression, Literal):
            pass  # Literals have correct type
        elif isinstance(expression, FunctionCall):
            self.check_function_call(expression)
        elif isinstance(expression, VariableReference):
            self.check_variable_reference(expression.name)
        elif isinstance(expression, ArrayAccess):
            self.check_array_access(expression)
        else:
            self.errors.append(f"Unknown expression type: {type(expression)}")

    def check_binary_expression(self, binary_expr):
        self.check_expression(binary_expr.left)
        self.check_expression(binary_expr.right)

    def check_unary_expression(self, unary_expr):
        self.check_expression(unary_expr.operand)

    def check_function_call(self, func_call):
        # Check if function exists and if arguments match parameters in type and number
        if func_call.name not in self.functions:
            self.errors.append(f"Function '{func_call.name}' not declared")
            return

    def check_array_access(self, array_access):
        for scope in reversed(self.symbol_table_stack):
            if array_access.name in scope:
                array_type = scope[array_access.name]
                self.check_expression(array_access.index)
                return array_type
        self.errors.append(f"Array '{array_access.name}' not declared")
    
    def check_print_statement(self, print_stmt):
        self.check_expression(print_stmt.expression)
        # Store result in validation_result
        self.validation_result[f"Print: {print_stmt.expression}"] = self.get_expression_type(print_stmt.expression)

    def are_types_compatible(self, type1, type2):
        # Implement specific rules based on your language specifications
        if type1 == type2:
            return True
        
        if type1 in ["int", "float", "double"] and type2 in ["int", "float", "double"]:
            return True
        
        return False
        
    def determine_common_type(self, type1, type2):
        # Implement type coercion or common type determination logic
        pass

    def get_expression_type(self, expression):
        if isinstance(expression, Literal):
            computed_type = type(expression.value).__name__.lower()
            if computed_type == "str":
                computed_type = "string"
            # Store result in validation_result
            self.validation_result[f"Literal: {expression}"] = computed_type
            return computed_type
        elif isinstance(expression, BinaryExpression):
            left_type = self.get_expression_type(expression.left)
            right_type = self.get_expression_type(expression.right)
            
            # Example type compatibility logic
            if left_type == right_type:
                result_type = left_type
            elif self.are_types_compatible(left_type, right_type):
                result_type = self.determine_common_type(left_type, right_type)
            else:
                self.errors.append(f"Type mismatch in binary expression: {left_type} and {right_type}")
                result_type = None
            
            self.validation_result[f"Binary: {expression}"] = result_type
            return result_type
        elif isinstance(expression, UnaryExpression):
            return self.get_expression_type(expression.operand)
        elif isinstance(expression, FunctionCall):
            # Determine return type of function call
            computed_type = self.functions.get(expression.name, None)
            # Store result in validation_result
            self.validation_result[expression.__str__()] = computed_type
            return computed_type
        elif isinstance(expression, VariableReference):
            for scope in reversed(self.symbol_table_stack):
                if expression.name in scope:
                    # Store result in validation_result
                    self.validation_result[expression.__str__()] = scope[expression.name]
                    return scope[expression.name]
            
            # Variable not in symbol table
            self.errors.append(f"Variable '{expression.name}' not declared, no type found")
            return None
        elif isinstance(expression, ArrayAccess):
            return self.check_array_access(expression)
        else:
            self.errors.append(f"Unknown expression type: {type(expression)}, expression: {expression}")
        return None

if __name__ == "__main__":
    # Test type checking
    from grammar.grammar import parser
    import print_tree
    import json

    print("Global variables test cases")
    print("Test 0")
    type_checker = TypeChecker()
    test_input = """
    var x : int;
    var x : float;
    function test(): float {
        x := 1;
        return 1.0;
    }
    """
    print("Test input:\n", test_input)
    result = parser.parse(test_input)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:\n", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))

    print("Type checking test cases")
    print("Test 1")
    type_checker = TypeChecker()

    test_input = """
    function compute(x: int, y: float): float {
        val z : float := 0.0;
        return x + y;
    }
    """
    print("Test input:\n", test_input)
    result = parser.parse(test_input)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:\n", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))

    print("Test 2")
    type_checker = TypeChecker()
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
        var z : bool := false;
        y := 1.0;
        x := 2;
        z := true;
        var last : string := test(x, y);
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:\n", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))


    print("Test 3")
    type_checker = TypeChecker()
    s = """
    function test(x: int, y: float): string {
        var z : string := "hello";
        while (x > 0) {
            x := x - 1;
            z := z + "!";
        };
        return z;
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:\n", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))

    print("Error tests:\n")

    print("Test 4")
    type_checker = TypeChecker()
    s = """
    function test(x: int, y: float): float {
        a :=   2 * x + y;
        b                := 3 * (x - y);
        return x + y * 2;
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:", type_checker.errors)
    print("Expected errors: ['Variable \'a\' not declared', 'Variable \'b\' not declared']")
    print(json.dumps(type_checker.validation_result, indent=4))

    print("Test 5")
    type_checker = TypeChecker()
    s = """
    function test(x: int, y: float): float {
        a := 1;
        w := 2 * x + y;
        b := 3 * (x - y);
        val z : string := "hello";
        z := x + y * 2;
        z := z + 1;
        return z;
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:", type_checker.errors)
    print(json.dumps(type_checker.validation_result, indent=4))

    print("Fully Correct Program")
    print("Test 6")
    type_checker = TypeChecker()
    s = """
    val x : int := 1;
    var y : float := 1.2;
    # This is a comment
    function test(z: int, w: float): float {
        var k: int := z;
        while (k > x) {
            k := k - 1;
            y := y + w;
        };
        if (k == 0) {
            return y;
        } 
        if (k == 1) {
            return y + 1.0;
        } else {
            w := w + y;
        }
        return w;
    }

    function main(): void {
        var a: int := 2;
        var b: float := 3.0;
        var c: float := test(a, b);
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse normal result:")
    print(result)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))

    print("Test 7")
    type_checker = TypeChecker()
    s = """
    val x : int := 1;
    function main(): void {
        var a: int := 2;
        if (a > x) {
            a := a + 1;
        } else {
            a := a - 1;
        }
        return;
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse normal result:")
    print(result)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))

    print("Test 8")
    type_checker = TypeChecker()
    s = """
    val x : int := 1;
    val y : float := 2.0;
    function test(a: int, b: float): float {
        if (a > x) {
            return y+x;
        } else {
            return y-x;
        }
    }
    function main(): void {
        var a: int := 2;
        var b: float := 3.0;
        var c: float := test(a, b);
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse normal result:")
    print(result)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))


    print("Test 9")
    type_checker = TypeChecker()
    # int a = 10;

    # double test(int x) {
    #     int b = a;
    #     int c = a;
    #     int y = x;
    #     a = 20;
    #     b += 10;
    #     return b;
    # }

    # int main() {
    #     printf("%f\n", test(10));
    #     double f = test(a);
    #     printf("%f\n",f);
    #     return 0;
    # }
    s = """
    var a : int := 10;
    function test(x: int): float {
        var b: int := a;
        var c: int := a;
        var y: int := x;
        a := 20 + x;
        b := b + 10;
        return b;
    }
    function main(): int {
        var f: float := test(11);
        var g: float := test(a);
        return 0;
    }
    """
    print("Test input:\n", s)
    result = parser.parse(s)
    print("Parse normal result:")
    print(result)
    print("Parse result:")
    print_tree.pretty_print(result)
    type_checker.check_program(result)
    print("Typecheck errors:", type_checker.errors)
    print("Typecheck results:\n", json.dumps(type_checker.validation_result, indent=4))
