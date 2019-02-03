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

def process_user_input(u_in): 
    MOD_COUNT = "mod_count"
    MODS = "mods"

    progs = { MOD_COUNT: int(u_in[0]), MODS: [] }
    list_to_process = u_in[1:]

    for _ in range(progs[MOD_COUNT]): 
        mod, list_to_process = parse_mod(list_to_process)
        progs[MODS].append(mod)

    return progs

def process_mod_component(component, mod, cur): 
    TYPE = "type"
    WORD = "word"
    COUNT = component + '_count'
    LIST = component + '_list'
    
    comp = { COUNT: int(mod[cur]), LIST: [] }
    cur += 1
    
    while cur < len(mod):
        if len(comp[LIST]) < comp[COUNT]: 
            if component == "def" or component == "use": 
                comp[LIST].append({ mod[cur]: mod[cur + 1] })
                cur += 2
                continue
            else: 
                comp[LIST].append({ TYPE: mod[cur], WORD: mod[cur + 1] })
                cur += 2
                continue
        else: 
            break

    return comp, cur

def parse_mod(md_in): 
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

def get_sym_table(mods): 
    # for item in 
    pass

def main():
    user_input = get_input()
    processed_mod = process_user_input(user_input)
    print("progs is " + str(processed_mod))

if __name__ == "__main__":
    main()