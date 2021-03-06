"""
ExCov Functions
Modified by: Michelle Aluf Medina
"""
import miscfunctions as misc
import logging
import nusmv


def receive_subsets(num_subsets):
    """
    Receive user input of set of subsets
        Input:
            num_subsets: number of subsets to be input
        Output:
            subsets_arr: array of the subsets
    """
    j = 0
    subsets_arr = list()
    for i in range(1, (num_subsets + 1)):
        subset = set()
        prompt_size = 'Enter the number of elements in subset ' + str(i) + ': '
        num_elements = misc.int_input(out_str=prompt_size)
        print('Enter the numbers in subset ' + str(i) + ': ')
        while j < num_elements:
            temp = misc.int_input()
            subset.add(temp)
            j += 1
        print('Your subset is ' + str(subset) + '\n')
        subsets_arr.append(subset)
        j = 0

    print('Your subsets are: ' + str(subsets_arr) + '\n')
    return subsets_arr


def read_ec(filename):
    """
    Parse the ExCov input file for list of ExCov problems
    Find file format in README
        Input:
            filename: ExCov input file
        Output:
            uni_list: List of universes of all problems
            subsets_list: List of sets of subsets for each problem
            num_prob: Number of problems in the input file
    """
    logging.info('Opening ExCov input file')
    in_data = open(filename, "r")
    # Data for return
    uni_list = list()
    subsets_list = list()
    num_prob = 0
    
    # Temp collection variables
    num_subsets = 0
    subset_count = 0
    sset = list()
    sset_list = list()
    uni = list()
    
    # Run through the lines of data in the file
    for line in in_data:
        tokens = line.split()
        if len(tokens) != 0 and tokens[0].lower() == 'p':
            # Validation of file input
            if tokens[1].lower() == "excov":
                num_subsets = int(tokens[2])
                num_prob += 1
            else:
                print("Problem " + str(num_prob) + " not in excov format. Edit and resubmit.")
                logging.warning('Problem ' + str(num_prob) + ' not in excov format. Edit file and resubmit.')
                return -1
            # If lists are NOT empty
            if uni and sset_list:
                if subset_count != num_subsets:
                    logging.warning('Number of subsets does not match that indicated for problem ' + str(num_prob))
                subset_count = 0
                uni_list.append(uni[:])
                subsets_list.append(sset_list[:])
                uni.clear()
                sset_list.clear()
        elif len(tokens) != 0 and tokens[0].lower() == 'u':
            for tok in tokens[1:]:
                element = int(tok)
                if element == 0:
                    logging.info('Universe: ' + str(uni))
                else:
                    uni.append(element)
        elif len(tokens) != 0 and tokens[0].lower() == 's':
            for tok in tokens[1:]:
                element = int(tok)
                if element == 0:
                    subset_count += 1
                    logging.info('Subset ' + str(subset_count) + ' of ' + str(num_subsets) + ': ' + str(sset))
                    sset_list.append(sset[:])
                    sset.clear()
                else:
                    sset.append(element)
    # Reached the end, input last problem's data
    subset_count = 0
    uni_list.append(uni[:])
    subsets_list.append(sset_list[:])
    uni.clear()
    sset_list.clear()
    
    logging.info('Total number of ExCov problems: ' + str(num_prob))
    return uni_list, subsets_list, num_prob


def smv_gen(universes, subsets, num_probs):
    """
    Loop through array of ExCov problems and generate two smv files for each (with and without tags)
        Input:
            universes: the list of universes
            subsets: The list of sets of subsets
            num_probs: The number of problems (nuumber of universes and subset sets)
        Output:
            ec_smv: list of smv file names with tags
            ec_smv_nt: list of smv file names without tags
            ec_outputs: list of outputs of interest (ExCov output) for each problem
            max_sums: list of maximum sum of each problem
    """
    ec_smv = list()
    ec_smv_nt = list()
    ec_outputs = list()
    max_sums = list()
    for uni, sets in zip(universes, subsets):
        logging.info('Universe is: ' + str(uni) + '\n')
        
        # Generate binary universe representation
        logging.info('Converting universe to binary format.')
        uni_bin = list()
        for i in range(0,len(uni)):
            uni_bin.append('1')
        uni_bin_s = ''.join(str(e) for e in uni_bin)
        logging.info('Universe in binary is: ' + uni_bin_s + '\n')
        
        # Convert binary universe to integer representation
        uni_bin_int = int(uni_bin_s, base=2)
        ec_outputs.append(uni_bin_int)
        logging.info('Integer convesion of binary universe is: ' + str(uni_bin_int))
        
        # Convert subsets to binary representation
        sets_bin = list()
        for i in range(0, len(sets)):
            sets_bin.append(bin_rep(sets[i], uni))
            logging.info('Set ' + str(i+1) + ' in binary is: ' + str(sets_bin[-1]))

        # Convert binary to integer representation
        sets_bin_int = list()
        for i in range(0, len(sets_bin)):
            sets_bin_int.append(int(sets_bin[i], base=2))
        logging.info('These sets will be treated as the following integers: ' + str(sets_bin_int) + '\n')
        max_sums.append(sum(sets_bin_int))

        # Create EC NuSMV File
        # With tags
        logging.info('Generating NuSMV file with tags...')
        ec_smv_name = file_name_smv(uni, len(uni))
        max_tag_id = list()
        print_smv_ec(ec_smv_name, uni, sets, sets_bin, sets_bin_int, uni_bin_int, uni_bin_s, max_tag_id)
        logging.info('Generated NuSMV file with tags')
        ec_smv.append(ec_smv_name)
        
        # Without tags
        logging.info('Generating NuSMV file without tags...')
        ec_smv_name_nt = 'NT_' + ec_smv_name
        print_smv_ec_nt(ec_smv_name_nt, uni, sets, sets_bin, sets_bin_int, uni_bin_int, uni_bin_s)
        logging.info('Generated NuSMV file without tags')
        ec_smv_nt.append(ec_smv_name_nt)
        
    return ec_smv, ec_smv_nt, ec_outputs, max_sums


def print_ec_menu():
    """
    Print menu for ExCov options to screen.
    """
    print('What would you like to do on this universe and set of subsets:\n')
    print('\t[1] Check if an exact cover exists')
    print('\t[2] Find total number of different exact covers')
    print('\t[3] Return to Main Menu')


def file_name_smv(universe_array, arr_length):
    """
    Generate smv file name for given ExCov problem using universe.
        Inputs:
            universe_array: the given universe
            arr_length: number of elements in universe
        Output:
            filename: smv file name for ExCov network with formatting
    """
    filename = 'autoExCov_'
    for i in range(arr_length):
        filename += str(universe_array[i]) + '_'
    filename += 'Universe_{0}.smv'
    return misc.file_name_cformat(filename)


def print_smv_ec(filename, universe_array, ss_array, bin_ss, int_ss, int_uni,
                 bin_uni, max_tag_id):
    """
    Print out the ExCov network description to the smv file
        Input:
            filename: the smv filename to be used
            universe_array: universe set defining the ExCov
            ss_array: array of subsets that may take part in the ExCov
            bin_ss: array of binary subsets
            int_ss: array of integer subsets
            int_uni: integer universe array
            bin_uni: binary universe array
            max_tag_id: empty array containing the last tag element
    """

    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------
    # Open file and write header into file
    f = open(filename, 'w')
    f.write('--Exact Cover\n' + '--Universe:\t' + str(universe_array)
            + '\tBit Form:\t' + bin_uni)
    f.write('\n--Set of Subsets:\t' + str(ss_array) + '\tBit Form:\t'
            + str(bin_ss) + '\n')
    f.write('--This will be treated as k = ' + str(int_uni) + ' and ss = '
            + str(int_ss) + '\n-------------------------------\n')

    # ----------------
    # Find row locations of split junctions
    split_j_loc = [0]
    for i in range(0, len(ss_array) - 1):
        split_j_loc.append(int_ss[i] + split_j_loc[i])
    # Calculate number of split junctions
    num_split_j = sum(split_j_loc) + len(split_j_loc)
    max_tag_id.append(num_split_j - 1)
    sum_total = sum(int_ss)
    # ----------------

    # Write beginning of module and variable definitions
    f.write('MODULE main\n' + 'DEFINE\n' + '\tk := ' + str(int_uni)
            + ';\n\nVAR\n')
    f.write('\trow: 0..' + str(sum_total) + ';\n')
    f.write('\tcolumn: 0..' + str(sum_total) + ';\n')
    f.write('\tjunction: {pass, split, forceDwn};\n')
    f.write('\tdir: {dwn, diag};\n')
    f.write('\tflag: boolean;\n\n')
    f.write('\ttag: array 0..' + str(num_split_j - 1) + ' of boolean;\n')

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
    f.write('\tnext(row) := (row + 1) mod ' + str(sum_total + 1) + ';\n')

    # Write flag transitions to file
    f.write('\n\t--Flag turns on when row is ' + str(sum_total) + '\n')
    f.write('\tnext(flag) := (next(row) = ' + str(sum_total)
            + ' ? TRUE : FALSE);\n')

    # Write junction transitions to file
    # Find all split junctions
    f.write('\n\t--Split junctions at rows ')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write(str(split_j_loc[i]) + ', ')
        else:
            f.write(str(split_j_loc[i]))
    f.write(' and forceDwn junctions at (r,c): ')
    rc_f_dwn = []

    # Find all frcDwn junctions
    for i in range(0, len(ss_array)):
        for j in range(i + 1, len(ss_array)):
            if not(set(ss_array[i]).isdisjoint(set(ss_array[j]))):
                c = int_ss[i]
                r = sum(int_ss[0:j])
                rc_f_dwn.append([r, c])
                f.write('(' + str(r) + ',' + str(c) + ') ')
                for k in range(i + 1, j):
                    c = int_ss[i] + int_ss[k]
                    rc_f_dwn.append([r, c])
                    f.write('(' + str(r) + ',' + str(c) + ') ')
                    ctemp = sum(int_ss[i:k + 1])
                    if ctemp > c:
                        rc_f_dwn.append([r, ctemp])
                        f.write('(' + str(r) + ',' + str(ctemp) + ') ')

    f.write('\n\n\tnext(junction) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t(')
    for i in range(0, len(rc_f_dwn)):
        if i < len(rc_f_dwn) - 1:
            f.write('((next(row) = ' + str(rc_f_dwn[i][0])
                    + ')&(next(column) = ' + str(rc_f_dwn[i][1]) + '))|')
        else:
            f.write('((next(row) = ' + str(rc_f_dwn[i][0])
                    + ')&(next(column) = ' + str(rc_f_dwn[i][1])
                    + '))): forceDwn;\n\t\t\t\t\t\t(')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')|')
        else:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')): split;\n')
            f.write('\t\t\t\t\t\tTRUE: pass;\n\t\t\t\t\tesac;\n\n')

    # Write direction transitions to file
    f.write('\t--Decide next direction for move by to current junction\n')
    f.write('\tnext(dir) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(junction = split): {dwn, diag};\n\t\t\t\t\t\t')
    f.write('(junction = pass): dir;\n\t\t\t\t\t\t')
    f.write('(junction = forceDwn): dwn;\n\t\t\t\t\t\t')
    f.write('TRUE: {dwn, diag};\n\t\t\t\t\tesac;\n\n')

    # Write column transitions to file
    f.write('\t--If diag, increase column, otherwise dwn, same column\n')
    f.write('\tnext(column) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(next(row) = 0): 0;\n\t\t\t\t\t\t')
    f.write('(next(dir) = diag): (column + 1) mod ' + str(sum_total)
            + ';\n\t\t\t\t\t\t')
    f.write('(next(dir) = dwn): column;\n\t\t\t\t\t\t')
    f.write('TRUE: column;\n\t\t\t\t\tesac;\n\n')

    # Write tag transitions to file
    f.write('\t--Set tag TRUE if curr row = split, dir is diag\n')
    i = 0
    while i < num_split_j:
        for j in range(0, len(split_j_loc)):
            for k in range(0, split_j_loc[j] + 1):
                f.write('\tnext(tag[' + str(i)
                        + ']) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t')
                f.write('(row = ' + str(split_j_loc[j])
                        + ') & (column = ' + str(k)
                        + ') & next(dir) = diag: TRUE;\n\t\t\t\t\t\t')
                f.write('(next(row) = 0): FALSE;\n\t\t\t\t\t\t')
                f.write('TRUE: tag[' + str(i) + '];\n\t\t\t\t\tesac;\n\n')
                i += 1

    # ----------------
    # Write specifications
    f.write('LTLSPEC\tNAME\tltl_k := G! ((flag = TRUE) & (column = k));\n')
    f.write('CTLSPEC\tNAME\tctl_k := EF ((flag = TRUE) & (column = k));\n')
    # ----------------

    # Close file
    f.close()


def print_smv_ec_nt(filename, universe_array, ss_array, bin_ss, int_ss, int_uni,
                 bin_uni):
    """
    Print out the ExCov network description to the smv file
        Input:
            filename: the smv filename to be used
            universe_array: universe set defining the ExCov
            ss_array: array of subsets that may take part in the ExCov
            bin_ss: array of binary subsets
            int_ss: array of integer subsets
            int_uni: integer universe array
            bin_uni: binary universe array
    """

    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------
    # Open file and write header into file
    f = open(filename, 'w')
    f.write('--Exact Cover\n' + '--Universe:\t' + str(universe_array)
            + '\tBit Form:\t' + bin_uni)
    f.write('\n--Set of Subsets:\t' + str(ss_array) + '\tBit Form:\t'
            + str(bin_ss) + '\n')
    f.write('--This will be treated as k = ' + str(int_uni) + ' and ss = '
            + str(int_ss) + '\n-------------------------------\n')

    # ----------------
    # Find row locations of split junctions
    split_j_loc = [0]
    for i in range(0, len(ss_array) - 1):
        split_j_loc.append(int_ss[i] + split_j_loc[i])
    sum_total = sum(int_ss)
    # ----------------

    # Write beginning of module and variable definitions
    f.write('MODULE main\n' + 'DEFINE\n' + '\tk := ' + str(int_uni)
            + ';\n\nVAR\n')
    f.write('\trow: 0..' + str(sum_total) + ';\n')
    f.write('\tcolumn: 0..' + str(sum_total) + ';\n')
    f.write('\tjunction: {pass, split, forceDwn};\n')
    f.write('\tdir: {dwn, diag};\n')
    f.write('\tflag: boolean;\n\n')

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
    f.write('\tnext(row) := (row + 1) mod ' + str(sum_total + 1) + ';\n')

    # Write flag transitions to file
    f.write('\n\t--Flag turns on when row is ' + str(sum_total) + '\n')
    f.write('\tnext(flag) := (next(row) = ' + str(sum_total)
            + ' ? TRUE : FALSE);\n')

    # Write junction transitions to file
    # Find all split junctions
    f.write('\n\t--Split junctions at rows ')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write(str(split_j_loc[i]) + ', ')
        else:
            f.write(str(split_j_loc[i]))
    f.write(' and forceDwn junctions at (r,c): ')
    rc_f_dwn = []

    # Find all frcDwn junctions
    for i in range(0, len(ss_array)):
        for j in range(i + 1, len(ss_array)):
            if not(set(ss_array[i]).isdisjoint(set(ss_array[j]))):
                c = int_ss[i]
                r = sum(int_ss[0:j])
                rc_f_dwn.append([r, c])
                f.write('(' + str(r) + ',' + str(c) + ') ')
                for k in range(i + 1, j):
                    c = int_ss[i] + int_ss[k]
                    rc_f_dwn.append([r, c])
                    f.write('(' + str(r) + ',' + str(c) + ') ')
                    ctemp = sum(int_ss[i:k + 1])
                    if ctemp > c:
                        rc_f_dwn.append([r, ctemp])
                        f.write('(' + str(r) + ',' + str(ctemp) + ') ')

    f.write('\n\n\tnext(junction) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t(')
    for i in range(0, len(rc_f_dwn)):
        if i < len(rc_f_dwn) - 1:
            f.write('((next(row) = ' + str(rc_f_dwn[i][0])
                    + ')&(next(column) = ' + str(rc_f_dwn[i][1]) + '))|')
        else:
            f.write('((next(row) = ' + str(rc_f_dwn[i][0])
                    + ')&(next(column) = ' + str(rc_f_dwn[i][1])
                    + '))): forceDwn;\n\t\t\t\t\t\t(')
    for i in range(0, len(split_j_loc)):
        if i < len(split_j_loc) - 1:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')|')
        else:
            f.write('(next(row) = ' + str(split_j_loc[i]) + ')): split;\n')
            f.write('\t\t\t\t\t\tTRUE: pass;\n\t\t\t\t\tesac;\n\n')

    # Write direction transitions to file
    f.write('\t--Decide next direction for move by to current junction\n')
    f.write('\tnext(dir) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(junction = split): {dwn, diag};\n\t\t\t\t\t\t')
    f.write('(junction = pass): dir;\n\t\t\t\t\t\t')
    f.write('(junction = forceDwn): dwn;\n\t\t\t\t\t\t')
    f.write('TRUE: {dwn, diag};\n\t\t\t\t\tesac;\n\n')

    # Write column transitions to file
    f.write('\t--If diag, increase column, otherwise dwn, same column\n')
    f.write('\tnext(column) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(next(row) = 0): 0;\n\t\t\t\t\t\t')
    f.write('(next(dir) = diag): (column + 1) mod ' + str(sum_total)
            + ';\n\t\t\t\t\t\t')
    f.write('(next(dir) = dwn): column;\n\t\t\t\t\t\t')
    f.write('TRUE: column;\n\t\t\t\t\tesac;\n\n')

    # ----------------
    # Write specifications
    f.write('LTLSPEC\tNAME\tltl_k := G! ((flag = TRUE) & (column = k));\n')
    f.write('CTLSPEC\tNAME\tctl_k := EF ((flag = TRUE) & (column = k));\n')
    # ----------------

    # Close file
    f.close()


def bin_rep(subset, universe):
    """
    Generate binary encoding of given ExCov problem
        Input:
            arr: subset being converted into binary representation
            universe: the universe array
        Output:
            bin_rep: binary representation of the given subset (string)
    """
    temp_bin = []
    for i in range(0, len(universe)):
        if universe[i] in subset:
            temp_bin.append('1')
        else:
            temp_bin.append('0')
    temp_bin.reverse()
    bin_rep = ''.join(str(e) for e in temp_bin)
    return bin_rep


def run_nusmv(universe, subsets, out_interest, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn):
    """
    Loop through array of ExCov smv files and run NuSMV. Save results in Excel
        Input:
            universes: array of ExCov universes problems
            subsets: array of ExCov sets of subsets
            out_interest: array of relevant exact cover outputs
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
    """
    for index, (uni, sets) in enumerate(zip(universe, subsets)):
        # Save index, universe, num subsets, subsets, and filenames in excel
        logging.info('Inputting ID, uni, num subsets, and set data into Excel...')
        __ = wsheet.cell(column=1, row=(index + 4), value=index)
        __ = wsheet.cell(column=2, row=(index + 4), value=repr(uni))
        __ = wsheet.cell(column=3, row=(index + 4), value=len(sets))
        __ = wsheet.cell(column=4, row=(index + 4), value=repr(sets))
        __ = wsheet.cell(column=5, row=(index + 4), value=smv_t_arr[index])
        __ = wsheet.cell(column=6, row=(index + 4), value=smv_nt_arr[index])
        wbook.save(xl_fn)
        
        # Run NuSMV on with tags
        out_fn, out_rt = nusmv.call_nusmv_pexpect_singleout(smv_t_arr[index], 2, out_interest[index])

        # Parse output files:
        ltl_res = nusmv.get_spec_res(out_fn[0])
        logging.info('LTL Result: ' + ltl_res)
        ctl_res = nusmv.get_spec_res(out_fn[1])
        logging.info('CTL Result: ' + ctl_res)
        
        if ltl_res == 'false' and ctl_res == 'true':
            __ = wsheet.cell(column=7, row=(index + 4), value='YES')
        elif ltl_res == 'true' and ctl_res == 'false':
            __ = wsheet.cell(column=7, row=(index + 4), value='NO')
        else:
            __ = wsheet.cell(column=7, row=(index + 4), value='INVALID RESULT')
                
        logging.info('Saving Tags data in Excel')
        __ = wsheet.cell(column=8, row=(index + 4), value=out_fn[0])
        __ = wsheet.cell(column=9, row=(index + 4), value=ltl_res)
        __ = wsheet.cell(column=10, row=(index + 4), value=out_rt[0])
        __ = wsheet.cell(column=11, row=(index + 4), value=out_fn[1])
        __ = wsheet.cell(column=12, row=(index + 4), value=ctl_res)
        __ = wsheet.cell(column=13, row=(index + 4), value=out_rt[1])
        wbook.save(xl_fn)

        # Run NuSMV on no tags
        out_fn, out_rt = nusmv.call_nusmv_pexpect_singleout(smv_nt_arr[index], 2, out_interest[index])
        
        # Parse output files:
        ltl_res = nusmv.get_spec_res(out_fn[0])
        logging.info('LTL Result: ' + ltl_res)
        ctl_res = nusmv.get_spec_res(out_fn[1])
        logging.info('CTL Result: ' + ctl_res)
        
        logging.info('Saving Tags data in Excel')
        __ = wsheet.cell(column=14, row=(index + 4), value=out_fn[0])
        __ = wsheet.cell(column=15, row=(index + 4), value=ltl_res)
        __ = wsheet.cell(column=16, row=(index + 4), value=out_rt[0])
        __ = wsheet.cell(column=17, row=(index + 4), value=out_fn[1])
        __ = wsheet.cell(column=18, row=(index + 4), value=ctl_res)
        __ = wsheet.cell(column=19, row=(index + 4), value=out_rt[1])
        wbook.save(xl_fn)


def run_nusmv_bmc(universe, subsets, out_interest, max_sums, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn):
    """
    Loop through array of ExCov smv files and run NuSMV. Save results in Excel
        Input:
            universes: array of ExCov universes problems
            subsets: array of ExCov sets of subsets
            out_interest: array of relevant exact cover outputs
            max_sums: the maximum number of rows for each problem
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
    """
    for index, (uni, sets) in enumerate(zip(universe, subsets)):
        # Save index, universe, num subsets, subsets, and filenames in excel
        logging.info('Inputting ID, uni, num subsets, and set data into Excel...')
        __ = wsheet.cell(column=1, row=(index + 4), value=index)
        __ = wsheet.cell(column=2, row=(index + 4), value=repr(uni))
        __ = wsheet.cell(column=3, row=(index + 4), value=len(sets))
        __ = wsheet.cell(column=4, row=(index + 4), value=repr(sets))
        __ = wsheet.cell(column=5, row=(index + 4), value=max_sums[index])
        __ = wsheet.cell(column=6, row=(index + 4), value=smv_t_arr[index])
        __ = wsheet.cell(column=7, row=(index + 4), value=smv_nt_arr[index])
        wbook.save(xl_fn)
        
        # Run NuSMV on with tags
        out_res, out_rt = nusmv.call_nusmv_pexpect_bmc(smv_t_arr[index], 2, out_interest[index], max_sums[index])
                
        logging.info('Saving Tags data in Excel')
        __ = wsheet.cell(column=8, row=(index + 4), value=out_res)
        __ = wsheet.cell(column=9, row=(index + 4), value=out_rt)
        wbook.save(xl_fn)

        # Run NuSMV on no tags
        out_res, out_rt = nusmv.call_nusmv_pexpect_bmc(smv_nt_arr[index], 2, out_interest[index], max_sums[index])
        
        logging.info('Saving Tags data in Excel')
        __ = wsheet.cell(column=10, row=(index + 4), value=out_res)
        __ = wsheet.cell(column=11, row=(index + 4), value=out_rt)
        wbook.save(xl_fn)
        