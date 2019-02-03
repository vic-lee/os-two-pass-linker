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

def parse_mod(user_input): 
    '''
    Return a list of modules, parsed from user input. 
    Raise errors if there are less modules than mod_count. 
    - get mod_count
    - for mod_count times, repeat: 
        - get the first number after mod_count as def_count
        - repeat def pair storing process for def_count times
        - get the next number as use_count
        - repeat use pair storing process for use_count times
        - get the next number as prog_count
        - repeat prog pair storing process for prog_count times 
    '''
    progs = {
        "mod_count": get_mod_count(user_input), 
        "mods": []
    }
    # MOD_COUNT = progs["mod_count"]
    # print("Mod count is: " + MOD_COUNT if MOD_COUNT.isdigit() else "N/A")
    pass

def mod_str_to_dict(str): 
    '''
    Input: a string containing a module
    Return: the remaining string after a module is parsed and removed from str.  
    '''

    DEF = "def"
    DEF_COUNT = "def_count"
    DEF_LIST = "def_list"
    USE = "use"
    USE_COUNT = "use_count"
    USE_LIST = "use_list"
    PROG = "prog"
    PROG_COUNT = "prog_count"
    PROG_LIST = "prog_list"

    mod_dict = {
        DEF: {
            DEF_COUNT: None,
            DEF_LIST: []
        }, 
        USE: {
            USE_COUNT: None,
            USE_LIST: []
        }, 
        PROG: {
            PROG_COUNT: None, 
            PROG_LIST: []
        }
    }

    for _, c in enumerate(str):
        if mod_dict[DEF][DEF_COUNT] is None:
            if c.isdigit(): 
                mod_dict[DEF][DEF_COUNT] = c
            continue
        # elif len(mod_dict[DEF][DEF_LIST]) < mod_dict[DEF][DEF_COUNT]:
            

    

def main():
    input_set = get_input()
    print(input_set)

if __name__ == "__main__":
    main()
