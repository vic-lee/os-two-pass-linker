import os, sys, re
from collections import ChainMap

DEF = "def"
USE = "use"
PROG = "prog"
MOD_COUNT = "mod_count"
MODS = "mods"

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

def process_user_input(u_in): 

    progs = { MOD_COUNT: int(u_in[0]), MODS: [] }
    list_to_process = u_in[1:]
    base_accum = 0
    for _ in range(progs[MOD_COUNT]): 
        mod, list_to_process, base_accum = parse_mod(list_to_process, base_accum)
        progs[MODS].append(mod)

    return progs

def process_mod_component(component, mod, cur, base=0): 
    TYPE = "type"
    WORD = "word"
    BASE = "base"
    COUNT = component + '_count'
    LIST = component + '_list'
    comp = {}
    if component == DEF or component == USE: 
        comp = { COUNT: int(mod[cur]), LIST: {} }
    else: 
        comp = { COUNT: int(mod[cur]), BASE: base, LIST: [] }
    cur += 1
    
    while cur < len(mod):
        if len(comp[LIST]) < comp[COUNT]: 
            if component == DEF or component == USE: 
                comp[LIST][mod[cur]] = int(mod[cur + 1])
                cur += 2
                continue
            else: 
                comp[LIST].append({ TYPE: mod[cur], WORD: int(mod[cur + 1]) })
                cur += 2
                continue
        else: 
            break

    return comp, cur

def parse_mod(md_in, base): 
    '''
    Input: a string containing a module
    Return: the remaining string after a module is parsed and removed from str.  
    '''

    md_out = { DEF: {}, USE: {}, PROG: {} }

    cur = 0

    md_out[DEF], cur = process_mod_component(DEF, md_in, cur)
    md_out[USE], cur = process_mod_component(USE, md_in, cur)
    md_out[PROG], cur = process_mod_component(PROG, md_in, cur, base)

    base += md_out[PROG]['prog_count']

    return (md_out, md_in[cur:], base)

def generate_sym_table(mods):
    sym_table = {}
    base_accum = 0
    for mod in mods[MODS]:
        def_dict = mod[DEF]["def_list"]
        for sym in def_dict:
            def_dict[sym] += base_accum
        sym_table.update(def_dict)
        base_accum += mod[PROG]["prog_count"]
    return sym_table

def resolve_addresses(mods):
    for mod in mods[MODS]: 
        prog = mod[PROG]
        print(prog)
        print("\n")
    pass

def main():
    user_input = get_input()
    processed_mod = process_user_input(user_input)
    # print("progs is " + str(processed_mod))
    sym_table = generate_sym_table(processed_mod)
    # print(sym_table)
    resolve_addresses(processed_mod)
    

if __name__ == "__main__":
    main()