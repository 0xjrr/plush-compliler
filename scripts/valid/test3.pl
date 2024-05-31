function main(val args:[string]) {
	var counter : int := 0;
	while counter < 10 {
		if counter == 5 {
			break;
		}
		print_int(counter);
		counter := counter + 1;
	}

	counter := 0;
	while counter < 10 {
		counter := counter + 1;
		if counter % 2 == 0 {
			continue;
		}
		print_int(counter);
	}
}