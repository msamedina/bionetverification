"""
Miscellaneous Functions
Michelle Aluf Medina
"""
import os
import logging


def file_name_cformat(filename):
    """
    Format given file name using a counter. Intended for generated files with
    inherently identical names.
        Input:
            filename: the non formatted filename with counter placeholder
        Output:
            filename: formatted file name
    """
    i = 0
    while os.path.exists(filename.format(i)):
        i += 1
    return filename.format(i)


def int_input(out_str=None):
    """
    Receive integer input value. On failure (non-integer), loop to request new
    integer
        Input:
            out_str: OPTIONAL Used for output prompt to user. Default is none.
        Output:
            is_int: the input value as an integer
    """
    is_int = -1
    while is_int == -1:
        if out_str is not None:
            user_input = input(out_str)
        else:
            user_input = input()
        try:
            is_int = int(user_input)
            # logging.info('Input is a valid integer')
        except ValueError:
            # logging.info('Input is not a valid integer')
            print('Input is not a valid integer. Please input an integer.')
            out_str = None
    return is_int


def print_menu():
    """
    Menu for user selection
    """
    print('Select a problem type:')
    print('\t[0] General Network')
    print('\t[1] SSP')
    print('\t[2] ExCov')
    print('\t[3] SAT')
    print('\t[4] Quit')


def strike(text):
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result


def subset_sums(arr, n):
    """
    Receive set array and length of array to find all distinct subset sums.
    Using dynamic programming
    Source: https://www.geeksforgeeks.org/find-distinct-subset-subsequence-sums-array/
        Input:
            arr: set array
            n: length of set array
        Output:
            is_int: list of all distinct subset sums
    """

    max_sum = sum(arr)

    # dp[i][j] = true if arr[0..i-1] has a subset with sum equal to j
    # setup dp as all false initially
    dp = [[False for i in range(max_sum + 1)]
          for i in range(n + 1)]

    # There is always a subset with 0 Sum
    for i in range(n + 1):
        dp[i][0] = True

    # Fill dp[][] in bottom up manner
    for i in range(1, n + 1):

        dp[i][arr[i - 1]] = True

        for j in range(1, max_sum + 1):

            # Achievable sums w/o current array element
            if (dp[i - 1][j] == True):
                dp[i][j] = True
                dp[i][j + arr[i - 1]] = True

    # Last row True values are valid sums, False values are invalid sums
    vsum = list()
    isum = list()
    for j in range(max_sum + 1):
        if (dp[n][j] == True):
            # print(j, end = " ")
            vsum.append(j)
        else:
            isum.append(j)

    return vsum, isum


def input_exists(in_path, p_str):
    """
    Receive input file name and check existence of inout file in input directory.
        Input:
            in_path: input directory
            p_str: the prompt string
        Output:
            is_int: list of all distinct subset sums
    """
    # While filename is not in Inputs
    f_name = ''
    check_input = -1
    while check_input == -1:
        f_name = input(p_str)
        if os.path.isfile(in_path + f_name):
            check_input = 1
        else:
            print('File does not exist in Inputs directory. Please re-enter filename.')
    return in_path + f_name


def modcheck_select():
    """
    Select a model checker
    Output:
        str_modc: string for model checker name
    """
    mod_c_opt = ['NuSMV', 'nuXmv', 'prism']
    menu = 'Please select a model checker:\n\t[1] NuSMV\n\t[2] nuXmv\n\t[3] Prism\n'
    val = -1
    while val == -1:
        mod_c = int_input(out_str=menu)
        if mod_c in range(1, 4):
            val = 1
            str_modc = mod_c_opt[mod_c - 1]
            print('Selected ' + str_modc)
            return str_modc
        else:
            print('Invalid option selected.')


def prism_set_mu():
    print(
        'What would you like to set mu (probability of pass junction to change the direction)?\n mu should be in [0,1], while mu = 0 meaning no errors')
    user_input = float(input())

    return user_input


def cmd_parsing_problem(problem):
    problem_list = ['GN', 'SSP', 'ExCov', 'SAT']
    return problem_list.index(problem)


def cmd_parsing_prism_spec(spec):
    if spec == 'p' or spec == 'prob':
        spec = 'probability'
    if spec == 'r' or spec == 'reach':
        spec = 'reachability'
    spec_list = [None, 'reachability', 'probability']
    return spec_list.index(spec)


def cmd_parsing_mc(mc=None):
    # parsing the model checker without case sensitivity
    if mc is None:
        return
    if mc.lower() == 'all':
        return ['NuSMV', 'nuXmv', 'prism']
    if mc.lower() == 'smv' or mc.lower() == 'nusmv':
        return ['NuSMV']
    if mc.lower() == 'xmv' or mc.lower() == 'nuxmv':
        return ['nuXmv']
    if mc.lower() == 'prism':
        return ['prism']


def cmd_parsing_verbosity(ver):
    if ver is None:
        return '0'
    return ver


def cmd_parsing_bit_mapping(bit_m):
    if bit_m is None:
        return True
    return bit_m


def cmd_parsing_cut(cut):
    if cut is None:
        return True
    return cut


def cmd_parsing_opt(opt):
    if opt is None:
        return 3
    return opt


def cmd_parsing_tags(tags):
    if tags is None:
        return 'without'
    return tags


def cmd_parsing_error(error):
    if error is None:
        return 0
    return error


def cmd_parsing_vro(vro):
    if vro is None:
        return 'without'
    return vro


def ssp_create_m_file(Su=None):
    with open(f'SSP.m', 'w') as f:
        f.write('% MATLAB file for running SSP\n\n')
        for S in Su:
            f.write(f'% S = {str(S)}\n')
            f.write(f'SSP=SubSumNetworkClass({S})\n')
            f.write('Figure=SSP.drawNetwork\n')
            f.write('Figure.Visible=\'on\'\n')
            f.write('Figure=SSP.multisim(\'Iterations\', 10)\n')
            f.write('Figure.Visible=\'on\'\n\n')
        f.close()


def ec_create_m_file(Un=None, Su=None):
    with open(f'EC.m', 'w') as f:
        f.write('% MATLAB file for running ExCov\n\n')
        for U, S in zip(Un, Su):
            f.write(f'% S = {str(S)}\n')
            f.write(f'% Universe = {str(U)}\n')
            f.write(f'Sets=zeros({len(U)},{len(S)})\n')
            for s in S:
                set_i = ''
                for e in range(len(U)):
                    e += 1
                    if e in s:
                        set_i += '1;'
                    else:
                        set_i += '0;'
                set_i = '[' + set_i[:-1] + ']'
                f.write(f'Sets(:,{e})={set_i}\n')
            f.write(f'EXCOV=ExcovClass(\'inputSets\',Sets,\'Optimize\',false)\n')
            f.write('Figure = EXCOV.drawExcovNetwork\n')
            f.write('Figure.Visible=\'on\'\n')
            f.write('Figure = EXCOV.makeCombinedPlot\n')
            f.write('Figure.Visible=\'on\'\n\n')
        f.close()


def read_gn(fn=None):
    """
    Parse the general network input file
    Find file format in README
        Input:
            filename: General Network input file name
        Output:
            Depth: The size of the network
            split_junc: list of split junctions
            force_down_junc: list of split junctions
    """
    logging.info('Opening General Network input file')
    in_data = open(fn, "r")
    split_junc = list()
    force_down_junc = list()

    # Run through the lines of data in the file
    gn = in_data.readlines()
    depth = eval((gn[0])[:-1])
    sj = lambda x, y: eval(gn[1])
    if len(gn) > 2:
        fdj = lambda x, y: eval(gn[2])
    else:
        fdj = lambda x, y: False

    for i in range(depth):
        for j in range(i + 1):
            if fdj(i, j):
                force_down_junc.append([i, j])
            elif sj(i, j):
                split_junc.append([i, j])

    # read to .txt file
    logging.info('Save General Network')
    with open('gn.txt', 'w') as f:
        f.write('General Network with the following architecture:\n')
        f.write(f'Depth: {depth}\n')
        f.write(f'Split junctions: {split_junc}\n')
        f.write(f'Force-down junctions: {force_down_junc}\n')
        f.close()

    return depth, split_junc, force_down_junc


def cmd_parsing_ic3(ic3):
    if ic3 is None:
        return False
    elif ic3.lower() == 'y' or ic3.lower() == 'yes':
        return True
    elif ic3.lower() == 'n' or ic3.lower() == 'no':
        return False