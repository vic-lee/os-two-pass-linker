import os, sys, re

def get_input():
    print("Paste your input, then enter Ctrl-D to exit input mode:")
    user_input = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        user_input.append(line)
    user_input = " ".join(user_input)
    return user_input

def get_mod_count(s):
    for _, c in enumerate(s):
        if c.isdigit():
            return c    
    return None

def main():
    input_set = get_input()
    print(input_set)
    MOD_COUNT = get_mod_count(input_set)
    print("Mod count is: " + MOD_COUNT if MOD_COUNT.isdigit() else "N/A")

if __name__ == "__main__":
    main()
