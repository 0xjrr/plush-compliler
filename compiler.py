import sys
import os
import json
from grammar.grammar import parser
from checker import checker
from gen_llvm_ir import generator as llvmir_c
from tree.ast_nodes import MainFunctionStatement
import json_converter
import print_tree

def compile_program(filename, print_tree_flag=False, pretty=False, typecheck_print=False):
    with open(filename, "r") as f:
        source_code = f.read()

    # Parse the source code
    result = parser.parse(source_code)

    if result is None:
        print(f"Syntax error in file: {filename}")
        return
    
    if result.imports:
        for import_file in result.imports:
            import_file = import_file.replace('"', '')
            folder = os.path.dirname(filename)
            import_file_path = os.path.join(folder, f"{import_file}.pl")

            if os.path.exists(import_file_path):
                with open(import_file_path, "r") as import_f:
                    import_source_code = import_f.read()
                import_result = parser.parse(import_source_code)
                
                if import_result is None:
                    print(f"Syntax error in import file: {import_file_path}")
                    return
                
                # Remove MainFunctionStatement from import_result.declarations and append to result.declarations
                not_main_function_statements = [
                    decl for decl in import_result.declarations if not isinstance(decl, MainFunctionStatement)
                ]

                result.declarations = not_main_function_statements + result.declarations
            else:
                print(f"Import file '{import_file_path}' not found.")
                return

    # Perform semantic checking
    analyzer = checker.Analyzer()
    try:
        analyzer.check_program(result)
        errors = analyzer.errors
        #print("Typecheck errors:", errors)
    except Exception as e:
        print(f"Semantic error: {str(e)}")
        

    # Generate LLVM IR
    generator = llvmir_c.LLVMIRGenerator(result)
    llvm_ir = generator.generate()

    if print_tree_flag:
        # Print the AST as JSON
        json_ast = json_converter.convert_ast_to_json(result)
        print(json_ast)
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
    elif "--typecheck_print" in sys.argv:
        sys.argv.remove("--typecheck_print")
        compile_program(sys.argv[1], typecheck_print=True)
    else:
        compile_program(sys.argv[1])
