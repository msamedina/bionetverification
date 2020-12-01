"""
bionetverification
Modified by: Michelle Aluf-Medina
"""

import logging
from openpyxl import load_workbook as loadwb
import sat
import ssp
import ec
import miscfunctions as misc
import os


"""
MAIN
-----
This is the main body of the script. All functions are called from here.

LOGGING
--------
Setup log file and logging format
"""
log_dir = 'Logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_path = misc.file_name_cformat(os.path.join(os.getcwd(), log_dir, 'log_{0}.log'))
fmt = ('%(asctime)s\t%(module)s\t%(funcName)s\t-\t\t%(levelname)s:\t%(message)s')
logging.basicConfig(filename=log_path, level=logging.DEBUG, format=fmt,
                    datefmt='%Y-%m-%d %H:%M:%S')

"""
CURRENT WORKING DIRECTORY
--------------------------
Make a directory for output files
Change the working directory to this new directory
"""
logging.info('Change working directory')
dir_name = misc.file_name_cformat('bionetverification_out_{0}')
os.mkdir(dir_name)
cwd = os.getcwd()
template_dir = cwd + '/Template/'
input_dir = cwd + '/Inputs/'
new_cwd = os.path.join(cwd, dir_name)
os.chdir(new_cwd)
cwd = os.getcwd()
print('Current working directory:\n' + cwd)
logging.info('New working directory:' + cwd)

"""
PROBLEM TYPE SELECTION
-----------------------
Get the problem type being looked at
    [1] SSP
    [2] ExCov
    [3] SAT
    [4] Quit
"""
problem_type = ''
while problem_type != 4:    # While not quit
    print('Bionetverification\n')
    logging.info('Bionetverification')
    logging.info('Printing problem selection menu')
    misc.print_menu()
    problem_type = misc.int_input()
    logging.info('Selected option: ' + str(problem_type))

    """
    SSP SELECTED
    """
    if problem_type == 1:
        """
        Get and Parse SSP sets from input file
        --------------------------------------
        """
        # While filename is not in Inputs
        ssp_pstr = 'Please enter SSP problems filename: '
        ssp_fn = misc.input_exists(input_dir, ssp_pstr)
        ssp_arr, num_sets = ssp.read_ssp(ssp_fn)
        
        # Setup worksheet for data recording
        ssp_wb = loadwb(template_dir + 'SSP_Template.xlsx')
        ssp_wb_num_of_sheets = len(ssp_wb.sheetnames)
        ssp_xl_fn = misc.file_name_cformat('SSP_{0}.xlsx')
        ssp_wb.save(ssp_xl_fn)

        # Pick a model checker (NuSMV or nuXmv)
        str_modc = misc.modcheck_select()
        ssp_opt = ''

        if str_modc == "NuSMV" or str_modc == "nuXmv":
            """
            Generate smv files
            """
            # Use specification per output
            ssp_smv, ssp_smv_nt = ssp.smv_gen(ssp_arr)

            # Use new specifications (csum and nsum for whole network)
            ssp_smv_new, ssp_smv_nt_new = ssp.smv_gen_newspec(ssp_arr)

            while ssp_opt != 4:
                logging.info('Printing SSP menu')
                ssp.print_ssp_menu(str_modc)
                logging.info('Printed SSP menu.')
                # Get user input for menu selection
                valid_opt = -1
                while valid_opt == -1:
                    ssp_opt = misc.int_input()
                    if ssp_opt in range(1, 5):
                        valid_opt = 1
                        print('Selected option ', str(ssp_opt))
                        logging.info('Selected option: ' + str(ssp_opt))
                    else:
                        print('Invalid option selected. '
                              'Please select a number 1-4.')
                        logging.info('Invalid option selected.')

                # If selected bulk run
                if ssp_opt == 1:
                    """
                    Run NuSMV
                    Bulk run specs for per output specs
                    ------------------
                    """
                    # Add another worksheet based on the template
                    a_source = ssp_wb['ALL_Template']
                    ssp_a_ws = ssp_wb.copy_worksheet(a_source)
                    ssp_a_ws.title = ('Bulk_OutSpec')
                    ssp_wb.save(ssp_xl_fn)

                    # Run NuSMV and get output filename for specification
                    ssp.run_nusmv_all(ssp_arr, ssp_smv, ssp_smv_nt, ssp_wb, ssp_a_ws, ssp_xl_fn, str_modc)

                # If selected individual out run
                elif ssp_opt == 2:
                    """
                    Run NuSMV
                    Run each per output spec individually
                    ------------------
                    """
                    # Add another worksheet based on the template
                    s_source = ssp_wb['SINGLE_Template']
                    ssp_s_ws = ssp_wb.copy_worksheet(s_source)
                    ssp_s_ws.title = ('Single_OutSpec')
                    ssp_wb.save(ssp_xl_fn)

                    # Run NuSMV and get outputs for each individual specification
                    ssp.run_nusmv_single(ssp_arr, ssp_smv, ssp_smv_nt, ssp_wb, ssp_s_ws, ssp_xl_fn, str_modc)

                # If selected general specifications
                elif ssp_opt == 3:
                    """
                    Run NuSMV
                    Run new specs (csum and nsum for whole network)
                    ------------------
                    """
                    # Add another worksheet based on the template
                    s_source = ssp_wb['NewSpec_Template']
                    ssp_s_ws = ssp_wb.copy_worksheet(s_source)
                    ssp_s_ws.title = ('SSP_GenSpec')
                    ssp_wb.save(ssp_xl_fn)

                    # Run NuSMV and get outputs for each individual specification
                    ssp.run_nusmv_newspec(ssp_arr, ssp_smv_new, ssp_smv_nt_new, ssp_wb, ssp_s_ws, ssp_xl_fn, str_modc)

        elif str_modc == "prism":
            while ssp_opt != 3:
                logging.info('Printing SSP menu')
                ssp.print_ssp_menu(str_modc)
                logging.info('Printed SSP menu.')
                # Get user input for menu selection
                valid_opt = -1
                while valid_opt == -1:
                    ssp_opt = misc.int_input()
                    if ssp_opt in range(1, 4):
                        valid_opt = 1
                        print('Selected option ', str(ssp_opt))
                        logging.info('Selected option: ' + str(ssp_opt))
                    else:
                        print('Invalid option selected. '
                              'Please select a number 1-3.')
                        logging.info('Invalid option selected.')
                """
                Generate prism files
                """
                # Use specification per output
                ssp_prism_nt = ssp.prism_gen(ssp_arr)

                if ssp_opt == 1 or ssp_opt == 2:
                    """
                    Run Prism
                    ------------------
                    """
                    # Add another worksheet based on the template
                    s_source = ssp_wb['Prism_Template']
                    ssp_s_ws = ssp_wb.copy_worksheet(s_source)
                    ssp_s_ws.title = 'SSP_Prism_Results'
                    ssp_wb.save(ssp_xl_fn)

                    # Run Prism and get outputs for each individual specification
                    ssp.run_prism(ssp_arr, ssp_prism_nt, ssp_wb, ssp_s_ws, ssp_xl_fn, str_modc, ssp_opt)

        # If selected return to main
        """
        Finished running SSP problems
        Remove template sheets and close file
        In case there was no action - delete the file
        """
        if len(ssp_wb.sheetnames) > ssp_wb_num_of_sheets:
            ssp_wb.remove(ssp_wb['ALL_Template'])
            ssp_wb.remove(ssp_wb['SINGLE_Template'])
            ssp_wb.remove(ssp_wb['NewSpec_Template'])
            ssp_wb.remove(ssp_wb['Prism_Template'])
            ssp_wb.save(ssp_xl_fn)
            logging.info('Output Excel file is: ' + ssp_xl_fn)
        else:
            logging.info('There was no action in file: ' + ssp_xl_fn)
            logging.info('delete file: ' + ssp_xl_fn)
            os.remove(ssp_xl_fn)
        logging.info('Closing workbook')
        ssp_wb.close()

    """
    ExCov SELECTED
    """
    if problem_type == 2:
        """
        Get and Parse ExCov universes and sets from input file
        --------------------------------------
        """
        # While filename is not in Inputs
        excov_pstr = 'Please enter ExCov problems filename: '
        excov_fn = misc.input_exists(input_dir, excov_pstr)
        universes, subsets_arrays, num_probs = ec.read_ec(excov_fn)

        # Pick a model checker (NuSMV or nuXmv)
        str_modc = misc.modcheck_select()

        if str_modc == "NuSMV" or str_modc == "nuXmv":
            """
            Generate smv files
            """
            ec_smv, ec_smv_nt, ec_outputs, max_sums = ec.smv_gen(universes, subsets_arrays, num_probs)

            """
            Run NuSMV
            Single spec for exact cover output
            ------------------
            """
            # Setup worksheet for data recording
            ec_wb = loadwb(template_dir + 'EC_Template.xlsx')
            ec_xl_fn = misc.file_name_cformat('ExCov_{0}.xlsx')
            ec_wb.save(ec_xl_fn)

            # Add another worksheet based on the template
            source = ec_wb['EC_Template']
            ec_ws = ec_wb.copy_worksheet(source)
            ec_ws.title = ('ExCov')
            ec_wb.save(ec_xl_fn)

            # Run NuSMV and get outputs for each individual specification
            ec.run_nusmv(universes, subsets_arrays, ec_outputs, ec_smv, ec_smv_nt, ec_wb, ec_ws, ec_xl_fn, str_modc)
            ec_wb.remove(ec_wb['EC_Template'])
            ec_wb.save(ec_xl_fn)

        elif str_modc == "prism":

            """
            Generate prism files
            """
            ec_smv_nt, ec_outputs, max_sums = ec.prism_gen(universes, subsets_arrays)

            """
            Run prism
            Single spec for exact cover output
            ------------------
            """
            # Setup worksheet for data recording
            ec_wb = loadwb(template_dir + 'EC_Template.xlsx')
            ec_xl_fn = misc.file_name_cformat('ExCov_{0}.xlsx')
            ec_wb.save(ec_xl_fn)

            # Add another worksheet based on the template
            source = ec_wb['EC_Template']
            ec_ws = ec_wb.copy_worksheet(source)
            ec_ws.title = ('ExCov')
            ec_wb.save(ec_xl_fn)

            # Run Prism and get outputs for each individual specification
            ec.run_prism(universes, subsets_arrays, ec_outputs, ec_smv_nt, ec_wb, ec_ws, ec_xl_fn, str_modc)
            ec_wb.remove(ec_wb['EC_Template'])
            ec_wb.save(ec_xl_fn)

        """
        Finished running ExCov
        """
        logging.info('Output Excel file is: ' + ec_xl_fn)
        logging.info('Closing workbook')
        ec_wb.close()
    """
    SAT SELECTED
    """
    if problem_type == 3:
        # Prep for excel output
        run_count = 0
        # Setup workbook for data recording
        xl_wb = loadwb(template_dir + 'SAT_Template.xlsx')
        xl_fn = misc.file_name_cformat('SAT_{0}.xlsx')
        # Grab the active worksheet
        xl_ws = xl_wb.active
        xl_ws.title = 'Template'
        
        # Pick a model checker (NuSMV or nuXmv)
        str_modc = misc.modcheck_select()

        # Start output
        print('3-CNF SAT Network Verification')
        logging.info('3-CNF SAT Network Verification')
        main_opt = ''
        while main_opt != 2:    # While not Quit
            logging.info('Printing SAT menu')
            sat.print_sat_menu()
            logging.info('Printed SAT menu.')
            # Get user input for menu selection
            valid_opt = -1
            while valid_opt == -1:
                main_opt = misc.int_input()
                if main_opt in [1, 2]:
                    valid_opt = 1
                    print('Selected option ', str(main_opt))
                    logging.info('Selected option: ' + str(main_opt))
                else:
                    print('Invalid option selected. '
                          'Please select option 1 or 2.')
                    logging.info('Invalid option selected.')

            # If selected sample size:
            if main_opt == 1:
                xl_wb.save(xl_fn)
                prompt_samp_size = ('What sample size would you like to'
                                    ' generate?\nINPUT SHOULD BE INTEGER,'
                                    ' i.e. [50]\n')
                sample_size = misc.int_input(out_str=prompt_samp_size)
                logging.info('Sample size is: ' + str(sample_size))
                for row in range(6, sample_size + 6):
                    __ = xl_ws.cell(column=1, row=row, value=(row - 6))
                
                # Get max allowed number of variable to randomly generate                 
                maxv_p = ('Please enter max number of variables allowed.\n')
                max_vars = misc.int_input(out_str=maxv_p)
                
                
                # Add another worksheet based on the template
                source = xl_wb['Template']
                xl_ws = xl_wb.copy_worksheet(source)
                xl_ws.title = ('Run_' + str(run_count) + '_MaxVars_'
                               + str(max_vars))
                run_count += 1
                    
                # Generate DIMACS samples
                dimacs_fns, nm_tuples = sat.cnf_gen(sample_size, max_vars,
                                                    xl_ws, xl_wb, xl_fn)

                logging.info('DIMACS file names are: ' + str(dimacs_fns))
                logging.info('(Var, Clause) Tuples are: ' + str(nm_tuples))
                xl_wb.save(xl_fn)

                # Run DIMACS samples in MiniSat Solver to check satisfiability
                logging.info('Check satisfiability using MiniSat')
                minisat_results = sat.mini_sat_solver(dimacs_fns,
                                                      sample_size, xl_ws,
                                                      xl_wb, xl_fn)
                logging.info('Satisfiability checked')
                xl_wb.save(xl_fn)

                # Read each DIMACS, generate two network descriptions
                # Get list of file names for each
                logging.info('Generate network descriptions')
                smv_nc_fns, smv_c_fns = sat.dimacs_to_smv(dimacs_fns,
                                                          sample_size, xl_ws,
                                                          xl_wb, xl_fn)
                logging.info('Network descriptions generated')
                xl_wb.save(xl_fn)

                # Run NuSMV on all samples (LTL, CTL, variable re-ordering)
                logging.info('Run NuSMV on both network descriptions')
                sat.smv_run_specs(smv_nc_fns, smv_c_fns, sample_size,
                                       xl_ws, xl_wb, xl_fn, str_modc)
                logging.info('NuSMV runs complete')
                xl_wb.save(xl_fn)

            elif main_opt == 2:
                xl_wb.remove(xl_wb['Template'])
                xl_wb.save(xl_fn)
                logging.info('Output Excel file is: ' + xl_fn)
                print('Closing Python Script')

# Finished running, close logging
logging.info('Selected Quit')
logging.info('Closing python script')
logging.shutdown()
print('Output directory: ' + cwd)
print('Log file location: ' + log_path)
