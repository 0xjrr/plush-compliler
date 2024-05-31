function main(val args:[string]) {
	val a : int := 10;
	val b : int := 20;
	if a > b {
		print_string("a is greater than b");
	} else {
        if a < b {
		    print_string("a is less than b");
	    } else {
		    print_string("a is equal to b");
	    }
    }
}