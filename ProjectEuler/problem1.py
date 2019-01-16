def main():
    summation = 0
    for i in range(1000):
        if i % 3 == 0 or i % 5 == 0:
            summation += i
    print(summation)


if __name__ == "__main__":
    main()
