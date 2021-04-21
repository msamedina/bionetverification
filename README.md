# BNVerify
BNVerify is a tool used to model and verify the design of network-based biocomputation circuits for the SSP, ExCov and 3-SAT problems as part of the Bio4Comp project. The tool generates network description files in SMV and then runs them in the NuSMV model checker. Results of verification and their runtimes are saved in Excel files based on the provided template files.

Each run generates a new local directory that holds all generated smv files, output results, and Excel data files. The directory name is of the format:
```sh
bionetverification_out_{0}
```
Where {0} is the index of the run of the script.

## 0. Contents
* [1. Built With](#1-Built-With)
* [2. Setup](#2-Setup)
* [3. System Requirements](#3-System-Requirements)
* [4. Usage](#4-Usage)
* [5. Additional Files](#5-Additional-Files)
* [6, Comprehensive Reproduction of Table Results](#6-Comprehensive-Reproduction-of-Table-Results)

## 1. Built With
For scripts to run properly the following must be installed:
* [NuSMV](http://nusmv.fbk.eu/)
* [nuXmv](https://nuxmv.fbk.eu/)
* [PRISM](https://www.prismmodelchecker.org/manual/Main/AllOnOnePage)
* [Storm](https://www.stormchecker.org/)
* [MiniSat](http://minisat.se/)
* [CNFgen](https://massimolauria.net/cnfgen/)

## 2. Setup
### Prerequisites
Before running the scripts, run the following to make sure all prerequisites are installed.

#### Automated installation
All prerequisite installations and setups are located in the `install_additionals.sh` bash script. This should be run as:
```sh
. install_additionals.sh
```

This prompts for sudo access and confirmation (y).

### Running the scripts
The scripts are run using Python 3
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
* Number of Cores: 1-2
* CPU freq: 1.30GHz

## 4. Usage
The user is first supplied with a menu for selecting the problem type to be looked at:
1. SSP
2. ExCov
3. SAT
4. Quit

Enter a number to select the problem type.

For SSP and ExCov, the user is prompted to supply an input file containing the problems to be looked at. All input files should be saved in the `Inputs` directory. Sample input files for SSP and ExCov are included.

### SSP
The script requests an input file name. This file should be saved in the `Inputs` directory.

The input file format is a derivative of DIMACS format. Each row is a new set, mark end of line with 0. The input for S = {2, 5, 9} would be denoted as:
```sh
2 5 9 0
```

The user is then prompted with a menu for which method to use when running NuSMV:
1. Bulk run output specifications
2. Run individual output specifications
3. Run general valid-invalid output specifications
4. Main Menu

Enter a number to select the relevant method.

Methods 1 and 2 run on specifications from Table 1.
Method 3 runs on specifications from Table 2.

Each method runs on the full list of input problems and their relevant specifications. Verification results, runtimes and/or relevant output file names are saved in Excel, separate  worksheet per method, as follows:
1. Bulk_OutSpec
2. Single_OutSpec
3. SSP_GenSpec

The NuSMV outputs and Excel files are all saved in the current run's output directory (`bionetverification_out_{0}`).

#### Minimal running example
For a minimal running example, use the supplied input file:
```sh
SSP_Input
```
When prompted with the menu for which method to use when running NuSMV (1. Bulk output, 2. Single output, 3. General specs), select method 3. This corresponds with Table 7.

Approximate runtime: **~1 minute**

Methods 1 and 2, which correspond with Tables 5 and 6 respectively, can be run as part of section 6 (Comprehensive Reproduction of Table Results).

The output files can be accessed from the run's output directory. A preloaded version of the minimal running example's Excel output, by the name of `SSP_0.xlsx`, can be found in the `Examples/SSP` directory.

### ExCov
The script requests an input file name. This file should be saved in the `Inputs` directory.

The input file format is a derivative of the DIMACS format. Please see `ExCov_Input` under the `Inputs` directory for more information on the correct format.

After entering the input file, the script runs NuSMV on all input problems and their specifications, as described in Table 1 for the single ExCov output 'k'. Verification results, runtimes and/or relevant output file names are saved in Excel. The output file name is in the following format:
```sh
ExCov_{0}.xlsx
```
Where {0} is the sequential ExCov input index (when using multiple input files).

#### Minimal running example
For a minimal running example, use the supplied input file:
```sh
ExCov_Input
```
Approximate runtime: **~1 minute**

Output files can be accessed from the run's output directory (`bionetverification_out_{0}`). A preloaded version of the minimal running example's Excel output, by the name of `ExCov_0.xlsx`, can be found in the `Examples/ExCov` directory. This file contains a subset of Table 10.

### SAT
For SAT, an input file is not needed as the tool generates random 3-SAT problems.

The user is prompted with a menu:
1. Enter sample size for SAT 
2. Main Menu

Option 1 prompts the user to enter the number of problems to be generated, and then the maximum number of literals to use during 3-SAT generation. Enter a number for each of these options.

After entering these values, the script runs MiniSat to check satisfiability, and NuSMV on the network descriptions using the specifications defined in Table 4. Verification results are then parsed as "SATISFIABLE" or "UNSATISFIABLE".

MiniSat results, parsed verification results, runtimes and/or relevant output file names are saved in Excel. The output file name is in the following format:
```sh
SAT_{0}.xlsx
```
Each entered sample size (multiple uses of option 1) is saved in a separate Excel worksheet. The sheet name uses the format:
```sh
Run_{0}_MaxVars_{1}
```

Where {0} is the index of the current SAT run and {1} is the number of max allowed literals.

#### Minimal running example
For a minimal running example, use the input sample size:
```sh
10
```
and maximum number of literals:
```sh
20
```

Approximate runtime: **30 minutes**

Output files can be accessed from the run's output directory (`bionetverification_out_{0}`). A preloaded version of the minimal running example's Excel output, by the name of `SAT_0.xlsx`, can be found in the `Examples/SAT` directory. This reflects the results shown in Table 12.

**As each run randomly generates 3-SAT problems, this is not an exact reproduction.**

## 5. Additional Files

### Inputs
The `Inputs` directory is used for containing the input files for use with the SSP and ExCov problems. Input files for the minimal running examples are preloaded in this folder.

### Template
The `Template` directory contains the templates for the Excel output files. Do not edit these.

### Examples
The `Examples` directory contains example input files, generated SMV files and Excel outputs for each of the minimal running examples for the defined problems.

Columns of the Excel worksheets that correspond with those of the tables in the paper are marked in yellow. The 'csum' and 'nsum' rows from worksheet SSP_GenSpecs in `SSP_0.xlsx` have been have been transposed in Tables 7 and 8, and unified into a single row.

### SSP and ExCov Bad Networks
The `SSP_BN` and `ExCov_BN` directories contain SMV network descriptions, for SSP and ExCov respectively, that contain **induced errors**. These network descriptions were manually constructed (inclusion of errors) and individually run in NuSMV.

SSP networks include the error type in their file name `B_errortype_...`.

These examples are used to show correctness of the network descriptions by comparing verification results with those of the valid networks generated by the scripts. This comparision is included in Tables 9 and 11. See paper sections 7.1 and 7.2.

## 6. Comprehensive Reproduction of Table Results
Additional input files for reproduction of the results in the paper are provided under `Inputs`. A full reproduction can take over 24 hours.

### SSP
In order to reproduce Tables 5-7 from the paper, methods 1-3 should be run on input file:
```sh
SSP_table5_7
```
For Table 8, run method 3 on:
```sh
SSP_table8
```

### ExCov
In order to reproduce Table 10, run on input file:
```sh
ExCov_table10
```

### SAT
As each run randomly generates 3-SAT problems, it is not possible to exactly replicate results from Table 12. The input values used to aquire Table 12 were:
* Number of samples:
```sh
100
```
* Maximum number of literals:
```sh
50
```
