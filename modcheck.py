"""
NuSMV and nuXmv Functions for running and parsing model checking results
"""
import sys
if sys.platform.startswith("linux"):
    import pexpect
import subprocess
import re
import datetime
import logging
import miscfunctions as misc
from operator import itemgetter


#DONE
def call_nusmv_pexpect_sat(filename, var_ord_fn, col_ids, s_id, xl_ws, xl_wb,
                           xl_fn, str_modchecker, vro='both', verbosity=0):
    """
    Run NuSMV or nuXmv Model Checker on a given SMV file
    Uses the pexpect library to run NuSMV in verbose interactive format.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS ONLY TO SOLVE THE SAT PROBLEM
        Input:
            filename: The smv filename on which to run
            var_ord_fn: File for variable re-ordering
            col_ids: Initial column indices for saving data in Excel for current sample
            s_id: ID of the sample being inspected
            xl_ws: the excel worksheet where data is being saved
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
    """

    out_fn_arr = []
    out_rt_arr = []
    inval = []

    # NuSMV inputs without re-ordering variables
    if vro in ['without', 'both']:
        ltl_spec = misc.file_name_cformat('output_SAT_LTL_{0}')
        ctl_spec = misc.file_name_cformat('output_SAT_CTL_{0}')
        inval_nvro = ['read_model\n', 'flatten_hierarchy\n', 'encode_variables\n',
                  'build_model\n', 'check_ltlspec -o ' + ltl_spec + '\n',
                  'check_ctlspec -o ' + ctl_spec + '\n', 'quit\n']
        inval.append(inval_nvro)
        out_fn_arr.extend([ltl_spec, ctl_spec])
                
    # NuSMV inputs with re-ordering variables
    if vro in ['with', 'both']:
        ltl_spec = misc.file_name_cformat('output_SAT_LTL_vro_{0}')
        ctl_spec = misc.file_name_cformat('output_SAT_CTL_vro_{0}')
        inval_vro = ['read_model\n', 'flatten_hierarchy\n',
                 'encode_variables -i ' + var_ord_fn + '\n', 'build_model\n',
                 'check_ltlspec -o ' + ltl_spec + '\n',
                 'check_ctlspec -o ' + ctl_spec + '\n', 'quit\n']
        inval.append(inval_vro)
        out_fn_arr.extend([ltl_spec, ctl_spec])

    check_spec = [4, 5]
    out_count = 0
    
    for inputval in inval:
        # prepare to catch runtimes
        start = 0
        stop = 0
        runtime = 0
        err_flag = 0
        indx = inval.index(inputval)
        if vro == 'with':
            indx = 1

        logging.info('Opening process: ' + str_modchecker)
        if sys.platform.startswith('linux'):
            child = pexpect.spawn(str_modchecker, args=['-v', verbosity, '-int', filename],
                              logfile=sys.stdout, encoding='utf-8',
                              timeout=None)
            logging.info('Process opened')
            for i in range(0, len(inputval)):
                while True:
                    try:
                        # Expect pattern to identify model checker waiting for input
                        child.expect('\n' + str_modchecker)
                        # If previous input was a spec check do:
                        if (i - 1) in check_spec:
                            stop = datetime.datetime.now()
                            runtime = int((stop - start).total_seconds() * 1000)
                            out_rt_arr.append(runtime)
                            prev_rec = child.before
                            logging.info(prev_rec)
                            print('Spec Run-time: ' + str(runtime) + ' milliseconds')
                            logging.info('Spec Run-time: ' + str(runtime) +
                                        ' milliseconds')
                            out_count += 1
                            # If LTL
                            if (i - 1) == 4:
                                # Enter output filename into Excel
                                __ = xl_ws.cell(column=col_ids[indx],
                                                row=(s_id + 6),
                                                value=out_fn_arr[out_count - 1])
                                xl_wb.save(xl_fn)
                                # Enter spec runtime into Excel
                                __ = xl_ws.cell(column=(col_ids[indx] + 2),
                                                row=(s_id + 6),
                                                value=runtime)
                                xl_wb.save(xl_fn)
                            # Otherwise must have been CTL
                            else:
                                # Enter output filename into Excel
                                __ = xl_ws.cell(column=(col_ids[indx] + 3),
                                                row=(s_id + 6),
                                                value=out_fn_arr[out_count - 1])
                                xl_wb.save(xl_fn)
                                # Enter spec runtime into Excel
                                __ = xl_ws.cell(column=(col_ids[indx] + 5),
                                                row=(s_id + 6),
                                                value=runtime)
                                xl_wb.save(xl_fn)
                        else:
                            prev_rec = child.before
                            logging.info(prev_rec)
                        break
                    except pexpect.EOF:
                        err_flag = 1
                        prev_rec = child.before
                        logging.info(prev_rec)
                        ermsg = "Process " + str_modchecker + " was killed."
                        logging.exception(msg=ermsg)
                        break
                
                if err_flag == 0:
                    if i in check_spec:
                        print('Running Specs...')
                        start = datetime.datetime.now()
                
                    logging.info(str_modchecker + ' command: ' + inputval[i])
                    child.send(inputval[i])
                elif err_flag == 1:
                    """
                    Need to add error handling for SAT as runtime is added while running
                    while len(out_rt_arr) < 4:
                        out_rt_arr.append('Killed')
                    """
                    break
        
            child.close()
        elif sys.platform.startswith('win32'):
            #[LTL, CTL]
            inputval_win = [''.join(itemgetter(0, 1, 2, 3, 4,-1)(inputval)), ''.join(itemgetter(0, 1, 2, 3, 5,-1)(inputval))]
            for inputval in inputval_win:
                    start = datetime.datetime.now()
                    try:
                        child = subprocess.run(args=[str_modchecker, '-v', verbosity, '-int', filename], timeout=None, input=inputval, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                        stop = datetime.datetime.now()
                        runtime = int((stop - start).total_seconds() * 1000)
                    except subprocess.CalledProcessError:
                        runtime = 'Killed'
                    out_rt_arr.append(runtime)
                    out_count += 1
                    
                    # If LTL
                    if inputval_win.index(inputval) == 0:
                        # Enter output filename into Excel
                        __ = xl_ws.cell(column=col_ids[indx],
                                        row=(s_id + 6),
                                        value=out_fn_arr[out_count - 1])
                        xl_wb.save(xl_fn)
                        # Enter spec runtime into Excel
                        __ = xl_ws.cell(column=(col_ids[indx] + 2),
                                        row=(s_id + 6),
                                        value=runtime)
                        xl_wb.save(xl_fn)
                    # Otherwise must have been CTL
                    else:
                        # Enter output filename into Excel
                        __ = xl_ws.cell(column=(col_ids[indx] + 3),
                                        row=(s_id + 6),
                                        value=out_fn_arr[out_count - 1])
                        xl_wb.save(xl_fn)
                        # Enter spec runtime into Excel
                        __ = xl_ws.cell(column=(col_ids[indx] + 5),
                                        row=(s_id + 6),
                                        value=runtime)
                        xl_wb.save(xl_fn)
    
    return out_fn_arr


#DONE
#MISSING RUNTIME FOR LINUX RUN
def call_prism_pexpect_sat(filename, str_modchecker):
    """
    Run Prism Model Checker on a given file
    Uses the pexpect library to run the relevant model checker.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP (new spec)
        Input:
            filename: The Prism filename on which to run
            str_modchecker: string containing name of model checker (NuSMV, nuXmv or Prism)
    """

    fn_arr = f'res_sat'
    out_fn_arr = []
    out_rt_arr = []
    runtime = 0
    # run 2 specifications: 1. check if exist EC. 2. what is the probability to get the EC.
    for spec_num in range(1, 3, 1):
        input_fn = ['-cuddmaxmem', '4g', filename, 'spec_sat.pctl', '-prop', f'{spec_num}', '-exportresults', f'{fn_arr}_{spec_num}.txt:csv']
        out_fn_arr.append(f'{fn_arr}_{spec_num}.txt')
        logging.info('Opening process: ' + str_modchecker)
        
        if sys.platform.startswith('linux'):
            start = datetime.datetime.now()
            stop = 0
            runtime = 0
            child = pexpect.spawn(str_modchecker, args=input_fn, logfile=sys.stdout, encoding='utf-8', timeout=None)
            try:
                child.expect('\n' + str_modchecker)
            except pexpect.EOF:
                print('')
                if 'Out of memory' in child.before:
                    runtime = 'Out of memory'
                else:
                    stop = datetime.datetime.now()
                    runtime = int((stop - start).total_seconds() * 1000)
            out_rt_arr.append(runtime)
            child.close()
        elif sys.platform.startswith('win32'):
            inputval_win = [str_modchecker]
            inputval_win.extend(input_fn)
            start = datetime.datetime.now()
            try:
                child = subprocess.run(args=inputval_win, timeout=None, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                stop = datetime.datetime.now()
                runtime = int((stop - start).total_seconds() * 1000)
            except subprocess.CalledProcessError:
                runtime = 'Killed'
            out_rt_arr.append(runtime)

    return out_fn_arr, out_rt_arr


#OBSOLETE
def call_nusmv_out_all(filename, spectype, str_modchecker):
    """
    OBSOLETE
    Run NuSMV or nuXmv Model Checker on a given SMV file for all specs of given type
    Only used for SSP
        Input:
            filename: The NuSMV filename on which to run
            spectype: specification type being looked at
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
    """

    checkvar = ''
    if spectype == 1:
        checkvar = 'check_ltlspec'
        outputfilename = misc.file_name_cformat('output_SSP_LTL_{0}')
    else:
        checkvar = 'check_ctlspec'
        outputfilename = misc.file_name_cformat('output_SSP_CTL_{0}')

    # prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    
    start = datetime.datetime.now()
    inval = ('read_model\nflatten_hierarchy\nencode_variables\nbuild_model\n'
             + checkvar + ' -o ' + outputfilename + '\nquit\n')
    p = subprocess.run((str_modchecker + ' -int ' + filename), stdout=subprocess.PIPE,
                       input=inval, encoding='ascii', shell=True)
    stop = datetime.datetime.now()
    runtime = int((stop - start).total_seconds() * 1000)
    print('Overall  Run-time: ' + str(runtime) + ' milliseconds')
    logging.info('Spec Run-time: ' + str(runtime) + ' milliseconds')
    
    return outputfilename


#OBSOLETE
def call_nusmv_out_single(filename, probtype, spectype, outputvalue, str_modchecker):
    """
    OBSOLETE
    Run NuSMV or nuXmv Model Checker on a given SMV file for given spec and out val
        Input:
            filename: The NuSMV filename on which to run
            probtype: SSP or EC
            spectype: spec type being looked at or given spec name
            outputvalue: value of interest
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
    """
    checkvar = ''
    if spectype == 1:
        checkvar = 'check_ltlspec'
        outputfilename = misc.file_name_cformat('output_' + probtype + '_LTL_'
                                                + str(outputvalue) + '_k_{0}')
        if probtype == 'EC':
            spec_name = 'ltl_k'
        else:
            spec_name = 'ltl_' + str(outputvalue)
    elif spectype == 2:
        checkvar = 'check_ctlspec'
        outputfilename = misc.file_name_cformat('output_' + probtype + '_CTL_'
                                                + str(outputvalue) + '_k_{0}')
        if probtype == 'EC':
            spec_name = 'ctl_k'
        else:
            spec_name = 'ctl_' + str(outputvalue)
    # For finding additional paths
    else:
        checkvar = 'check_ltlspec'
        spec_name = spectype
        path_count = spectype.split('_')[-1]
        outputfilename = misc.file_name_cformat('output_' + probtype + '_LTL_'
                                                + str(outputvalue) + '_k_Path_'
                                                + str(path_count) + '_{0}')
    # prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    
    inval = ('read_model\nflatten_hierarchy\nencode_variables\nbuild_model\n'
             + checkvar + ' -o ' + outputfilename + ' -P "' + spec_name
             + '"\nquit\n')
    start = datetime.datetime.now()
    p = subprocess.run((str_modchecker + ' -int ' + filename), stdout=subprocess.PIPE,
                       input=inval, encoding='ascii', shell=True)
    stop = datetime.datetime.now()
    runtime = int((stop - start).total_seconds() * 1000)
    print('Overall ' + probtype + ' ' + spec_name + ' Run-time: ' + str(runtime)
          + ' milliseconds')
    logging.info('Overall ' + probtype + ' ' + spec_name + ' Run-time: '
                 + str(runtime) + ' milliseconds')
    return outputfilename

#DONE - fix
def call_nusmv_pexpect_allout(filename, ssp_id, xl_ws, xl_wb, xl_fn, str_modchecker, verbosity=0):
    """
    Run NuSMV or nuXmv Model Checker on a given SMV file
    Uses the pexpect library to run NuSMV in verbose interactive format.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP ALL OUTPUTS
        Input:
            filename: The NuSMV filename on which to run
            ssp_id: ID of the SSP problem being inspected
            xl_ws: the excel worksheet where data is being saved
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
    """

    out_fn_arr = [misc.file_name_cformat('output_SSP_LTL_{0}'),
                  misc.file_name_cformat('output_SSP_CTL_{0}')]
    out_rt_arr = []

    # Prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    err_flag = 0
    
    # NuSMV inputs without re-ordering variables
    inputval = ['go\n', 'check_ltlspec -o ' + out_fn_arr[0] + '\n',
                'check_ctlspec -o ' + out_fn_arr[1] + '\n', 'quit\n']
    check_spec = [1, 2]

    logging.info('Opening process: ' + str_modchecker)
    
    if sys.platform.startswith('linux'):
        child = pexpect.spawn(str_modchecker, args=['-v', verbosity, '-int', filename],
                            logfile=sys.stdout, encoding='utf-8',
                            timeout=None)
        logging.info('Process opened')
        for i in range(0, len(inputval)):
            while True:
                try:
                    # Expect pattern to identify model checker waiting for input
                    child.expect('\n' + str_modchecker)
                    # If previous input was a spec check do:
                    if (i - 1) in check_spec:
                        stop = datetime.datetime.now()
                        runtime = int((stop - start).total_seconds() * 1000)
                        out_rt_arr.append(runtime)
                        prev_rec = child.before
                        logging.info(prev_rec)
                        print('Spec Run-time: ' + str(runtime) + ' milliseconds')
                        logging.info('Spec Run-time: ' + str(runtime) +
                                    ' milliseconds')
                    else:
                        prev_rec = child.before
                        logging.info(prev_rec)
                    break
                except pexpect.EOF:
                    err_flag = 1
                    prev_rec = child.before
                    logging.info(prev_rec)
                    ermsg = "Process " + str_modchecker + " was killed."
                    logging.exception(msg=ermsg)
                    break
            
            if err_flag == 0:
                if i in check_spec:
                    print('Running Specs...')
                    start = datetime.datetime.now()
            
                logging.info(str_modchecker + ' command: ' + inputval[i])
                child.send(inputval[i])
            elif err_flag == 1:
                while len(out_rt_arr) < 2:
                    out_rt_arr.append('Killed')
                break

        child.close()
    elif sys.platform.startswith('win32'):
        inputval_win = [''.join(itemgetter(0,1,-1)(inputval)), ''.join(itemgetter(0,2,-1)(inputval))]
        for inputval in inputval_win:
            start = datetime.datetime.now()
            try:
                child = subprocess.run(args=[str_modchecker, '-v', verbosity, '-int', filename], timeout=None, input=inputval, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                stop = datetime.datetime.now()
                runtime = int((stop - start).total_seconds() * 1000)
            except subprocess.CalledProcessError:
                runtime = 'Killed'
            out_rt_arr.append(runtime)
    
    return out_fn_arr, out_rt_arr


#DONE
def call_nusmv_pexpect_singleout(filename, probtype, outval, str_modchecker, verbosity=0):
    """
    Run NuSMV or nuXmv Model Checker on a given SMV file
    Uses the pexpect library to run NuSMV in verbose interactive format.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP SINGLE OUTPUTS AND ExCov OUTPUT
        Input:
            filename: The NuSMV filename on which to run
            probtype: Problem type being looked at (1 for SSP or 2 for ExCov)
            outval: The value of interest being looked at
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
    """
    if probtype == 1:
        pt = 'SSP'
        ltlspec = 'ltl_' + str(outval)
        ctlspec = 'ctl_' + str(outval)
    elif probtype == 2:
        pt = 'EC'
        ltlspec = 'ltl_k'
        ctlspec = 'ctl_k'
    
    out_fn_arr = [misc.file_name_cformat('output_' + pt + '_LTL_k_' + str(outval) + '_{0}'),
                  misc.file_name_cformat('output_' + pt + '_CTL_k_' + str(outval) + '_{0}')]
    out_rt_arr = []

    # Prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    err_flag = 0

    # NuSMV inputs
    inputval = ['go\n', 'check_ltlspec -o ' + out_fn_arr[0] + ' -P "' + ltlspec + '"\n',
                'check_ctlspec -o ' + out_fn_arr[1] + ' -P "' + ctlspec + '"\n', 'quit\n']
    check_spec = [1, 2]

    logging.info('Opening process: ' + str_modchecker)

    if sys.platform.startswith('linux'):
        child = pexpect.spawn(str_modchecker, args=['-v', verbosity, '-int', filename],
                            logfile=sys.stdout, encoding='utf-8',
                            timeout=None)
        logging.info('Process opened')
        for i in range(0, len(inputval)):
            while True:
                try:
                    # Expect pattern to identify model checker waiting for input
                    child.expect('\n' + str_modchecker)
                    # If previous input was a spec check do:
                    if (i - 1) in check_spec:
                        stop = datetime.datetime.now()
                        runtime = int((stop - start).total_seconds() * 1000)
                        out_rt_arr.append(runtime)
                        prev_rec = child.before
                        logging.info(prev_rec)
                        print('Spec Run-time: ' + str(runtime) + ' milliseconds')
                        logging.info('Spec Run-time: ' + str(runtime) +
                                    ' milliseconds')
                    else:
                        prev_rec = child.before
                        logging.info(prev_rec)
                    break
                except pexpect.EOF:
                    err_flag = 1
                    prev_rec = child.before
                    logging.info(prev_rec)
                    ermsg = "Process " + str_modchecker + " was killed."
                    logging.exception(msg=ermsg)
                    break
            
            if err_flag == 0:
                if i in check_spec:
                    print('Running Specs...')
                    logging.info('Running specs...')
                    start = datetime.datetime.now()
                
                logging.info(str_modchecker + ' command: ' + inputval[i])
                child.send(inputval[i])
            elif err_flag == 1:
                while len(out_rt_arr) < 2:
                    out_rt_arr.append('Killed')
                break

        child.close()

    elif sys.platform.startswith('win32'):
        # NuSMV inputs
        inputval_win = [''.join(itemgetter(0,1,-1)(inputval)), ''.join(itemgetter(0,2,-1)(inputval))]

        for inputval in inputval_win:
            start = datetime.datetime.now()
            try:
                child = subprocess.run(args=[str_modchecker, '-v', verbosity, '-int', filename], timeout=None, input=inputval, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                stop = datetime.datetime.now()
                runtime = int((stop - start).total_seconds() * 1000)
            except subprocess.CalledProcessError:
                runtime = 'Killed'
            out_rt_arr.append(runtime)

    return out_fn_arr, out_rt_arr


#UNDER CONSTRUCTION
def call_nusmv_pexpect_bmc(filename, probtype, outval, max_row, str_modchecker, verbosity=0):
    """
    Run NuSMV or nuXmv Model Checker on a given SMV file using bounded model checking
    Uses the pexpect library to run NuSMV in verbose interactive format.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP (original spec) SINGLE OUTPUTS AND ExCov OUTPUT
        Input:
            filename: The NuSMV filename on which to run
            probtype: Problem type being looked at (1 for SSP or 2 for ExCov)
            outval: The value of interest being looked at
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
        Output:
            output: The result of the BMC run
            runtime: The BMC runtime of the given specification
    """
    if probtype == 1:
        ltlspec = 'ltl_' + str(outval)
    elif probtype == 2:
        ltlspec = 'ltl_k'

    # NuSMV/nuXmv inputs, No Loopback
    inputval = ['go_bmc\n', 'check_ltlspec_bmc_onepb -P "' + ltlspec + '" -k ' + str(max_row) + ' -l X\n', 'quit\n']
    check_spec = [1]

    # Prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    err_flag = 0
    output = ''
    out_rt_arr = []
                    
    logging.info('Opening process: ' + str_modchecker)
    child = pexpect.spawn(str_modchecker, args=['-v', verbosity, '-int', filename],
                          logfile=sys.stdout, encoding='utf-8',
                          timeout=None)
    logging.info('Process opened')
    for i in range(0, len(inputval)):
        while True:
            try:
                # Expect pattern to identify NuSMV waiting for input
                child.expect('\n' + str_modchecker)
                # If previous input was a spec check do:
                if (i - 1) in check_spec:
                    stop = datetime.datetime.now()
                    runtime = int((stop - start).total_seconds() * 1000)
                    # out_rt_arr.append(runtime)
                    prev_rec = child.before
                    logging.info(prev_rec)
                    logging.info('Parsing output...')
                    output = parse_cmdout(prev_rec)
                    print('Spec Run-time: ' + str(runtime) + ' milliseconds')
                    logging.info('Spec Run-time: ' + str(runtime) +
                                 ' milliseconds')
                else:
                    prev_rec = child.before
                    logging.info(prev_rec)
                break
            except pexpect.EOF:
                err_flag = 1
                prev_rec = child.before
                logging.info(prev_rec)
                ermsg = "Process " + str_modchecker + " was killed."
                logging.exception(msg=ermsg)
                break
        
        if err_flag == 0:
            if i in check_spec:
                print('Running Specs...')
                logging.info('Running specs...')
                start = datetime.datetime.now()
            
            logging.info(str_modchecker + ' command: ' + inputval[i])
            child.send(inputval[i])
        elif err_flag == 1:
            while len(out_rt_arr) < 2:
                out_rt_arr.append('Killed')
            break

    child.close()

    return output, runtime


#DONE
def call_nusmv_pexpect_ssp_newspec(filename, str_modchecker, verbosity=0):
    """
    Run NuSMV or nuXmv Model Checker on a given SMV file
    Uses the pexpect library to run NuSMV in verbose interactive format.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP (new spec)
        Input:
            filename: The NuSMV filename on which to run
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
    """
    out_fn_arr = [misc.file_name_cformat('output_SSP_CTL_csum_{0}'),
                  misc.file_name_cformat('output_SSP_CTL_nsum_{0}')]
    out_rt_arr = []

    # Prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    err_flag = 0

    # NuSMV inputs
    inputval = ['go\n', 'check_ctlspec -o ' + out_fn_arr[0] + ' -P "csum"\n', 'check_ctlspec -o ' + out_fn_arr[1] + ' -P "nsum"\n', 'quit\n']

    logging.info('Opening process: ' + str_modchecker)
    if sys.platform.startswith('linux'):
        check_spec = [1, 2]
        child = pexpect.spawn(str_modchecker, args=['-v', verbosity, '-int', filename],
                          logfile=sys.stdout, encoding='utf-8',
                          timeout=None)
        logging.info('Process opened')
        for i in range(0, len(inputval)):
            while True:
                try:
                    # Expect pattern to identify model checker waiting for input
                    child.expect('\n' + str_modchecker)
                    # If previous input was a spec check do:
                    if (i - 1) in check_spec:
                        stop = datetime.datetime.now()
                        runtime = int((stop - start).total_seconds() * 1000)
                        out_rt_arr.append(runtime)
                        prev_rec = child.before
                        logging.info(prev_rec)
                        print('Spec Run-time: ' + str(runtime) + ' milliseconds')
                        logging.info('Spec Run-time: ' + str(runtime) +
                                    ' milliseconds')
                    else:
                        prev_rec = child.before
                        logging.info(prev_rec)
                    break
                except pexpect.EOF:
                    err_flag = 1
                    prev_rec = child.before
                    logging.info(prev_rec)
                    ermsg = "Process " + str_modchecker + " was killed."
                    logging.exception(msg=ermsg)
                    break

            if err_flag == 0:
                if i in check_spec:
                    print('Running Specs...')
                    logging.info('Running specs...')
                    start = datetime.datetime.now()

                logging.info(str_modchecker + ' command: ' + inputval[i])
                child.send(inputval[i])
            elif err_flag == 1:
                while len(out_rt_arr) < 2:
                    out_rt_arr.append('Killed')
                break

        child.close()
    
    elif sys.platform.startswith('win32'):
        inputval_win = [''.join(itemgetter(0,1,-1)(inputval)), ''.join(itemgetter(0,2,-1)(inputval))]
        for inputval in inputval_win:
            start = datetime.datetime.now()
            try:
                child = subprocess.run(args=[str_modchecker, '-v', verbosity, '-int', filename], timeout=None, input=inputval, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                stop = datetime.datetime.now()
                runtime = int((stop - start).total_seconds() * 1000)
            except subprocess.CalledProcessError:
                runtime = 'Killed'
            out_rt_arr.append(runtime)

    return out_fn_arr, out_rt_arr


#DONE
def call_pexpect_ssp_prism(filename, str_modchecker, maxrow, spec_num):
    """
    Run Prism Model Checker on a given file
    Uses the pexpect library to run the relevant model checker.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP (new spec)
        Input:
            filename: The Prism filename on which to run
            str_modchecker: string containing name of model checker (NuSMV, nuXmv or Prism)
            maxrow: sum of subset, for prism file
            spec_num: choose spec to running - true/false or probabilities calculation
    """

    # run specifications: 1. check the profile of output.
    out_fn = f'res_{maxrow}.txt'
    max_cudd = '{:.2e}'.format(0.5**(filename.count('_') - 3))
    cudd_epsilon = '1' + max_cudd[max_cudd.index('e'):]
    input_fn = [filename, 'spec_ssp.pctl', '-prop', f'{spec_num}', '-const', f'k=0:1:{maxrow}', '-cuddepsilon', f'{cudd_epsilon}', '-exportresults', f'{out_fn}:csv']

    logging.info('Opening process: ' + str_modchecker)
    if sys.platform.startswith('linux'):
        start = datetime.datetime.now()
        child = pexpect.spawn(str_modchecker, args=input_fn,
                            logfile=sys.stdout, encoding='utf-8',
                            timeout=None)
        try:
            child.expect('\n' + str_modchecker)
        except pexpect.EOF:
            print('')
        child.close()
        stop = datetime.datetime.now()
        # Milliseconds
        out_rt = int((stop - start).total_seconds() * 1000)
    elif sys.platform.startswith('win32'):
        inputval_win = [str_modchecker]
        inputval_win.extend(input_fn)
        start = datetime.datetime.now()
        try:
            child = subprocess.run(args=inputval_win, timeout=None, stdout=subprocess.PIPE, encoding='ascii', shell=True)
            stop = datetime.datetime.now()
            out_rt = int((stop - start).total_seconds() * 1000)
        except subprocess.CalledProcessError:
            out_rt = 'Killed'
    
    return out_fn, out_rt


#DONE
def call_pexpect_ec_prism(filename, universe, spec_num, str_modchecker):
    """
    Run Prism Model Checker on a given file
    Uses the pexpect library to run the relevant model checker.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP (new spec)
        Input:
            filename: The Prism filename on which to run
            universe: universe of Ec to be checking
            str_modchecker: string containing name of model checker (NuSMV, nuXmv or Prism)
    """

    fn_arr = f'res_{universe}'
    out_fn_arr = []
    out_rt_arr = []
    input_fn = []
    runtime = 0

    for i in range(0, 2, 1):
        # check if ExCov exist
        if i == 0:
            input_fn = ['-javastack', '1g', filename, 'spec_ec.pctl', '-prop', '1', '-const', f'k={universe}',
                        '-exportresults', f'{fn_arr}_0.txt:csv']
            out_fn_arr.append(f'{fn_arr}_0.txt')
        # calculate the probabilities of the outputs (following user input: 1. only ExCov, 2. all outputs).
        else:
            if spec_num == 1:
                input_fn = ['-javastack', '1g', filename, 'spec_ec.pctl', '-prop', '2', '-const', f'k={universe}',
                            '-exportresults', f'{fn_arr}_{spec_num}.txt:csv']
            elif spec_num == 2:
                input_fn = ['-javastack', '1g', filename, 'spec_ec.pctl', '-prop', '2', '-const', f'k=0:1:{universe}',
                            '-exportresults', f'{fn_arr}_{spec_num}.txt:csv']
            out_fn_arr.append(f'{fn_arr}_{spec_num}.txt')

        logging.info('Opening process: ' + str_modchecker)
        if sys.platform.startswith('linux'):
            start = datetime.datetime.now()
            child = pexpect.spawn(str_modchecker, args=input_fn, logfile=sys.stdout, encoding='utf-8', timeout=None)
            try:
                child.expect('\n' + str_modchecker)
            except pexpect.EOF:
                print('')
            child.close()
            stop = datetime.datetime.now()
            # Milliseconds
            out_rt_arr.append(int((stop - start).total_seconds() * 1000))
        elif sys.platform.startswith('win32'):
            inputval_win = [str_modchecker]
            inputval_win.extend(input_fn)
            start = datetime.datetime.now()
            try:
                child = subprocess.run(args=inputval_win, timeout=None, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                stop = datetime.datetime.now()
                runtime = int((stop - start).total_seconds() * 1000)
            except subprocess.CalledProcessError:
                runtime = 'Killed'
            out_rt_arr.append(runtime)

    return out_fn_arr, out_rt_arr


def get_path(output_filename, output_interest):
    """
    Parse the ltl output to find the path of the counter-example
    Relevant for SSP (original spec) and ExCov
        Input:
            output_filename: output file to be looked at
            output_interest: the output we are interested in looking at
        Output:
            path_tag: the list of the tags marked for the output path to
    """
    # Open the output file and initialize variables
    file = open(output_filename, "r")
    column = 'initial'
    flag = 'FALSE'
    path_tag = []

    # All patterns we are looking for
    spec_pattern = re.compile(r"specification.+(false|true)")
    tag_pattern = re.compile(r"tag\[([0-9]+)] = TRUE")
    column_pattern = re.compile(r"column = ([0-9]+)")
    flag_pattern = re.compile(r"flag = (FALSE|TRUE)")

    # Run through output file
    for i, line in enumerate(file):
        # First check initial specification
        if i == 0:
            initial_match = re.search(spec_pattern, line)
            if initial_match.groups()[0] != "false":
                # print('This is not a valid output. No output path.')
                path_tag.append('nil')
                return path_tag
        # If initial specification passed, check end of path
        # Skip first line to ignore spec being checked (no change to variables)
        elif (column != str(output_interest)) or (flag != 'TRUE'):
            for flag_match in re.finditer(flag_pattern, line):
                flag = flag_match.groups()[0]
            for column_match in re.finditer(column_pattern, line):
                column = column_match.groups()[0]
            for path_tag_match in re.finditer(tag_pattern, line):
                path_tag.append(path_tag_match.groups()[0])

    # Close the file
    file.close()

    # Return the path taken
    return path_tag


def add_path_spec(path, path_count, output_interest, filename, maxtagid,
                  ssp_or_ec):
    """
    Add specification to smv file that checks for additional paths to output
    Relevant for SSP (original spec) and ExCov, has no meaning for SAT
    Only LTL specification as counter-example returns path to output
        Input:
            path: last found path
            path_count: current number of paths found
            output_interest: output being investigated
            filename: the smv filename where to add the specification
            maxtagid: the largest tag index
            ssp_or_ec: problem type being investigated ('ssp'and 'ec')
        Output:
            the name of the new specification
    """
    new_spec = ''
    if ssp_or_ec == 'ssp':
        new_spec = ('\nLTLSPEC\tNAME\tltl_' + str(output_interest) + '_path_'
                    + str(path_count) + ' := G! ((flag = TRUE) & (column = '
                    + str(output_interest) + ') & !(')
    elif ssp_or_ec == 'ec':
        new_spec = ('\nLTLSPEC\tNAME\tltl_k_path_' + str(path_count)
                    + ' := G! ((flag = TRUE) & (column = '
                    + str(output_interest) + ') & !(')
    # Make list for the tags
    tag_list = ''
    for path_id in range(1, path_count):
        if path_id != 1:
            tag_list += ' | ('
        else:
            tag_list += '('
        for i in range(0, maxtagid + 1):
            if i != 0:
                tag_list += ' & '
            if str(i) in path[path_id]:
                tag_list += '(tag[' + str(i) + '] = TRUE)'
            else:
                tag_list += '(tag[' + str(i) + '] = FALSE)'
        tag_list += ')'
    tag_list += '));'
    new_spec += tag_list
    
    # Append new spec to the NuSMV file
    f = open(filename, "a+")
    f.write(new_spec)
    f.close()
    
    # Return the name of the spec
    if ssp_or_ec == 'ssp':
        return 'ltl_' + str(output_interest) + '_path_' + str(path_count)
    elif ssp_or_ec == 'ec':
        return 'ltl_k_path_' + str(path_count)


def get_spec_res(spec_res_fn, ic3=False):
    """
    Parse the NuSMV output file
        Input:
            spec_res_fn: NuSMV output file name
        Output:
            result: The specification's truth value result
    """
    # Pattern for result
    spec_pattern = re.compile("specification.+(false|true|unknown)")
    result = ''

    # Open the output file and read first line
    # Spec result is always in first line for non ic3
    with open(spec_res_fn) as f:
        if not ic3:
            first_line = f.readline()
            match = re.search(spec_pattern, first_line)
            result = match.groups()[0]
        else:
            for line in f:
                match = re.search(spec_pattern, line)
                if match is not None:
                    result = match.groups()[0]

    # Return result
    return result


def parse_cmdout(data):
    """
    Parse the NuSMV output for BMC or IC3
        Input:
            data: Spec command line data
        Output:
            result: The bmc result
    """
    # Pattern for result
    bmc_pattern = re.compile("-- (no counterexample|specification)")
    result = ''
    
    # Search for spec result in command line data
    match = re.search(bmc_pattern, data)
    if match.groups()[0] == 'specification':
        logging.info('The Output is reachable.')
        result = 'reachable'
    else:
        logging.info('No counterexample found under the given conditions.')
        result = match.groups()[0]
        
    return result
        

def ic3_output(filename, filecontent):
    f = open(filename, 'w')
    text = filecontent
    # logging.info('SMV file has been opened for editing')
    f.write(filecontent)
    f.close()


def pexpect_nuxmv_ic3_allout(filename, str_modchecker, max_row, verbosity=0):
    """
    Run nuXmv Model Checker on a given SMV file using the ic3 engine on the LTL specifications
    Uses the pexpect library to run NuSMV in verbose interactive format.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP ALL OUTPUTS, ONLY LTL
        Input:
            filename: The nuXmv filename on which to run
            verbosity: nuXmv verbosity level
    """
    out_fn_arr = [misc.file_name_cformat('output_SSP_IC3_LTL_{0}'),
                misc.file_name_cformat('output_SSP_CTL_{0}')]
    out_rt_arr = []

    # Prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    err_flag = 0
    
    # nuXmv inputs
    inputval = ['read_model\n', 'flatten_hierarchy\n', 'encode_variables\n',
                'build_boolean_model\n', 'check_ltlspec_ic3 -k ' + str(max_row) + '\n',
                'build_model\n', 'check_ctlspec -o ' + out_fn_arr[1] + '\n', 'quit\n']
    check_spec = [4, 6]

    logging.info('Opening process: ' + str_modchecker)
    
    if sys.platform.startswith('linux'):
        child = pexpect.spawn(str_modchecker, args=['-v', verbosity, '-int', filename],
                            logfile=sys.stdout, encoding='utf-8',
                            timeout=None)
        logging.info('Process opened')
        for i in range(0, len(inputval)):
            while True:
                try:
                    # Expect pattern to identify model checker waiting for input
                    child.expect('\n' + str_modchecker)
                    # If previous input was a spec check do:
                    if (i - 1) == check_spec:
                        stop = datetime.datetime.now()
                        runtime = int((stop - start).total_seconds() * 1000)
                        out_rt_arr.append(runtime)
                        prev_rec = child.before
                        logging.info(prev_rec)
                        if (i - 1) == check_spec[0]:
                            ic3_output(out_fn_arr[0], prev_rec)
                        print('Spec Run-time: ' + str(runtime) + ' milliseconds')
                        logging.info('Spec Run-time: ' + str(runtime) +
                                    ' milliseconds')
                    else:
                        prev_rec = child.before
                        logging.info(prev_rec)
                    break
                except pexpect.EOF:
                    err_flag = 1
                    prev_rec = child.before
                    logging.info(prev_rec)
                    ermsg = "Process " + str_modchecker + " was killed."
                    logging.exception(msg=ermsg)
                    break
            
            if err_flag == 0:
                if i in check_spec:
                    print('Running Specs...')
                    start = datetime.datetime.now()
            
                logging.info(str_modchecker + ' command: ' + inputval[i])
                child.send(inputval[i])
            elif err_flag == 1:
                while len(out_rt_arr) < 2:
                    out_rt_arr.append('Killed')
                break

        child.close()
    # WINDOWS SUPPORT FOR FUTURE DEVELOPEMENT
    """ elif sys.platform.startswith('win32'):
        inputval_win = [''.join(itemgetter(0,1,-1)(inputval)), ''.join(itemgetter(0,2,-1)(inputval))]
        for inputval in inputval_win:
            start = datetime.datetime.now()
            try:
                child = subprocess.run(args=[str_modchecker, '-v', verbosity, '-int', filename], timeout=None, input=inputval, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                stop = datetime.datetime.now()
                runtime = int((stop - start).total_seconds() * 1000)
            except subprocess.CalledProcessError:
                runtime = 'Killed'
            out_rt_arr.append(runtime) """
    
    return out_fn_arr, out_rt_arr


def pexpect_nuxmv_ic3_singleout(filename, probtype, outval, str_modchecker, max_row, verbosity=0):
    """
    Run nuXmv Model Checker on a given SMV file using the ic3 engine on the LTL specifications
    Uses the pexpect library to run NuSMV in verbose interactive format.
    NOTE: THIS CAN ONLY BE USED ON A UNIX SYSTEM. WILL NOT WORK ON WINDOWS.
    NOTE: THIS IS FOR SSP SINGLE OUTPUTS AND ExCov OUTPUT
        Input:
            filename: The nuXmv filename on which to run
            probtype: Problem type being looked at (1 for SSP or 2 for ExCov)
            outval: The value of interest being looked at
            str_modchecker: string containing name of model checker (NuSMV or nuXmv)
    """

    if probtype == 1:
        pt = 'SSP'
        ltlspec = 'ltl_' + str(outval)
        ctlspec = 'ctl_' + str(outval)
    elif probtype == 2:
        pt = 'EC'
        ltlspec = 'ltl_k'
        ctlspec = 'ctl_k'
    
    out_fn_arr = [misc.file_name_cformat('output_' + pt + '_LTL_IC3_k_' + str(outval) + '_{0}'),
                  misc.file_name_cformat('output_' + pt + '_CTL_k_' + str(outval) + '_{0}')]
    out_rt_arr = []


    # Prepare to catch runtimes
    start = 0
    stop = 0
    runtime = 0
    err_flag = 0

    # nuXmv inputs
    inputval = ['read_model\n', 'flatten_hierarchy\n', 'encode_variables\n',
                'build_boolean_model\n', 'check_ltlspec_ic3 -P "' + ltlspec + '" -k ' + str(max_row) + '\n', 
                'build_model\n', 'check_ctlspec -o ' + out_fn_arr[1] + ' -P "' + ctlspec + '"\n', 'quit\n']
    check_spec = [4, 6]

    logging.info('Opening process: ' + str_modchecker)

    if sys.platform.startswith('linux'):
        child = pexpect.spawn(str_modchecker, args=['-v', verbosity, '-int', filename],
                            logfile=sys.stdout, encoding='utf-8',
                            timeout=None)
        logging.info('Process opened')
        for i in range(0, len(inputval)):
            while True:
                try:
                    # Expect pattern to identify model checker waiting for input
                    child.expect('\n' + str_modchecker)
                    # If previous input was a spec check do:
                    if (i - 1) in check_spec:
                        stop = datetime.datetime.now()
                        runtime = int((stop - start).total_seconds() * 1000)
                        out_rt_arr.append(runtime)
                        prev_rec = child.before
                        logging.info(prev_rec)
                        if (i - 1) == check_spec[0]:
                            ic3_output(out_fn_arr[0], prev_rec)
                        print('Spec Run-time: ' + str(runtime) + ' milliseconds')
                        logging.info('Spec Run-time: ' + str(runtime) +
                                    ' milliseconds')
                    else:
                        prev_rec = child.before
                        logging.info(prev_rec)
                    break
                except pexpect.EOF:
                    err_flag = 1
                    prev_rec = child.before
                    logging.info(prev_rec)
                    ermsg = "Process " + str_modchecker + " was killed."
                    logging.exception(msg=ermsg)
                    break
            
            if err_flag == 0:
                if i in check_spec:
                    print('Running Specs...')
                    logging.info('Running specs...')
                    start = datetime.datetime.now()
                
                logging.info(str_modchecker + ' command: ' + inputval[i])
                child.send(inputval[i])
            elif err_flag == 1:
                while len(out_rt_arr) < 2:
                    out_rt_arr.append('Killed')
                break

        child.close()
    # WINDOWS SUPPORT FOR FUTURE DEVELOPEMENT
    """ elif sys.platform.startswith('win32'):
        # NuSMV inputs
        inputval_win = [''.join(itemgetter(0,1,-1)(inputval)), ''.join(itemgetter(0,2,-1)(inputval))]

        for inputval in inputval_win:
            start = datetime.datetime.now()
            try:
                child = subprocess.run(args=[str_modchecker, '-v', verbosity, '-int', filename], timeout=None, input=inputval, stdout=subprocess.PIPE, encoding='ascii', shell=True)
                stop = datetime.datetime.now()
                runtime = int((stop - start).total_seconds() * 1000)
            except subprocess.CalledProcessError:
                runtime = 'Killed'
            out_rt = runtime """

    return out_fn_arr, out_rt_arr

