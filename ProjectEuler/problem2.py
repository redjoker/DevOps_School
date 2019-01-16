import math

PHI = (1 + math.sqrt(5))/2


def fib(n):
    return (math.pow(PHI, n) - math.pow(-PHI, -n))/math.sqrt(5)


def sum_even_fibs(stop):
    summation = 0
    i = 0
    this_fib = fib(i)
    while this_fib < stop:
        summation += this_fib
        i += 3
        this_fib = fib(i)
    return summation


def main():
    print(sum_even_fibs(4000000))


if __name__ == '__main__':
    main()
