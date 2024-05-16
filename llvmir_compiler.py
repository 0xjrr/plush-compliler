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
        # self.transform_ast(self.program)

    def transform_ast(self, program: Program):
        literal_to_var: Dict[tuple, str] = {}  # Maps (value, type): variable name
        global_var_index = 1

        def generate_var_name(literal):
            nonlocal global_var_index
            dtype = type(literal.value).__name__
            var_name = f"const_{dtype}_{global_var_index}"
            global_var_index += 1
            return var_name

        def process_node(node):
            if isinstance(node, Literal):
                literal_key = (node.value, type(node.value).__name__)
                if literal_key not in literal_to_var:
                    var_name = generate_var_name(node)
                    literal_to_var[literal_key] = var_name
                    # Create and add the global variable
                    new_global_var = VariableDeclaration(
                        var_kind="val",
                        name=var_name,
                        data_type=type(node.value).__name__.lower(),
                        value=node,  # Use the literal itself as the initial value
                    )
                    program.global_variables.declarations.append(new_global_var)
                # Replace the literal with a variable reference
                return VariableReference(name=literal_to_var[literal_key])
            elif isinstance(node, list):
                return [process_node(elem) for elem in node]
            elif hasattr(node, "__dataclass_fields__"):
                for field in node.__dataclass_fields__:
                    elem = getattr(node, field)
                    if isinstance(elem, (ASTNode, list)):
                        setattr(node, field, process_node(elem))
            return node

        # Process all declarations
        for declaration in program.declarations:
            process_node(declaration)

    def emit(self, line):
        self.output.append("    " * self.indentation + line)

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

    def add_to_symbol_table(self, name, var_type, _var_name):
        if self.symbol_table_stack:
            self.symbol_table_stack[-1][name] = (var_type, _var_name)

    def lookup_symbol(self, name):
        # Search from the top of the stack downwards
        for table in reversed(self.symbol_table_stack):
            if name in table:
                return table[name]
        raise Exception(f"Undefined variable '{name}'")

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
        lit_type, value = self.visit(node.value) if node.value else "0"
        if self.declaration_scope == "global":
            var_vame = f"g{self.var_count}"
            self.var_count += 1
            if type_ir in ("float", "double"):
                self.emit(f"@{var_vame} = global {type_ir} {float(value)}, align 8")
            else:
                self.emit(f"@{var_vame} = global {type_ir} {value}, align 4")
        else:
            var_vame = f"x{self.var_count}"
            self.var_count += 1
            # Allocate memory for the variable
            self.emit(f"%{var_vame} = alloca {type_ir}, align 4")
            # Store the initial value
            if node.value:
                if isinstance(node.value, Literal):
                    if type_ir in ("float", "double"):
                        self.emit(f"store {type_ir} {float(value)}, {type_ir}* %{var_vame}, align 8")
                    else:
                        self.emit(f"store {type_ir} {value}, {type_ir}* %{var_vame}, align 4")
                else:
                    if lit_type in ("float", "double"):
                        self.emit(f"store {lit_type} {value}, {lit_type}* %{var_vame}, align 8")
                    else:
                        self.emit(f"store {type_ir}* {value}, {type_ir}* %{var_vame}, align 4")

        self.add_to_symbol_table(node.name, node.data_type, var_vame)

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

    def visit_FunctionDeclaration(self, node):
        self.push_symbol_table()  # New scope for function
        arg_list = []
        for param_name, param_type in node.parameters:
            arg_type = self.get_type(param_type)
            arg_name = f"p{self.var_count}"
            self.var_count += 1
            arg_list.append(f"{arg_type} %{arg_name}")
            # Add parameter to symbol table
            self.add_to_symbol_table(param_name, param_type, arg_name)

        self.function_signatures[node.name] = node.return_type

        self.emit(
            f"define {self.get_type(node.return_type)} @{node.name}({', '.join(arg_list)}) {{"
        )
        self.indentation += 1
        self.visit(node.body)
        self.indentation -= 1
        self.emit("}")
        self.pop_symbol_table()

    def visit_MainFunctionDeclaration(self, node):
        if node.parameters and any(node.parameters):
            arg_list = ", ".join(
                f"{self.get_type(p.type)} %{p.name}" for p in node.parameters
            )
        else:
            arg_list = ""

        self.emit(f"define {self.get_type(node.return_type)} @main({arg_list}) {{")
        self.indentation += 1
        self.visit(node.body)
        if node.return_type == "void":
            self.emit("ret void")
        self.indentation -= 1
        self.emit("}")

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
        self.emit("br label %cond")
        self.emit("cond:")
        self.indentation += 1
        cond_var = self.visit(node.condition)
        cond_var_type, cond_var_name = cond_var
        self.emit(f"br i1 {cond_var_name}, label %body, label %end")
        self.indentation -= 1

        self.emit("body:")
        self.indentation += 1
        self.visit(node.body)
        self.emit("br label %cond")
        self.indentation -= 1

        self.emit("end:")
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
            self.emit(f"ret {ret_type} {ret_val}")
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
            str_ptr = f"i8* getelementptr inbounds ([{len(node.value) + 1} x i8], [{len(node.value) + 1} x i8]* @.str, i32 0, i32 0)"
            return ("i8*", str_ptr)

    def get_type(self, type_str):
        return {
            "int": "i32",
            "float": "double",
            "double": "double",
            "bool": "i1",
            "void": "void",
        }.get(type_str, "void")


'''ast = Program(
    global_variables=GlobalVariables(
        [
            VariableDeclaration(
                var_kind="val", name="x", data_type="double", value=Literal(value=1)
            )
        ]
    ),
    declarations=[
        MainFunctionDeclaration(
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
)'''

ast = Program(
    global_variables=GlobalVariables(
        [
            VariableDeclaration(
                var_kind="val", name="x", data_type="int", value=Literal(value=1)
            ),
            VariableDeclaration(
                var_kind="val", name="y", data_type="float", value=Literal(value=2.0)
            ),
        ]
    ),
    declarations=[
        FunctionDeclaration(
            name="test",
            parameters=[("a", "int"), ("b", "float")],
            return_type="float",
            body=[
                IfStatement(
                    condition=BinaryExpression(
                        operator=">",
                        left=VariableReference(name="a"),
                        right=VariableReference(name="x"),
                    ),
                    then_block=[
                        ReturnStatement(
                            value=BinaryExpression(
                                operator="+",
                                left=VariableReference(name="y"),
                                right=VariableReference(name="x"),
                            )
                        )
                    ],
                    else_block=[
                        ReturnStatement(
                            value=BinaryExpression(
                                operator="-",
                                left=VariableReference(name="y"),
                                right=VariableReference(name="x"),
                            )
                        )
                    ],
                )
            ],
        ),
        MainFunctionDeclaration(
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
)

# Test the LLVMIRGenerator
'''ast = Program(
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
        FunctionDeclaration(
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
        MainFunctionDeclaration(
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
)'''
generator = LLVMIRGenerator(ast)
llvm_ir = generator.generate()
print(ast)
print(llvm_ir)
