import ast_nodes
from grammar import parser
import semantics_check
import llvmir_compiler
import json_converter
import os

if __name__ == "__main__":
    with open("./example.pl", "r") as f:
        s = f.read()
    
    result = parser.parse(s)
    print(result)
    semantics_checker = semantics_check.TypeChecker()
    semantics_checker.check_program(result)
    generator = llvmir_compiler.LLVMIRGenerator(result)
    llvm_ir = generator.generate()
    json_ast = json_converter.convert_ast_to_json(result)
    # Save the LLVM IR to a file
    with open("./output.ll", "w+") as f:
        # print current directory
        print("Writing LLVM IR to output.ll")
        f.write(llvm_ir)
    print(llvm_ir)