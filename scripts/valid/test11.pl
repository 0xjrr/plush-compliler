# Function to calculate Fibonacci using iteration and store in a global array
function fibonacci_iterative(n:int): void {
    var fib : [10]int;
    fib[0] := 0;
    fib[1] := 1;
    var i : int := 2;
    while i <= n {
        fib[i] := fib[i - 1] + fib[i - 2];
        i := i + 1;
    }

    i := 0;
    while i <= n {
        print_int(fib[i]);
        i := i + 1;
    }
    
}

function main(val args:[string]) {
    val n : int := 10;

    # Calculate Fibonacci using iteration
    print_string("Fibonacci sequence (iterative):");
    fibonacci_iterative(n);
}