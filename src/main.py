import os
import sys


def main():
    print("Paste your input, then enter Ctrl-D to complete:")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    contents = " ".join(contents)
    print(contents)

if __name__ == "__main__":
    main()
