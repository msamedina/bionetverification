"""
GN Functions
Michelle Aluf Medina
"""
import logging
import miscfunctions as misc
import modcheck
import pandas as pd


def run_nusmv_gn(gn_smv_fn, wbook, wsheet, xl_fn, str_modchecker, with_tags='without', verbosity=0, depth=[],
                 ic3=False):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
    Using new specification type
        Input:
            gn_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
            with_tags: Flag for using networks with tags
    """
    row_id = 0
    for index, gn in enumerate(gn_smv_fn):
        for output in range(depth[index] + 1):
            # Save index, k, set, filenames, and output of interest in excel file
            logging.info('Inputting ID, k, set, filenames, and output data into Excel...')
            __ = wsheet.cell(column=1, row=(row_id + 4), value=index)
            __ = wsheet.cell(column=2, row=(row_id + 4), value=depth[index])
            __ = wsheet.cell(column=4, row=(row_id + 4), value=output)
            wbook.save(xl_fn)

            ltl_res = ''
            ctl_res = ''

            if with_tags in ['without', 'both']:
                __ = wsheet.cell(column=3, row=(row_id + 4), value=gn_smv_fn[index])
                wbook.save(xl_fn)

                if ic3 and str_modchecker == "nuXmv":
                    out_fn, out_rt = modcheck.pexpect_nuxmv_ic3_singleout(gn[index], 0, output, str_modchecker,
                                                                          depth, verbosity)
                else:
                    out_fn, out_rt = modcheck.call_nusmv_pexpect_singleout(gn_smv_fn[index], 0, output, str_modchecker,
                                                                           verbosity)

                # Parse output files:
                ltl_res = modcheck.get_spec_res(out_fn[0], ic3)
                logging.info('LTL Result: ' + ltl_res)
                ctl_res = modcheck.get_spec_res(out_fn[1])
                logging.info('CTL Result: ' + ctl_res)
                logging.info('Saving Tags data in Excel')
                __ = wsheet.cell(column=6, row=(row_id + 4), value=out_fn[0])
                __ = wsheet.cell(column=7, row=(row_id + 4), value=ltl_res)
                __ = wsheet.cell(column=8, row=(row_id + 4), value=out_rt[0])
                __ = wsheet.cell(column=9, row=(row_id + 4), value=out_fn[1])
                __ = wsheet.cell(column=10, row=(row_id + 4), value=ctl_res)
                __ = wsheet.cell(column=11, row=(row_id + 4), value=out_rt[1])
                wbook.save(xl_fn)

            if ltl_res == 'false' and ctl_res == 'true' and not ic3:
                __ = wsheet.cell(column=5, row=(row_id + 4), value='YES')
            elif ltl_res == 'true' and ctl_res == 'false' and not ic3:
                __ = wsheet.cell(column=5, row=(row_id + 4), value='NO')
            elif ic3 and ltl_res == 'unknown':
                val = 'UNKNOWN-YES' if ctl_res == 'true' else 'UNKNOWN-NO'
                __ = wsheet.cell(column=5, row=(row_id + 4), value=val)
            else:
                __ = wsheet.cell(column=5, row=(row_id + 4), value='INVALID RESULT')
            wbook.save(xl_fn)

            # Prepare for next input
            row_id = row_id + 1

    wbook.close()


def run_prism_gn(gn_prism_fn, wbook, wsheet, xl_fn, str_modchecker, spec_number=1, depth=None, mu=.0):
    """
    Loop through array of SSP smv files and run NuSMV. Save results in Excel
    Using new specification type
        Input:
            gn_arr: array of SSP problems
            smv_t_arr: array of smv files using tagging
            smv_nt_arr: array of smv files not using tagging
            wbook: The excel workbook
            wsheet: the excel worksheet
            xl_fn: excel file name
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
            with_tags: Flag for using networks with tags
    """

    row_id = 0

    for index, gn in enumerate(gn_prism_fn):
        # Run Prism on no tags

        if index % 2 == 0 or mu > .0:
            out_fn_nt, out_rt_nt = modcheck.call_pexpect_ssp_prism(gn, str_modchecker, depth[int(index / 2)], spec_number,
                                                               spec_name='spec_gn.pctl', cudd_epsilon_input=1e-5)
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
            logging.info('Inputting ID, k, set, filenames, and output data into Excel...')
            __ = wsheet.cell(column=1, row=(row_id + 4), value=index)
            __ = wsheet.cell(column=2, row=(row_id + 4), value=depth[index])
            __ = wsheet.cell(column=3, row=(row_id + 4), value=gn_prism_fn[index])
            __ = wsheet.cell(column=4, row=(row_id + 4), value=repr(reachable_col))
            __ = wsheet.cell(column=5, row=(row_id + 4), value=repr(unreachable_col))
            __ = wsheet.cell(column=7, row=(row_id + 4), value=out_rt_nt)
            if spec_number == 2:
                __ = wsheet.cell(column=6, row=(row_id + 4), value=str(prob_col))
        else:
            __ = wsheet.cell(column=8, row=(row_id + 4), value=str(reachable_col))
            __ = wsheet.cell(column=9, row=(row_id + 4), value=str(unreachable_col))
            __ = wsheet.cell(column=11, row=(row_id + 4), value=out_rt_nt)
            if spec_number == 2:
                __ = wsheet.cell(column=10, row=(row_id + 4), value=str(prob_col))
        wbook.save(xl_fn)

        # Prepare for next input
        if index % 2 == 1:
            row_id += 1

        wbook.close()


def smv_gen(filename, depth, split, force_down):
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
    f.write('--Auto General Network ' + str(depth)
            + '\n-------------------------------\n')

    # ----------------
    # Write beginning of module and variable definitions
    f.write('MODULE main\n' + 'VAR\n')
    f.write('\trow: 0..' + str(depth) + ';\n')
    f.write('\tcolumn: 0..' + str(depth) + ';\n')
    f.write('\tjunction: {pass, split, reset};\n')
    f.write('\tdir: {dwn, diag};\n')
    f.write('\tflag: boolean;\n')

    # Write assignment definitions
    f.write('ASSIGN\n')
    f.write('\tinit(row) := 0;\n')
    f.write('\tinit(column) := 0;\n')
    init_junction = ''
    if [0, 0] in split:
        init_junction = 'split'
    elif [0, 0] in force_down:
        init_junction = 'reset'
    else:
        init_junction = 'pass'
    f.write(f'\tinit(junction) := {init_junction};\n')
    f.write('\tinit(dir) := dwn;\n')
    f.write('\tinit(flag) := FALSE;\n\n')

    # ----------------
    # Write row transitions to file
    f.write('\n\n\t--Always advance to next row\n')
    f.write('\tnext(row) := (row + 1) mod ' + str(depth + 1) + ';\n')

    # Write flag transitions to file
    f.write('\n\t--Flag turns on when row is ' + str(depth) + '\n')
    f.write('\tnext(flag) := (next(row) = ' + str(depth) +
            ' ? TRUE : FALSE);\n')

    # Write junction transitions to file
    f.write(f'\n\t--Split junctions at [r, c] in {str(split)}')
    f.write(f'\n\t--Reset junctions at [r, c] in {str(force_down)}')

    f.write('\n\n\tnext(junction) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t(')
    for i in range(0, len(force_down)):
        if i < len(force_down) - 1:
            f.write('((next(row) = ' + str(force_down[i][0])
                    + ')&(next(column) = ' + str(force_down[i][1]) + '))|')
        else:
            f.write('((next(row) = ' + str(force_down[i][0])
                    + ')&(next(column) = ' + str(force_down[i][1])
                    + '))): reset;\n\t\t\t\t\t\t(')

    for i in range(0, len(split)):
        if i < len(split) - 1:
            f.write('((next(row) = ' + str(split[i][0])
                    + ')&(next(column) = ' + str(split[i][1]) + '))|')
        else:
            f.write('((next(row) = ' + str(split[i][0])
                    + ')&(next(column) = ' + str(split[i][1])
                    + '))): split;\n')
            f.write('\t\t\t\t\t\tTRUE: pass;\n\t\t\t\t\tesac;\n\n')

    # Write direction transitions to file
    f.write('\t--Decide next direction for move by to current junction\n')
    f.write('\tnext(dir) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(junction = split): {dwn, diag};\n\t\t\t\t\t\t')
    f.write('(junction = pass): dir;\n\t\t\t\t\t\t')
    f.write('(junction = reset): dwn;\n\t\t\t\t\t\t')
    f.write('TRUE: {dwn, diag};\n\t\t\t\t\tesac;\n\n')

    # Write column transitions to file
    f.write('\t--If diag, increase column, otherwise dwn, same column\n')
    f.write('\tnext(column) := \n\t\t\t\t\tcase\n\t\t\t\t\t\t')
    f.write('(next(row) = 0): 0;\n\t\t\t\t\t\t')
    f.write('(next(dir) = diag): (column + 1) mod ' + str(depth) + ';\n\t\t\t\t\t\t')
    f.write('(next(dir) = dwn): column;\n\t\t\t\t\t\t')
    f.write('TRUE: column;\n\t\t\t\t\tesac;\n\n')

    # ----------------
    # Write specifications for each network output
    for i in range(0, depth + 1):
        f.write('LTLSPEC\tNAME\tltl_' + str(i)
                + ' := G! ((flag = TRUE) & (column = ' + str(i) + '));\n')
        f.write('CTLSPEC\tNAME\tctl_' + str(i)
                + ' := EF ((flag = TRUE) & (column = ' + str(i) + '));\n')

    # ----------------
    # CLOSE THE FILE
    f.close()


def prism_gen(filename, depth, split, force_down, mu=0.):
    """
    Loop through array of SSP problems and generate prism file
        Input:
            filename: Prism output file name
        Output:
            ssp_list: List of all SSP problems
            set_id: Max set ID (starts from 0)
    """

    # ----------------
    # BEGINNING OF FILE CREATION
    # ----------------

    # Open file and write header into file
    f = open(filename, 'w')
    f.write(f'// General Network for depth = {depth}\n')

    f.write('dtmc\n')

    # ----------------
    #      CONSTS
    # ----------------
    f.write('\n// Consts:\n')
    f.write('const pass = 0;\n')
    f.write('const split = 1;\n')
    f.write('const dwn = 0;\n')
    f.write('const diag = 1;\n')
    f.write(f'const maxrow = {depth};\n')
    f.write('const maxrow_1 = maxrow + 1;\n')
    f.write('const maxcol = maxrow;\n')
    f.write(f'const maxcol_1 = maxcol + 1;\n')
    f.write(f'const double mu  = {mu};\n')

    # ------------------
    #      FORMULAS
    # ------------------

    # fill 'next is split'
    f.write('\n\n// Formulas:\n')
    f.write('formula next_is_split = (')
    split_list = []
    for fs in split:
        if fs[1] != 0:
            split_list.append(fs)
    for sj in split_list:
        f.write(f' (row = {sj[0] - 1} & column = {sj[1] - 1})')
        if sj != split_list[-1]:
            f.write(' | ')
    f.write(') & !reach_maxcol & !ExCov_force;\n')

    # fill 'next is not split'
    f.write('formula next_is_not_split = !start & !next_is_split & row != maxrow & !reach_maxcol & !ExCov_force;\n')
    # for sj in split:
    #     f.write(f' (row = {sj[0]} & column = {sj[1]})')
    # if sj != split[-1]:
    #     f.write(' | ')
    # f.write(') & row != maxrow & !reach_maxcol & !ExCov_force;\n')

    # fill 'next is maxrow', start and maxcol
    f.write('formula row_is_maxrow = row = maxrow;\n')
    f.write('formula start = row = -1;\n')
    f.write(f'formula reach_maxcol = column = {depth + 1};\n')

    # fill ExCov force down
    f.write('formula ExCov_force =')
    rc_f_dwn_list = []
    for fs in force_down:
        if fs[1] != 0:
            rc_f_dwn_list.append(fs)
    rc_f_dwn_list = force_down
    if rc_f_dwn_list:
        for rc in rc_f_dwn_list:
            f.write(f' (row = {rc[0]} & column = {rc[1]})')
            if rc != rc_f_dwn_list[-1]:
                f.write(' | ')
            else:
                f.write(';')
    else:
        f.write(' false;')

    # ------------------
    #    MODULE NET
    # ------------------

    # declaration
    f.write('\n\n// Module:\n')
    f.write('module net\n')
    f.write('\trow: [-1..maxrow] init -1;\n')
    f.write('\tcolumn: [-1..maxcol] init -1;\n')
    f.write('\tjunction: [pass..split];\n')
    f.write('\tdir: [dwn..diag] init dwn;\n')
    f.write(f'\tsum: [-1..maxcol] init -1;\n')

    # transition relation
    str_temp = "[] (start | row_is_maxrow) -> 0.5 : (junction' = split) & (dir' = diag) & (column' = 0) & (row' = 0) & (sum' = column) + 0.5 : (junction' = split) & (dir' = dwn) & (column' = 0) & (row' = 0) & (sum' = column);"
    f.write('\n\t' + str_temp + '\n')
    str_temp = "	[] next_is_split -> 0.5 : (junction' = split) & (dir' = diag) & (column' = mod(column + dir, maxcol_1)) & (row' = mod(row + 1, maxrow_1)) + 0.5 : (junction' = split) & (dir' = dwn) & (column' = mod(column + dir, maxcol_1)) & (row' = mod(row + 1, maxrow_1));"
    f.write(str_temp + '\n')
    str_temp = "	[] next_is_not_split -> (1-mu): (junction' = pass) & (column' = mod(column + dir, maxcol_1)) & (row' = mod(row + 1, maxrow_1)) & (dir'=dir) + mu:(junction' = pass) & (column' = mod(column + dir, maxcol_1)) & (row' = mod(row + 1, maxrow_1)) & (dir' = mod(dir+1,2));"
    f.write(str_temp + '\n')
    str_temp = "	[] ExCov_force -> (junction' = pass) & (column' = column) & (row' = mod(row + 1, maxrow_1)) & (dir'=dwn);"
    f.write(str_temp + '\n')
    str_temp = "	[] reach_maxcol  -> 0.5 : (junction' = split) & (dir' = diag) & (column' = 0) & (row' = 0) & (sum' = -1) + 0.5 : (junction' = split) & (dir' = dwn) & (column' = 0) & (row' = 0) & (sum' = -1);"
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


def gen_prism_spec(filename):
    """
    Print out the ExCov spec for prism file
        Input:
            filename: name of the spec file
    """

    # write 2 specifications: 1. check if exist EC. 2. what is the probability to get the EC.
    f = open(filename, 'w')
    f.write('const int k;\n\n')
    f.write('P>0 [ F = maxrow+1 row=maxrow & column = k]\n')
    f.write('P=? [ F = maxrow+1 row=maxrow & column = k]\n')
    f.close()
