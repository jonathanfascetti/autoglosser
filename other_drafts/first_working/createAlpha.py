def main():
    ###source file used for creating alphabet (copy and pasted MOOREWORD from main glossary w/o ka...ye)
    with open("dictionary.txt") as file:
        data = file.readlines()

    for i in range(len(data)):
        if "\n" in data[i]:
            data[i] = data[i][:-1]

    alphabet = []
    for i in data:
        for j in i:
            if j not in alphabet:
                alphabet.append(j)

    return alphabet


if __name__ == "__main__":
    main()
