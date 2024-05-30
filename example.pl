    function aux(x: int): int {
        return 10 * x;
    }
    
    function main(): int {
        var x : int := 120;
        var y : int := 10;
        var z : int := 0;
        x++;
        y--;
        ++x;
        --y;
        --x;
        x += 1;

        var a : int := aux(y);
        
        while (z < 10) {
            x += 2;
            z++;
        }

        do {
            x += 2;
            z++;
        } while (z < 20);

        while (z < 100) {
            x += 2;
            z++;
            if (z % 2 == 0) {
                continue;
            }
            if (z == 25) {
                break;
            }
        }
        if (x > 10) {
            x += 10;
        } else {
            x -= 10;
        }
        y -= 1;
        x := x + y    + (x                                          *4);
        return x + y;
    
    }