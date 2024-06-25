import os
import subprocess
import time
import pandas as pd
import threepartition

def run_nuxmv(model_filename, k=None, engine=None):
    """
    Run nuXmv model checker with the given model file and parameters.

    :param model_filename (str): The filename of the nuXmv model.
    :param k (int, optional): The number of steps for bounded model checking. Defaults to None.
    :param engine (str, optional): The engine to use for model checking.
                                Options: "SAT" for SAT-based BMC, "BDD" for BDD-based BMC. Defaults to None.
    :return: The filename of the output file.
    """

    # get current directory
    cwd = os.getcwd()

    #### CHANGE HERE TO THE PATH OF YOUR nuXmv BIN FOLDER ####
    os.chdir(r'C:\Users\shoham\Desktop\bionetverification')
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # run the command
    args = [".\\nuXmv.exe", "-int", model_filename]
    nuxmv_process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout= subprocess.PIPE, universal_newlines=True)

    # enter cnrl + c to exit
    nuxmv_process.stdin.write("quit\n")

    # generate output file name
    output_filename = model_filename.split(".")[0] + ".out"

    stdout, _ = nuxmv_process.communicate()

    # save output to file
    with open(output_filename, "w") as f:
        f.write(stdout)
    print(f"Output saved to {output_filename}")

    # change the directory back to the original directory
    os.chdir(cwd)

