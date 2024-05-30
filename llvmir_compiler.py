from typing import Dict
from ast_nodes import *

class LLVMIRGenerator:
    def __init__(self, program: Program):
        self.output = []
        self.indentation = 0
        self.temp_count = 0
        self.var_count = 0
        self.symbol_table_stack = []  # Stack of symbol tables
        self.function_signatures = {}
        self.declaration_scope = None
        self.program = program

    def emit(self, line):
        self.output.append("    " * self.indentation + line)

    def emit_global(self, line):
        self.output.insert(0, line)

    def generate(self):
        # self.emit("; ModuleID = 'my_program'")
        self.emit("declare dso_local i32 @printf(i8*, ...)")
        self.emit("declare dso_local i32 @scanf(i8*, ...)")
        self.emit("declare double @pow(double, double)")
        self.emit("")
        self.push_symbol_table()  # Global scope
        self.process_global_variables(self.program.global_variables)
        for decl in self.program.declarations:
            self.visit(decl)
        self.pop_symbol_table()  # End global scope
        return "\n".join(self.output)

    def push_symbol_table(self):
        self.symbol_table_stack.append({})

    def pop_symbol_table(self):
        if self.symbol_table_stack:
            self.symbol_table_stack.pop()

    def add_to_symbol_table(self, name, var_type, _var_name, _var_type=None):
        if self.symbol_table_stack:
            if name in self.symbol_table_stack[-1]:
                raise Exception(f"Variable '{name}' already defined")
            elif _var_type == "parameter":
                _params = self.symbol_table_stack[-1].get("params", {})
                _params[name] = (var_type, _var_name)
                self.symbol_table_stack[-1]["params"] = _params
            else:
                self.symbol_table_stack[-1][name] = (var_type, _var_name)
    
    def lookup_symbol(self, name):
        # Search from the top of the stack downwards
        for table in reversed(self.symbol_table_stack):
            if name in table:
                return table[name]
        raise Exception(f"Undefined variable '{name}'")

    def add_while_blocks_to_symbol_table(self, while_condition, while_body, while_end):
        self.symbol_table_stack[-1]["while_condition"] = while_condition
        self.symbol_table_stack[-1]["while_body"] = while_body
        self.symbol_table_stack[-1]["while_end"] = while_end

    def get_while_blocks(self):
        for table in reversed(self.symbol_table_stack):
            if table.get("while_condition"):
                return (
                    table.get("while_condition"),
                    table.get("while_body"),
                    table.get("while_end"),
                )

    def calculate_array_size(self, value):
        if isinstance(value, list):
            return len(value) * self.calculate_array_size(value[0])
        return 1

    def calculate_array_dimensions(self, value):
        # Calculate the dimensions of the array recursively
        if isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], list):
                return [len(value)] + self.calculate_array_dimensions(value[0])
            else:
                return [len(value)]
        return [0]

    def process_global_variables(self, globals):
        self.declaration_scope = "global"
        for var_decl in globals.declarations:
            self.visit(var_decl)

        self.declaration_scope = None

    def visit(self, node):
        """Dispatch method to visit nodes."""
        if isinstance(node, list):
            for item in node:
                self.visit(item)
        else:
            method_name = "visit_" + node.__class__.__name__
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)

    def generic_visit(self, node):
        """Fallback method."""
        raise Exception(f"No visit_{node.__class__.__name__} method")

    def visit_VariableDeclaration(self, node):
        type_ir = self.get_type(node.data_type)
        if isinstance(node.data_type, list):  # Check if it's an array
            element_type_ir = self.get_type(node.data_type[-1])
            dimensions = self.calculate_array_dimensions(node.value)
            var_name = f"x{self.var_count}"
            self.var_count += 1
            array_type = f"[{dimensions[0]} x [{dimensions[1]} x {element_type_ir}]]"
            
            self.emit(f"%{var_name} = alloca {array_type}, align 16")
            
            # Initialize the array with values
            for i, row in enumerate(node.value):
                for j, value in enumerate(row):
                    element_ptr = f"%{var_name}_{i}_{j}_ptr"
                    self.emit(f"{element_ptr} = getelementptr inbounds {array_type}, {array_type}* %{var_name}, i32 0, i32 {i}, i32 {j}")
                    self.emit(f"store {element_type_ir} {value.value}, {element_type_ir}* {element_ptr}, align 16")
        else:
            lit_type, value = self.visit(node.value) if node.value else "0"
            if self.declaration_scope == "global":
                var_vame = f"g{self.var_count}"
                self.var_count += 1
                if type_ir in ("float", "double"):
                    self.emit(f"@{var_vame} = global {type_ir} {float(value)}, align 8")
                elif type_ir == "i1":
                    self.emit(f"@{var_vame} = global {type_ir} {int(value)}, align 1")
                else:
                    self.emit(f"@{var_vame} = global {type_ir} {value}, align 4")
            else:
                var_vame = f"x{self.var_count}"
                self.var_count += 1
                # Allocate memory for the variable
                # Store the initial value
                if node.value:
                    if isinstance(node.value, Literal):
                        if type_ir in ("float", "double"):
                            self.emit(f"%{var_vame} = alloca {type_ir}, align 8")
                            self.emit(
                                f"store {type_ir} {float(value)}, {type_ir}* %{var_vame}, align 8"
                            )
                        elif type_ir == "i1":
                            self.emit(f"%{var_vame} = alloca {type_ir}, align 1")
                            self.emit(
                                f"store {type_ir} {int(value)}, {type_ir}* %{var_vame}, align 1"
                            )
                        elif type_ir == "i8":
                            self.emit(f"%{var_vame} = {value}")
                        else:
                            self.emit(f"%{var_vame} = alloca {type_ir}, align 4")
                            self.emit(
                                f"store {type_ir} {value}, {type_ir}* %{var_vame}, align 4"
                            )
                    else:
                        if lit_type in ("float", "double"):
                            self.emit(f"%{var_vame} = alloca {lit_type}, align 8")
                            self.emit(
                                f"store {lit_type} {value}, {lit_type}* %{var_vame}, align 8"
                            )
                        elif lit_type == "i1":
                            self.emit(f"%{var_vame} = alloca {lit_type}, align 1")
                            self.emit(
                                f"store {lit_type} {value}, {lit_type}* %{var_vame}, align 1"
                            )
                        else:
                            self.emit(f"%{var_vame} = alloca {lit_type}, align 4")
                            self.emit(
                                f"store {type_ir} {value}, {type_ir}* %{var_vame}, align 4"
                            )

        self.add_to_symbol_table(node.name, node.data_type, var_vame)
    
    def calculate_alignment(self, type_str):
        if type_str in ("float", "double"):
            return "align 8"
        elif type_str == "i1":
            return "align 1"
        return "align 4"
    
    def calculate_array_type(self, element_type, dimensions):
        if dimensions:
            return f"[{dimensions[0]} x {self.calculate_array_type(element_type, dimensions[1:])}]"
        return element_type

    def process_value(self, value, indices, var_name, array_type, element_type_ir):
        if isinstance(value, list):
            for i, subvalue in enumerate(value):
                self.process_value(subvalue, indices + [i], var_name, array_type, element_type_ir)
        else:
            element_ptr = f"%{var_name}{''.join(f'_{idx}' for idx in indices)}_ptr"
            indices_str = ", ".join(f"i32 {idx}" for idx in [0] + indices)
            self.emit(f"{element_ptr} = getelementptr inbounds {array_type}, {array_type}* %{var_name}, {indices_str}")
            self.emit(f"store {element_type_ir} {value.value}, {element_type_ir}* {element_ptr}, align 16")

    def is_last_line_block_statement(self):
        """Check if the last line of the output is a block statement."""
        if not self.output:
            return False
        last_line = self.output[-1].strip()
        return last_line.endswith(":")
    
    def visit_ArrayAllocation(self, node: ArrayAllocation):
        element_type_ir = self.get_type(node.data_type[-1])
        dimensions = node.lengths
        var_name = f"x{self.var_count}"
        self.var_count += 1
        # dimensions is a list of the array dimensions
        array_type = self.calculate_array_type(element_type_ir, dimensions)
        
        self.emit(f"%{var_name} = alloca {array_type}, align 16")
        
        self.add_to_symbol_table(node.name, [array_type, node.data_type], var_name)

    def visit_ArrayDeclaration(self, node):
        element_type_ir = self.get_type(node.data_type[-1])
        dimensions = self.calculate_array_dimensions(node.value)
        var_name = f"x{self.var_count}"
        self.var_count += 1
        # dimensions is a list of the array dimensions
        array_type = self.calculate_array_type(element_type_ir, dimensions)
        
        self.emit(f"%{var_name} = alloca {array_type}, align 16")
        
        # Initialize the array with values
        self.process_value(node.value, [], var_name, array_type, element_type_ir)
        
        self.add_to_symbol_table(node.name, [array_type, node.data_type], var_name)

    def visit_ArrayAccess(self, node):
        var_type, var_name = self.lookup_symbol(node.name)
        _array_shape_str, _array_shape_list = var_type
        element_type_ir = self.get_type(_array_shape_list[-1])
        
        index_vals = [self.visit(index)[1] for index in node.index]
        array_access_str = ", ".join([f"i32 {index_val}" for index_val in index_vals])
        element_ptr = f"%{var_name}_element_ptr_{self.var_count}"
        self.var_count += 1
        self.emit(f"{element_ptr} = getelementptr inbounds {_array_shape_str}, {_array_shape_str}* %{var_name}, i32 0, {array_access_str}")
        
        load_var = f"%{node.name}_tmp{self.temp_count}"
        self.temp_count += 1
        self.emit(f"{load_var} = load {element_type_ir}, {element_type_ir}* {element_ptr}, align 16")
        return element_type_ir, load_var

    def visit_ArrayAssignmentStatement(self, node):
        var_type, var_name = self.lookup_symbol(node.target)
        _array_shape_str, _array_shape_list = var_type
        element_type_ir = self.get_type(_array_shape_list[-1])
        
        index_vals = [self.visit(index)[1] for index in node.index]
        array_access_str = ", ".join([f"i32 {index_val}" for index_val in index_vals])
        element_ptr = f"%{var_name}_element_ptr_{self.var_count}"
        self.var_count += 1
        self.emit(f"{element_ptr} = getelementptr inbounds {_array_shape_str}, {_array_shape_str}* %{var_name}, i32 0, {array_access_str}")
        
        value_type, value_ir = self.visit(node.value)
        self.emit(f"store {element_type_ir} {value_ir}, {element_type_ir}* {element_ptr}, align 16")

    def visit_VariableReference(self, node):
        var_type, var_name = self.lookup_symbol(node.name)
        var_type = self.get_type(var_type)
        tmp_var = f"%{node.name}_tmp{self.temp_count}"
        self.temp_count += 1
        if var_name.startswith("g"):
            self.emit(f"{tmp_var} = load {var_type}, {var_type}* @{var_name}, {self.calculate_alignment(var_type)}")
        elif var_name.startswith("x"):
            self.emit(f"{tmp_var} = load {var_type}, {var_type}* %{var_name}, {self.calculate_alignment(var_type)}")
        elif var_name.startswith("p"):
            return (var_type, f"%{var_name}")
        else:
            self.emit(f"{tmp_var} = alloca {var_type}, {self.calculate_alignment(var_type)}")
            self.emit(f"store {var_type} %{var_name}, {var_type}* {tmp_var}, {self.calculate_alignment(var_type)}")
        return (var_type, tmp_var)

    def visit_FunctionCall(self, node):
        function_return_type = self.function_signatures.get(
            node.name, "void"
        )  # Default to "void" if unknown
        arg_results = [self.visit(arg) for arg in node.arguments]
        arg_list = [f"{arg_type} {arg_val}" for arg_type, arg_val in arg_results]
        result_var = f"%tmp{self.temp_count}"
        self.temp_count += 1
        self.emit(
            f"{result_var} = call {self.get_type(function_return_type)} @{node.name}({', '.join(arg_list)})"
        )
        return (self.get_type(function_return_type), result_var)

    def function_statement(self, node, function_name):
        self.push_symbol_table()  # New scope for function
        arg_list = []
        if node.parameters and any(node.parameters):
            for param_name, param_type in node.parameters:
                arg_type = self.get_type(param_type)
                arg_name = f"p{self.var_count}"
                self.var_count += 1
                arg_list.append(f"{arg_type} %{arg_name}")
                # Add parameter to symbol table
                self.add_to_symbol_table(param_name, param_type, arg_name, "parameter")

        self.function_signatures[function_name] = node.return_type

        self.emit(
            f"define {self.get_type(node.return_type)} @{function_name}({', '.join(arg_list)}) {{"
        )

        self.indentation += 1

        # Add return variable to symbol table
        if node.return_type != "void":
            _return_var = f"retval{self.var_count}"
            self.var_count += 1
            self.emit(
                f"%{_return_var} = alloca {self.get_type(node.return_type)}, align 4"
            )
            self.add_to_symbol_table("return", node.return_type, _return_var)
            _return_block = f"retblock{self.var_count}"
            self.add_to_symbol_table("return_code_block", "block", _return_block)

        _params = self.symbol_table_stack[-1].get("params", {})
        if _params:
            for param_name, (param_type, param_var) in _params.items():
                arg_name = f"x{self.var_count}"
                self.var_count += 1
                self.emit(f"%{arg_name} = alloca {self.get_type(param_type)}, align 4")
                self.emit(
                    f"store {self.get_type(param_type)} %{param_var}, {self.get_type(param_type)}* %{arg_name}, align 4"
                )
                self.add_to_symbol_table(param_name, param_type, param_var)

        self.visit(node.body)
        self.indentation -= 1

        if node.return_type == "void":
            self.indentation += 1
            self.emit("ret void")
            self.indentation -= 1
        else:
            _return_block = self.lookup_symbol("return_code_block")[1]
            # Check if the last line was an empty block
            if self.is_last_line_block_statement():
                self.indentation += 1
                self.emit(f"br label %{_return_block}")
                self.indentation -= 1
            
            self.emit(f"{_return_block}:")
            self.indentation += 1
            ret_type, ret_val = self.lookup_symbol("return")
            var_name = f"%return{self.var_count}"
            self.var_count += 1
            self.emit(
                f"{var_name} = load {self.get_type(ret_type)}, {self.get_type(ret_type)}* %{ret_val}, align 4"
            )
            self.emit(f"ret {self.get_type(ret_type)} {var_name}")
            self.indentation -= 1

        self.emit("}")
        self.pop_symbol_table()

    def visit_FunctionStatement(self, node):
        self.function_statement(node, node.name)

    def visit_MainFunctionStatement(self, node):
        self.function_statement(node, "main")

    def visit_FunctionDeclaration(self, node):
        arg_list = [f"{self.get_type(param_type)}" for _, param_type in node.parameters]
        self.function_signatures[node.name] = node.return_type
        self.emit_global(
            f"declare {self.get_type(node.return_type)} @{node.name}({', '.join(arg_list)})"
        )

    def visit_StatementBlock(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ExpressionStatement(self, node):
        self.visit(node.expression)

    def visit_BreakStatement(self, node):
        _, _, end_block = self.get_while_blocks()
        self.emit(f"br label %{end_block}")
    
    def visit_ContinueStatement(self, node):
        cond_block, _, _ = self.get_while_blocks()
        self.emit(f"br label %{cond_block}")

    def visit_IfStatement(self, node):
        self.push_symbol_table()  # New scope for if block
        _, cond_var = self.visit(node.condition)
        if_count = self.temp_count
        self.temp_count += 1
        self.emit(f"br i1 {cond_var}, label %then{if_count}, label %else{if_count}")
        if self.indentation > 0:
            self.indentation -= 1
        self.emit(f"then{if_count}:")
        self.indentation += 1
        self.visit(node.then_block)
        self.emit(f"br label %ifcont{if_count}")
        self.indentation -= 1
        self.emit(f"else{if_count}:")
        self.indentation += 1
        if node.else_block:
            self.visit(node.else_block)
        self.emit(f"br label %ifcont{if_count}")

        self.indentation -= 1
        self.emit(f"ifcont{if_count}:")
        self.indentation += 1
        self.pop_symbol_table()

    def visit_WhileStatement(self, node):
        self.push_symbol_table()  # New scope for while block
        _while_count = self.temp_count
        self.temp_count += 1
        self.add_while_blocks_to_symbol_table(f"cond{_while_count}", f"body{_while_count}", f"end{_while_count}")
        self.emit(f"br label %cond{_while_count}")
        if self.indentation > 0:
            self.indentation -= 1
        self.emit(f"cond{_while_count}:")
        self.indentation += 1
        cond_var = self.visit(node.condition)
        cond_var_type, cond_var_name = cond_var
        self.emit(f"br i1 {cond_var_name}, label %body{_while_count}, label %end{_while_count}")
        self.indentation -= 1

        self.emit(f"body{_while_count}:")
        self.indentation += 1
        self.visit(node.body)
        self.emit(f"br label %cond{_while_count}")
        self.indentation -= 1

        self.emit(f"end{_while_count}:")
        self.indentation += 1
        self.pop_symbol_table()

    def visit_DoWhileStatement(self, node):
        self.push_symbol_table()
        _do_while_count = self.temp_count
        self.temp_count += 1
        self.add_while_blocks_to_symbol_table(f"cond{_do_while_count}", f"body{_do_while_count}", f"end{_do_while_count}")
        self.emit(f"br label %body{_do_while_count}")
        self.indentation -= 1
        self.emit(f"body{_do_while_count}:")
        self.indentation += 1
        self.visit(node.body)
        self.emit(f"br label %cond{_do_while_count}")
        self.indentation -= 1
        self.emit(f"cond{_do_while_count}:")
        self.indentation += 1
        cond_var = self.visit(node.condition)
        cond_var_type, cond_var_name = cond_var
        self.emit(f"br i1 {cond_var_name}, label %body{_do_while_count}, label %end{_do_while_count}")
        self.emit(f"end{_do_while_count}:")
        self.pop_symbol_table()

    def visit_AssignmentStatement(self, node):
        lit_type, value = self.visit(node.value)
        var_type, var_name = self.lookup_symbol(node.target)
        var_type = self.get_type(var_type)
        if var_name.startswith("g"):
            self.emit(f"store {lit_type} {value}, {var_type}* @{var_name}")
        else:
            self.emit(f"store {lit_type} {value}, {var_type}* %{var_name}")

    def visit_ReturnStatement(self, node):
        if node.value:
            ret_type, ret_val = self.visit(node.value)
            self.emit(
                f"store {ret_type} {ret_val}, {ret_type}* %{self.lookup_symbol('return')[1]}"
            )
            _return_code_block_var = self.lookup_symbol("return_code_block")[1]
            self.emit(f"br label %{_return_code_block_var}")
        else:
            self.emit("ret void")
    
    def visit_UnaryExpression(self, node):
        operand_type, operand_ir = self.visit(node.operand)
        result_var = f"%tmp{self.temp_count}"
        self.temp_count += 1

        if node.operator == "!":
            if operand_type != "i1":
                raise Exception(f"Invalid operand type for unary '!': {operand_type}")
            self.emit(f"{result_var} = xor i1 {operand_ir}, true")
            return ("i1", result_var)
        elif node.operator == "-":
            if operand_type == "i32":
                self.emit(f"{result_var} = sub i32 0, {operand_ir}")
                return ("i32", result_var)
            elif operand_type == "double":
                self.emit(f"{result_var} = fsub double 0.0, {operand_ir}")
                return ("double", result_var)
            else:
                raise Exception(f"Invalid operand type for unary '-': {operand_type}")
        else:
            raise Exception(f"Unsupported unary operator: {node.operator}")


    def visit_BinaryExpression(self, node):
        left_type, left = (
            self.visit(node.left)
            if not isinstance(node.left, VariableReference)
            else (
                self.get_type(self.lookup_symbol(node.left.name)[0]),
                self.visit(node.left),
            )
        )
        right_type, right = (
            self.visit(node.right)
            if not isinstance(node.right, VariableReference)
            else (
                self.get_type(self.lookup_symbol(node.right.name)[0]),
                self.visit(node.right),
            )
        )

        if isinstance(left, tuple):
            left_var_type, left_var_name = left  # Reference Unpack tuple
        else:
            left_var_type, left_var_name = left_type, left  # Is literal

        if isinstance(right, tuple):
            right_var_type, right_var_name = right  # Reference Unpack tuple
        else:
            right_var_type, right_var_name = right_type, right  # Is literal

        if node.operator in ("||", "&&"):
            if left_var_type != "i1" or right_var_type != "i1":
                raise Exception(f"Invalid operand types for logical operator '{node.operator}': {left_var_type} and {right_var_type}")

            true_block = f"true_block{self.temp_count}"
            false_block = f"false_block{self.temp_count}"
            end_block = f"end_block{self.temp_count}"
            result_var = f"%tmp{self.temp_count}"
            self.temp_count += 1

            if node.operator == "||":
                self.emit(f"br i1 {left_var_name}, label %{true_block}, label %{false_block}")
                self.indentation -= 1
                self.emit(f"{true_block}:")
                self.indentation += 1
                self.emit(f"br label %{end_block}")
                self.indentation -= 1

                self.emit(f"{false_block}:")
                self.indentation += 1
                self.emit(f"br label %{end_block}")
                self.indentation -= 1

                self.emit(f"{end_block}:")
                self.indentation += 1
                self.emit(f"{result_var} = phi i1 [ true, %{true_block} ], [ {right_var_name}, %{false_block} ]")
            elif node.operator == "&&":
                self.emit(f"br i1 {left_var_name}, label %{false_block}, label %{true_block}")
                self.indentation -= 1
                self.emit(f"{true_block}:")
                self.indentation += 1
                self.emit(f"br label %{end_block}")
                self.indentation -= 1

                self.emit(f"{false_block}:")
                self.indentation += 1
                self.emit(f"br label %{end_block}")
                self.indentation -= 1

                self.emit(f"{end_block}:")
                self.indentation += 1
                self.emit(f"{result_var} = phi i1 [ false, %{false_block} ], [ {right_var_name}, %{true_block} ]")

            return ("i1", result_var)

        # Handle type promotion
        if left_type == "float" and right_type == "double":
            # Promote left to double
            tmp_var = f"%tmp{self.temp_count}"
            self.temp_count += 1
            self.emit(f"{tmp_var} = fpext float {left_var_name} to double")
            left_var_name = tmp_var
            left_type = "double"
        elif left_type == "double" and right_type == "float":
            # Promote right to double
            tmp_var = f"%tmp{self.temp_count}"
            self.temp_count += 1
            self.emit(f"{tmp_var} = fpext float {right_var_name} to double")
            right_var_name = tmp_var
            right_type = "double"
        elif left_type == "i32" and right_type == "double":
            # Promote left to double
            tmp_var = f"%tmp{self.temp_count}"
            self.temp_count += 1
            self.emit(f"{tmp_var} = sitofp i32 {left_var_name} to double")
            left_var_name = tmp_var
            left_type = "double"
        elif left_type == "double" and right_type == "i32":
            # Promote right to double
            tmp_var = f"%tmp{self.temp_count}"
            self.temp_count += 1
            self.emit(f"{tmp_var} = sitofp i32 {right_var_name} to double")
            right_var_name = tmp_var
            right_type = "double"
        elif left_type == "i32" and right_type == "float":
            # Promote left to float
            tmp_var = f"%tmp{self.temp_count}"
            self.temp_count += 1
            self.emit(f"{tmp_var} = sitofp i32 {left_var_name} to float")
            left_var_name = tmp_var
            left_type = "float"
        elif left_type == "float" and right_type == "i32":
            # Promote right to float
            tmp_var = f"%tmp{self.temp_count}"
            self.temp_count += 1
            self.emit(f"{tmp_var} = sitofp i32 {right_var_name} to float")
            right_var_name = tmp_var
            right_type = "float"

        if left_type != right_type:
            raise Exception(
                f"Type mismatch in binary expression: {left_type} and {right_type}"
            )

        result_var = f"%tmp{self.temp_count}"
        self.temp_count += 1
        if (left_type in ("float", "double")) and node.operator in ["+", "-", "*", "/", "%", ">", "<", "==", ">=", "<="]:
            op_code = {
                "+": "fadd",
                "-": "fsub",
                "*": "fmul",
                "/": "fdiv",
                "%": "frem",
                ">": "fcmp ogt",
                "<": "fcmp olt",
                "==": "fcmp oeq",
                ">=": "fcmp oge",
                "<=": "fcmp ole",
                "!=": "fcmp one"
            }.get(node.operator)
        else:
            op_code = {
                "+": "add",
                "-": "sub",
                "*": "mul",
                "/": "sdiv",
                "%": "srem",
                "<<": "shl",
                ">>": "ashr",
                ">": "icmp sgt",
                "<": "icmp slt",
                "==": "icmp eq",
                "!=": "icmp ne",
                ">=": "icmp sge",
                "<=": "icmp sle"
            }.get(node.operator)

        if node.operator == "^":  # Call power function
            if left_type in ("float", "double"):
                self.emit(
                    f"{result_var} = call double @pow(double {left_var_name}, double {right_var_name})"
                )
            elif left_type == "i32":
                tmp_double_left = f"%tmp{self.temp_count}"
                self.temp_count += 1
                tmp_double_right = f"%tmp{self.temp_count}"
                self.temp_count += 1
                tmp_double_result = f"%tmp{self.temp_count}"
                self.temp_count += 1

                self.emit(f"{tmp_double_left} = sitofp i32 {left_var_name} to double")
                self.emit(f"{tmp_double_right} = sitofp i32 {right_var_name} to double")
                self.emit(
                    f"{tmp_double_result} = call double @pow(double {tmp_double_left}, double {tmp_double_right})"
                )
                self.emit(f"{result_var} = fptosi double {tmp_double_result} to i32")
            else:
                raise Exception(f"Unsupported type for power operator: {left_type}")
        elif not op_code:
            raise Exception(f"Unsupported operator: {node.operator}")
        else:
            self.emit(
                f"{result_var} = {op_code} {left_type} {left_var_name}, {right_var_name}"
            )
        return (left_type, result_var)

    def visit_Literal(self, node):
        if isinstance(node.value, bool):
            return ("i1", f"{int(node.value)}")
        elif isinstance(node.value, int):
            return ("i32", f"{node.value}")
        elif isinstance(node.value, float):
            return ("double", f"{node.value}")
        elif isinstance(node.value, str):
            self.emit_global(f"@.str{self.var_count} = private unnamed_addr constant [{len(node.value) + 1} x i8] c\"{node.value}\\00\"")
            str_ptr = f"getelementptr inbounds [{len(node.value) + 1} x i8], [{len(node.value) + 1} x i8]* @.str{self.var_count}, i32 0, i32 0"
            self.var_count += 1
            return (f"[{len(node.value) + 1} x i8]", str_ptr)

    def get_type(self, type_str):
        return {
            "int": "i32",
            "float": "double",
            "double": "double",
            "bool": "i1",
            "string": "i8",
            "void": "void",
        }.get(type_str, "void")

if __name__ == "__main__":
    ast = Program(
        global_variables=GlobalVariables(
            [
                VariableDeclaration(
                    var_kind="var", name="a", data_type="int", value=Literal(value=10)
                )
            ]
        ),
        declarations=[
            FunctionStatement(
                name="test",
                parameters=[("x", "int")],
                return_type="float",
                body=[
                    VariableDeclaration(
                        var_kind="var",
                        name="b",
                        data_type="int",
                        value=VariableReference(name="a"),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="c",
                        data_type="int",
                        value=VariableReference(name="a"),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="y",
                        data_type="int",
                        value=VariableReference(name="x"),
                    ),
                    AssignmentStatement(
                        target="a",
                        value=BinaryExpression(
                            operator="+",
                            left=Literal(value=20),
                            right=VariableReference(name="x"),
                        ),
                    ),
                    AssignmentStatement(
                        target="b",
                        value=BinaryExpression(
                            operator="+",
                            left=VariableReference(name="b"),
                            right=Literal(value=10),
                        ),
                    ),
                    ReturnStatement(value=VariableReference(name="b")),
                ],
            ),
            MainFunctionStatement(
                parameters=[None],
                return_type="int",
                body=[
                    VariableDeclaration(
                        var_kind="var",
                        name="f",
                        data_type="float",
                        value=FunctionCall(name="test", arguments=[Literal(value=11)]),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="g",
                        data_type="float",
                        value=FunctionCall(
                            name="test", arguments=[VariableReference(name="a")]
                        ),
                    ),
                    ReturnStatement(value=Literal(value=0)),
                ],
            ),
        ],
    )

    """ast = Program(
        global_variables=GlobalVariables(
            [
                VariableDeclaration(
                    var_kind="val", name="x", data_type="double", value=Literal(value=1)
                )
            ]
        ),
        declarations=[
            MainFunctionStatement(
                parameters=[None],
                return_type="void",
                body=[
                    VariableDeclaration(
                        var_kind="var", name="a", data_type="double", value=Literal(value=2)
                    ),
                    IfStatement(
                        condition=BinaryExpression(
                            operator=">",
                            left=VariableReference(name="a"),
                            right=VariableReference(name="x"),
                        ),
                        then_block=[
                            AssignmentStatement(
                                target="a",
                                value=BinaryExpression(
                                    operator="+",
                                    left=VariableReference(name="a"),
                                    right=Literal(value=1),
                                ),
                            )
                        ],
                        else_block=[
                            AssignmentStatement(
                                target="a",
                                value=BinaryExpression(
                                    operator="-",
                                    left=VariableReference(name="a"),
                                    right=Literal(value=1),
                                ),
                            )
                        ],
                    ),
                    ReturnStatement(value=None),
                ],
            )
        ],
    )"""

    # ast = Program(
    #     global_variables=GlobalVariables(
    #         [
    #             VariableDeclaration(
    #                 var_kind="val", name="x", data_type="int", value=Literal(value=1)
    #             ),
    #             VariableDeclaration(
    #                 var_kind="val", name="y", data_type="float", value=Literal(value=2.0)
    #             ),
    #         ]
    #     ),
    #     declarations=[
    #         FunctionStatement(
    #             name="test",
    #             parameters=[("a", "int"), ("b", "float")],
    #             return_type="float",
    #             body=[
    #                 IfStatement(
    #                     condition=BinaryExpression(
    #                         operator=">",
    #                         left=VariableReference(name="a"),
    #                         right=VariableReference(name="x"),
    #                     ),
    #                     then_block=[
    #                         ReturnStatement(
    #                             value=BinaryExpression(
    #                                 operator="+",
    #                                 left=VariableReference(name="y"),
    #                                 right=VariableReference(name="x"),
    #                             )
    #                         )
    #                     ],
    #                     else_block=[
    #                         ReturnStatement(
    #                             value=BinaryExpression(
    #                                 operator="-",
    #                                 left=VariableReference(name="y"),
    #                                 right=VariableReference(name="x"),
    #                             )
    #                         )
    #                     ],
    #                 )
    #             ],
    #         ),
    #         MainFunctionStatement(
    #             parameters=[None],
    #             return_type="void",
    #             body=[
    #                 VariableDeclaration(
    #                     var_kind="var", name="a", data_type="int", value=Literal(value=2)
    #                 ),
    #                 VariableDeclaration(
    #                     var_kind="var",
    #                     name="b",
    #                     data_type="float",
    #                     value=Literal(value=3.0),
    #                 ),
    #                 VariableDeclaration(
    #                     var_kind="var",
    #                     name="c",
    #                     data_type="float",
    #                     value=FunctionCall(
    #                         name="test",
    #                         arguments=[
    #                             VariableReference(name="a"),
    #                             VariableReference(name="b"),
    #                         ],
    #                     ),
    #                 ),
    #             ],
    #         ),
    #     ],
    # )

    # Test the LLVMIRGenerator
    """ast = Program(
        global_variables=GlobalVariables(
            [
                VariableDeclaration(
                    var_kind="val", name="x", data_type="int", value=Literal(value=1)
                ),
                VariableDeclaration(
                    var_kind="var", name="y", data_type="float", value=Literal(value=1.2)
                ),
            ]
        ),
        declarations=[
            FunctionStatement(
                name="test",
                parameters=[("z", "int"), ("w", "float")],
                return_type="float",
                body=[
                    VariableDeclaration(
                        var_kind="var",
                        name="k",
                        data_type="int",
                        value=VariableReference(name="z"),
                    ),
                    WhileStatement(
                        condition=BinaryExpression(
                            operator=">",
                            left=VariableReference(name="k"),
                            right=VariableReference(name="x"),
                        ),
                        body=[
                            AssignmentStatement(
                                target="k",
                                value=BinaryExpression(
                                    operator="-",
                                    left=VariableReference(name="k"),
                                    right=Literal(value=1),
                                ),
                            ),
                            AssignmentStatement(
                                target="y",
                                value=BinaryExpression(
                                    operator="+",
                                    left=VariableReference(name="y"),
                                    right=VariableReference(name="w"),
                                ),
                            ),
                        ],
                    ),
                    IfStatement(
                        condition=BinaryExpression(
                            operator="==",
                            left=VariableReference(name="k"),
                            right=Literal(value=0),
                        ),
                        then_block=[ReturnStatement(value=VariableReference(name="y"))],
                        else_block=None,
                    ),
                    IfStatement(
                        condition=BinaryExpression(
                            operator="==",
                            left=VariableReference(name="k"),
                            right=Literal(value=1),
                        ),
                        then_block=[
                            ReturnStatement(
                                value=BinaryExpression(
                                    operator="+",
                                    left=VariableReference(name="y"),
                                    right=Literal(value=1.0),
                                )
                            )
                        ],
                        else_block=[
                            AssignmentStatement(
                                target="w",
                                value=BinaryExpression(
                                    operator="+",
                                    left=VariableReference(name="w"),
                                    right=VariableReference(name="y"),
                                ),
                            )
                        ],
                    ),
                    ReturnStatement(value=VariableReference(name="w")),
                ],
            ),
            MainFunctionStatement(
                parameters=[None],
                return_type="void",
                body=[
                    VariableDeclaration(
                        var_kind="var", name="a", data_type="int", value=Literal(value=2)
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="b",
                        data_type="float",
                        value=Literal(value=3.0),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="c",
                        data_type="float",
                        value=FunctionCall(
                            name="test",
                            arguments=[
                                VariableReference(name="a"),
                                VariableReference(name="b"),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )"""
    ast = Program(
        global_variables=GlobalVariables([]),
        declarations=[
            MainFunctionStatement(
                parameters=[None],
                return_type="int",
                body=[
                    VariableDeclaration(
                        var_kind="var",
                        name="x",
                        data_type="string",
                        value=Literal(value="hello"),
                    ),
                    ReturnStatement(value=Literal(0)),
                ],
            )
        ],
    )
    ast = Program(
        global_variables=GlobalVariables([]),
        declarations=[
            MainFunctionStatement(
                parameters=[None],
                return_type="int",
                body=[
                    ArrayDeclaration(
                        var_kind="var",
                        name="x",
                        data_type=["array", "array", "int"],
                        value=[
                            [Literal(value=1), Literal(value=2)],
                            [Literal(value=3), Literal(value=4)],
                        ],
                    ),
                    ArrayDeclaration(
                        var_kind="var",
                        name="q",
                        data_type=["array", "int"],
                        value=[
                            Literal(value=1), Literal(value=2),
                            Literal(value=3), Literal(value=4)
                        ],
                    ),
                    ArrayDeclaration(
                        var_kind="var",
                        name="z",
                        data_type=["array", "array", "array", "int"],
                        value=[
                            [[Literal(value=1), Literal(value=2)], [Literal(value=3), Literal(value=4)]],
                            [[Literal(value=5), Literal(value=6)], [Literal(value=7), Literal(value=8)]],
                        ],
                        
                    ),
                    ArrayAssignmentStatement(
                        target="x",
                        index=[Literal(value=1), Literal(value=1)],
                        value=Literal(value=100),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="y",
                        data_type="int",
                        value=ArrayAccess(
                            name="x", index=[Literal(value=1), Literal(value=1)]
                        ),
                    ),
                    ReturnStatement(value=VariableReference(name="y")),
                ],
            )
        ],
    )
    ast = Program(
        global_variables=GlobalVariables([]),
        declarations=[
            MainFunctionStatement(
                parameters=[None],
                return_type="int",
                body=[
                    ArrayDeclaration(
                        var_kind="var",
                        name="x",
                        data_type=["array", "array", "int"],
                        value=[
                            [Literal(value=1), Literal(value=2)],
                            [Literal(value=3), Literal(value=4)],
                        ],
                    ),
                    ArrayDeclaration(
                        var_kind="var",
                        name="z",
                        data_type=["array", "int"],
                        value=[Literal(value=1), Literal(value=2), Literal(value=3)],
                    ),
                    ArrayDeclaration(
                        var_kind="var",
                        name="q",
                        data_type=["array", "array", "array", "int"],
                        value=[
                            [
                                [Literal(value=1), Literal(value=2)],
                                [Literal(value=3), Literal(value=4)],
                            ],
                            [
                                [Literal(value=5), Literal(value=6)],
                                [Literal(value=7), Literal(value=8)],
                            ],
                        ],
                    ),
                    ArrayAllocation(
                        var_kind="var",
                        name="v",
                        data_type=[("array", 2), "int"],
                        lengths=[2],
                    ),
                    ArrayAllocation(
                        var_kind="var",
                        name="w",
                        data_type=[("array", 3), ("array", 4), "int"],
                        lengths=[3, 4],
                    ),
                    ArrayAssignmentStatement(
                        target="w",
                        index=[Literal(value=1), Literal(value=1)],
                        value=Literal(value=100),
                    ),
                    ArrayAssignmentStatement(
                        target="w",
                        index=[Literal(value=2), Literal(value=2)],
                        value=Literal(value=200),
                    ),
                    ArrayAssignmentStatement(
                        target="w",
                        index=[Literal(value=1), Literal(value=2)],
                        value=Literal(value=300),
                    ),
                    ArrayAssignmentStatement(
                        target="w",
                        index=[Literal(value=2), Literal(value=3)],
                        value=Literal(value=400),
                    ),
                    ArrayAssignmentStatement(
                        target="v", index=[Literal(value=0)], value=Literal(value=100)
                    ),
                    ArrayAssignmentStatement(
                        target="v", index=[Literal(value=1)], value=Literal(value=200)
                    ),
                    ArrayAssignmentStatement(
                        target="x",
                        index=[Literal(value=1), Literal(value=1)],
                        value=Literal(value=100),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="y",
                        data_type="int",
                        value=ArrayAccess(
                            name="x", index=[Literal(value=1), Literal(value=1)]
                        ),
                    ),
                    ReturnStatement(value=VariableReference(name="y")),
                ],
            )
        ],
    )

    ast = Program(
        global_variables=GlobalVariables([]),
        declarations=[
            MainFunctionStatement(
                parameters=[None],
                return_type="int",
                body=[
                    VariableDeclaration(
                        var_kind="var",
                        name="x",
                        data_type="bool",
                        value=Literal(value=True),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="y",
                        data_type="bool",
                        value=Literal(value=False),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="z",
                        data_type="bool",
                        value=BinaryExpression(
                            operator="||",
                            left=UnaryExpression(
                                operator="!", operand=VariableReference(name="x")
                            ),
                            right=VariableReference(name="y"),
                        ),
                    ),
                    AssignmentStatement(
                        target="z",
                        value=UnaryExpression(
                            operator="!", operand=VariableReference(name="z")
                        ),
                    ),
                    IfStatement(
                        condition=BinaryExpression(
                            operator="&&",
                            left=VariableReference(name="x"),
                            right=VariableReference(name="y"),
                        ),
                        then_block=[ReturnStatement(value=Literal(value=1))],
                        else_block=[ReturnStatement(value=Literal(value=0))],
                    ),
                ],
            )
        ],
    )
    ast = Program(
        global_variables=GlobalVariables([]),
        declarations=[
            MainFunctionStatement(
                parameters=[None],
                return_type="int",
                body=[
                    VariableDeclaration(
                        var_kind="var",
                        name="x",
                        data_type="int",
                        value=Literal(value=2),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="y",
                        data_type="int",
                        value=BinaryExpression(
                            operator="^",
                            left=VariableReference(name="x"),
                            right=Literal(value=3),
                        ),
                    ),
                    ReturnStatement(value=VariableReference(name="y")),
                ],
            )
        ],
    )

    ast = Program(
        global_variables=GlobalVariables([]),
        declarations=[
            FunctionDeclaration(
                name="test", parameters=[("x", "int"), ("y", "int")], return_type="int"
            ),
            MainFunctionStatement(
                parameters=[None],
                return_type="int",
                body=[
                    VariableDeclaration(
                        var_kind="var",
                        name="x",
                        data_type="int",
                        value=Literal(value=1),
                    ),
                    VariableDeclaration(
                        var_kind="var",
                        name="y",
                        data_type="int",
                        value=Literal(value=2),
                    ),
                    ReturnStatement(
                        value=FunctionCall(
                            name="test",
                            arguments=[
                                VariableReference(name="x"),
                                VariableReference(name="y"),
                            ],
                        )
                    ),
                ],
            ),
        ],
    )
    generator = LLVMIRGenerator(ast)
    llvm_ir = generator.generate()
    print(ast)
    print(llvm_ir)
