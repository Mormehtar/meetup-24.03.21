import asyncio


def foo(loop, callback, *args):
    print("FOO!", args)
    loop.call_soon(callback, *args)


def bar(*args):
    print("BAR!", args)


def finish(loop):
    print("FINISH ME!")
    loop.stop()


def raise_exception(*args):
    raise Exception(args)


def chain(loop, *args):
    print("Chain length:", len(args))
    func, *new_args = args
    loop.call_soon(func, loop, *new_args)


def main():
    loop = asyncio.new_event_loop()
    loop.call_later(1, finish, loop)
    loop.call_soon(foo, loop, bar, 1, 2, 3)
    loop.call_soon(foo, loop, bar, 4, 5, 6)
    print("HERE")
    loop.run_forever()
    print("THERE")

    loop.call_soon(chain, loop, chain, chain, raise_exception, chain)
    loop.call_later(1, finish, loop)
    print("HERE")
    loop.run_forever()
    print("THERE")


main()
