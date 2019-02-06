import os, sys, re
from collections import ChainMap

DEF = "def"
USE = "use"
PROG = "prog"
BASE = "base"
MOD_COUNT = "mod_count"
MODS = "mods"
TYPE = "type"
WORD = "word"

def print_list(l):
    for item in l: 
        print(item)

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
    for mod in mods[MODS]:
        def_dict = mod[DEF]["def_list"]
        for sym in def_dict:
            def_dict[sym] += mod[PROG][BASE]
        sym_table.update(def_dict)
    return sym_table

def process_external_addr(old_addr, new_addr):
    first_digit = int(str(old_addr)[0])
    return (first_digit * 1000 + new_addr)

def resolve_external_addr(prog_list, addr, new_addr):
    pass

def resolve_addresses(mods, sym_table): 
    for mod in mods[MODS]:
        use_list = mod[USE]['use_list']
        prog = mod[PROG]
        prog_list = prog['prog_list']
        for usym, uaddr in use_list.items():
            '''Resolve external addresses'''
            old_sym_addr = prog_list[uaddr][WORD]
            addr_cur = str(old_sym_addr)
            new_sym_addr = sym_table[usym]
            prog_list[uaddr][WORD] = process_external_addr(old_sym_addr, new_sym_addr)
            while addr_cur[-3:] != '777':
                next_addr = str(prog_list[int(addr_cur[-3:])][WORD])
                prog_list[int(addr_cur[-3:])][WORD] = process_external_addr(int(next_addr), new_sym_addr)
                addr_cur = next_addr
        for progpair in prog_list: 
            '''Resolve relative addresses'''
            if progpair[TYPE] == 'R': 
                progpair[WORD] += prog[BASE]
        print_list(prog_list)
        print('\n')
    return mods

# def resolve_addresses(mods, sym_table):
#     for mod in mods[MODS]: 
#         used = mod[USE]["use_list"]
#         prog = mod[PROG]
#         prog_list = prog["prog_list"]
#         for used_sym, used_addr in used.items():
#             '''TODO: 
#             1) handle if this addr is not E; 
#             2) handle if list is shorter than used_addr
#             3) Handle if sym table does not contain this used sym
#             '''
#             print(used_sym)
#             old_addr = prog_list[used_addr][WORD]
#             new_addr = sym_table[used_sym]
#             prog_list = resolve_external_addr(prog_list, old_addr, new_addr)
#         for pair in prog_list: 
#             if pair[TYPE] == "R":
#                 pair[WORD] += prog[BASE]
#         print(prog)
#         print('\n')
#     return mods

def main():
    user_input = get_input()
    print('\n')
    processed_mod = process_user_input(user_input)
    # print("progs is " + str(processed_mod))
    sym_table = generate_sym_table(processed_mod)
    print(sym_table)
    print('\n')
    processed_mod = resolve_addresses(processed_mod, sym_table)
    

if __name__ == "__main__":
    main()