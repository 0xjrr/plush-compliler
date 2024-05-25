import ast_nodes
from grammar import parser
import semantics_check
import llvmir_compiler
import os

if __name__ == "__main__":
    s = """
    function main(): int {
        var x : int := 120;
        var y : int := 10;
        x++;
        y--;
        ++x;
        --y;
        --x;
        x += 1;
        y -= 1;
        x := x + y    + (x                                          *4);
        return x + y;
    }
    """
    result = parser.parse(s)
    semantics_checker = semantics_check.TypeChecker()
    semantics_checker.check_program(result)
    generator = llvmir_compiler.LLVMIRGenerator(result)
    llvm_ir = generator.generate()
    # Save the LLVM IR to a file
    with open("./output.ll", "w+") as f:
        # print current directory
        print("Current directory: ", os.getcwd())

        print("Writing LLVM IR to output.ll")
        f.write(llvm_ir)
    print(llvm_ir)