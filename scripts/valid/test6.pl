function main(val args:[string]) {
    val arr : [int] := [1, 2, 3];
    val arr2 : [[int]] := [[1, 2], [3, 4]];
    val arr3 : [[[int]]] := [[[1, 2], [3, 4]], [[5, 6], [7, 8]]];
    val arr4 : [][]int := [[1, 2], [3, 4]];

    print_int(arr[0]);   # Should print 1
    print_int(arr2[1][1]); # Should print 4
    print_int(arr3[1][1][0]); # Should print 7
    print_int(arr4[0][1]); # Should print 2
}
