#!/bin/bash

# ------------------------------------------------------------------------- #
# This script is a wrapper for the run_make_skimfile.sh script that makes   # 
# skim files out of R-SIDIS hcana ROOT files.                               #
# ---------                                                                 #
# P. Datta <pdbforce@jlab.org> CREATED 10-15-2025                           #
# ---------                                                                 #
# ** Do not tamper with this sticker! Log any updates to the script above.  #
# ------------------------------------------------------------------------- #

# -------------------------------------------------------------------------- #
# ----------------- VERY IMPORTANT TO SET UP CORRECTLY !!! ----------------- #
# -------------------------------------------------------------------------- #
# Path to make_skimfiles directory. It MUST include all the following scripts
# 1. submit_run_make_skimfile.sh
# 2. run_make_skimfile.sh
# 3. make_skimmed_rootfile.C
# ---
SCRIPT_DIR=/u/group/c-rsidis/pdbforce/analysis/make_skimfiles

runlist=$1        # run list (single column txt file w/ run numbers to analyze)
runtype=$2        # run type : SIDIS / HEEP / HMSDIS / SHMSDIS
indir=$3          # input directory (directory with R-SIDIS hcana ROOT files)
outdir=$4         # output directory (destination for the generated skim files)
run_on_ifarm=$5   # want to run on ifarm instead of batch farm? 1 => yes

workflow_name="rsidis_skim_${runtype}"

# Job specifications
jram='2000MB'    # per-job requested RAM
jtime='1h'       # per-job requested walltime

# Creating the workflow
if [[ $run_on_ifarm -ne 1 ]]; then
    swif2 create -workflow ${workflow_name}
else
    echo -e "\nRunning all jobs on ifarm!\n"
fi

while read run; do
    script=$SCRIPT_DIR'/run_make_skimfile.sh'' '${run}' '${runtype}' '${indir}' '${outdir}' '${run_on_ifarm}' '${SCRIPT_DIR}
    if [[ $run_on_ifarm -ne 1 ]]; then
	swif2 add-job \
	      -workflow ${workflow_name} \
	      -name rsidis_skim_${runtype}_${run} \
	      -partition production \
	      -cores 1 \
	      -ram $jram \
	      -time $jtime \
	      $script
    else
	$script
    fi
    
done < "$runlist"

# run the workflow and then print status
if [[ $run_on_ifarm -ne 1 ]]; then
    swif2 run -workflow ${workflow_name}
    echo -e "\n Getting workflow status.. [may take a few minutes!] \n"
    swif2 status -workflow ${workflow_name}
fi

# Example execution
#./submit_run_make_skimfile.sh heep_runlist_pass0.txt HEEP /cache/hallc/c-rsidis/analysis/replays/pass0 /work/hallc/c-rsidis/skimfiles/pass0/ 0
#./submit_run_make_skimfile.sh hms_runlist_pass0.txt HMSDIS /cache/hallc/c-rsidis/analysis/replays/pass0 /work/hallc/c-rsidis/skimfiles/pass0/ 0
#./submit_run_make_skimfile.sh shms_runlist_pass0.txt SHMSDIS /cache/hallc/c-rsidis/analysis/replays/pass0 /work/hallc/c-rsidis/skimfiles/pass0/ 0
#./submit_run_make_skimfile.sh sidis_runlist_pass0.txt SIDIS /cache/hallc/c-rsidis/analysis/replays/pass0 /work/hallc/c-rsidis/skimfiles/pass0/ 0
