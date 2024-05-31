# PLush Compiler

Welcome to the official repository for the PLush Compiler, developed as part of the compilers course. This compiler is designed to translate PLush programming language code into executable machine code. PLush is a simple, yet powerful programming language designed to teach the fundamentals of programming language design and compiler construction.

## Language Description

PLush is designed with simplicity and readability in mind, supporting basic programming constructs and types. Here's a quick overview of the language features:

- **Comments**: Start with `#` and end at the end of the line.
- **Whitespace Insensitivity**: Spaces, tabs, and newlines are ignored outside of string literals.
- **Declarations and Definitions**: Programs are composed of declarations or definitions that precede the main body.
- **Data Types**: Supports `double`, `int`, `string`, `void`, and parametric arrays (e.g., `[double]`, `[int]`, `[[int]]`).
- **Variables**: Supports both constant (`val`) and mutable (`var`) variables.
- **Functions**: Functions can either be defined with a body of code or declared for external linkage.
- **Control Structures**: Includes `if` statements with optional `else` blocks and `while` loops.
- **Expressions**: Supports binary operators with C-like precedence, unary operators, literals (boolean, integer, float, string), and variable/index access.
- **Imports**: Allows for modularity by importing functions from other files.

## Plush Programming Language

### Overview

Plush is a statically-typed, high-level programming language. It supports various features such as functions, variable declarations, control structures, arrays, and more. This document serves as a comprehensive guide to understanding the syntax and grammar of Plush.

### Table of Contents

1. [Installation](#installation)
2. [Basic Syntax](#basic-syntax)
   - [Comments](#comments)
   - [Data Types](#data-types)
   - [Variables](#variables)
3. [Control Structures](#control-structures)
   - [If Statements](#if-statements)
   - [Loops](#loops)
4. [Functions](#functions)
5. [Operators](#operators)
6. [Arrays](#arrays)
7. [Imports](#imports)
8. [Examples](#examples)

## Installation

To use Plush, you need to have Python installed along with the PLY library. You can install PLY using pip:

```bash
pip install ply
```

Clone the Plush repository and navigate to the directory:

```bash
git clone <repository-url>
cd plush
```

## Basic Syntax

### Comments

Comments in Plush are denoted using the `#` symbol:

```plush
# This is a comment
```

### Data Types

Plush supports several basic data types:

- `int`: Integer
- `float`: Floating-point number
- `string`: String of characters
- `bool`: Boolean (`true` or `false`)

### Variables

Variables can be declared using the `var` or `val` keywords. `var` declares a mutable variable, while `val` declares an immutable variable.

```plush
var x : int := 10;
val y : float := 20.5;
```

## Control Structures

### If Statements

Conditional execution can be performed using `if` and `else` statements:

```plush
if (x > y) {
    # Code to execute if x is greater than y
} else {
    # Code to execute if x is not greater than y
}
```

### Loops

Plush supports `while` and `do-while` loops:

```plush
while (x < 10) {
    x++;
}

do {
    x--;
} while (x > 0);
```

## Functions

Functions in Plush are declared using the `function` keyword. The `main` function is the entry point of the program.

```plush
function main(): void {
    var x : int := 1;
    var y : float := 2.0;
    var result : float := compute(x, y);
}

function compute(x: int, y: float): float {
    return x + y;
}
```

## Operators

Plush supports a variety of operators for arithmetic, comparison, logical, and bitwise operations:

- Arithmetic: `+`, `-`, `*`, `/`, `%`, `^`
- Comparison: `>`, `<`, `>=`, `<=`, `==`, `!=`
- Logical: `and`, `or`, `not`
- Bitwise: `&`, `|`, `~`, `<<`, `>>`
- Increment and Decrement: `++`, `--`

## Arrays

Arrays in Plush can be declared with fixed sizes and can be nested:

```plush
var arr : [int] := [1, 2, 3];
var arr2 : [[int]] := [[1, 2], [3, 4]];
var arr3 : [[[int]]] := [[[1, 2], [3, 4]], [[5, 6], [7, 8]]];
var arr4 : []double := [1.0, 1.2, 1.4];

# allocation
arr : [3][4]int;

var arr_value : int := arr[2];
arr[1] := 10;
```

## Imports

The `import` statement in Plush allows you to include functions from other files, promoting modularity and code reuse.

### Syntax

```plush
import filename;
```

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

### How It Works

1. **Define Functions in a Separate File**: Create a file (e.g., `math_functions.pl`) and define the functions you want to reuse.
2. **Import the File**: Use the `import` statement in your main file (e.g., `main.pl`) to include the functions defined in `math_functions.pl`.
3. **Call Imported Functions**: After importing, you can call the functions as if they were defined in the main file.

## Examples

### Example 1: Basic Function

```plush
function add(a: int, b: int): int {
    return a + b;
}

function main(): void {
    var result : int := add(5, 10);
    print(result);
}
```

### Example 2: Control Structures

```plush
function main(): void {
    var x : int := 0;
    while (x < 5) {
        if (x == 3) {
            break;
        }
        x++;
    }

    var y : int := 10;
    do {
        y--;
    } while (y > 5);
}
```

### Example 3: Arrays and Loops

```plush
function main(): void {
    var arr : [int] := [1, 2, 3, 4, 5];
    var sum : int := 0;

    for (var i : int := 0; i < len(arr); i++) {
        sum += arr[i];
    }

    print(sum);
}
```

## Next Steps

This guide provides a basic understanding of the Plush programming language. For more detailed information, please refer to the examples and experiment with the language using the provided parser and lexer. Happy coding!

## Getting Started

To get started with the PLush Compiler, clone this repository to your local machine:

```bash
git clone https://github.com/0xjrr/plush-compiler.git
```

Ensure you have the necessary environment to compile and run the compiler. Instructions for setting up the environment are provided in the subsequent sections.

## Installation

Before you can use the PLush Compiler, you need to set up your environment:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/0xjrr/plush-compiler.git
   ```
2. **Build the Compiler** (assuming a UNIX-like environment):
   ```bash
   cd plush-compiler
   ./setup.sh
   ```

## Debugging

1. **Chmod**:
   ```bash
   chmod +x setup.sh
   chmod +x plush
   ```

## Usage

To compile a PLush program, use the following command:

```bash
./plush hello_world.pl
```

To print the Abstract Syntax Tree (AST) of a PLush program, use:

```bash
./plush --tree hello_world.pl
```

To compile and execute a PLush program, use:

```bash
./plush --exec hello_world.pl
```

To compile, execute, and print the output of a PLush program, use:

```bash
./plush --exec --out hello_world.pl
```

To compile and link multiple files (e.g., `.c`, `.o`, `.ll`, and `.pl` files) into a single executable:

```bash
./plush file1.c

 file2.o file3.ll hello_world.pl
```

This will compile and link all the specified files into an executable named `output_executable`.

## Contributing

Contributions to the PLush Compiler are welcome! Whether you're fixing bugs, adding new features, or improving the documentation, your help is appreciated. Please send pull requests through GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This compiler is developed as part of the compilers course.
