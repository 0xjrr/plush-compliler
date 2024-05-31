function main(val args:[string]) {
    # Allocation
    val matrix : [2][2]double;
    matrix[0][0] := 1.1;
    matrix[0][1] := 2.2;
    matrix[1][0] := 3.3;
    matrix[1][1] := 4.4;

    # Initialization
    val arr : [double] := [5.5, 6.6, 7.7];
    val nested_arr : [[double]] := [[8.8, 9.9], [10.10, 11.11]];

    # Retrieval
    var matrix_value : double := matrix[0][0];
    var arr_value : double := arr[2];
    var nested_arr_value : double := nested_arr[1][0];

    # Insertion
    arr[1] := 12.12;
    nested_arr[0][1] := 13.13;
    matrix[1][1] := 14.14;

    # Printing values
    print_double(matrix[0][0]);   # Should print 1.1
    print_double(matrix[0][1]);   # Should print 2.2
    print_double(matrix[1][0]);   # Should print 3.3
    print_double(matrix[1][1]);   # Should print 14.14

    print_double(arr[0]);         # Should print 5.5
    print_double(arr[1]);         # Should print 12.12
    print_double(arr[2]);         # Should print 7.7

    print_double(nested_arr[0][0]); # Should print 8.8
    print_double(nested_arr[0][1]); # Should print 13.13
    print_double(nested_arr[1][0]); # Should print 10.10
    print_double(nested_arr[1][1]); # Should print 11.11

    print_double(matrix_value);    # Should print 1.1
    print_double(arr_value);       # Should print 7.7
    print_double(nested_arr_value);# Should print 10.10

    # Summation and printing the sum
    var sum : double := matrix[0][0] + matrix[0][1] + matrix[1][0] + matrix[1][1] + arr[0] + arr[1] + arr[2] + nested_arr[0][0] + nested_arr[0][1] + nested_arr[1][0] + nested_arr[1][1];
    print_double(sum); # Should print the sum of all elements
}
