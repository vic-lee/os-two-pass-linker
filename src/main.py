def main():
    with open("myfile", "rb") as f:
        byte = f.read(1)
        while byte:
            # Do stuff with byte.
            byte = f.read(1)
            print(byte)

if __name__ == "__main__":
    main()
