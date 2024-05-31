import sys
import os
import json
from grammar.grammar import parser
from checker import checker
from gen_llvm_ir import generator as llvmir_c
import json_converter
import print_tree

def compile_program(filename, print_tree_flag=False, pretty=False):
    with open(filename, "r") as f:
        source_code = f.read()

    # Parse the source code
    result = parser.parse(source_code)

    # If there's a syntax error, print it and exit
    if result is None:
        print(f"Syntax error in file: {filename}")
        return

    # Perform semantic checking
    analyzer = checker.Analyzer()
    try:
        analyzer.check_program(result)
        errors = analyzer.errors
        print("Typecheck errors:", errors)
    except Exception as e:
        print(f"Semantic error: {str(e)}")
        return

    # Generate LLVM IR
    generator = llvmir_c.LLVMIRGenerator(result)
    llvm_ir = generator.generate()

    if print_tree_flag:
        # Print the AST as JSON
        json_ast = json_converter.convert_ast_to_json(result)
        print(json.dumps(json_ast, indent=4))
    elif pretty:
        # Print the AST in a pretty format
        print_tree.pretty_print(result, indent=0)
    else:
        # Save the LLVM IR to a file and return its path
        output_filename = os.path.splitext(filename)[0] + ".ll"
        with open(output_filename, "w") as f:
            f.write(llvm_ir)
        print(output_filename)

if __name__ == "__main__":
    if "--tree" in sys.argv:
        sys.argv.remove("--tree")
        compile_program(sys.argv[1], print_tree_flag=True)
    elif "--pretty" in sys.argv:
        sys.argv.remove("--pretty")
        compile_program(sys.argv[1], pretty=True)
    else:
        compile_program(sys.argv[1])