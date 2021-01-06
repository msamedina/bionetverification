"""
Miscellaneous Functions
Michelle Aluf Medina
"""
import os


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
            #print(j, end = " ")
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