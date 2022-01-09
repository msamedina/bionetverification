"""
GN Functions
Michelle Aluf Medina
"""
import logging
import miscfunctions as misc
import modcheck
import pandas as pd


def run_nusmv_gn(gn_smv_fn, wbook, wsheet, xl_fn, str_modchecker, with_tags='without', verbosity=0, depth=[], ic3=False):
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
    for index, gn in enumerate(gn_smv_fn):
        for output in range(depth[index] + 1):
            # Save index, k, set, filenames, and output of interest in excel file
            logging.info('Inputting ID, k, set, filenames, and output data into Excel...')
            __ = wsheet.cell(column=1, row=(row_id + 4), value=index)
            __ = wsheet.cell(column=2, row=(row_id + 4), value=depth[index])
            # __ = wsheet.cell(column=3, row=(row_id + 4), value=)
            __ = wsheet.cell(column=6, row=(row_id + 4), value=output)
            wbook.save(xl_fn)

            ltl_res = ''
            ctl_res = ''

            # # Run NuSMV on with tags
            # if with_tags in ['with', 'both']:
            #     __ = wsheet.cell(column=4, row=(row_id + 4), value=smv_t_arr[index])
            #     wbook.save(xl_fn)
            #
            #     if ic3 and str_modchecker == "nuXmv":
            #         out_fn, out_rt = modcheck.pexpect_nuxmv_ic3_singleout(smv_t_arr[index], 1, output, str_modchecker,
            #                                                               max_sum, verbosity)
            #     else:
            #         out_fn, out_rt = modcheck.call_nusmv_pexpect_singleout(smv_t_arr[index], 1, output, str_modchecker,
            #                                                                verbosity)
            #
            #     # Parse output files:
            #     ltl_res = modcheck.get_spec_res(out_fn[0], ic3)
            #     logging.info('LTL Result: ' + ltl_res)
            #     ctl_res = modcheck.get_spec_res(out_fn[1])
            #     logging.info('CTL Result: ' + ctl_res)
            #
            #     logging.info('Saving Tags data in Excel')
            #     __ = wsheet.cell(column=8, row=(row_id + 4), value=out_fn[0])
            #     __ = wsheet.cell(column=9, row=(row_id + 4), value=ltl_res)
            #     __ = wsheet.cell(column=10, row=(row_id + 4), value=out_rt[0])
            #     __ = wsheet.cell(column=11, row=(row_id + 4), value=out_fn[1])
            #     __ = wsheet.cell(column=12, row=(row_id + 4), value=ctl_res)
            #     __ = wsheet.cell(column=13, row=(row_id + 4), value=out_rt[1])
            #     wbook.save(xl_fn)
            #

            # Run NuSMV on no tags
            if with_tags in ['without', 'both']:
                __ = wsheet.cell(column=5, row=(row_id + 4), value=gn_smv_fn[index])
                wbook.save(xl_fn)

                if ic3 and str_modchecker == "nuXmv":
                    out_fn, out_rt = modcheck.pexpect_nuxmv_ic3_singleout(gn[index], 0, output, str_modchecker,
                                                                          depth, verbosity)
                else:
                    out_fn, out_rt = modcheck.call_nusmv_pexpect_singleout(gn_smv_fn[index], 0, output, str_modchecker, verbosity)

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
