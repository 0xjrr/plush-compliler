# PLush Compiler Project: Final Phase Report

Author: José Ricado Ribeiro, 62761, FCUL, 2024

## Introduction

In this final phase of the PLush Compiler project, I focused on implementing several key features to enhance the functionality and usability of the PLush programming language. These features include the `import` functionality, break and continue statements, increment and decrement operations, various print statements, and the power operator. This report provides an overview of these features, their implementation, and their integration into the compiler.

## Import Functionality

### Purpose

The `import` statement allows PLush programs to include functions and variables defined in separate files. This promotes better code organization and reusability, making it easier to manage larger projects.

### Syntax

The syntax for the `import` statement in PLush is straightforward:

```plush
import filename;
```

This statement can be placed at the beginning of a PLush file to import all functions and global variables from the specified file.

### Implementation Details

#### AST Construction

1. **Main File Parsing**:

   - The main PLush file is parsed to generate its Abstract Syntax Tree (AST). This AST represents the structure of the program, including all declarations and definitions.

2. **Import File Parsing**:
   - Each file specified in an `import` statement is parsed separately to generate its own AST. These ASTs represent the structure of the imported files.

#### AST Merging

3. **Declaration Extraction**:

   - From the ASTs of the imported files, all declarations and definitions that are not `MainFunctionStatement` are extracted. This includes functions, variable declarations, and other relevant constructs.

4. **AST Integration**:
   - The extracted declarations and definitions from the imported files are integrated into the AST of the main file. This is done by appending the extracted nodes to the main file's AST.

#### LLVM IR Translation

5. **LLVM IR Generation**:
   - After integrating the ASTs, the combined AST is translated into LLVM Intermediate Representation (IR). This process ensures that the imported functions are correctly linked and available for use in the main program.

### Example

#### File: `math_functions.pl`

```plush
function fibonacci_recursive(val n:int) : int {
    if n <= 1 {
        return n;
    }
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}
```

#### File: `main.pl`

```plush
import math_functions;

function main(val args:[string]) {
    val n : int := 10;

    print_string("Fibonacci sequence (recursive):");
    var i : int := 0;
    while i <= n {
        var fib_value : int := fibonacci_recursive(i);
        print_int(fib_value);
        i := i + 1;
    }
}
```

### Process

1. The `main.pl` file is parsed to generate its AST.
2. The `math_functions.pl` file is parsed to generate its AST.
3. Declarations from `math_functions.pl` (excluding `MainFunctionStatement`) are moved to the AST of `main.pl`.
4. The combined AST is then translated into LLVM IR, ensuring that the imported functions are correctly integrated and available for use in the main program.

## Additional Features

### Break and Continue Statements

Implemented support for `break` and `continue` statements within loops:

- **Break Statement**: Exits the current loop.
- **Continue Statement**: Skips the remaining statements in the current iteration and proceeds to the next iteration of the loop.

### Increment and Decrement Operations

Implemented support for increment and decrement operations:

- Post-increment: `i++`
- Pre-increment: `++i`
- Post-decrement: `i--`
- Pre-decrement: `--i`
- Increment by value: `i += 1`
- Decrement by value: `i -= 1`

These operations are essential for concise and readable loop constructs and other iterative processes.

### Print Statements

Implemented various print statements to output different data types:

- `print_int`: Prints an integer value.
- `print_double`: Prints a double value.
- `print_string`: Prints a string value.
- `printf`: A versatile print function that uses C's `printf` through the Foreign Function Interface (FFI).

#### Example:

```plush
print_int(42);
print_double(3.14);
print_string("Hello, World!");
printf("Formatted output: %d, %f, %s", 42, 3.14, "Hello");
```

### Power Operator

Implemented the power operator `^` using C's `pow` function through the Foreign Function Interface (FFI). This allows for exponentiation operations within PLush programs. The result if the variable assignment has type `int` is casted from the double that returns from the `pow` function to an `int`.

#### Example:

```plush
var result : double := 2.0 ^ 3.0;  # Equivalent to pow(2.0, 3.0)
```

## Struggles and Workarounds

### Type and Semantic Checking

One significant challenge I faced was implementing the type and semantic checker. This component is crucial for ensuring that the code adheres to type rules and semantic constraints, preventing many common programming errors. However, due to time constraints and the complexity of this feature, the type and semantic checker is currently semi-complete.

- **Current Implementation**:

  - The compiler includes a call to the type and semantic checker function.
  - The checker is not fully reliable and often throws errors incorrectly.
  - To prioritize getting the compiler to function, these errors are bypassed, allowing the compilation process to continue.

- **Future Work**:
  - Completing and refining the type and semantic checker to ensure robust error checking and reliable enforcement of language rules.
