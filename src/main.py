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

def parse_mod(user_input): 
    MOD_COUNT = "mod_count"
    MODS = "mods"

    progs = { MOD_COUNT: int(user_input[0]), MODS: [] }
    list_to_process = user_input[1:]

    for _ in range(progs[MOD_COUNT]): 
        mod, list_to_process = mod_list_to_dict(list_to_process)
        progs[MODS].append(mod)

    return progs

def process_mod_component(component, mod, cur): 
    SYM = "sym"
    ADDR = "rel_addr"
    COUNT = component + '_count'
    LIST = component + '_list'
    
    comp = { COUNT: int(mod[cur]), LIST: [] }
    cur += 1
    
    while cur < len(mod):
        if len(comp[LIST]) < comp[COUNT]: 
            comp[LIST].append({
                SYM: mod[cur],
                ADDR: mod[cur + 1]
            })
            cur += 2
            continue
        else: 
            break

    return comp, cur

def mod_list_to_dict(md_in): 
    '''
    Input: a string containing a module
    Return: the remaining string after a module is parsed and removed from str.  
    '''
    DEF = "def"
    USE = "use"
    PROG = "prog"

    md_out = { DEF: {}, USE: {}, PROG: {} }

    cur = 0

    md_out[DEF], cur = process_mod_component(DEF, md_in, cur)
    md_out[USE], cur = process_mod_component(USE, md_in, cur)
    md_out[PROG], cur = process_mod_component(PROG, md_in, cur)

    return (md_out, md_in[cur:])

def main():
    u_in = get_input()
    processed_mod = parse_mod(u_in)
    print("progs is " + str(processed_mod))

if __name__ == "__main__":
    main()