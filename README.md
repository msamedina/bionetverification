# bionetverification
Bionetverification is a tool used to model and verify the design of network-based biocomputation circuits for the SSP, ExCov and 3-SAT problems as part of the Bio4Comp project. The tool generates network description files in SMV and then runs them in the NuSMV model checker. Results of verification and their runtimes are saved in Excel files based on the provided template files.

Each run generates a new local directory that holds all generated smv files, output results, and excel data files.

## 0. Contents
1. Built With 
2. Setup
3. System Requirements
4. Usage
5. Additional Files

## 1. Built With
For scripts to run properly the following must be installed:
* [NuSMV](http://nusmv.fbk.eu/)
* [MiniSat](http://minisat.se/)
* [CNFgen](https://massimolauria.net/cnfgen/)

## 2. Setup
### Prerequisites
Before running the scripts, run the following to make sure all prerequisites are installed. In order to install python packages, it is recommended to use pip.

NOTE: sudo access may be necessary.

* MiniSat SAT Solver
```sh
apt-get install minisat
```
* Python packages: CNFGen, openpyxl, pexpect, scipy, networkx
```sh
pip install CNFgen openpyxl==3.0.1 pexpect scipy networkx
```
or
```sh
pip3 install CNFgen openpyxl==3.0.1 pexpect scipy networkx
```
* NuSMV

It is recommended to download the [NuSMV Binaries](http://nusmv.fbk.eu/NuSMV/download/getting_bin-v2.html).
Extract binaries into directory of your choice. Add the directory to your command search PATH environment variable (X.Y.Z is the release number):
```sh
export PATH=${PATH}:/your_directory/nusmv-X.Y.Z/bin
```
Make sure that all of the above are added to the command search PATH environment variable.

### Running the scripts
The scripts are run using python 
```sh
python bionetverification.py
```
or
```sh
python3 bionetverification.py
```

## 3. System Requirements
Bionetverification has been tested on systems running Linux (Ubuntu 18.04.5 LTS, Ubuntu 20.04.1 LTS)
* RAM: 4 GB
* Number of Cores: 2
* CPU freq: 1.30GHz

Scripts should be run using Python 3.

## 4. Usage
See `Examples` for examples of runs for each of the problem types described below. Sample input files and verification results are available as well.

### SSP
An input file with the problems to be looked at is necessary. Format of the input file is expected to be a derivative of the DIMACS format. Each row is a new set, mark end of line with 0. So the SSP for S = {2, 5, 9} would be denoted as:
```sh
2 5 9 0
```
There is the option to run NuSMV on the generated network descriptions using 3 methods:
1. Bulk run output specifications
2. Run individual output specifications
3. Run general valid-invalid output specifications

### ExCov
An input file with the problems to be looked at is necessary. Format of the input file is another derivative of the DIMACS format. Please see the `ExCov_Input` file under `Examples` for more information.

### 3-SAT
The tool generates random 3-SAT problems. The number of problems to be generated and the maximum number of literals are entered by the user when prompted. Example runs for SAT were run using the following input values:
* 10 samples (number or problems)
* 20 literals maximum

## 5. Additional Files
Templates for Excel files are saved under `Template`.

Examples of runs on the SSP, ExCov and SAT problems are included with all generated files (SMV, output text files, Excel files).
Examples of network descriptions in SMV with induced errors are included for SSP and ExCov. They are located in the `SSP_BN` and `ExCov_BN` directories.
