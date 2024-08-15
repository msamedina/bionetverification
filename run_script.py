import os
import subprocess
import time
import pandas as pd
import threepartition
import modcheck


#set = [20,23,25,30,49,45,27,30,30,40,22,19]
set=[4,5,6,7,8,9,10,11,15]


sum_sub = threepartition.pre_calc_3partition(set)
print("The Target Sum is: " + str(sum_sub) + " of the set", set)

f = open('smv_file.smv', 'w')
threepartition.print_smv_3partition('smv_file.smv', set, sum(set), len(set), [], int(sum_sub))

modcheck.call_nusmv_pexpect_3partition("smv_file.smv", "nuXmv", len(set), int(sum_sub), set)