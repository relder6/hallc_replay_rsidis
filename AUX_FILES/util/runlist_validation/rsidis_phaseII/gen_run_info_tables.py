#!/usr/bin/env python3

import os
import sys
import rcdb
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List

def get_rcdb(rcdb_server):
    '''Connect to DB'''
    if "RCDB_CONNECTION" in os.environ:
        rcdb_server = os.environ["RCDB_CONNECTION"]
    return rcdb.RCDBProvider(rcdb_server)    

def read_runlist(runlist, rmin, rmax):
    '''Raad parsed runlist for the desired range'''
    try:
        rlist = pd.read_csv(runlist)
    except FileNotFoundError:
        # Prints the error and immediately shuts down the entire script
        sys.exit(f"Fatal Error: The file '{runlist}' was not found. Stopping execution.")
    frlist = rlist[(rlist['run'] >= rmin) & (rlist['run'] < rmax)]
    return frlist

def calc_time_diff(start, stop):
    '''Calculates time diff in format "%Y-%m-%d %H:%M:%S"'''
    time1 = datetime.strptime(str(start), "%Y-%m-%d %H:%M:%S")
    time2 = datetime.strptime(str(stop), "%Y-%m-%d %H:%M:%S")
    tdiff = time2 - time1
    return np.round(tdiff.total_seconds(), decimals = 2)

def write_csv(csvdata, outcsv):
    df = pd.DataFrame(csvdata).to_csv(outcsv, index=False)

def write_json(jsondata, outjson):
    with open(outjson, "w") as f:
        json.dump(jsondata, f, indent=4)

def process_runs(rcdb_server: str, runlist: str, rmin: int, rmax: int, outcsv: str, outjson: str, outlog: str):
    '''
        Main processor:
        1. Get RCDB
        2. Read runlist based on rmin and rmax
        3. Create CSV for run_start_stop log
        4. Create JSON for RCDBinfo
    '''
    rcdb = get_rcdb(rcdb_server)
    rlistdf = read_runlist(runlist, rmin, rmax)

    csvdata: List[Dict[str, Any]] = []
    jsondata: Dict[int, Dict[str, Any]] = {}
    mrunsdata: List[Dict[int, str]] = []

    for _, row in rlistdf.iterrows():
        run_num = row['run']
        run = rcdb.get_run(run_num)

        print(f"Processing run {run_num}..")

        start_time = run.start_time
        stop_time = run.end_time
        
        if start_time is None or stop_time is None:
            print(f"Warning: Missing start-end time for {run_num}. Skipping..")
            mrunsdata.append({"run" : run_num, "comment" : "missing start-end time"})
            continue

        duration = calc_time_diff(start_time, stop_time)

        conditions_map = {cond.name : cond.value for cond in run.conditions}
        if len(conditions_map) < 20:
            print(f"Warning: Some run condition entries are missing for {run_num}.")
            mrunsdata.append({"run" : run_num, "comment" : "some run condition entries are missing"})

        csvdict = {
            "run_number": run_num,
            "start_time": start_time,
            "stop_time": stop_time,
            "duration_seconds": duration,
            "IHWP": conditions_map.get("ihwp"), 
            "hms_p": conditions_map.get("hms_momentum"),
            "shms_p": conditions_map.get("shms_momentum"),
        }
        csvdata.append(csvdict)
        
        jsondict = {
            "start_time": str(start_time),
            "stop_time": str(stop_time),
            "duration_seconds": duration,
            **conditions_map # Unpacks all remaining key-value conditions cleanly
        }
        jsondata[run_num] = jsondict

    write_csv(csvdata, outcsv)
    write_json(jsondata, outjson)
    write_csv(mrunsdata, outlog)

def main():
    rmin = 0 #27355
    rmax = 99999 #27356
    rcdb_server = "mysql://rcdb@hallcdb.jlab.org/rsidis"
    runlist = "/home/cdaq/rsidis-2025/hallc_replay_rsidis/AUX_FILES/util/parse_runlist/parsed_runlist_phase2.csv"
    outcsv = "output/rsidis_phaseII_run_start_stop_table.csv"
    outjson = "output/rsidis_phaseII_rcdb_info.json"
    outlog = "output/rsidis_phaseII_run_missing_info_log.csv"
    process_runs(rcdb_server, runlist, rmin, rmax, outcsv, outjson, outlog)

if __name__ == "__main__":
    main()
