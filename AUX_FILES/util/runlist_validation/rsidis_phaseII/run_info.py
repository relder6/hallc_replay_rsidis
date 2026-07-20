#!/usr/bin/env python3

import os
import sys
import rcdb

def get_rcdb():
    # Connect to DB
    if "RCDB_CONNECTION" in os.environ:
        con_str = os.environ["RCDB_CONNECTION"]
    else:
        con_str = "mysql://rcdb@hallcdb.jlab.org/rsidis"
    return rcdb.RCDBProvider(con_str)    

def main():

    db = get_rcdb()

    run_num = sys.argv[1]
    run = db.get_run(run_num)
    start_time = run.start_time
    end_time = run.end_time
    
    print("run number:", run.number)
    print("start time:", start_time)
    print("end time:", end_time)
    
    for condition in run.conditions:
        print(condition.name, ":", condition.value)

if __name__ == "__main__":
    main()
