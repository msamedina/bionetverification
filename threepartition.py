"""
3-Partition Functions
Michelle Aluf Medina
"""
import logging
import miscfunctions as misc
# import nusmv
import modcheck
import pandas as pd
import re

# Pre calcultions of the set s:
def pre_calc_3partition(s_arr):
    """
    Function for precalculating the sum of the subsets in a 3-partition problem.

    Input:
        s_arr (list): A list of integers representing the input array.

    Ouyput:
        float or bool: The target sum for each subset if the array can be partitioned
                   into three equal subsets, otherwise False.
    """
    if len(s_arr) % 3 != 0:
        return False
    else:
        count_sub = len(s_arr)/3
    sum_s = sum(s_arr)
    sum_sub = sum_s / count_sub

    return sum_sub

def file_name_gen_3part(set_array, arr_length, str_mc='NuSMV'):
    """
    Generate smv file name for given 3partition problem using the set
        Input:
            set_array: The input set
            arr_length: Number of elements in the set
        Output:
            filename: smv file name for the 3partition network with formatting
    """
    if str_mc == 'NuSMV' or str_mc == 'nuXmv':
        filename = 'auto3partition_'
        for i in range(arr_length):
            filename += str(set_array[i]) + '_'
        filename += 'Set_{0}.smv'
        return misc.file_name_cformat(filename)

    elif str_mc == 'prism':
        filename = 'auto3partition_'
        for i in range(arr_length):
            filename += str(set_array[i]) + '_'
        filename += 'Set.pm'
        return misc.file_name_cformat(filename)

#CHANGED
def print_smv_3partition(filename, set_array, max_sum, set_size, max_tag_id, sum_sub):
    """
    Print out the 3Partition network description to the smv file
        Input:
            filename: The NuSMV filename in which to write the description
            set_array: the set being looked at for the 3partition problem
            max_sum: the total sum of all elements in the set
            set_size: the size of the set
            max_tag_id: empty array containing the last tag element
            sum_sub: the sum of the subsets
    """
    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------
    # Write header into file
    subset = []
    f = open(filename, 'w')
    f.write('--Auto Subset Sum ' + str(set_array)
            + '\n-------------------------------\n')

    # ----------------
    # Find row locations of split junctions
    split_j_loc = [0]
    for i in range(0, len(set_array) - 1):
        split_j_loc.append(set_array[i] + split_j_loc[i])
    # Calculate number of split junctions
    num_split_j = len(split_j_loc)
    max_tag_id.append(num_split_j - 1)
    # ----------------
    # Write beginning of module and variable definitions
    f.write('MODULE main\n' + 'VAR\n')
    f.write('\trow: 0..' + str(max_sum) + ';\n')
    f.write('\tcolumn: 0..' + str(max_sum) + ';\n')
    f.write('\tjunction: {pass, split};\n')
    f.write('\tdir: {dwn, diag};\n')
    f.write('\tflag: boolean;\n')
    f.write('\ttag: array 0.. ' + str(len(split_j_loc)-1) + ' of boolean;\n') # ------- CHANGED- add tags of split junctions


    # Define tcounter variable
    f.write('\nDEFINE\n')
    f.write('\ttcounter := ')
    for i in range(0, num_split_j):
        if (i == num_split_j-1):
            f.write('\t\t(tag[' + str(i) + '] ? 1 : 0);\n\n')
        elif (i == 0):
            f.write(' (tag[' + str(i) + '] ? 1 : 0) +\n')
        else:
            f.write('\t\t(tag[' + str(i) + '] ? 1 : 0) +\n')


    # Write assignment definitions
    f.write('ASSIGN\n')
    f.write('\tinit(row) := 0;\n')
    f.write('\tinit(column) := 0;\n')
    f.write('\tinit(junction) := split;\n')
    f.write('\tinit(dir) := dwn;\n')
    f.write('\tinit(flag) := FALSE;\n')


    for i in range(0, num_split_j):
        if (((i + 1) % 5) == 0) or (i == num_split_j - 1):
            f.write('\tinit(tag[' + str(i) + ']) := FALSE;\n') # ---------- CHANGED- the location of the tags
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
        for j in range(0, len(split_j_loc)): # ------- CHANGED- rows only- without columns
            f.write('\tnext(tag[' + str(j)
                    + ']) :=\n\t\t\t\t\tcase\n\t\t\t\t\t\t')
            f.write('(row = ' + str(split_j_loc[j]) + ') & next(dir) = diag: TRUE;\n\t\t\t\t\t\t')
            f.write('(next(row) = 0): FALSE;\n\t\t\t\t\t\t')
            f.write('TRUE: tag[' + str(j) + '];\n\t\t\t\t\tesac;\n\n')
            i += 1

    # ----------------
    # Write specifications for each network output
    #for i in range(0, max_sum + 1):
        f.write('LTLSPEC\tNAME\tltl_' + str(0)
                + ' := G! ((flag = TRUE) & (tcounter = 3) & (column = ' + str(int(sum_sub)) + '));\n')

    print(split_j_loc)

    # ----------------
    # CLOSE THE FILE
    f.close()

def tags_count(output_filename):
    """
    Parse the ltl output to find the count of tags that has changed for TRUE
    Save their numbers in a set of changed_tags
        Input:
            output_filename: output file to be looked at
        Output:
            path_tag: the count of unique tags that changed to TRUE ant their values.
    """
    # Initialize a set to track tags that have changed to TRUE
    changed_tags = set()

    # Regular expression to find tag changes
    tag_pattern = re.compile(r"tag\[(\d+)] = TRUE")

    # Read the file
    with open(output_filename, 'r') as file:
        for line in file:
            # Search for tag changes
            match = tag_pattern.search(line)
            if match:
                tag_number = int(match.group(1))
                changed_tags.add(tag_number)

    # Return the count of unique tags that changed to TRUE
    return changed_tags, len(changed_tags)




def smv_gen(arr_3partition, str_modc, with_tags='with'):
    """
    Loop through array of 3partition problems and generate two smv files for each (with and without tags)
        Input:
            filename: NuSMV output file name
            with_tags: Flag for using networks with tags
        Output:
            smv_3partition: List of all 3partition problems
            set_id: Max set ID (starts from 0)
    """
    smv_3partition = []

    for p3part in arr_3partition:
        # Create 3partition NuSMV File
        max_tag_id = []
        # With tags
        smv_name_3part = file_name_gen_3part(p3part, len(p3part), str_modc)
        if with_tags in ['with', 'both']:
            logging.info('Generating NuSMV file with tags...')
            print_smv_3partition(smv_name_3part, p3part, sum(p3part), len(p3part), max_tag_id)
            logging.info('Generated NuSMV file with tags')
            smv_3partition.append(smv_name_3part)

    return smv_3partition

#To check if this functions are rellevant?

def run_nusmv_newspec(ssp_arr, smv_t_arr, wbook, wsheet, xl_fn, str_modchecker, with_tags='both', verbosity=0):
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
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
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

            #out_fn, out_rt = modcheck.call_nusmv_pexpect_ssp_newspec(smv_t_arr[index], str_modchecker, verbosity)

            sum_sub = threepartition.pre_calc_3partition(ssp_arr[0])

            out_fn, out_rt, is_solve = modcheck.call_nusmv_pexpect_3partition(smv_t_arr[index], str_modchecker, len(ssp_arr[0]), sum_sub, ssp_arr[0])

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

        # Prepare for next input
        row_id = row_id + 2


def run_nusmv_all(ssp_arr, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn, str_modchecker, with_tags='both', ic3=False,
                  verbosity=0):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
        Input:
            ssp_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
            with_tags: Flag for using networks with tags
            ic3: Use IC3 engine for ltlspec rather than default

        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """
    for index, ssp in enumerate(ssp_arr):
        max_sum = sum(ssp)
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

            if ic3 and str_modchecker == "nuXmv":
                out_fn, out_rt = modcheck.pexpect_nuxmv_ic3_allout(smv_t_arr[index], str_modchecker, max_sum, verbosity)
            else:
                out_fn, out_rt = modcheck.call_nusmv_pexpect_allout(smv_t_arr[index], index, wsheet, wbook, xl_fn,
                                                                    str_modchecker, verbosity)

            __ = wsheet.cell(column=6, row=(index + 4), value=out_fn[0])
            __ = wsheet.cell(column=7, row=(index + 4), value=out_rt[0])
            __ = wsheet.cell(column=8, row=(index + 4), value=out_fn[1])
            __ = wsheet.cell(column=9, row=(index + 4), value=out_rt[1])
            wbook.save(xl_fn)

        # Run NuSMV on no tags
        if with_tags in ['without', 'both']:
            __ = wsheet.cell(column=5, row=(index + 4), value=smv_nt_arr[index])
            wbook.save(xl_fn)

            if ic3 and str_modchecker == "nuXmv":
                out_fn, out_rt = modcheck.pexpect_nuxmv_ic3_allout(smv_nt_arr[index], str_modchecker, max_sum,
                                                                   verbosity)
            else:
                out_fn, out_rt = modcheck.call_nusmv_pexpect_allout(smv_nt_arr[index], index, wsheet, wbook, xl_fn,
                                                                    str_modchecker, verbosity)

            __ = wsheet.cell(column=10, row=(index + 4), value=out_fn[0])
            __ = wsheet.cell(column=11, row=(index + 4), value=out_rt[0])
            __ = wsheet.cell(column=12, row=(index + 4), value=out_fn[1])
            __ = wsheet.cell(column=13, row=(index + 4), value=out_rt[1])
            wbook.save(xl_fn)


def run_nusmv_single(ssp_arr, smv_t_arr, smv_nt_arr, wbook, wsheet, xl_fn, str_modchecker, with_tags='both', ic3=False,
                     verbosity=0):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
        Input:
            ssp_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
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

                if ic3 and str_modchecker == "nuXmv":
                    out_fn, out_rt = modcheck.pexpect_nuxmv_ic3_singleout(smv_t_arr[index], 1, output, str_modchecker,
                                                                          max_sum, verbosity)
                else:
                    out_fn, out_rt = modcheck.call_nusmv_pexpect_singleout(smv_t_arr[index], 1, output, str_modchecker,
                                                                           verbosity)

                # Parse output files:
                ltl_res = modcheck.get_spec_res(out_fn[0], ic3)
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

                if ic3 and str_modchecker == "nuXmv":
                    out_fn, out_rt = modcheck.pexpect_nuxmv_ic3_singleout(smv_nt_arr[index], 1, output, str_modchecker,
                                                                          max_sum, verbosity)
                else:
                    out_fn, out_rt = modcheck.call_nusmv_pexpect_singleout(smv_nt_arr[index], 1, output, str_modchecker,
                                                                           verbosity)

                # Parse output files:
                ltl_res = modcheck.get_spec_res(out_fn[0], ic3)
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

            if ltl_res == 'false' and ctl_res == 'true' and not ic3:
                __ = wsheet.cell(column=7, row=(row_id + 4), value='YES')
            elif ltl_res == 'true' and ctl_res == 'false' and not ic3:
                __ = wsheet.cell(column=7, row=(row_id + 4), value='NO')
            elif ic3 and ltl_res == 'unknown':
                val = 'UNKNOWN-YES' if ctl_res == 'true' else 'UNKNOWN-NO'
                __ = wsheet.cell(column=7, row=(row_id + 4), value=val)
            else:
                __ = wsheet.cell(column=7, row=(row_id + 4), value='INVALID RESULT')
            wbook.save(xl_fn)

            # Prepare for next input
            row_id = row_id + 1


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
        ssp_prism_name = file_name_gen_3part(ssp, len(ssp), 'prism')
        # Without tags
        logging.info('Generating Prism file without tags...')
        ssp_prism_name_nt = 'NT_mu_0_' + ssp_prism_name
        print_prism_ssp_nt(ssp_prism_name_nt, ssp, sum(ssp), len(ssp), mu=0, bug_cell=None)
        logging.info('Generated Prism file with mu = 0')
        ssp_prism_nt.append(ssp_prism_name_nt)

        ssp_prism_name_nt = misc.file_name_cformat(f'NT_mu_{mu_user_input}_' + '_{0}' + ssp_prism_name)
        print_prism_ssp_nt(ssp_prism_name_nt, ssp, sum(ssp), len(ssp), mu=mu_user_input, bug_cell=None)
        logging.info('Generated Prism file without tags')
        ssp_prism_nt.append(ssp_prism_name_nt)

    # create spec file
    print_prism_ssp_nt_spec('spec_ssp.pctl')

    return ssp_prism_nt


def run_prism(ssp_arr, prism_nt_arr, wbook, wsheet, xl_fn, str_modchecker, spec_number):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
    Using new specification type
        Input:
            ssp_arr: array of SSP problems
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modchecker: PRISM
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

        if index % 2 == 0 or (index % 2 == 1 and prism_nt_arr[index][6:10] != '0.0_'):  # if mu = 0 -> skip
            out_fn_nt, out_rt_nt = modcheck.call_pexpect_ssp_prism(prism_nt_arr[index], str_modchecker, sum(ssp),
                                                                   spec_number)
        else:
            row_id += 1
            continue

        # Parse the results from txt file
        df = pd.read_csv(out_fn_nt)

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
            __ = wsheet.cell(column=10, row=(row_id + 4), value=out_rt_nt)
            if spec_number == 2:
                __ = wsheet.cell(column=9, row=(row_id + 4), value=str(prob_col))
        else:
            __ = wsheet.cell(column=11, row=(row_id + 4), value=str(reachable_col))
            __ = wsheet.cell(column=12, row=(row_id + 4), value=str(unreachable_col))
            __ = wsheet.cell(column=14, row=(row_id + 4), value=out_rt_nt)
            if spec_number == 2:
                __ = wsheet.cell(column=13, row=(row_id + 4), value=str(prob_col))
        wbook.save(xl_fn)

        # Prepare for next input
        if index % 2 == 1:
            row_id += 1


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
