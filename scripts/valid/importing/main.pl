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