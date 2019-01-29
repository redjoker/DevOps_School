factorials = {0: 1}


def factorial(n):
    if n > len(factorials):
        for i in range(len(factorials), n + 1):
            factorials[i] = i * factorials[i - 1]

    return factorials[n]


def multinomial_coeff(n, m):
    num = factorial(n)
    den = 1

    for i in m:
        den *= factorial(i)

    return num / den


def grid_paths(x=0, y=0):
    return multinomial_coeff(x * y, [x, y])


def main():
    print(grid_paths(20))


if __name__ == '__main__':
    main()
