import time


def memoize_single_parameter_function(f):
    d = {}

    def inner(n):
        if n in d:
            return d[n]
        d[n] = f(inner, n)
        return d[n]

    return inner


@memoize_single_parameter_function
def fib_memo(f, n):
    if n == 0:
        return 0

    if n == 1:
        return 1

    return f(n - 1) + f(n - 2)


def fib(n):
    fib_i = 0
    fib_i_plus_1 = 1

    i = 0

    while i < n:
        fib_i_plus_2 = fib_i + fib_i_plus_1
        fib_i = fib_i_plus_1
        fib_i_plus_1 = fib_i_plus_2
        i += 1

    return fib_i


def sum_even_fibs(stop):
    summation = 0
    i = 0
    this_fib = fib_memo(i)
    while this_fib < stop:
        if this_fib % 2 == 0:
            summation += this_fib
        i += 1
        this_fib = fib_memo(i)
    return summation


def main():
    return sum_even_fibs(4000000)


if __name__ == '__main__':
    start = time.time()
    x = main()
    end = time.time()
    print(x)
    print("Took {}ns".format((end - start) * 1000000000))

