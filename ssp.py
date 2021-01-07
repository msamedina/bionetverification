"""
SSP Functions
Michelle Aluf Medina
"""
import logging
import miscfunctions as misc
# import nusmv
import modcheck
import pandas as pd


def print_ssp_menu(str_mc):
    """
    Print menu for SSP options to screen.
    """
    if str_mc == 'NuSMV' or str_mc == 'nuXmv':
        print('What would you like to look at with this set:\n')
        print('\t[1] Bulk run output specifications')
        print('\t[2] Run individual output specifications')
        print('\t[3] Run general valid-invalid output specifications')
        print('\t[4] Main Menu')
    elif str_mc == 'prism':
        print('What would you like to look at with this set:\n')
        print('\t[1] Run general valid-invalid output')
        print('\t[2] Calculate the probabilities of outputs')
        print('\t[3] Main Menu')


def file_name_gen(set_array, arr_length, str_mc='NuSMV'):
    """
    Generate smv file name for given SSP problem using the set
        Input:
            set_array: The input set
            arr_length: Number of elements in the set
        Output:
            filename: smv file name for the SSP network with formatting
    """
    if str_mc == 'NuSMV' or str_mc == 'NuSMV':
        filename = 'autoSSP_'
        for i in range(arr_length):
            filename += str(set_array[i]) + '_'
        filename += 'Set_{0}.smv'
        return misc.file_name_cformat(filename)

    elif str_mc == 'prism':
        filename = 'autoSSP_'
        for i in range(arr_length):
            filename += str(set_array[i]) + '_'
        filename += 'Set.pm'
        return misc.file_name_cformat(filename)


def print_smv_ssp(filename, set_array, max_sum, set_size, max_tag_id):
    """
    Print out the SSP network description to the smv file
        Input:
            filename: The NuSMV filename in which to write the description
            set_array: the set being looked at for the subset sum problem
            max_sum: the total sum of all elements in the set
            set_size: the size of the set
            max_tag_id: empty array containing the last tag element
    """
    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------
    # Write header into file
    f = open(filename, 'w')
    f.write('--Auto Subset Sum ' + str(set_array)
            + '\n-------------------------------\n')

    # ----------------
    # Find row locations of split junctions
    split_j_loc = [0]
    for i in range(0, len(set_array) - 1):
        split_j_loc.append(set_array[i] + split_j_loc[i])
    # Calculate number of split junctions
    num_split_j = sum(split_j_loc) + len(split_j_loc)
    max_tag_id.append(num_split_j - 1)
    # ----------------
    # Write beginning of module and variable definitions
    f.write('MODULE main\n' + 'VAR\n')
    f.write('\trow: 0..' + str(max_sum) + ';\n')
    f.write('\tcolumn: 0..' + str(max_sum) + ';\n')
    f.write('\tjunction: {pass, split};\n')
    f.write('\tdir: {dwn, diag};\n')
    f.write('\tflag: boolean;\n')
    f.write('\ttag: array 0..' + str(num_split_j - 1) + ' of boolean;\n\n')

    # Write assignment definitions
    f.write('ASSIGN\n')
    f.write('\tinit(row) := 0;\n')
    f.write('\tinit(column) := 0;\n')
    f.write('\tinit(junction) := split;\n')
    f.write('\tinit(dir) := dwn;\n')
    f.write('\tinit(flag) := FALSE;\n\n')
    for i in range(0, num_split_j):
        if (((i + 1) % 5) == 0) or (i == num_split_j - 1):
            f.write('\tinit(tag[' + str(i) + ']) := FALSE;\n')
        else:
            f.write('\tinit(tag[' + str(i) + ']) := FALSE;\t')

    # ----------------
    # Write row transitions to file
    f.write('\n\n\t--Always advance to next row\n')
    f.write('\tnext(row) := (row + 1) mod ' + str(max_sum + 1) + ';\n')

    # Write flag transitions to file
    f.write('\n\t--Flag turns on when row is ' + str(max_sum) + '\n')
    f.write('\tnext(flag) := (next(row) = ' + str(max_sum) +
            ' ? TRUE : FALSE);\n')

    # Write junction transitions to file
    f.write('\n\t--Split junctions at rows ')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write(str(split_j_loc[i]) + ', ')
        else:
            f.write(str(split_j_loc[i]) + '\n')
    f.write('\tnext(junction) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t(')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')|')
        else:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')): split;\n')
            f.write('\t\t\t\t\t\tTRUE: pass;\n\t\t\t\t\tesac;\n\n')

    # Write direction transitions to file
    f.write('\t--Decide direction for next move by to current junction\n')
    f.write('\tnext(dir) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(junction = split): {dwn, diag};\n\t\t\t\t\t\t')
    f.write('(junction = pass): dir;\n\t\t\t\t\t\t')
    f.write('TRUE: {dwn, diag};\n\t\t\t\t\tesac;\n\n')

    # Write column transitions to file
    f.write('\t--If diag, increase column, otherwise dwn, same column\n')
    f.write('\tnext(column) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(next(row) = 0): 0;\n\t\t\t\t\t\t')
    f.write('(next(dir) = diag): (column + 1) mod ' + str(max_sum + 1)
            + ';\n\t\t\t\t\t\t')
    f.write('(next(dir) = dwn): column;\n\t\t\t\t\t\t')
    f.write('TRUE: column;\n\t\t\t\t\tesac;\n\n')

    # Write tag transitions to file
    f.write('\t--Set tag TRUE if curr row = split, dir = diag\n')
    i = 0
    while i < num_split_j:
        for j in range(0, len(split_j_loc)):
            for k in range(0, split_j_loc[j] + 1):
                f.write('\tnext(tag[' + str(i)
                        + ']) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
                f.write('(row = ' + str(split_j_loc[j]) + ') & (column = '
                        + str(k) + ') & next(dir) = diag: TRUE;\n\t\t\t\t\t\t')
                f.write('(next(row) = 0): FALSE;\n\t\t\t\t\t\t')
                f.write('TRUE: tag[' + str(i) + '];\n\t\t\t\t\tesac;\n\n')
                i += 1

    # ----------------
    # Write specifications for each network output
    for i in range(0, max_sum + 1):
        f.write('LTLSPEC\tNAME\tltl_' + str(i)
                + ' := G! ((flag = TRUE) & (column = ' + str(i) + '));\n')
        f.write('CTLSPEC\tNAME\tctl_' + str(i)
                + ' := EF ((flag = TRUE) & (column = ' + str(i) + '));\n')

    # ----------------
    # CLOSE THE FILE
    f.close()


def print_smv_ssp_nt(filename, set_array, max_sum, set_size):
    """
    Print out the SSP network description to the smv file
        Input:
            filename: The NuSMV filename in which to write the description
            set_array: the set being looked at for the subset sum problem
            max_sum: the total sum of all elements in the set
            set_size: the size of the set
    """
    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------
    # Write header into file
    f = open(filename, 'w')
    f.write('--Auto Subset Sum ' + str(set_array)
            + '\n-------------------------------\n')

    # ----------------
    # Find row locations of split junctions
    split_j_loc = [0]
    for i in range(0, len(set_array) - 1):
        split_j_loc.append(set_array[i] + split_j_loc[i])
    # ----------------
    # Write beginning of module and variable definitions
    f.write('MODULE main\n' + 'VAR\n')
    f.write('\trow: 0..' + str(max_sum) + ';\n')
    f.write('\tcolumn: 0..' + str(max_sum) + ';\n')
    f.write('\tjunction: {pass, split};\n')
    f.write('\tdir: {dwn, diag};\n')
    f.write('\tflag: boolean;\n')

    # Write assignment definitions
    f.write('ASSIGN\n')
    f.write('\tinit(row) := 0;\n')
    f.write('\tinit(column) := 0;\n')
    f.write('\tinit(junction) := split;\n')
    f.write('\tinit(dir) := dwn;\n')
    f.write('\tinit(flag) := FALSE;\n\n')

    # ----------------
    # Write row transitions to file
    f.write('\n\n\t--Always advance to next row\n')
    f.write('\tnext(row) := (row + 1) mod ' + str(max_sum + 1) + ';\n')

    # Write flag transitions to file
    f.write('\n\t--Flag turns on when row is ' + str(max_sum) + '\n')
    f.write('\tnext(flag) := (next(row) = ' + str(max_sum) +
            ' ? TRUE : FALSE);\n')

    # Write junction transitions to file
    f.write('\n\t--Split junctions at rows ')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write(str(split_j_loc[i]) + ', ')
        else:
            f.write(str(split_j_loc[i]) + '\n')
    f.write('\tnext(junction) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t(')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')|')
        else:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')): split;\n')
            f.write('\t\t\t\t\t\tTRUE: pass;\n\t\t\t\t\tesac;\n\n')

    # Write direction transitions to file
    f.write('\t--Decide direction for next move by to current junction\n')
    f.write('\tnext(dir) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(junction = split): {dwn, diag};\n\t\t\t\t\t\t')
    f.write('(junction = pass): dir;\n\t\t\t\t\t\t')
    f.write('TRUE: {dwn, diag};\n\t\t\t\t\tesac;\n\n')

    # Write column transitions to file
    f.write('\t--If diag, increase column, otherwise dwn, same column\n')
    f.write('\tnext(column) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(next(row) = 0): 0;\n\t\t\t\t\t\t')
    f.write('(next(dir) = diag): (column + 1) mod ' + str(max_sum + 1)
            + ';\n\t\t\t\t\t\t')
    f.write('(next(dir) = dwn): column;\n\t\t\t\t\t\t')
    f.write('TRUE: column;\n\t\t\t\t\tesac;\n\n')

    # ----------------
    # Write specifications for each network output
    for i in range(0, max_sum + 1):
        f.write('LTLSPEC\tNAME\tltl_' + str(i)
                + ' := G! ((flag = TRUE) & (column = ' + str(i) + '));\n')
        f.write('CTLSPEC\tNAME\tctl_' + str(i)
                + ' := EF ((flag = TRUE) & (column = ' + str(i) + '));\n')

    # ----------------
    # CLOSE THE FILE
    f.close()


def print_smv_ssp_newspec(filename, set_array, max_sum, set_size, max_tag_id, use_tag):
    """
    Print out the SSP network description to the smv file
    Use new specifications checking valid and invalid sum values
        Input:
            filename: The NuSMV filename in which to write the description
            set_array: the set being looked at for the subset sum problem
            max_sum: the total sum of all elements in the set
            set_size: the size of the set
            max_tag_id: empty array containing the last tag element
            use_tag: true - add tag variable, flase - do not add tag variable
    """
    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------
    # Write header into file
    f = open(filename, 'w')
    f.write('--Auto Subset Sum ' + str(set_array)
            + '\n-------------------------------\n')

    # ----------------
    # Find row locations of split junctions
    split_j_loc = [0]
    for i in range(0, len(set_array) - 1):
        split_j_loc.append(set_array[i] + split_j_loc[i])
    # Calculate number of split junctions
    num_split_j = sum(split_j_loc) + len(split_j_loc)
    max_tag_id.append(num_split_j - 1)
    # ----------------
    # Write beginning of module and variable definitions
    f.write('MODULE main\n' + 'VAR\n')
    f.write('\trow: 0..' + str(max_sum) + ';\n')
    f.write('\tcolumn: 0..' + str(max_sum) + ';\n')
    f.write('\tjunction: {pass, split};\n')
    f.write('\tdir: {dwn, diag};\n')
    f.write('\tflag: boolean;\n')
    f.write('\tsum: 0..' + str(max_sum + 1) + ';\n')
    f.write('\txsum: 0..' + str(max_sum + 1) + ';\n')
    if use_tag:
        f.write('\ttag: array 0..' + str(num_split_j - 1) + ' of boolean;\n')

    # Write assignment definitions
    f.write('\nASSIGN\n')
    f.write('\tinit(row) := 0;\n')
    f.write('\tinit(column) := 0;\n')
    f.write('\tinit(junction) := split;\n')
    f.write('\tinit(dir) := dwn;\n')
    f.write('\tinit(flag) := FALSE;\n')
    f.write('\tinit(sum) := ' + str(max_sum + 1) + ';\n')
    f.write('\tinit(xsum) := ' + str(max_sum + 1) + ';\n\n')
    if use_tag:
        for i in range(0, num_split_j):
            if (((i + 1) % 5) == 0) or (i == num_split_j - 1):
                f.write('\tinit(tag[' + str(i) + ']) := FALSE;\n')
            else:
                f.write('\tinit(tag[' + str(i) + ']) := FALSE;\t')

    # ----------------
    # Write row transitions to file
    f.write('\n\n\t--Always advance to next row\n')
    f.write('\tnext(row) := (row + 1) mod ' + str(max_sum + 1) + ';\n')

    # Write flag transitions to file
    f.write('\n\t--Flag turns on when row is ' + str(max_sum) + '\n')
    f.write('\tnext(flag) := (next(row) = ' + str(max_sum) +
            ' ? TRUE : FALSE);\n')

    # Write junction transitions to file
    f.write('\n\t--Split junctions at rows ')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write(str(split_j_loc[i]) + ', ')
        else:
            f.write(str(split_j_loc[i]) + '\n')
    f.write('\tnext(junction) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t(')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')|')
        else:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')): split;\n')
            f.write('\t\t\t\t\t\tTRUE: pass;\n\t\t\t\t\tesac;\n\n')

    # Write direction transitions to file
    f.write('\t--Decide direction for next move by to current junction\n')
    f.write('\tnext(dir) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(junction = split): {dwn, diag};\n\t\t\t\t\t\t')
    f.write('(junction = pass): dir;\n\t\t\t\t\t\t')
    f.write('TRUE: {dwn, diag};\n\t\t\t\t\tesac;\n\n')

    # Write column transitions to file
    f.write('\t--If diag, increase column, otherwise dwn, same column\n')
    f.write('\tnext(column) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(next(row) = 0): 0;\n\t\t\t\t\t\t')
    f.write('(next(dir) = diag): (column + 1) mod ' + str(max_sum + 1)
            + ';\n\t\t\t\t\t\t')
    f.write('(next(dir) = dwn): column;\n\t\t\t\t\t\t')
    f.write('TRUE: column;\n\t\t\t\t\tesac;\n\n')

    # Write sum and xsum transitions to file
    vsum, ivsum = misc.subset_sums(set_array, set_size)
    vsum_str = ", ".join(repr(e) for e in vsum)
    ivsum_str = ", ".join(repr(e) for e in ivsum)
    f.write('\t--Pick random sum and xsum after initial state\n')
    f.write('\tnext(sum) := (sum = ' + str(max_sum + 1) + ' ? {' + vsum_str + '} : sum);\n')
    f.write('\tnext(xsum) := (xsum = ' + str(max_sum + 1) + ' ? {' + ivsum_str + '} : xsum);\n')

    # Write tag transitions to file
    if use_tag:
        f.write('\t--Set tag TRUE if curr row = split, dir = diag\n')
        i = 0
        while i < num_split_j:
            for j in range(0, len(split_j_loc)):
                for k in range(0, split_j_loc[j] + 1):
                    f.write('\tnext(tag[' + str(i)
                            + ']) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
                    f.write('(row = ' + str(split_j_loc[j]) + ') & (column = '
                            + str(k) + ') & next(dir) = diag: TRUE;\n\t\t\t\t\t\t')
                    f.write('(next(row) = 0): FALSE;\n\t\t\t\t\t\t')
                    f.write('TRUE: tag[' + str(i) + '];\n\t\t\t\t\tesac;\n\n')
                    i += 1

    # ----------------
    # Write new specifications
    f.write('--Valid Network:\tSpec returns true, the network always exits on a valid sum\n')
    f.write(
        '--Invalid Network:\tSpec returns false, there exists a non-reachable valid sum. Counter-example shows one non-reachable valid sum\n')
    f.write('CTLSPEC\tNAME\tcsum := !(EX (AG ((flag = FALSE) | (!(column = sum)))));\n')

    f.write('--Valid Network:\tSpec returns true, there exists no path to an invalid sum\n')
    f.write(
        '--Invalid Network:\tSpec returns false, there exists a path to an invalid sum. Counter-example shows one reachable invalid sum\n')
    f.write('CTLSPEC\tNAME\tnsum := !(EF ((flag = TRUE) & (column = xsum)));\n')

    # ----------------
    # CLOSE THE FILE
    f.close()


def manual_input():
    """
    MANUALLY ENTER SSP SET
    """
    # Receive set size
    logging.info('Receiving SSP set manually')
    set_array = list()
    set_size = misc.int_input(out_str='How many numbers are in your set: ')
    # Receive the set elements
    print('Enter numbers in your set (use return between elements): ')
    for i in range(0, set_size):
        temp = misc.int_input()
        set_array.append(temp)
    print('Your set is ' + str(set_array) + '\n')
    logging.info('Set is: ' + str(set_array))
    # Calculate the maximum sum of elements in the set
    max_sum = sum(set_array)
    return set_array, max_sum


def read_ssp(filename):
    """
    Parse the ssp input file for list of ssp problems
    Find file format in README
        Input:
            filename: SSP input file name
        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """
    logging.info('Opening SSP input file')
    in_data = open(filename, "r")
    ssp_list = list()
    ssp_list.append(list())

    # Run through the lines of data in the file
    for set_id, line in enumerate(in_data):
        tokens = line.split()
        if len(tokens) != 0:
            for tok in tokens:
                lit = int(tok)
                if lit == 0:
                    logging.info('Set ' + str(set_id) + ': ' + str(ssp_list[-1]))
                    ssp_list.append(list())
                else:
                    ssp_list[-1].append(lit)
    ssp_list.pop()
    logging.info('Total number of SSP sets: ' + str(set_id + 1))
    return ssp_list, set_id


def smv_gen(ssp_arr, with_tags='both'):
    """
    Loop through array of SSP problems and generate two smv files for each (with and without tags)
        Input:
            filename: NuSMV output file name
            with_tags: Flag for using networks with tags
        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """
    ssp_smv = []
    ssp_smv_nt = []
    ssp_smv_name = ''

    for ssp in ssp_arr:
        # Create SSP NuSMV File
        max_tag_id = []
        # With tags
        if with_tags in ['with', 'both']:
            logging.info('Generating NuSMV file with tags...')
            ssp_smv_name = file_name_gen(ssp, len(ssp), 'NuSMV')
            print_smv_ssp(ssp_smv_name, ssp, sum(ssp), len(ssp), max_tag_id)
            logging.info('Generated NuSMV file with tags')
            ssp_smv.append(ssp_smv_name)

        # Without tags
        if with_tags in ['without', 'both']:
            logging.info('Generating NuSMV file without tags...')
            ssp_smv_name_nt = 'NT_' + ssp_smv_name
            print_smv_ssp_nt(ssp_smv_name_nt, ssp, sum(ssp), len(ssp))
            logging.info('Generated NuSMV file without tags')
            ssp_smv_nt.append(ssp_smv_name_nt)

    return ssp_smv, ssp_smv_nt


def run_nusmv_all(ssp_arr, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn, str_modcheker, with_tags='both'):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
        Input:
            ssp_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modcheker: string containing name of model checker (NuSMV or nuXmv)
            with_tags: Flag for using networks with tags

        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """
    for index, ssp in enumerate(ssp_arr):
        # Save index, k, set, and filenames in excel file
        logging.info('Inputting ID, k, and set data into Excel...')
        __ = wsheet.cell(column=1, row=(index + 4), value=index)
        __ = wsheet.cell(column=2, row=(index + 4), value=len(ssp))
        __ = wsheet.cell(column=3, row=(index + 4), value=repr(ssp))
        wbook.save(xl_fn)

        # Run NuSMV on with tags
        if with_tags in ['with', 'both']:
            __ = wsheet.cell(column=4, row=(index + 4), value=smv_t_arr[index])
            wbook.save(xl_fn)

            out_fn, out_rt = modcheck.call_nusmv_pexpect_allout(smv_t_arr[index], index, wsheet, wbook, xl_fn,
                                                                str_modcheker)
            __ = wsheet.cell(column=6, row=(index + 4), value=out_fn[0])
            __ = wsheet.cell(column=7, row=(index + 4), value=out_rt[0])
            __ = wsheet.cell(column=8, row=(index + 4), value=out_fn[1])
            __ = wsheet.cell(column=9, row=(index + 4), value=out_rt[1])
            wbook.save(xl_fn)

        # Run NuSMV on no tags
        if with_tags in ['without', 'both']:
            __ = wsheet.cell(column=5, row=(index + 4), value=smv_nt_arr[index])
            wbook.save(xl_fn)

            out_fn, out_rt = modcheck.call_nusmv_pexpect_allout(smv_nt_arr[index], index, wsheet, wbook, xl_fn,
                                                                str_modcheker)
            __ = wsheet.cell(column=10, row=(index + 4), value=out_fn[0])
            __ = wsheet.cell(column=11, row=(index + 4), value=out_rt[0])
            __ = wsheet.cell(column=12, row=(index + 4), value=out_fn[1])
            __ = wsheet.cell(column=13, row=(index + 4), value=out_rt[1])
            wbook.save(xl_fn)


def run_nusmv_single(ssp_arr, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn, str_modcheker, with_tags='both'):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
        Input:
            ssp_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modcheker: string containing name of model checker (NuSMV or nuXmv)
            with_tags: Flag for using networks with tags
        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """
    row_id = 0
    for index, ssp in enumerate(ssp_arr):
        max_sum = sum(ssp)
        for output in range(max_sum + 1):
            # Save index, k, set, filenames, and output of interest in excel file
            logging.info('Inputting ID, k, set, filenames, and output data into Excel...')
            __ = wsheet.cell(column=1, row=(row_id + 4), value=index)
            __ = wsheet.cell(column=2, row=(row_id + 4), value=len(ssp))
            __ = wsheet.cell(column=3, row=(row_id + 4), value=repr(ssp))
            __ = wsheet.cell(column=6, row=(row_id + 4), value=output)
            wbook.save(xl_fn)

            ltl_res = ''
            ctl_res = ''

            # Run NuSMV on with tags
            if with_tags in ['with', 'both']:
                __ = wsheet.cell(column=4, row=(row_id + 4), value=smv_t_arr[index])
                wbook.save(xl_fn)

                out_fn, out_rt = modcheck.call_nusmv_pexpect_singleout(smv_t_arr[index], 1, output, str_modcheker)

                # Parse output files:
                ltl_res = modcheck.get_spec_res(out_fn[0])
                logging.info('LTL Result: ' + ltl_res)
                ctl_res = modcheck.get_spec_res(out_fn[1])
                logging.info('CTL Result: ' + ctl_res)

                logging.info('Saving Tags data in Excel')
                __ = wsheet.cell(column=8, row=(row_id + 4), value=out_fn[0])
                __ = wsheet.cell(column=9, row=(row_id + 4), value=ltl_res)
                __ = wsheet.cell(column=10, row=(row_id + 4), value=out_rt[0])
                __ = wsheet.cell(column=11, row=(row_id + 4), value=out_fn[1])
                __ = wsheet.cell(column=12, row=(row_id + 4), value=ctl_res)
                __ = wsheet.cell(column=13, row=(row_id + 4), value=out_rt[1])
                wbook.save(xl_fn)

            # Run NuSMV on no tags
            if with_tags in ['without', 'both']:
                __ = wsheet.cell(column=5, row=(row_id + 4), value=smv_nt_arr[index])
                wbook.save(xl_fn)

                out_fn, out_rt = modcheck.call_nusmv_pexpect_singleout(smv_nt_arr[index], 1, output, str_modcheker)

                # Parse output files:
                ltl_res = modcheck.get_spec_res(out_fn[0])
                logging.info('LTL Result: ' + ltl_res)
                ctl_res = modcheck.get_spec_res(out_fn[1])
                logging.info('CTL Result: ' + ctl_res)
                logging.info('Saving Tags data in Excel')
                __ = wsheet.cell(column=14, row=(row_id + 4), value=out_fn[0])
                __ = wsheet.cell(column=15, row=(row_id + 4), value=ltl_res)
                __ = wsheet.cell(column=16, row=(row_id + 4), value=out_rt[0])
                __ = wsheet.cell(column=17, row=(row_id + 4), value=out_fn[1])
                __ = wsheet.cell(column=18, row=(row_id + 4), value=ctl_res)
                __ = wsheet.cell(column=19, row=(row_id + 4), value=out_rt[1])
                wbook.save(xl_fn)

            if ltl_res == 'false' and ctl_res == 'true':
                __ = wsheet.cell(column=7, row=(row_id + 4), value='YES')
            elif ltl_res == 'true' and ctl_res == 'false':
                __ = wsheet.cell(column=7, row=(row_id + 4), value='NO')
            else:
                __ = wsheet.cell(column=7, row=(row_id + 4), value='INVALID RESULT')
            wbook.save(xl_fn)

            # Prepare for next input
            row_id = row_id + 1


def run_nusmv_bmc(ssp_arr, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn, str_modcheker):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
        Input:
            ssp_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modcheker: string containing name of model checker (NuSMV or nuXmv)
        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """
    row_id = 0
    for index, ssp in enumerate(ssp_arr):
        max_sum = sum(ssp)
        for output in range(max_sum + 1):
            # Save index, k, set, filenames, and output of interest in excel file
            logging.info('Inputting ID, k, set, filenames, and output data into Excel...')
            __ = wsheet.cell(column=1, row=(row_id + 4), value=index)
            __ = wsheet.cell(column=2, row=(row_id + 4), value=len(ssp))
            __ = wsheet.cell(column=3, row=(row_id + 4), value=repr(ssp))
            __ = wsheet.cell(column=4, row=(row_id + 4), value=max_sum)
            __ = wsheet.cell(column=5, row=(row_id + 4), value=smv_t_arr[index])
            __ = wsheet.cell(column=6, row=(row_id + 4), value=smv_nt_arr[index])
            __ = wsheet.cell(column=7, row=(row_id + 4), value=output)
            wbook.save(xl_fn)

            # Run NuSMV on with tags
            out_res, out_rt = modcheck.call_nusmv_pexpect_bmc(smv_t_arr[index], 1, output, max_sum, str_modcheker)

            logging.info('Saving Tags data in Excel')
            __ = wsheet.cell(column=8, row=(row_id + 4), value=out_res)
            __ = wsheet.cell(column=9, row=(row_id + 4), value=out_rt)
            wbook.save(xl_fn)

            # Run NuSMV on no tags
            out_res, out_rt = modcheck.call_nusmv_pexpect_bmc(smv_nt_arr[index], 1, output, max_sum, str_modcheker)

            logging.info('Saving No Tags data in Excel')
            __ = wsheet.cell(column=10, row=(row_id + 4), value=out_res)
            __ = wsheet.cell(column=11, row=(row_id + 4), value=out_rt)
            wbook.save(xl_fn)

            # Prepare for next input
            row_id = row_id + 1


def smv_gen_newspec(ssp_arr, with_tags='both'):
    """
    Loop through array of SSP problems and generate two smv files for each (with and without tags)
    Using the new specification setup
        Input:
            filename: NuSMV output file name
            with_tags: Flag for using networks with tags
        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """
    ssp_smv = []
    ssp_smv_nt = []
    for ssp in ssp_arr:
        # Create SSP NuSMV File
        max_tag_id = []
        ssp_smv_name = ''
        # With tags
        if with_tags in ['with', 'both']:
            logging.info('Generating NuSMV file with tags...')
            ssp_smv_name = file_name_gen(ssp, len(ssp), 'NuSMV')
            print_smv_ssp_newspec(ssp_smv_name, ssp, sum(ssp), len(ssp), max_tag_id, True)
            logging.info('Generated NuSMV file with tags')
            ssp_smv.append(ssp_smv_name)

        # Without tags
        if with_tags in ['without', 'both']:
            logging.info('Generating NuSMV file without tags...')
            ssp_smv_name_nt = 'NT_' + ssp_smv_name
            print_smv_ssp_newspec(ssp_smv_name_nt, ssp, sum(ssp), len(ssp), max_tag_id, False)
            logging.info('Generated NuSMV file without tags')
            ssp_smv_nt.append(ssp_smv_name_nt)

    return ssp_smv, ssp_smv_nt


def run_nusmv_newspec(ssp_arr, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn, str_modcheker, with_tags='both'):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
    Using new specification type
        Input:
            ssp_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modcheker: string containing name of model checker (NuSMV or nuXmv)
            with_tags: Flag for using networks with tags
    """
    row_id = 0
    for index, ssp in enumerate(ssp_arr):
        # Save index, k, set, filenames, and output of interest in excel file
        logging.info('Inputting ID, k, set, filenames, and spec data into Excel...')
        __ = wsheet.cell(column=1, row=(row_id + 4), value=index)
        __ = wsheet.cell(column=1, row=(row_id + 5), value=index)
        __ = wsheet.cell(column=2, row=(row_id + 4), value=len(ssp))
        __ = wsheet.cell(column=2, row=(row_id + 5), value=len(ssp))
        __ = wsheet.cell(column=3, row=(row_id + 4), value=repr(ssp))
        __ = wsheet.cell(column=3, row=(row_id + 5), value=repr(ssp))
        __ = wsheet.cell(column=6, row=(row_id + 4), value='csum')
        __ = wsheet.cell(column=6, row=(row_id + 5), value='nsum')
        wbook.save(xl_fn)

        # Run NuSMV new spec on with tags
        if with_tags in ['with', 'both']:
            __ = wsheet.cell(column=4, row=(row_id + 4), value=smv_t_arr[index])
            __ = wsheet.cell(column=4, row=(row_id + 5), value=smv_t_arr[index])
            wbook.save(xl_fn)

            out_fn, out_rt = modcheck.call_nusmv_pexpect_ssp_newspec(smv_t_arr[index], str_modcheker)

            # Parse output files if runtime not = "Killed":
            if out_rt[0] != 'Killed':
                csum = modcheck.get_spec_res(out_fn[0])
            else:
                csum = 'Killed'
            if out_rt[1] != 'Killed':
                nsum = modcheck.get_spec_res(out_fn[1])
            else:
                nsum = 'Killed'
            logging.info('csum Result: ' + csum)
            logging.info('nsum Result: ' + nsum)

            if csum == 'false':
                __ = wsheet.cell(column=7, row=(row_id + 4), value='INVALID')
            elif csum == 'true':
                __ = wsheet.cell(column=7, row=(row_id + 4), value='VALID')
            elif csum == 'Killed':
                __ = wsheet.cell(column=7, row=(row_id + 4), value=csum)
            if nsum == 'false':
                __ = wsheet.cell(column=7, row=(row_id + 5), value='INVALID')
            elif nsum == 'true':
                __ = wsheet.cell(column=7, row=(row_id + 5), value='VALID')
            elif nsum == 'Killed':
                __ = wsheet.cell(column=7, row=(row_id + 5), value=nsum)

            logging.info('Saving Tags data in Excel')
            __ = wsheet.cell(column=8, row=(row_id + 4), value=out_fn[0])
            __ = wsheet.cell(column=9, row=(row_id + 4), value=out_rt[0])
            __ = wsheet.cell(column=8, row=(row_id + 5), value=out_fn[1])
            __ = wsheet.cell(column=9, row=(row_id + 5), value=out_rt[1])
            wbook.save(xl_fn)

        # Run NuSMV on no tags
        if with_tags in ['without', 'both']:
            __ = wsheet.cell(column=5, row=(row_id + 4), value=smv_nt_arr[index])
            __ = wsheet.cell(column=5, row=(row_id + 5), value=smv_nt_arr[index])
            wbook.save(xl_fn)

            out_fn_nt, out_rt_nt = modcheck.call_nusmv_pexpect_ssp_newspec(smv_nt_arr[index], str_modcheker)

            # Parse output files if runtime not = "Killed":
            if out_rt_nt[0] != 'Killed':
                csum = modcheck.get_spec_res(out_fn_nt[0])
            else:
                csum = 'Killed'
            if out_rt_nt[1] != 'Killed':
                nsum = modcheck.get_spec_res(out_fn_nt[1])
            else:
                nsum = 'Killed'
            logging.info('csum Result: ' + csum)
            logging.info('nsum Result: ' + nsum)

            if csum == 'false':
                __ = wsheet.cell(column=7, row=(row_id + 4), value='INVALID')
            elif csum == 'true':
                __ = wsheet.cell(column=7, row=(row_id + 4), value='VALID')
            elif csum == 'Killed':
                __ = wsheet.cell(column=7, row=(row_id + 4), value=csum)
            if nsum == 'false':
                __ = wsheet.cell(column=7, row=(row_id + 5), value='INVALID')
            elif nsum == 'true':
                __ = wsheet.cell(column=7, row=(row_id + 5), value='VALID')
            elif nsum == 'Killed':
                __ = wsheet.cell(column=7, row=(row_id + 5), value=nsum)

            logging.info('Saving Tags data in Excel')
            __ = wsheet.cell(column=10, row=(row_id + 4), value=out_fn_nt[0])
            __ = wsheet.cell(column=11, row=(row_id + 4), value=out_rt_nt[0])
            __ = wsheet.cell(column=10, row=(row_id + 5), value=out_fn_nt[1])
            __ = wsheet.cell(column=11, row=(row_id + 5), value=out_rt_nt[1])
            wbook.save(xl_fn)

        # Prepare for next input
        row_id = row_id + 2


def prism_gen(ssp_arr, mu_user_input):
    """
    Loop through array of SSP problems and generate prism file
        Input:
            filename: Prism output file name
        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """

    ssp_prism_nt = []
    for ssp in ssp_arr:
        # Create SSP Prism File
        max_tag_id = []
        ssp_prism_name = file_name_gen(ssp, len(ssp), 'prism')
        # Without tags
        logging.info('Generating Prism file without tags...')
        ssp_prism_name_nt = 'NT_mu_0_' + ssp_prism_name
        print_prism_ssp_nt(ssp_prism_name_nt, ssp, sum(ssp), len(ssp), mu=0, bug_cell=None)
        logging.info('Generated Prism file with mu = 0')
        ssp_prism_nt.append(ssp_prism_name_nt)
        ssp_prism_name_nt = f'NT_mu_{mu_user_input}_' + ssp_prism_name
        print_prism_ssp_nt(ssp_prism_name_nt, ssp, sum(ssp), len(ssp), mu=mu_user_input, bug_cell=None)
        logging.info('Generated Prism file without tags')
        ssp_prism_nt.append(ssp_prism_name_nt)

    # create spec file
    print_prism_ssp_nt_spec('spec_ssp.pctl')

    return ssp_prism_nt


def print_prism_ssp_nt(filename, primes, maxrow, num_of_primes, mu=0, bug_cell=None):
    """
    Print out the SSP network description to the prism file
        Input:
            num_of_primes: the number of elements in the set S.
            bug_cell: option to add a bug. bug cell is a list, [r, c, dir]. By default there are no bugs.
            mu: a probability of an error. By default there is no error, so mu = 0.
    """

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
    f.write(f'const maxrow = {maxrow};\n')
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
    f.write('formula row_is_maxrow = row = maxrow;\n')
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

    # transition relation
    str_temp = "[] (start | row_is_maxrow) & !force_dir -> 0.5 : (junction' = split) & (dir' = diag) & (column' = 0) & (row' = 0) + 0.5 : (junction' = split) & (dir' = dwn) & (column' = 0) & (row' = 0);"
    f.write('\n\t' + str_temp + '\n')
    str_temp = "	[] next_is_split -> 0.5 : (junction' = split) & (dir' = diag) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1)) + 0.5 : (junction' = split) & (dir' = dwn) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1));"
    f.write(str_temp + '\n')
    str_temp = "	[] next_is_not_split -> (1 - mu): (junction' = pass) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1)) & (dir'=dir) + mu:(junction' = pass) & (column' = mod(column + dir, maxrow_1)) & (row' = mod(row + 1, maxrow_1)) & (dir' = mod(dir+1,2));"
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


def print_prism_ssp_nt_spec(filename):
    """
    Print out the SSP network description to the prism file
        Input:
            num_of_primes: the number of elements in the set S.
            bug_cell: option to add a bug. bug cell is a list, [r, c, dir]. By default there are no bugs.
            mu: a probability of an error. By default there is no error, so mu = 1.
    """

    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------

    # Open file and write header into file
    f = open(filename, 'w')
    f.write('const int k;\n\n')
    f.write('P>0 [ F = maxrow+1 row=maxrow & column = k ]\n')
    f.write('P=? [ F = maxrow+1 row=maxrow & column = k ]\n')
    f.close()


def run_prism(ssp_arr, prism_nt_arr, wbook, wsheet, xl_fn, str_modcheker, spec_number):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
    Using new specification type
        Input:
            ssp_arr: array of SSP problems
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modcheker: PRISM
            spec_number: type of spec - reachability or	probability

    """
    row_id = 0
    out_fn_nt = []

    # duplicate for calculating each spec twice - with and without errors (mu = 0 and  mu > 0)
    ssp_arr_temp = []
    for i in ssp_arr:
        ssp_arr_temp.extend([i, i])
    ssp_arr = ssp_arr_temp

    for index, ssp in enumerate(ssp_arr):
        # Run Prism on no tags

        if index % 2 == 0 or (index % 2 == 1 and prism_nt_arr[index][6:10] != '0.0_'): # if mu = 0 -> skip
            out_fn_nt, out_rt_nt = modcheck.call_pexpect_ssp_prism(prism_nt_arr[index], str_modcheker, sum(ssp), spec_number)
        else:
            row_id += 1
            continue

        # Parse the results from txt file
        df = pd.read_csv(out_fn_nt, sep=" ")

        # Valid-invalid output
        reachable_col = []
        prob_col = []
        unreachable_col = []
        if spec_number == 1:
            reachable_col = df.index[df['Result'] == True].tolist()
            unreachable_col = df.index[df['Result'] == False].tolist()
        # probabilities
        elif spec_number == 2:
            reachable_col = df.index[df['Result'] > 0].tolist()
            unreachable_col = df.index[df['Result'] == 0].tolist()
            prob_col = df['Result'].tolist()
            # prob_col = [x for x in prob_col if x > 0]

        # Parse the results into excel file
        if index % 2 == 0:
            logging.info('Inputting ID, k, set, filenames, and spec data into Excel...')
            __ = wsheet.cell(column=1, row=(row_id + 4), value=int(index / 2))
            __ = wsheet.cell(column=2, row=(row_id + 4), value=len(ssp))
            __ = wsheet.cell(column=3, row=(row_id + 4), value=repr(ssp))
            __ = wsheet.cell(column=4, row=(row_id + 4), value=prism_nt_arr[index])
            __ = wsheet.cell(column=7, row=(row_id + 4), value=str(reachable_col))
            __ = wsheet.cell(column=8, row=(row_id + 4), value=str(unreachable_col))
            if spec_number == 2:
                __ = wsheet.cell(column=9, row=(row_id + 4), value=str(prob_col))
        else:
            __ = wsheet.cell(column=10, row=(row_id + 4), value=str(reachable_col))
            __ = wsheet.cell(column=11, row=(row_id + 4), value=str(unreachable_col))
            if spec_number == 2:
                __ = wsheet.cell(column=12, row=(row_id + 4), value=str(prob_col))
        wbook.save(xl_fn)

        # Prepare for next input
        if index % 2 == 1:
            row_id += 1
