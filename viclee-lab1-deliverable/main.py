DEF = "def"
DEF_LIST = 'def_list'
DEF_COUNT = 'def_count'

USE = "use"
USE_LIST = "use_list"
USE_COUNT = "use_count"

INSTRUCTIONS = "instructions"
INSTRUCTION_LIST = 'instruction_list'
INSTRUCTION_COUNT = 'instruction_count'

BASE = "base"
MOD_COUNT = "mod_count"
MODS = "mods"

TYPE = "type"
WORD = "word"
PROG_ERR = "error"
PROG_SYM_USED_FLAG = "used_flag"

SYM_KEY = "sym"
SYM_VAL = "symbol_value"
SYM_ERR = "symbol_error_msg"
SYM_MULT_USE_FLAG = "symbol_multibly_used"

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
    mod_out = { DEF: {}, USE: {}, INSTRUCTIONS: {} }
    cur = 0

    mod_out[DEF], cur, sym_table = parse_def(mod_in, cur, sym_table, base)
    mod_out[USE], cur = parse_use(mod_in, cur)
    mod_out[INSTRUCTIONS], cur = parse_instructions(mod_in, cur, base)

    base += mod_out[INSTRUCTIONS][INSTRUCTION_COUNT]
    return mod_out, mod_in[cur:], base, sym_table

def parse_def(mod, cur, sym_table, base): 
    def_count = int(mod[cur])
    def_list = { DEF_COUNT: def_count, DEF_LIST: {} }
    cur += 1
    for _ in range(def_count):
        sym = mod[cur]
        sym_val = mod[cur + 1]
        def_list[DEF_LIST][sym] = int(sym_val)
        if sym in sym_table: 
            sym_table[sym][SYM_ERR] = "Error: This variable is multiply defined; last value used."
        else:
            sym_table[sym] = { SYM_VAL: None, SYM_ERR: "" }
        sym_table[sym][SYM_VAL] = int(sym_val) + base
        cur += 2
    return def_list, cur, sym_table

def parse_use(mod, cur): 
    use_count = int(mod[cur])
    use_list = { USE_COUNT: use_count, USE_LIST: {} }
    cur += 1
    for _ in range(use_count):
        sym = mod[cur]
        sym_use_rel_addr = mod[cur + 1]
        if sym_use_rel_addr in use_list[USE_LIST]:
            use_list[USE_LIST][sym_use_rel_addr][SYM_KEY] = sym
            use_list[USE_LIST][sym_use_rel_addr][SYM_MULT_USE_FLAG] = True
        else: 
            use_list[USE_LIST][sym_use_rel_addr] = { 
                SYM_KEY: sym, 
                SYM_MULT_USE_FLAG: False 
            }
        cur += 2
    return use_list, cur

def parse_instructions(mod, cur, base): 
    # COUNT = 'instruction_count'
    # LIST = 'instruction_list'
    instruction_count = int(mod[cur])
    instruction_list = { 
        INSTRUCTION_COUNT: instruction_count, 
        BASE: base, 
        INSTRUCTION_LIST: [] }
    cur += 1
    for _ in range(instruction_count):
        instruction_list[INSTRUCTION_LIST].append({ 
            TYPE: mod[cur], 
            WORD: int(mod[cur + 1]), 
            PROG_SYM_USED_FLAG: False,
            PROG_ERR: ""
        })
        cur += 2
    return instruction_list, cur

def process_ext_addr(old_addr, new_addr):
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

def check_multiple_sym_usage(instruction_pair):
    MULT_SYM_USAGE_ERR = 'Error: Multiple symbols used here; last one used'
    if instruction_pair[PROG_SYM_USED_FLAG] == True: 
        instruction_pair[PROG_ERR] = MULT_SYM_USAGE_ERR
    else: 
        instruction_pair[PROG_SYM_USED_FLAG] = True
    return instruction_pair

def check_sym_used_not_defined(progpair, sym, sym_table, sym_use_stat): 
    is_sym_used_not_defined = False
    if sym in sym_table: 
        new_sym_addr = sym_table[sym][SYM_VAL]
        sym_use_stat[sym] = True
    else: 
        is_sym_used_not_defined = True
        new_sym_addr = '111'
        progpair[PROG_ERR] = 'Error: ' + sym + ' was used but not defined. It has been given the value 111.'
    return new_sym_addr, is_sym_used_not_defined

def modify_word_last_three_digits(word, replacement):
    return int(str(word)[0]) * 1000 + replacement

def input_second_pass(mods, sym_table): 
    mmap = []
    sym_use_stat = {}
    for sym in sym_table: 
        sym_use_stat[sym] = False
    for mod in mods[MODS]:
        use_list = mod[USE][USE_LIST]
        prog = mod[INSTRUCTIONS]
        inst_list = prog[INSTRUCTION_LIST]

        if use_list:
            process_use_list(use_list, inst_list, sym_table, sym_use_stat)
        
        process_instructions(inst_list, mmap, prog[BASE])

    mmap_out = format_mmap_out(mmap, sym_use_stat)
    return mmap_out

def process_use_list(use_list, inst_list, sym_table, sym_use_stat):
    for uaddr, sym_info in use_list.items():
        '''Resolve external addresses'''
        uaddr = int(uaddr)
        usym = sym_info[SYM_KEY]
        is_sym_multibly_used = sym_info[SYM_MULT_USE_FLAG]

        is_sym_used_not_defined = False
        old_sym_addr = inst_list[uaddr][WORD]
        addr_cur = str(old_sym_addr)

        new_sym_addr, is_sym_used_not_defined \
            = check_sym_used_not_defined(inst_list[uaddr], usym, sym_table, sym_use_stat)

        inst_list[uaddr][WORD] = process_ext_addr(old_sym_addr, int(new_sym_addr))
        if is_sym_multibly_used: 
            inst_list[uaddr][PROG_ERR] = 'Error: Multiple symbols used here; last one used'
        inst_list[uaddr] = check_multiple_sym_usage(inst_list[uaddr])
        
        while addr_cur[-3:] != '777':
            next_index = int(addr_cur[-3:])
            next_addr = str(inst_list[next_index][WORD])
            inst_list[next_index][WORD] = process_ext_addr(int(next_addr), int(new_sym_addr))

            inst_list[next_index] = check_multiple_sym_usage(inst_list[next_index])
            if is_sym_multibly_used: 
                inst_list[uaddr][PROG_ERR] = 'Error: Multiple symbols used here; last one used'
            if is_sym_used_not_defined == True: 
                inst_list[next_index][PROG_ERR] = 'Error: ' + usym + \
                    ' was used but not defined. It has been given the value 111.'
            addr_cur = next_addr

def process_instructions(inst_list, mmap, base):
    EXCEED_MOD_SIZE_ERR = 'Error: Type R address exceeds module size; 0 (relative) used'
    EXCEED_MACHINE_SIZE_ERR = 'Error: A type address exceeds machine size; max legal value used'
    for progpair in inst_list: 
        if progpair[TYPE] == 'R': 
            if int(str(progpair[WORD])[-3:]) >= len(inst_list):
                progpair[PROG_ERR] = EXCEED_MOD_SIZE_ERR
                progpair[WORD] = modify_word_last_three_digits(progpair[WORD], 0)
            progpair[WORD] += base
        elif progpair[TYPE] == 'A':
            if int(str(progpair[WORD])[-3:]) >= MACHINE_SIZE: 
                progpair[PROG_ERR] = EXCEED_MACHINE_SIZE_ERR
                progpair[WORD] = modify_word_last_three_digits(progpair[WORD], MAX_LEGAL_VAL)

        mmap.append(str(progpair[WORD]) + ' ' + progpair[PROG_ERR])

def main():
    uin = get_input()
    mods, sym_table = input_frist_pass(uin)
    print('\n' + format_sym_table_out(sym_table))
    mmap_out = input_second_pass(mods, sym_table)
    print(mmap_out)
    
if __name__ == "__main__":
    main()