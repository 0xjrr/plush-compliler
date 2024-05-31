function main(val args:[string]) {
    val arrx : [2][2]int;
    arrx[0][0] := 1;
    arrx[0][1] := 2;
    arrx[1][0] := 3;
    arrx[1][1] := 4;

    var sum : int := arrx[0][0] + arrx[0][1] + arrx[1][0] + arrx[1][1];
    print_int(sum); # Should print 10
}
