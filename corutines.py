from asyncio import new_event_loop
from promise import Promise


def chain_of_promise(loop, iterator_func):
    base_promise = Promise(loop)
    iterator = iterator_func(loop)

    def catch_callback(exception):
        base_promise.reject(exception)

    def callback(*_):
        try:
            next_promise = next(iterator)
            next_promise.then(callback, catch_callback)
        except StopIteration as exception:
            result = exception.args[0]
            base_promise.resolve(result)
        except Exception as exception:
            base_promise.reject(exception)

    callback()
    return base_promise


def wrapper(generator):
    def wrapped(loop):
        return chain_of_promise(loop, generator)
    return wrapped


def chunk_of_work(loop):
    promise = Promise(loop)
    print("Chunk of work should be finished in second!")
    loop.call_later(1, promise.resolve, None)
    return promise


def failing_chunk_of_work(loop):
    promise = Promise(loop)
    print("Chunk of work should be failed in second!")
    loop.call_later(1, promise.reject, Exception("I am failing in promise"))
    return promise


@wrapper
def async_func(loop):
    print("I start")
    yield chunk_of_work(loop)
    print("First chunk finished")
    yield chunk_of_work(loop)
    print("Second chunk finished")
    yield chunk_of_work(loop)
    print("Third chunk finished")
    return 42


@wrapper
def async_func_fail_in_promise(loop):
    print("I start")
    yield chunk_of_work(loop)
    print("First chunk finished")
    yield failing_chunk_of_work(loop)
    print("Second chunk finished")
    yield chunk_of_work(loop)
    print("Third chunk finished")
    return 42


@wrapper
def async_func_fail(loop):
    print("I start")
    yield chunk_of_work(loop)
    print("First chunk finished")
    raise Exception("I am failed!")
    yield chunk_of_work(loop)
    print("Second chunk finished")
    yield chunk_of_work(loop)
    print("Third chunk finished")
    return 42


def print_result(result):
    print(result)
    return


def example(func):
    loop = new_event_loop()

    (
        func(loop)
        .catch(Exception, lambda exception: exception)
        .then(print_result)
        .then(lambda _: loop.stop())
    )

    print("START")
    loop.run_forever()
    print("STOP")


def main():
    print("CORRECT")
    example(async_func)
    print()
    print("Fail between promises")
    example(async_func_fail)
    print()
    print("Fail in promise")
    example(async_func_fail_in_promise)


if __name__ == "__main__":
    main()
