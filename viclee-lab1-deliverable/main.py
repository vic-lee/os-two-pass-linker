import mod_keys as k

MACHINE_SIZE = 300
MAX_LEGAL_VAL = 299

def print_list(l):
    for item in l: 
        print(item)

def get_input():
    print("""
    1) Paste your input,
    2) Enter a line break if you're not on a new line,
    3) Enter Ctrl-D to exit input mode:
    """)
    user_input = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        user_input.append(line)
    user_input = " ".join(user_input).split()
    return user_input

def input_frist_pass(uin): 
    mods = { k.MOD_COUNT: int(uin[0]), k.MODS: [] }
    buffer = uin[1:]
    base_accum = 0
    syms = {}
    for _ in range(mods[k.MOD_COUNT]): 
        mod, buffer, base_accum, syms = parse_mod(buffer, base_accum, syms)
        mods[k.MODS].append(mod)
    return mods, syms

def parse_mod(mod_in, base, sym_table): 
    '''
    Input: a string containing a module
    Return: the remaining string after a module is parsed and removed from str.  
    '''
    mod_out = { k.DEF: {}, k.USE: {}, k.INSTRUCTIONS: {} }
    cur = 0

    mod_out[k.DEF], cur, sym_table = parse_def(mod_in, cur, sym_table, base)
    mod_out[k.USE], cur = parse_use(mod_in, cur)
    mod_out[k.INSTRUCTIONS], cur = parse_instructions(mod_in, cur, base)

    base += mod_out[k.INSTRUCTIONS][k.INSTRUCTION_COUNT]
    return mod_out, mod_in[cur:], base, sym_table

def parse_def(mod, cur, sym_table, base): 
    def_count = int(mod[cur])
    def_list = { k.DEF_COUNT: def_count, k.DEF_LIST: {} }
    cur += 1
    for _ in range(def_count):
        sym = mod[cur]
        sym_val = mod[cur + 1]
        def_list[k.DEF_LIST][sym] = int(sym_val)
        if sym in sym_table: 
            sym_table[sym][k.SYM_ERR] = "Error: This variable is multiply defined; last value used."
        else:
            sym_table[sym] = { k.SYM_VAL: None, k.SYM_ERR: "" }
        sym_table[sym][k.SYM_VAL] = int(sym_val) + base
        cur += 2
    return def_list, cur, sym_table

def parse_use(mod, cur): 
    use_count = int(mod[cur])
    use_list = { k.USE_COUNT: use_count, k.USE_LIST: {} }
    cur += 1
    for _ in range(use_count):
        sym = mod[cur]
        sym_use_rel_addr = mod[cur + 1]
        if sym_use_rel_addr in use_list[k.USE_LIST]:
            use_list[k.USE_LIST][sym_use_rel_addr][k.SYM_KEY] = sym
            use_list[k.USE_LIST][sym_use_rel_addr][k.SYM_MULT_USE_FLAG] = True
        else: 
            use_list[k.USE_LIST][sym_use_rel_addr] = { 
                k.SYM_KEY: sym, 
                k.SYM_MULT_USE_FLAG: False 
            }
        cur += 2
    return use_list, cur

def parse_instructions(mod, cur, base): 
    instruction_count = int(mod[cur])
    instruction_list = { 
        k.INSTRUCTION_COUNT: instruction_count, 
        k.BASE: base, 
        k.INSTRUCTION_LIST: [] }
    cur += 1
    for _ in range(instruction_count):
        instruction_list[k.INSTRUCTION_LIST].append({ 
            k.TYPE: mod[cur], 
            k.WORD: int(mod[cur + 1]), 
            k.PROG_SYM_USED_FLAG: False,
            k.PROG_ERR: ""
        })
        cur += 2
    return instruction_list, cur

def process_ext_addr(old_addr, new_addr):
    first_digit = int(str(old_addr)[0])
    return (first_digit * 1000 + new_addr)

def format_sym_table_out(syms):
    syms_out = "Symbol Table\n"
    for sym, sym_info in syms.items():
        syms_out += "{}={} {}\n".format(sym, sym_info[k.SYM_VAL], sym_info[k.SYM_ERR])
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

def check_multiple_sym_usage(instruction_pair):
    MULT_SYM_USAGE_ERR = 'Error: Multiple symbols used here; last one used'
    if instruction_pair[k.PROG_SYM_USED_FLAG] == True: 
        instruction_pair[k.PROG_ERR] = MULT_SYM_USAGE_ERR
    else: 
        instruction_pair[k.PROG_SYM_USED_FLAG] = True
    return instruction_pair

def check_sym_used_not_defined(inst_pair, sym, sym_table, sym_use_stat): 
    is_sym_used_not_defined = False

    if sym not in sym_table: 
        USED_NOT_DEFINED_ERR = 'Error: ' + sym + ' was used but not defined. It has been given the value 111.'
        inst_pair[k.PROG_ERR] = USED_NOT_DEFINED_ERR
        is_sym_used_not_defined = True
    else:
        sym_use_stat[sym] = True

    new_sym_addr = '111' if is_sym_used_not_defined else sym_table[sym][k.SYM_VAL]
    return new_sym_addr, is_sym_used_not_defined

def modify_word_last_three_digits(word, replacement):
    return int(str(word)[0]) * 1000 + replacement

def input_second_pass(mods, sym_table): 
    mmap = []
    sym_use_stat = {}
    for sym in sym_table: 
        sym_use_stat[sym] = False
    for mod in mods[k.MODS]:
        use_list = mod[k.USE][k.USE_LIST]
        prog = mod[k.INSTRUCTIONS]
        inst_list = prog[k.INSTRUCTION_LIST]

        if use_list:
            process_use_list(use_list, inst_list, sym_table, sym_use_stat)
        
        process_instructions(inst_list, mmap, prog[k.BASE])

    mmap_out = format_mmap_out(mmap, sym_use_stat)
    return mmap_out

def process_use_list(use_list, inst_list, sym_table, sym_use_stat):
    for addr, sym_info in use_list.items():
        '''Resolve external addresses'''
        addr = int(addr)
        sym = sym_info[k.SYM_KEY]
        is_sym_multibly_used = sym_info[k.SYM_MULT_USE_FLAG]

        is_sym_used_not_defined = False
        old_sym_addr = inst_list[addr][k.WORD]
        addr_cur = str(old_sym_addr)

        new_sym_addr, is_sym_used_not_defined \
            = check_sym_used_not_defined(inst_list[addr], sym, sym_table, sym_use_stat)

        inst_list[addr][k.WORD] = process_ext_addr(old_sym_addr, int(new_sym_addr))
        if is_sym_multibly_used: 
            inst_list[addr][k.PROG_ERR] = 'Error: Multiple symbols used here; last one used'
        inst_list[addr] = check_multiple_sym_usage(inst_list[addr])
        
        while addr_cur[-3:] != '777':
            next_index = int(addr_cur[-3:])
            next_addr = str(inst_list[next_index][k.WORD])
            inst_list[next_index][k.WORD] = process_ext_addr(int(next_addr), int(new_sym_addr))
            inst_list[next_index] = check_multiple_sym_usage(inst_list[next_index])
            if is_sym_multibly_used: 
                inst_list[addr][k.PROG_ERR] = 'Error: Multiple symbols used here; last one used'
            if is_sym_used_not_defined == True: 
                inst_list[next_index][k.PROG_ERR] = 'Error: ' + sym + \
                    ' was used but not defined. It has been given the value 111.'
            addr_cur = next_addr

def process_instructions(inst_list, mmap, base):
    EXCEED_MOD_SIZE_ERR = 'Error: Type R address exceeds module size; 0 (relative) used'
    EXCEED_MACHINE_SIZE_ERR = 'Error: A type address exceeds machine size; max legal value used'
    for progpair in inst_list: 
        if progpair[k.TYPE] == 'R': 
            if int(str(progpair[k.WORD])[-3:]) >= len(inst_list):
                progpair[k.PROG_ERR] = EXCEED_MOD_SIZE_ERR
                progpair[k.WORD] = modify_word_last_three_digits(progpair[k.WORD], 0)
            progpair[k.WORD] += base
        elif progpair[k.TYPE] == 'A':
            if int(str(progpair[k.WORD])[-3:]) >= MACHINE_SIZE: 
                progpair[k.PROG_ERR] = EXCEED_MACHINE_SIZE_ERR
                progpair[k.WORD] = modify_word_last_three_digits(progpair[k.WORD], MAX_LEGAL_VAL)

        mmap.append(str(progpair[k.WORD]) + ' ' + progpair[k.PROG_ERR])

def main():
    uin = get_input()
    mods, sym_table = input_frist_pass(uin)
    print('\n' + format_sym_table_out(sym_table))
    mmap_out = input_second_pass(mods, sym_table)
    print(mmap_out)
    
if __name__ == "__main__":
    main()