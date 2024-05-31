import sys
import os
import json
from grammar import parser
import semantics_check
import llvmir_compiler
import json_converter

def compile_program(filename, print_tree=False):
    with open(filename, "r") as f:
        source_code = f.read()

    # Parse the source code
    result = parser.parse(source_code)

    # If there's a syntax error, print it and exit
    if result is None:
        print(f"Syntax error in file: {filename}")
        return

    # Perform semantic checking
    semantics_checker = semantics_check.TypeChecker()
    try:
        semantics_checker.check_program(result)
    except Exception as e:
        print(f"Semantic error: {str(e)}")
        return

    # Generate LLVM IR
    generator = llvmir_compiler.LLVMIRGenerator(result)
    llvm_ir = generator.generate()

    if print_tree:
        # Print the AST as JSON
        json_ast = json_converter.convert_ast_to_json(result)
        print(json.dumps(json_ast, indent=4))
    else:
        # Save the LLVM IR to a file and return its path
        output_filename = os.path.splitext(filename)[0] + ".ll"
        with open(output_filename, "w") as f:
            f.write(llvm_ir)
        print(output_filename)

if __name__ == "__main__":
    if "--tree" in sys.argv:
        sys.argv.remove("--tree")
        compile_program(sys.argv[1], print_tree=True)
    else:
        compile_program(sys.argv[1])
