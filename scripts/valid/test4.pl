function addOne(val n:int) : int {
    return n + 1;
}

function incrementTwice(val n:int) : int {
    val firstIncrement : int := addOne(n);
    val secondIncrement : int := addOne(firstIncrement);
    incrementTwice := secondIncrement;
}

function main(val args:[string]) {
    val number : int := 5;
    val incrementedNumber : int := incrementTwice(number);
    print_int(incrementedNumber);
}
