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
    user_input = " ".join(user_input).split()
    return user_input

def process_mod_count(s):
    pass

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
    print("mod count is " + user_input[0])
    MOD_COUNT = "mod_count"
    MODS = "mods"
    progs = {
        MOD_COUNT: int(user_input[0]), 
        MODS: []
    }
    pending_ls = user_input[1:]
    for _ in range(progs["mod_count"]): 
        mod, pending_ls = mod_ls_to_dict(pending_ls)
        progs["mods"].append(mod)
    return progs

def mod_ls_to_dict(md_in): 
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
    SYM = "sym"
    ADDR = "rel_addr"

    md_out = {
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
    cur = 0
    while cur < len(md_in):
        if md_out[DEF][DEF_COUNT] is None: 
            md_out[DEF][DEF_COUNT] = int(md_in[cur])
            cur += 1
            continue 
        elif md_out[DEF][DEF_COUNT] is not None and len(md_out[DEF][DEF_LIST]) < md_out[DEF][DEF_COUNT]: 
            md_out[DEF][DEF_LIST].append({
                SYM: md_in[cur],
                ADDR: md_in[cur + 1]
            })
            cur += 2
            continue
        elif md_out[USE][USE_COUNT] is None:
            md_out[USE][USE_COUNT] = int(md_in[cur])
            cur += 1
            continue 
        elif md_out[USE][USE_COUNT] is not None and len(md_out[USE][USE_LIST]) < md_out[USE][USE_COUNT]:
            md_out[USE][USE_LIST].append({
                SYM: md_in[cur],
                ADDR: md_in[cur + 1]
            })
            cur += 2
            continue
        elif md_out[PROG][PROG_COUNT] is None:
            md_out[PROG][PROG_COUNT] = int(md_in[cur])
            cur += 1
            continue
        elif md_out[PROG][PROG_COUNT] is not None and len(md_out[PROG][PROG_LIST]) < md_out[PROG][PROG_COUNT]: 
            md_out[PROG][PROG_LIST].append({
                SYM: md_in[cur],
                ADDR: md_in[cur + 1]
            })
            cur += 2
            continue
        else: 
            break
    # print(md_out)
    return (md_out, md_in[cur:])
    

def main():
    u_in = get_input()
    processed_mod = parse_mod(u_in)
    print("progs is " + str(processed_mod))

if __name__ == "__main__":
    main()