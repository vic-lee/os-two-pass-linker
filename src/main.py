DEF = "def"
USE = "use"
PROG = "prog"
BASE = "base"
MOD_COUNT = "mod_count"
MODS = "mods"
TYPE = "type"
WORD = "word"
PROG_ERR = "error"
PROG_SYM_USED_FLAG = "used_flag"
SYM_VAL = "symbol_value"
SYM_ERR = "symbol_error_msg"

MACHINE_SIZE = 300
MAX_LEGAL_VAL = 299

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

def uin_frist_pass(uin): 
    mods = { MOD_COUNT: int(uin[0]), MODS: [] }
    buffer = uin[1:]
    base_accum = 0
    syms = {}
    for _ in range(mods[MOD_COUNT]): 
        mod, buffer, base_accum, syms = parse_mod(buffer, base_accum, syms)
        mods[MODS].append(mod)
    return mods, syms

def parse_mod(mod_in, base, sym_table): 
    '''
    Input: a string containing a module
    Return: the remaining string after a module is parsed and removed from str.  
    '''
    mod_out = { DEF: {}, USE: {}, PROG: {} }
    cur = 0

    mod_out[DEF], cur, sym_table = parse_def(mod_in, cur, sym_table, base)
    print("mod def")
    print(mod_out[DEF])
    mod_out[USE], cur = parse_use(mod_in, cur)
    mod_out[PROG], cur = parse_prog(mod_in, cur, base)
    print("mod prog")
    print(mod_out[PROG])

    base += mod_out[PROG]['prog_count']
    return mod_out, mod_in[cur:], base, sym_table

def parse_def(mod, cur, sym_table, base): 
    COUNT = 'def_count'
    LIST = 'def_list'
    def_list = { COUNT: int(mod[cur]), LIST: {} }
    cur += 1
    print('def count is: ' + str(def_list[COUNT]))
    while cur < len(mod):
        if len(def_list[LIST]) >= def_list[COUNT]:
            break
        else:
            sym = mod[cur]
            sym_val = mod[cur + 1]
            def_list[LIST][sym] = int(sym_val)
            if sym in sym_table: 
                sym_table[sym][SYM_ERR] = "Error: This variable is multiply defined; last value used."
            else:
                sym_table[sym] = { SYM_VAL: None, SYM_ERR: "" }
            sym_table[sym][SYM_VAL] = int(sym_val) + base
            cur += 2
    return def_list, cur, sym_table

def parse_use(mod, cur): 
    COUNT = 'use_count'
    LIST = 'use_list'
    use_list = { COUNT: int(mod[cur]), LIST: {} }
    cur += 1
    while cur < len(mod):
        if len(use_list[LIST]) >= use_list[COUNT]: 
            break
        else:
            print('current mod cur is: ' + str(mod[cur]))
            print('next mod cur is: ' + str(mod[cur + 1]))
            use_list[LIST][mod[cur]] = int(mod[cur + 1])
            cur += 2
    return use_list, cur

def parse_prog(mod, cur, base): 
    COUNT = 'prog_count'
    LIST = 'prog_list'
    prog_list = { COUNT: int(mod[cur]), BASE: base, LIST: [] }
    cur += 1
    while cur < len(mod):
        if len(prog_list[LIST]) >= prog_list[COUNT]: 
            break
        else: 
            print('type: ' + str(mod[cur]))
            print('word: ' + str(mod[cur+1]))
            prog_list[LIST].append({ 
                TYPE: mod[cur], 
                WORD: int(mod[cur + 1]), 
                PROG_SYM_USED_FLAG: False,
                PROG_ERR: ""
            })
            cur += 2
    return prog_list, cur

def p_ext_addr(old_addr, new_addr):
    first_digit = int(str(old_addr)[0])
    return (first_digit * 1000 + new_addr)

def format_sym_table_out(syms):
    syms_out = "Symbol Table\n"
    for sym, sym_info in syms.items():
        syms_out += "{}={} {}\n".format(sym, sym_info[SYM_VAL], sym_info[SYM_ERR])
    return syms_out

def format_mmap_out(mmap, sym_use_stat):
    mmap_str = "Memory Map\n"
    for index, item in enumerate(mmap):
        mmap_str += "{}:\t{}\n".format(str(index), item)
    mmap_str += '\n'
    for sym in sym_use_stat: 
        if sym_use_stat[sym] == False: 
            mmap_str += 'Warning: ' + sym + ' was defined but never used.\n'
    return mmap_str

def check_multiple_sym_usage(progpair):
    if progpair[PROG_SYM_USED_FLAG] == True: 
        progpair[PROG_ERR] = 'Error: Multiple symbols used here; last one used'
    else: 
        progpair[PROG_SYM_USED_FLAG] = True
    return progpair

def check_sym_used_not_defined(progpair, sym, sym_table, sym_use_stat): 
    is_sym_used_not_defined = False
    if sym in sym_table: 
        new_sym_addr = sym_table[sym][SYM_VAL]
        sym_use_stat[sym] = True
    else: 
        is_sym_used_not_defined = True
        new_sym_addr = '111'
        progpair[PROG_ERR] = 'Error: ' + sym + ' was used but not defined. It has been given the value 111.'
    return progpair, new_sym_addr, sym_use_stat, is_sym_used_not_defined

def modify_word_last_three_digits(word, replacement):
    return int(str(word)[0]) * 1000 + replacement

def uin_sec_pass(mods, sym_table): 
    mmap = []
    sym_use_stat = {}
    for sym in sym_table: 
        sym_use_stat[sym] = False
    c = 0
    for mod in mods[MODS]:
        use_list = mod[USE]['use_list']
        prog = mod[PROG]
        prog_list = prog['prog_list']
        # print('this is mod ' + str(c) + '\n')
        c += 1
        for usym, uaddr in use_list.items():
            '''Resolve external addresses'''
            is_sym_used_not_defined = False
            old_sym_addr = prog_list[uaddr][WORD]
            addr_cur = str(old_sym_addr)

            prog_list[uaddr], new_sym_addr, sym_use_stat, is_sym_used_not_defined \
                = check_sym_used_not_defined(prog_list[uaddr], usym, sym_table, sym_use_stat)

            prog_list[uaddr][WORD] = p_ext_addr(old_sym_addr, int(new_sym_addr))
            # print_list(prog_list)

            # print('\naddrcur: ' + addr_cur)
            prog_list[uaddr] = check_multiple_sym_usage(prog_list[uaddr])
            
            while addr_cur[-3:] != '777':
                next_index = int(addr_cur[-3:])
                # print('next idx is ' + str(next_index))
                # print_list(prog_list)
                next_addr = str(prog_list[next_index][WORD])
                prog_list[next_index][WORD] = p_ext_addr(int(next_addr), int(new_sym_addr))
                prog_list[next_index] = check_multiple_sym_usage(prog_list[next_index])
                if is_sym_used_not_defined == True: 
                    prog_list[next_index][PROG_ERR] = 'Error: ' + usym + \
                        ' was used but not defined. It has been given the value 111.'
                addr_cur = next_addr

        for progpair in prog_list: 

            if progpair[TYPE] == 'R': 
                if int(str(progpair[WORD])[-3:]) >= len(prog_list):
                    progpair[PROG_ERR] = 'Error: Type R address exceeds module size; 0 (relative) used'
                    progpair[WORD] = modify_word_last_three_digits(progpair[WORD], 0)
                progpair[WORD] += prog[BASE]

            elif progpair[TYPE] == 'A':
                if int(str(progpair[WORD])[-3:]) >= MACHINE_SIZE: 
                    progpair[PROG_ERR] = 'Error: A type address exceeds machine size; max legal value used'
                    progpair[WORD] = modify_word_last_three_digits(progpair[WORD], MAX_LEGAL_VAL)

            mmap.append(str(progpair[WORD]) + ' ' + progpair[PROG_ERR])

    mmap_out = format_mmap_out(mmap, sym_use_stat)
    return mmap_out

def main():
    uin = get_input()
    mods, sym_table = uin_frist_pass(uin)
    print('\n' + format_sym_table_out(sym_table))
    mmap_out = uin_sec_pass(mods, sym_table)
    print(mmap_out)
    
if __name__ == "__main__":
    main()