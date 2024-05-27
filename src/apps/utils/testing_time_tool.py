import time


def testing_time(funcion):
    def tested_function(*args, **kwargs):
        start = time.time()
        c = funcion(*args, **kwargs)
        print(time.time() - start)
        return c

    return tested_function
