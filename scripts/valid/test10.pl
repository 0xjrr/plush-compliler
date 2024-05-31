# Function to calculate Fibonacci using recursion
function fibonacci_recursive(val n:int) : int {
    if n <= 1 {
        return n;
    }
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

function main(val args:[string]) {
    val n : int := 10;

    # Calculate Fibonacci using recursion
    print_string("Fibonacci sequence (recursive):");
    var i : int := 0;
    while i <= n {
        var fib_recursive_value : int := fibonacci_recursive(i);
        print_int(fib_recursive_value);
        i := i + 1;
    }
}
