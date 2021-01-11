import argparse
from bionetverification import manual_menu, cmd_menu


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-p', '--problem', required=False, type=str, help='Problem type')  # SSP, ExCov or SAT
    p.add_argument('-o', '--opt', required=False, type=int, help='If SSP selected, there are 3 options for nuXmv/NuSMV')
    p.add_argument('-f', '--filename', required=False, type=str, help='Input file name. Files must be in defined formats for relevant problem types')
    p.add_argument('-m', '--modecheck', required=False, type=str, help='Model checker to be used')  # NuSMV, nuXmv, PRISM or all
    p.add_argument('-t', '--tags', required=False, type=str, help='Flag for using networks with tags (only relevant for SSP and ExCov)')  # with, without or both
    p.add_argument('-v', '--vro', required=False, type=str, help='Flag for using variable reordering (only relevant for SAT)')  # with, without or both
    p.add_argument('-s', '--spec', required=False, type=str, help='Spec type to be looked at')  # LTL (smv/xmv), CTL (smv/xmv), reachability (PRISM) or	probability (PRISM)
    p.add_argument('-e', '--error', required=False, type=float, help='error rate for Prism')  # number in range [0,1] - 0 for no errors
    # case sensitivity
    return p.parse_args()


if __name__ == '__main__':
    opts = parse_args()



    if opts.problem is None:
        manual_menu()
    else:
        cmd_menu(args=opts)