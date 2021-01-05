import warnings
warnings.filterwarnings("ignore")
import argparse
from bionetverification import main_menu


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-p', '--index', required=False, type=str, help='Problem type')
    p.add_argument('-f', '--filename', required=False, type=str, help='File name')
    p.add_argument('-m', '--modecheck', required=False, type=str, help='Model checker')
    return p.parse_args()


if __name__ == '__main__':
    opts = parse_args()
    index = opts.index
    filename = opts.filename
    modecheck = opts.modecheck
    print(index)
    if index is None:
        main_menu()
    # else:
      #  print(0)

