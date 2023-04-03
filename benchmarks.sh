#!/bin/bash
# Sequence of commands to run bemchmarks

# Problem - Model Checker - OPT - TAG - PRISMSPEC - PRISMERR
# SSP - ALL - 3 - WITHOUT - REACHABILITY - 0
#python3 main_NBC.py -p SSP -f SSP_Benchmarks_Light -m all -o 3 -t without -s reachability -e 0
# PRISM ONLY No Error
python3 main_NBC.py -p SSP -f SSP_Benchmarks -m prism -s reachability -e 0
python3 main_NBC.py -p SSP -f SSP_Benchmarks -m prism -s probability -e 0

# ExCov - ALL - NONE - WITHOUT - REACHABILITY - 0
#python3 main_NBC.py -p ExCov -f ExCov_Benchmarks -m all -t without -s reachability -e 0
# PRISM ONLY No Error
python3 main_NBC.py -p ExCov -f ExCov_Benchmarks -m prism -s reachability -e 0
python3 main_NBC.py -p ExCov -f ExCov_Benchmarks -m prism -s probability -e 0