'''
A module contains 1) definition list 2) use list 3) program text
'''

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

def parse_mod(user_input, mod_count): 
    '''
    Return a list of modules, parsed from user input. 
    Raise errors if there are less modules than mod_count. 
    - for mod_count times, repeat: 
        - get the first number after mod_count as def_count
        - repeat def pair storing process for def_count times
        - get the next number as use_count
        - repeat use pair storing process for use_count times
        - get the next number as prog_count
        - repeat prog pair storing process for prog_count times 
    '''
    mods = []
    pass

def main():
    input_set = get_input()
    print(input_set)
    MOD_COUNT = get_mod_count(input_set)
    print("Mod count is: " + MOD_COUNT if MOD_COUNT.isdigit() else "N/A")

if __name__ == "__main__":
    main()
