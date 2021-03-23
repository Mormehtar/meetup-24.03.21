const foo = (callback, arg1, arg2, arg3) => {
    console.log("FOO!", arg1, arg2, arg3);
    setTimeout(callback, 0, arg1, arg2, arg3);
};

const bar = (arg1, arg2, arg3) => {
    console.log("BAR!", arg1, arg2, arg3);
};


function main() {
    console.log("HERE!");
    setTimeout(foo, 0, bar, 1, 2, 3);
    setTimeout(foo, 0, bar, 4, 5, 6);
    console.log("THERE!");
}

main();

/*
HERE!
THERE!
FOO! 1 2 3
FOO! 4 5 6
BAR! 1 2 3
BAR! 4 5 6
*/
