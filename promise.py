import asyncio
from functools import wraps


class Promise(object):
    class States(object):
        PENDING = 'pending'
        RESOLVED = 'resolved'
        REJECTED = 'rejected'

    def __init__(self, loop):
        self.loop = loop
        self.state = self.States.PENDING
        self.data = None
        self.on_resolve = []
        self.on_reject = []

    def check_events(self):
        if self.state == self.States.RESOLVED:
            while self.on_resolve:
                self.on_resolve.pop()(self.data)
        elif self.state == self.States.REJECTED:
            while self.on_reject:
                self.on_reject.pop()(self.data)

    def resolve(self, data):
        self.state = self.States.RESOLVED
        self.data = data
        self.check_events()

    def reject(self, exception):
        self.state = self.States.REJECTED
        self.data = exception
        self.check_events()

    @classmethod
    def build_callback(cls, func, resolver, rejecter):
        def callback(data):
            try:
                result = func(data)
            except Exception as e:
                return rejecter(e)
            return resolver(result)
        return callback

    def build_then_handler(self, handler, next_promise):
        @wraps(handler)
        def then_handler(data):
            self.loop.call_soon(
                self.build_callback(
                    handler,
                    next_promise.resolve,
                    next_promise.reject,
                ),
                data,
            )
        return then_handler

    @classmethod
    def dummy(cls, data):
        return data

    @classmethod
    def dummy_fail(cls, exception):
        raise exception

    def then(self, resolve_handler=None, reject_handler=None):
        promise = Promise(loop=self.loop)
        if resolve_handler is None:
            resolve_handler = self.dummy
        self.on_resolve.append(
            self.build_then_handler(resolve_handler, promise)
        )
        if reject_handler is None:
            reject_handler = self.dummy_fail
        self.on_reject.append(
            self.build_then_handler(reject_handler, promise)
        )

        self.check_events()
        return promise

    def catch(self, exception, handler):
        def wrapper(data):
            if isinstance(data, exception):
                return handler(data)
            else:
                raise data
        return self.then(reject_handler=wrapper)

    @classmethod
    def all(cls, loop, *promises):
        result = []

        output_promise = cls(loop)

        def resolver(data):
            result.append(data)
            if len(result) == len(promises):
                output_promise.resolve(result)

        def rejecter(exception):
            output_promise.reject(exception)

        for promise in promises:
            promise.then(resolver, rejecter)

        return output_promise


def main():
    loop = asyncio.new_event_loop()

    class MyException(Exception):
        def __str__(self):
            return f"{self.__class__.__name__}: {self.args}"

    class NewException(MyException):
        pass

    def failing_func(data):
        print("failing_func", data)
        raise MyException(data)

    def i_am_called(data):
        print("i_am_called", data)
        data.append("HA!")
        return data

    def i_am_not_called(data):
        print("i_am_not_called", data)
        data.append("NOOOO!")
        return data

    def i_am_not_caught(data):
        print("i_am_not_caught", data)
        data.append("NO-no-no-no!")
        return data

    def i_am_caught(data):
        print("i_am_caught", data)
        extract_data = data.args[0]
        extract_data.append("YEAH!")
        return extract_data

    promise = Promise(loop)
    (
        promise
        .then(i_am_called)
        .then(i_am_called)
        .then(failing_func)
        .then(i_am_not_called)
        .catch(NewException, i_am_not_caught)
        .catch(MyException, i_am_caught)
        .then(failing_func)
        .then(i_am_not_called, i_am_caught)
        .then(i_am_called)
        .then(lambda x: print(x))
        .then(lambda _: loop.stop())
    )
    promise.resolve([42])

    loop.run_forever()

    print("PRIMITIVES")

    promise = Promise(loop)
    p1 = (
        promise
        .then(lambda x: [x[0] * 2])
        .then(i_am_called)
        .then(lambda x: print(x))
    )
    p2 = promise.then(i_am_called).then(lambda x: print(x))

    Promise.all(loop, p1, p2).then(lambda _: loop.stop())

    promise.resolve([42])

    loop.run_forever()


if __name__ == "__main__":
    main()
