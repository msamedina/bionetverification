bionetverification
------------------
Bionetverification is a tool used to model and verify the design of network-based biocomputation circuits for the SSP, ExCov and 3-SAT problems as part of the Bio4Comp project. The tool generates network description files in SMV and then runs them in the NuSMV model checker. Results of verification and their runtimes are saved in Excel files based on the provided template files.

Each run generates a new local directory that holds all generated smv files, output results, and excel data files.

---------------
0. Contents
---------------
1. Built With 
2. Setup
3. System Requirements
4. Usage
5. Additional Files

---------------
1. Built With
---------------
For scripts to run properly the following must be installed:
* [NuSMV](http://nusmv.fbk.eu/)
* [MiniSat](http://minisat.se/)
* [CNFgen](https://massimolauria.net/cnfgen/)

---------------
2. Setup
---------------

Prerequisites
=============
Before running the scripts, run the following to make sure all prerequisites are installed. In order to install python packages, it is recommended to use pip.

NOTE: sudo access may be necessary.

Automated installations
--================--
All prerequisite installations and setups are located in the `install_additionals.sh` bash script. This should be run as root:
	sudo bash install_additionals.sh

Manual installations
--================--
* MiniSat SAT Solver
	apt-get install minisat

* Python packages: CNFGen, openpyxl, pexpect, scipy, networkx
	pip install CNFgen openpyxl==3.0.1 pexpect scipy networkx
		or
	pip3 install CNFgen openpyxl==3.0.1 pexpect scipy networkx

* NuSMV

It is recommended to download the [NuSMV Binaries](http://nusmv.fbk.eu/NuSMV/download/getting_bin-v2.html).
Extract binaries into directory of your choice. Add the directory to your command search PATH environment variable (X.Y.Z is the release number):
```sh
export PATH=${PATH}:/your_directory/nusmv-X.Y.Z/bin
```
Make sure that all of the above are added to the command search PATH environment variable.

Running the scripts
=============
The scripts are run using python 
	python bionetverification.py
		or
	python3 bionetverification.py


---------------
3. System Requirements
---------------
Bionetverification has been tested on systems running Linux (Ubuntu 18.04.5 LTS, Ubuntu 20.04.1 LTS)
* RAM: 4 GB
* Number of Cores: 1-2
* CPU freq: 1.30GHz

Scripts should be run using Python 3.

---------------
4. Usage
---------------
See `Examples` for examples of runs for each of the problem types described below. Each problem includes the generated Excel file, the generated smv files and the input file used.

All input files to be used when running should be saved in the `Inputs` directory. Sample input files for SSP and ExCov are included.

SSP
=============
An input file with the problems to be looked at is necessary. Format of the input file is expected to be a derivative of the DIMACS format. Each row is a new set, mark end of line with 0. So the SSP for S = {2, 5, 9} would be denoted as:
	2 5 9 0

There is the option to run NuSMV on the generated network descriptions using 3 methods:
1. Bulk run output specifications (Table 5)
2. Run individual output specifications (Table 6)
3. Run general valid-invalid output specifications (Table 7)

When a method is selected, it runs on the full list of input problems.

The Excel output file contains one sheet per method above:
1. Bulk_OutSpec
2. Single_OutSpec
3. SSP_GenSpec

Each sheet contains information on the problem being looked at such as relevant file names, verification runtime, verification result and/or result output file. This is done for the specifications described in Tables 1 and 2. Methods 1 and 2 run on specifications from Table 1 and method 3 runs on specifications from Table 2.

ExCov
=============
An input file with the problems to be looked at is necessary. Format of the input file is another derivative of the DIMACS format. Please see the `ExCov_Input` file under `Inputs` for more information.

The Excel output file contains information on the problems run such as relevant file names, existence of an exact cover, verification runtimes, verification result and output file. This is run on the specification as described in Table 1 for the single exact cover output 'k'.

3-SAT
=============
The tool generates random 3-SAT problems. The number of problems to be generated and the maximum number of literals are entered by the user when prompted. Example runs for SAT were run using the following input values:
* 10 samples (number or problems)
* 20 literals maximum

---------------
5. Additional Files
---------------
Templates for Excel files are saved under `Template`.

Examples of runs on the SSP, ExCov and SAT problems are included with all generated files (SMV, output text files, Excel files).
Examples of network descriptions in SMV with induced errors are included for SSP and ExCov. They are located in the `SSP_BN` and `ExCov_BN` directories.
