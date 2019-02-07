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

def process_user_input(uin): 

    mods = { MOD_COUNT: int(uin[0]), MODS: [] }
    list_to_process = uin[1:]
    base_accum = 0
    for _ in range(mods[MOD_COUNT]): 
        mod, list_to_process, base_accum = parse_mod(list_to_process, base_accum)
        mods[MODS].append(mod)

    return mods

def parse_mod(mod_in, base): 
    '''
    Input: a string containing a module
    Return: the remaining string after a module is parsed and removed from str.  
    '''
    mod_out = { DEF: {}, USE: {}, PROG: {} }
    cur = 0

    mod_out[DEF], cur = process_mod_component(DEF, mod_in, cur)
    mod_out[USE], cur = process_mod_component(USE, mod_in, cur)
    mod_out[PROG], cur = process_mod_component(PROG, mod_in, cur, base)

    base += mod_out[PROG]['prog_count']

    return (mod_out, mod_in[cur:], base)

def process_mod_component(component, mod, cur, base=0): 
    '''
    This function processes any of a module's 3 components: 
    1) definition list; 2) use list; and 3) program text. 
    Input: 
        component:  component name, either DEF, USE, or PROG
        mod:        the current module in process
        cur:        current cursor location in module traversal
    Output: 
        comp_ret:   component returned, after processing
        cur:        cursor location after processing
    '''
    COUNT = component + '_count'
    LIST = component + '_list'
    comp_ret = {}
    if component == DEF or component == USE: 
        comp_ret = { COUNT: int(mod[cur]), LIST: {} }
    else: 
        comp_ret = { COUNT: int(mod[cur]), BASE: base, LIST: [] }
    cur += 1
    
    while cur < len(mod):
        if len(comp_ret[LIST]) < comp_ret[COUNT]: 
            if component == DEF or component == USE: 
                comp_ret[LIST][mod[cur]] = int(mod[cur + 1])
                cur += 2
                continue
            else: 
                comp_ret[LIST].append({ TYPE: mod[cur], WORD: int(mod[cur + 1]) })
                cur += 2
                continue
        else: 
            break

    return comp_ret, cur

def process_external_addr(old_addr, new_addr):
    first_digit = int(str(old_addr)[0])
    return (first_digit * 1000 + new_addr)

def resolve_addresses(mods, sym_table): 
    sym_use_stat = {}
    for sym in sym_table: 
        sym_use_stat[sym] = False
    for mod in mods[MODS]:
        use_list = mod[USE]['use_list']
        prog = mod[PROG]
        prog_list = prog['prog_list']
        for usym, uaddr in use_list.items():
            '''Resolve external addresses'''
            old_sym_addr = prog_list[uaddr][WORD]
            addr_cur = str(old_sym_addr)
            new_sym_addr = None
            if usym in sym_table: 
                new_sym_addr = sym_table[usym]
                sym_use_stat[usym] = True
            else: 
                new_sym_addr = 111
                print(usym + 'was used but not defined. It has been given the value 111.')
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
    for sym in sym_use_stat: 
        if sym_use_stat[sym] == False: 
            print('Warning: ' + sym + ' was defined but never used.')
    return mods

def generate_sym_table(mods):
    sym_table = {}
    multiple_def_syms = []
    for mod in mods[MODS]:
        def_dict = mod[DEF]["def_list"]
        for sym in def_dict:
            if sym in sym_table: 
                multiple_def_syms.append(sym)
            def_dict[sym] += mod[PROG][BASE]
        sym_table.update(def_dict)
    for elem in multiple_def_syms: 
        print(elem + ' has multiple definitions. Last definition used.')
    return sym_table

def main():
    uin = get_input()
    print('\n')
    mods = process_user_input(uin)
    # print("progs is " + str(processed_mod))
    sym_table = generate_sym_table(mods)
    print(sym_table)
    print('\n')
    mods = resolve_addresses(mods, sym_table)
    

if __name__ == "__main__":
    main()