    #     var x : int := 120;
    #     var y : int := 10;
    #     var z : int := 0;
    #     x++;
    #     y--;
    #     ++x;
    #     --y;
    #     --x;
    #     x += 1;
    #     while (z < 10) {
    #         x += 2;
    #         z++;
    #     }
    #     do {
    #         x += 2;
    #         z++;
    #     } while (z < 20);
    #     if (x > 10) {
    #         x += 10;
    #     } else {
    #         x -= 10;
    #     }
    #     y -= 1;
    #     x := x + y    + (x                                          *4);
    #     return x + y;
    function main(): int {
    var x : int := 120;
    var y : int := 10;
    if (x > 10) {
        x += 10;
    } else {
        x -= 10;
    }
    return x;
    }