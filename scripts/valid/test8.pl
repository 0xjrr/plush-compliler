function main(val args:[string]) {
    var arr : [int] := [1, 2, 3, 4, 5];
    arr[1] := 10;

    print_int(arr[1]); # Should print 10
}
