import mod_keys as k
from sys import stdin

MACHINE_SIZE = 300
MAX_LEGAL_VAL = 299


def read_next_line():
    line = ""
    while True:
        line = input()
        if line:
            return line.split()


def increment_cur(cur, incr, list):
    cur += incr
    next_line = None
    if cur > (len(list) - 1):
        next_line = read_next_line()
        list += next_line
    return cur, list


def linker_first_pass():

    user_input = []

    first_line = read_next_line()
    user_input += first_line

    cur = 0
    mod_count = int(user_input[cur])
    cur, user_input = increment_cur(cur, 1, user_input)

    sym_table = {}
    base_accum = 0

    mods = {k.MOD_COUNT: int(mod_count), k.MODS: []}
    for mod_index in range(mod_count):
        mod = {k.DEF: {}, k.USE: {}, k.INSTRUCTIONS: {}}

        def_list, user_input, cur = parse_def(
            user_input, cur, sym_table, base_accum, mod_index)
        mod[k.DEF] = def_list

        use_list, user_input, cur = parse_use(user_input, cur)
        mod[k.USE] = use_list

        instruction_list, user_input, cur, base_accum = parse_instructions(
            user_input, cur, base_accum, mod_index, mod_count)
        mod[k.INSTRUCTIONS] = instruction_list
        mods[k.MODS].append(mod)

    return mods, sym_table


def parse_def(user_input, cur, sym_table, base_accum, mod_index):
    SYM_MULT_DEF_ERR = "Error: This variable is multiply defined; last value used."
    def_count = int(user_input[cur])
    cur, user_input = increment_cur(cur, 1, user_input)
    def_list = {k.DEF_COUNT: def_count, k.DEF_LIST: {}}
    for _ in range(def_count):
        sym = user_input[cur]
        cur, user_input = increment_cur(cur, 1, user_input)
        sym_val = user_input[cur]
        cur, user_input = increment_cur(cur, 1, user_input)
        def_list[k.DEF_LIST][sym] = int(sym_val)

        if sym in sym_table:
            sym_table[sym][k.SYM_ERR] = SYM_MULT_DEF_ERR
        else:
            sym_table[sym] = {k.SYM_VAL: None,
                              k.SYM_DEF_MOD: None, k.SYM_ERR: None}

        sym_table[sym][k.SYM_VAL] = int(sym_val) + base_accum
        sym_table[sym][k.SYM_DEF_MOD] = mod_index
    return def_list, user_input, cur


def parse_use(user_input, cur):
    use_count = int(user_input[cur])
    cur, user_input = increment_cur(cur, 1, user_input)
    use_list = {k.USE_COUNT: use_count, k.USE_LIST: {}}
    for _ in range(use_count):
        sym = user_input[cur]
        cur, user_input = increment_cur(cur, 1, user_input)
        sym_use_rel_addr = user_input[cur]
        cur, user_input = increment_cur(cur, 1, user_input)
        if sym_use_rel_addr in use_list[k.USE_LIST]:
            use_list[k.USE_LIST][sym_use_rel_addr][k.SYM_KEY] = sym
            use_list[k.USE_LIST][sym_use_rel_addr][k.SYM_MULT_USE_FLAG] = True
        else:
            use_list[k.USE_LIST][sym_use_rel_addr] = {
                k.SYM_KEY: sym,
                k.SYM_MULT_USE_FLAG: False
            }
    return use_list, user_input, cur


def parse_instructions(user_input, cur, base_accum, mod_index, mod_count):
    instruction_count = int(user_input[cur])
    cur, user_input = increment_cur(cur, 1, user_input)
    instruction_list = {
        k.INSTRUCTION_COUNT: instruction_count,
        k.BASE: base_accum,
        k.INSTRUCTION_LIST: []
    }
    base_accum += instruction_count
    for inst_index in range(instruction_count):
        inst_type = user_input[cur]
        cur, user_input = increment_cur(cur, 1, user_input)
        inst_word = int(user_input[cur])
        if (mod_index == (mod_count - 1)) and (inst_index == (instruction_count - 1)):
            pass
        else:
            cur, user_input = increment_cur(cur, 1, user_input)
        instruction_list[k.INSTRUCTION_LIST].append({
            k.TYPE: inst_type,
            k.WORD: inst_word,
            k.PROG_SYM_USED_FLAG: False,
            k.PROG_ERR: "",
        })
    return instruction_list, user_input, cur, base_accum


def process_ext_addr(old_addr, new_addr):
    first_digit = int(str(old_addr)[0])
    return (first_digit * 1000 + new_addr)


def format_sym_table_out(syms):
    syms_out = "Symbol Table\n"
    for sym, sym_info in syms.items():
        syms_out += "{}={} {}\n".format(sym,
                                        sym_info[k.SYM_VAL], sym_info[k.SYM_ERR])
    return syms_out


def format_mmap_out(mmap, sym_use_stat, sym_table):
    mmap_str = "Memory Map\n"
    for index, item in enumerate(mmap):
        mmap_str += "{}:\t{}\n".format(str(index), item)
    mmap_str += '\n'
    for sym in sym_use_stat:
        if sym_use_stat[sym] == False:
            sym_def_loc = sym_table[sym][k.SYM_DEF_MOD]
            warning = "Warning: {} was defined in {} but never used.\n".format(
                sym, sym_def_loc)
            mmap_str += warning
    return mmap_str


def is_symbol_defined(sym, sym_table):
    return True if sym in sym_table else False


def undefined_sym_err(sym):
    USED_NOT_DEFINED_ERR = 'Error: ' + sym + \
        ' was used but not defined. It has been given the value 111.'
    return USED_NOT_DEFINED_ERR


def resolve_new_addr(is_sym_defined, sym, inst_pair, sym_table, sym_use_stat):
    new_addr = None
    old_addr = inst_pair[k.WORD]
    if is_sym_defined:
        new_addr = sym_table[sym][k.SYM_VAL]
        sym_use_stat[sym] = True
    else:
        inst_pair[k.PROG_ERR] = undefined_sym_err(sym)
        new_addr = 111
    inst_pair[k.WORD] = process_ext_addr(old_addr, new_addr)
    return inst_pair


def modify_word_last_three_digits(word, replacement):
    return int(str(word)[0]) * 1000 + replacement


def process_use_list(use_list, inst_list, sym_table, sym_use_stat):
    MULT_SYM_USAGE_ERR = 'Error: Multiple symbols used here; last one used'
    for addr, sym_info in use_list.items():
        addr = int(addr)
        sym = sym_info[k.SYM_KEY]

        is_sym_multibly_used = sym_info[k.SYM_MULT_USE_FLAG]
        if is_sym_multibly_used:
            inst_list[addr][k.PROG_ERR] = MULT_SYM_USAGE_ERR

        old_addr = inst_list[addr][k.WORD]
        addr_cur = str(old_addr)

        is_sym_defined = is_symbol_defined(sym, sym_table)
        inst_list[addr] = resolve_new_addr(
            is_sym_defined, sym, inst_list[addr], sym_table, sym_use_stat)

        new_addr = str(inst_list[addr][k.WORD])[-3:]

        while addr_cur[-3:] != '777':
            next_index = int(addr_cur[-3:])
            next_addr = str(inst_list[next_index][k.WORD])
            inst_list[next_index][k.WORD] = process_ext_addr(
                int(next_addr), int(new_addr))
            if is_sym_multibly_used:
                inst_list[addr][k.PROG_ERR] = MULT_SYM_USAGE_ERR
            if not is_sym_defined:
                inst_list[next_index][k.PROG_ERR] = undefined_sym_err(sym)
            addr_cur = next_addr


def process_instructions(inst_list, mmap, base):
    EXCEED_MOD_SIZE_ERR = 'Error: Type R address exceeds module size; 0 (relative) used'
    EXCEED_MACHINE_SIZE_ERR = 'Error: A type address exceeds machine size; max legal value used'
    for progpair in inst_list:
        if progpair[k.TYPE] == 'R':
            if int(str(progpair[k.WORD])[-3:]) >= len(inst_list):
                progpair[k.PROG_ERR] = EXCEED_MOD_SIZE_ERR
                progpair[k.WORD] = modify_word_last_three_digits(
                    progpair[k.WORD], 0)
            progpair[k.WORD] += base
        elif progpair[k.TYPE] == 'A':
            if int(str(progpair[k.WORD])[-3:]) >= MACHINE_SIZE:
                progpair[k.PROG_ERR] = EXCEED_MACHINE_SIZE_ERR
                progpair[k.WORD] = modify_word_last_three_digits(
                    progpair[k.WORD], MAX_LEGAL_VAL)

        mmap.append(str(progpair[k.WORD]) + ' ' + progpair[k.PROG_ERR])


def linker_second_pass(mods, sym_table):
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
    mmap_out = format_mmap_out(mmap, sym_use_stat, sym_table)
    return mmap_out


def main():
    mods, sym_table = linker_first_pass()
    print('\n' + format_sym_table_out(sym_table))
    mmap_out = linker_second_pass(mods, sym_table)
    print(mmap_out)


if __name__ == "__main__":
    main()
