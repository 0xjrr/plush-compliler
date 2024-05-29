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

    def calculate_array_size(self, value):
        if isinstance(value, list):
            return len(value) * self.calculate_array_size(value[0])
        return 1

    def calculate_array_dimensions(self, value):
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
            return [len(value), len(value[0])]
        return [0, 0]

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

    def visit_ArrayDeclaration(self, node):
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
        
        self.add_to_symbol_table(node.name, [array_type, node.data_type], var_name)

    def visit_ArrayAccess(self, node):
        var_type, var_name = self.lookup_symbol(node.name)
        _array_shape_str, _array_shape_list = var_type
        element_type_ir = self.get_type(_array_shape_list[-1])
        
        index_vals = [self.visit(index)[1] for index in node.index]
        array_access_str = ", ".join([f"i32 {index_val}" for index_val in index_vals])
        element_ptr = f"%{var_name}_element_ptr"
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
        element_ptr = f"%{var_name}_element_ptr"
        self.emit(f"{element_ptr} = getelementptr inbounds {_array_shape_str}, {_array_shape_str}* %{var_name}, i32 0, {array_access_str}")
        
        value_type, value_ir = self.visit(node.value)
        self.emit(f"store {element_type_ir} {value_ir}, {element_type_ir}* {element_ptr}, align 16")

    def visit_VariableReference(self, node):
        var_type, var_name = self.lookup_symbol(node.name)
        var_type = self.get_type(var_type)
        tmp_var = f"%{node.name}_tmp{self.temp_count}"
        self.temp_count += 1
        if var_name.startswith("g"):
            self.emit(f"{tmp_var} = load {var_type}, {var_type}* @{var_name}, align 4")
        elif var_name.startswith("x"):
            self.emit(f"{tmp_var} = load {var_type}, {var_type}* %{var_name}, align 4")
        elif var_name.startswith("p"):
            return (var_type, f"%{var_name}")
        else:
            self.emit(f"{tmp_var} = alloca {var_type}, align 4")
            self.emit(f"store {var_type} %{var_name}, {var_type}* {tmp_var}, align 4")
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

    def visit_StatementBlock(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_IfStatement(self, node):
        self.push_symbol_table()  # New scope for if block
        _, cond_var = self.visit(node.condition)
        if_count = self.temp_count
        self.temp_count += 1
        self.emit(f"br i1 {cond_var}, label %then{if_count}, label %else{if_count}")

        self.emit(f"then{if_count}:")
        self.indentation += 1
        self.visit(node.then_block)
        self.indentation -= 1
        self.emit(f"br label %ifcont{if_count}")
        self.emit(f"else{if_count}:")
        self.indentation += 1
        if node.else_block:
            self.visit(node.else_block)
        self.indentation -= 1
        self.emit(f"br label %ifcont{if_count}")

        self.emit(f"ifcont{if_count}:")
        self.pop_symbol_table()

    def visit_WhileStatement(self, node):
        self.push_symbol_table()  # New scope for while block
        _while_count = self.temp_count
        self.temp_count += 1
        self.emit(f"br label %cond{_while_count}")
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
        self.pop_symbol_table()

    def visit_DoWhileStatement(self, node):
        self.push_symbol_table()
        _do_while_count = self.temp_count
        self.temp_count += 1
        self.emit(f"br label %body{_do_while_count}")
        self.emit(f"body{_do_while_count}:")
        self.indentation += 1
        self.visit(node.body)
        self.indentation -= 1
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
        if (
            left_type in ("float", "double") or left_type in ("float", "double")
        ) and node.operator in ["+", "-", "*", "/", "%", ">", "<", "=="]:
            op_code = {
                "+": "fadd",
                "-": "fsub",
                "*": "fmul",
                "/": "fdiv",
                "%": "frem",
                ">": "fcmp ogt",
                "<": "fcmp olt",
                "==": "fcmp oeq",
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
            }.get(node.operator)

        if not op_code:
            raise Exception(f"Unsupported operator: {node.operator}")

        self.emit(
            f"{result_var} = {op_code} {left_type} {left_var_name}, {right_var_name}"
        )
        return (left_type, result_var)

    def visit_Literal(self, node):
        if isinstance(node.value, int):
            return ("i32", f"{node.value}")
        elif isinstance(node.value, float):
            return ("double", f"{node.value}")
        elif isinstance(node.value, bool):
            return ("i1", f"{int(node.value)}")
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
    generator = LLVMIRGenerator(ast)
    llvm_ir = generator.generate()
    print(ast)
    print(llvm_ir)
