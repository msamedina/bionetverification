import os


def calc_n_primes(n):
    """
    calculate n primes
        Input:
            num_of_primes: max value of the interval - [2, n]
        Output:
            list of n primes
    """
    primes_list = []
    num = 1
    while len(primes_list) < n:
        num += 1
        for i in range(2, num):
            if (num % i) == 0:
                break
        else:
            primes_list.append(num)
    return primes_list


def create_ssp_file(num_of_primes, bug_cell=None, mu=1):
    """
    Print out the SSP network description to the prism file
        Input:
            num_of_primes: the number of elements in the set S.
            bug_cell: option to add a bug. bug cell is a list, [r, c, dir]. By default there are no bugs.
            mu: a probability of an error. By default there is no error, so mu = 1.
    """

    # calculate the first n primes, while n = num_of_primes

    primes = calc_n_primes(num_of_primes)

    filename = f'SSP_{num_of_primes}.pm'
    if os.path.exists(filename):
        os.remove(filename)

    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------

    # Open file and write header into file
    f = open(filename, 'w')
    f.write(f'// SSP Network for {num_of_primes} primes\n')
    f.write('// S = {' + str(primes)[1:-1] + '}\n')

    # calculate the split junctions
    split_junctions = []
    for p in primes:
        split_junctions.append(sum(primes[0:primes.index(p)]))

    f.write('// Split junctions are: {' + str(split_junctions)[1:-1] + '}\n\n')
    f.write('dtmc\n')

    # ----------------
    #      CONSTS
    # ----------------
    f.write('\n// Consts:\n')
    f.write('const pass = 0;\n')
    f.write('const split = 1;\n')
    f.write('const dwn = 0;\n')
    f.write('const diag = 1;\n')
    f.write(f'const maxrow = {sum(primes)};\n')
    f.write('const maxrow_1 = maxrow + 1;\n')
    f.write(f'const double mu  = {mu};\n')
    if bug_cell is None:
        bug_cell = [-2, -2, 0]
    f.write(f'const row_bug  = {bug_cell[0]};\n')
    f.write(f'const col_bug  = {bug_cell[1]};\n')
    f.write(f'const dir_bug  = {bug_cell[2]};\n')

    # ------------------
    #      FORMULAS
    # ------------------

    # fill 'next is split'
    f.write('\n\n// Formulas:\n')
    f.write('formula next_is_split = (')
    for sj in split_junctions[1:]:
        f.write(f'row = {sj - 1}')
        if sj != split_junctions[-1]:
            f.write(' | ')
    f.write(') & !force_dir;\n')

    # fill 'next is not split'
    f.write('formula next_is_not_split = !start & ')
    for sj in split_junctions[1:]:
        f.write(f'row != {sj - 1} & ')
    f.write('row != maxrow & !force_dir;\n')

    # fill next is maxrow or start
    f.write('formula next_is_maxrow = row = maxrow;\n')
    f.write('formula start = row = -1;\n')

    # fill error cell
    f.write('formula force_dir = row = row_bug & column = col_bug;\n')

    # ------------------
    #    MODULE NET
    # ------------------

    # declaration
    f.write('\n\n// Module:\n')
    f.write('module net\n')
    f.write('\trow: [-1..maxrow] init -1;\n')
    f.write('\tcolumn: [-1..maxrow] init -1;\n')
    f.write('\tjunction: [pass..split];\n')
    f.write('\tdir: [dwn..diag] init dwn;\n')
    f.write('\tsum: [-1..maxrow] init -1;\n')

    # transition relation
    str_temp = "[] (start | next_is_maxrow) & !force_dir -> 0.5 : (junction' = split) & (dir' = diag) & (column' = 0) & (row' = 0) & (sum' = column) + 0.5 : (junction' = split) & (dir' = dwn) & (column' = 0) & (row' = 0) & (sum' = column);"
    f.write('\n\t' + str_temp + '\n')
    str_temp = "	[] next_is_split -> 0.5 : (junction' = split) & (dir' = diag) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1)) + 0.5 : (junction' = split) & (dir' = dwn) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1));"
    f.write(str_temp + '\n')
    str_temp = "	[] next_is_not_split -> mu: (junction' = pass) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1)) & (dir'=dir) + (1-mu):(junction' = pass) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1)) & (dir' = mod(dir+1,2));"
    f.write(str_temp + '\n')
    str_temp = "	[] force_dir -> (junction' = pass) & (column' = column) & (row' = mod(row + 1, maxrow_1)) & (dir'=dir_bug);"
    f.write(str_temp + '\n')

    f.write('\nendmodule\n')

    # ------------------
    #  REWARD + LABELS
    # ------------------
    f.write('\n\n// Rewards:\n')
    f.write('rewards "steps"\n')
    f.write('\ttrue : 1;\n')
    f.write('endrewards\n')

    f.close()
