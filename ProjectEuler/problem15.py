factorials = {0: 1}


def factorial(n):
    if n > len(factorials):
        for i in range(len(factorials), n + 1):
            factorials[i] = i * factorials[i - 1]

    return factorials[n]


def multinomial_coeff(n, x, y):
    return factorial(n)/(factorial(x)*factorial(y))


def grid_paths(x = 1):
    return multinomial_coeff(2*x, x, x)


def main():
    print(grid_paths(20))


if __name__ == '__main__':
    main()
