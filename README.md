# BNVerify
BNVerify is a formal verification tool that facilitates proof of correctness of network-based biocomputation (NBC) circuits or error identification in design, and the ability to model various types of errors in the networks and study their effect on circuit behavior. This work supports analysis of both nondeterministic and probabilistic models and provides an integrated prototype tool that can generate models for simulation and apply verification using several underlying model checkers including NuSMV, nuXmv and PRISM. 
The tool is used to model and verify the design of NBC circuits for the SSP, ExCov and 3-SAT problems as part of the [Bio4Comp project](https://bio4comp.org/).

## People
* [Michelle Aluf-Medina](https://www.linkedin.com/in/michelle-aluf-medina-ba791b81/)
* [Avraham Raviv](https://www.linkedin.com/in/avraham-raviv-47b3b5158/)
* [Dr. Hillel Kugler](https://www.eng.biu.ac.il/hillelk/)

## 0. Contents
* [1. Built With](#1-Built-With)
* [2. Setup](#2-Setup)
* [3. System Requirements](#3-System-Requirements)
* [4. Usage](#4-Usage)
* [5. Additional Files](#5-Additional-Files)
* [6. Comprehensive Reproduction of Table Results](#6-Comprehensive-Reproduction-of-Table-Results)

## 1. Built With
For scripts to run properly the following must be installed:
* [NuSMV](http://nusmv.fbk.eu/)
* [nuXmv](https://nuxmv.fbk.eu/)
* [PRISM](https://www.prismmodelchecker.org/manual/Main/AllOnOnePage)
<!-- In progress: * [Storm](https://www.stormchecker.org/)-->
* [MiniSat](http://minisat.se/)
* [CNFgen](https://massimolauria.net/cnfgen/)

## 2. Setup
### Prerequisites
We assume Java is installed (version 8 or higher).

Before running the scripts, run the following to make sure prerequisites are installed.

#### Linux automated installation
All prerequisite installations and setups are located in the `install_additionals.sh` bash script. This should be run as:
```sh
. install_additionals.sh
```

This prompts for sudo access and confirmation (y).

#### Windows installation
At this time, prerequisites must be installed manually.

External programs that must be installed and able to run from commandline:
* [NuSMV](http://nusmv.fbk.eu/)
* [nuXmv](https://nuxmv.fbk.eu/)
* [PRISM](https://www.prismmodelchecker.org/manual/Main/AllOnOnePage)
<!-- In progress: * [Storm](https://www.stormchecker.org/)-->
* [MiniSat](http://minisat.se/)

Python library dependencies:
* [CNFgen (version 0.9.0 or higher)](https://massimolauria.net/cnfgen/)
* [openpyxl (version 3.0.1)]
* [pexpect]
* [scipy]
* [networkx]

### Running the scripts
The scripts are run using Python 3 (for command line arguments see [below](#4-Usage)):
```sh
python main_NBC.py
```
or
```sh
python3 main_NBC.py
```
Each run generates a new local directory that holds all generated SMV/PM files, output results, and Excel data files. The directory name is of the format:
```sh
bionetverification_out_{0}
```
Where {0} is the index of the run of the script.

## 3. System Requirements
Bionetverification has been tested on systems running Linux (Ubuntu 18.04.5 LTS, Ubuntu 20.04.1 LTS)
* RAM: 4 GB
* Number of Cores: 1-2
* CPU freq: 1.30GHz

## 4. Usage
### Command line mode
To run BNVerify, execute from the repo directory, using the following arguments:

| Short Arg | Long Arg                    | Use                        | Input values                          | Required? (Default) |
|:---------:|:---------------------------:|----------------------------|---------------------------------------|---------------------|
| -p        | --prob                      | Problem type               | SSP, ExCov, SAT or General            | Yes                 |
| -f        | --filename                  | Input file name            |                                       | Yes                 |
| -m        | --modecheck                 | Model checker              | NuSMV, nuXmv, PRISM, all              | Yes                 |
| -o        | --opt                       | Spec options (SSP in SMV)  | 1 (Bulk), 2 (Individual), 3 (General) | No (1)              |
| -t        | --tags                      | Tag variable (SSP, ExCov)  | with, without, both                   | No (without)        |
| -v        | --vro                       | Variable reordering (SAT)  | with, without, both                   | No (without)        |
| -s        | --spec                      | Spec type (PM)             | reachability, probability             | No (reachability)   |
| -e        | --error                     | Error rate *μ* (PM)        | Number in range [0, 1]                | No (0)              |
| -ver      | --verbosity                 | NuSMV/nuXmv verbosity      | Integer from 0 to 4                   | No (0)              |
| -c        | --cut\_in\_u                | Cut network at *k* (ExCov) | True, False                           | No (True)           |
| -b        | --bit\_mapping              | Bit-mapping optimization   | True, False                           | No (True)           |

Input files should be saved in the Inputs directory. Once this is done, it is enough to enter the file name without full path. If the file is saved within a subdirectory, that part of the path should be entered with the filename.

For example, for testing SSP_Benchmark file with all model checkers, and check the behavior with error rate *μ* = 0.01, run the following:
```sh
python3 main_NBC.py -p SSP -f SSP_Benchmark -m all -e 0.01
```
Input files for SAT problems should be a text file containing the dimacs 3-SAT file names, all of which should be located in the same directory (Inputs).  

### Interactive mode
There is also interactive mode, which starts after running the script.

The user is first supplied with a menu for selecting the problem type to be looked at:
0. General Circuit
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

The user is then prompted with a menu for which model checker to use:
1. NuSMV
2. nuXmv
3. Prism

Enter a number to select the relevant model checker.

If NuSMV/nuXmv has chosen, the user should select which method to use when running SMV file:
1. Bulk run output specifications
2. Run individual output specifications
3. Run general valid-invalid output specifications
4. Main Menu

Enter a number to select the relevant method.

Each method runs on the full list of input problems and their relevant specifications. Verification results, runtimes and/or relevant output file names are saved in Excel, separate  worksheet per method, as follows:
1. Bulk_OutSpec
2. Single_OutSpec
3. SSP_GenSpec

If Prism has chosen, the user should select which method to use when running PM file:
1. Run general valid-invalid output
2. Calculate the probabilities of outputs
3. Main Menu

Enter a number to select the relevant method.

The user is then asked for error rate (number between 0 to 1).

The model checker outputs and Excel files are all saved in the current run's output directory (`bionetverification_out_{0}`).

#### Minimal running example
For a minimal running example, use the supplied input file:
```sh
SSP_Input
```
When prompted with the menu for which method to use when running NuSMV (1. Bulk output, 2. Single output, 3. General specs), select method 3.
Approximate runtime: **~1 minute**

### ExCov
The script requests an input file name. This file should be saved in the `Inputs` directory.

The input file format is a derivative of the DIMACS format. Please see `ExCov_Input` under the `Inputs` directory for more information on the correct format.

After entering the input file, the script runs model checker on all input problems and their specifications for the single ExCov output 'k'. Verification results, runtimes and/or relevant output file names are saved in Excel. The output file name is in the following format:
```sh
ExCov_{0}.xlsx
```
Where {0} is the sequential ExCov input index (when using multiple input files).

#### Minimal running example
For a minimal running example, use NuSMV model checker and the supplied input file:
```sh
ExCov_Input
```
Approximate runtime: **~1 minute**

Output files can be accessed from the run's output directory (`bionetverification_out_{0}`). A preloaded version of the minimal running example's Excel output, by the name of `ExCov_0.xlsx`, can be found in the `Examples/ExCov` directory.

### SAT
For SAT, an input file is not needed as the tool generates random 3-SAT problems.

The user is prompted with a menu:
1. Enter sample size for SAT 
2. Main Menu

Option 1 prompts the user to enter the number of problems to be generated, and then the maximum number of literals to use during 3-SAT generation. Enter a number for each of these options.

After entering these values, the script runs MiniSat to check satisfiability, and NuSMV on the network descriptions using the defined specifications. Verification results are then parsed as "SATISFIABLE" or "UNSATISFIABLE".

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

Output files can be accessed from the run's output directory (`bionetverification_out_{0}`). A preloaded version of the minimal running example's Excel output, by the name of `SAT_0.xlsx`, can be found in the `Examples/SAT` directory.

**As each run randomly generates 3-SAT problems, this is not an exact reproduction.**

## 5. Additional Files

### Inputs
The `Inputs` directory is used for containing the input files for use with the SSP, ExCov and SAT problems. Input files for the minimal running examples are preloaded in this folder.

### Template
The `Template` directory contains the templates for the Excel output files. Do not edit these.

### Examples
The `Examples` directory contains example input files, generated SMV files and Excel outputs for each of the minimal running examples for the defined problems.

### SSP and ExCov Bad Networks
The `SSP_BN` and `ExCov_BN` directories contain SMV network descriptions, for SSP and ExCov respectively, that contain **induced errors**. These network descriptions were manually constructed (inclusion of errors) and individually run in NuSMV.

SSP networks include the error type in their file name `B_errortype_...`.

These examples are used to show correctness of the network descriptions by comparing verification results with those of the valid networks generated by the scripts. This comparision is included in published VMCAI'21 article Tables 9 and 11 (sections 7.1 and 7.2).

## 6. Comprehensive Reproduction of Table Results
Additional input files for reproduction of the results in the paper are provided under `Inputs/CMSB21_Inputs`. A full reproduction can take over 24 hours.

### SSP
In order to reproduce Table 2 from the paper, method 3 should be run on input file:
```sh
/CMSB21_Inputs/SSP_table2
```

### ExCov
In order to reproduce Table 3 and Table 5 (Appendix C), run on input file:
```sh
/CMSB21_Inputs/ExCov_table3
```

### SAT
In order to reproduce Table 4, run on input file:
```sh
/CMSB21_Inputs/SAT_table4
```
