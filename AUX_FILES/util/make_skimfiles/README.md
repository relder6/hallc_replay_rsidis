## Machinery to create skim files out of R-SIDIS hcana ROOT files

How-to:
1. Create a run list with the desired run numbers to analyze (e.g. sidis_runlist_pass0.txt etc.).
2. Open up submit_run_make_skimfile.sh in an editor.
3. Set up the $SCRIPT_DIR path appropriately. Read the description of the arguments.
4. Execute submit_run_make_skimfile.sh with the proper arguments. Here is an example to analyze pass0 SIDIS runs on the batch farm: `./submit_run_make_skimfile.sh sidis_runlist_pass0.txt SIDIS /cache/hallc/c-rsidis/analysis/replays/pass0 /work/hallc/c-rsidis/skimfiles/pass0/ 0`

Description of the scripts:
1. make_skimmed_rootfile.C : Main script written in C++. It creates skim file for a given run. The loose analysis cuts as well as the list of ROOT variables to be copied to the skimmed files are defined within.
2. run_make_skimfile.sh : It is a shell script to execute make_skimmed_rootfile.C script with appropriate arguments and environment setup.
3. submit_run_make_skimfile.sh : It is a wrapper script to run the run_make_skimfile.sh script. It reads from a run list (a single-column txt file w/ run numbers) and calls run_make_skimfile.sh for each run. User can choose whether they want to run the jobs on ifarm or submit them to the batch farm.