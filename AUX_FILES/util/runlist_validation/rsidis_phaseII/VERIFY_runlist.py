#!/usr/bin/env python3

import sys, os, argparse, uproot, csv, re
import numpy as np
import pandas as pd
import glob
import subprocess
import json

# --------------------------------------------------------------------------
# Exceptions list of KNOWN and DOCUMENTED problems
# --------------------------------------------------------------------------
# Use this kind of template for singe-run acknowledged problems
exceptions = {27961: {"checks": ["CHECK_MISSING_REPLAY"], "reason": "BCM Calibration run."},}

# Use this kind of template for run-ranges of problems              
exceptions.update({run: {"checks": ["CHECK_SHMS_TH"],
                         "reason": "Mismatch between tv and gui, hclog 4517645",} for run in range(27504, 27507)})
exceptions.update({run: {"checks": ["CHECK_SHMS_TH"],
                         "reason": "Mismatch between tv and gui, hclog  4536541",} for run in range(28310, 28407)})

# --------------------------------------------------------------------------
# Running some scripts via subprocess
# --------------------------------------------------------------------------
print("Running parse_runlist.py...")

subprocess.run(["python", "parse_runlist.py"], cwd="/home/cdaq/rsidis-2025/hallc_replay_rsidis/AUX_FILES/util/parse_runlist", stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

print("Running gen_run_info_tables.py...")
subprocess.run(["python", "gen_run_info_tables.py"], cwd="/home/cdaq/rsidis-2025/hallc_replay_rsidis/AUX_FILES/util/runlist_validation/rsidis_phaseII", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# --------------------------------------------------------------------------
# Defining directories and files and such,
# --------------------------------------------------------------------------
print("Validating runlist...")
root_directory = f"/net/cdaq/cdaql3data/cdaq/hallc-online-rsidis2025/ROOTfiles"
parsed_runlist = "/home/cdaq/rsidis-2025/hallc_replay_rsidis/AUX_FILES/util/parse_runlist/parsed_runlist_phase2.csv"

report_dir_coin = "/net/cdaq/cdaql3data/cdaq/hallc-online-rsidis2025/REPORT_OUTPUT/COIN/PRODUCTION"
report_dir_hms = "/net/cdaq/cdaql3data/cdaq/hallc-online-rsidis2025/REPORT_OUTPUT/HMS/PRODUCTION"
report_dir_shms = "/net/cdaq/cdaql3data/cdaq/hallc-online-rsidis2025/REPORT_OUTPUT/SHMS/PRODUCTION"

rcdb_json = "/home/cdaq/rsidis-2025/hallc_replay_rsidis/AUX_FILES/util/runlist_validation/rsidis_phaseII/output/rsidis_phaseII_rcdb_info.json"

outfile = "/home/cdaq/rsidis-2025/hallc_replay_rsidis/AUX_FILES/util/runlist_validation/rsidis_phaseII/output/verify_runlist_out.csv"

# --------------------------------------------------------------------------
# Reading the RCDB json file as well as the parsed runlist
# --------------------------------------------------------------------------
f = open(f"{rcdb_json}")
rcdb = json.load(f)

runlist = pd.read_csv(parsed_runlist, usecols = ["run", "ebeam", "current", "target", "hms_p", "hms_th", "shms_p", "shms_th", "ps1", "ps2", "ps3", "ps4", "ps5", "ps6", "run_type"])

rows = []

report_files = (glob.glob(f"{report_dir_coin}/replay_coin_production_*_-1.report") +
                glob.glob(f"{report_dir_hms}/replay_hms_coin_production_*_-1.report") +
                glob.glob(f"{report_dir_shms}/replay_shms_coin_production_*_-1.report"))

for report_file in sorted(report_files):
    filename = os.path.basename(report_file)
    m = re.search(r"production_(\d+)_-1\.report$", filename)
    if not m:
        continue
    runnum = int(m.group(1))

    if runnum < 27106:
        continue

    rcdb_entry = rcdb.get(str(runnum), {})

    rcdb_prescales = rcdb_entry.get("prescales") or {}
    if isinstance(rcdb_prescales, str):
        rcdb_prescales = json.loads(rcdb_prescales)

    rcdb_ps1 = rcdb_prescales.get("ps1")
    rcdb_ps2 = rcdb_prescales.get("ps2")
    rcdb_ps3 = rcdb_prescales.get("ps3")
    rcdb_ps4 = rcdb_prescales.get("ps4")
    rcdb_ps5 = rcdb_prescales.get("ps5")
    rcdb_ps6 = rcdb_prescales.get("ps6")

    # Decide which report type is valid based on the rcdb prescale,
    if rcdb_ps1 != -1 or rcdb_ps2 != -1:
        desired_type = "shms"
    elif rcdb_ps3 != -1 or rcdb_ps4 != -1:
        desired_type = "hms"
    elif rcdb_ps5 != -1 or rcdb_ps6 != -1:
        desired_type = "coin"
    else:
        desired_type = None

    runtype = ("hms" if "replay_hms_" in filename
               else "shms" if "replay_shms_" in filename
               else "coin")

    # Skipping the files that were replayed with the wrong type of replay,
    if desired_type is not None and runtype != desired_type:
        continue
    
    runtime = None

    with open(report_file) as f:
        for repline in f:

            if "Run Length" in repline:
                m = re.search(r":\s*([0-9.]+)", repline)
                if m:
                    rf_duration = float(m.group(1))
                    break
        
        rcdb_start_time = rcdb_entry.get("start_time")
        rcdb_stop_time = rcdb_entry.get("stop_time")
        rcdb_ebeam  = rcdb_entry.get("beam_energy")
        rcdb_ibeam = rcdb_entry.get("beam_current")
        rcdb_target = rcdb_entry.get("target")
        rcdb_hms_p  = rcdb_entry.get("hms_momentum")
        rcdb_hms_th = rcdb_entry.get("hms_angle")
        rcdb_shms_p = rcdb_entry.get("shms_momentum")
        rcdb_shms_th = rcdb_entry.get("shms_angle")
        rcdb_duration = rcdb_entry.get("duration_seconds")
        rcdb_prescales = rcdb_entry.get("prescales") or {}
        if isinstance(rcdb_prescales, str):
            rcdb_prescales = json.loads(rcdb_prescales)

        rcdb_valid = rcdb_entry.get("is_valid_run_end")
        
    rows.append([runnum, rf_duration, rcdb_ebeam, rcdb_ibeam, rcdb_target, rcdb_hms_p, rcdb_hms_th, rcdb_shms_p, rcdb_shms_th, rcdb_duration, rcdb_ps1, rcdb_ps2, rcdb_ps3, rcdb_ps4, rcdb_ps5, rcdb_ps6, rcdb_valid])

df = pd.DataFrame(rows, columns=["runnum", "rf_duration", "rcdb_ebeam", "rcdb_ibeam", "rcdb_target", "rcdb_hms_p", "rcdb_hms_th", "rcdb_shms_p", "rcdb_shms_th", "rcdb_duration", "rcdb_ps1", "rcdb_ps2", "rcdb_ps3", "rcdb_ps4", "rcdb_ps5", "rcdb_ps6", "rcdb_valid"])

#DEBUGGING
# print("DF duplicates:")
# print(df[df["runnum"].duplicated(keep=False)].sort_values("runnum"))

# print("DF rows:", len(df))
# print("DF unique runnum:", df["runnum"].nunique())

df2 = runlist.merge(df, left_on="run", right_on="runnum", how="outer", indicator=True, suffixes=("_rlist", "_repfile"))

#DEBUGGING
# print("\nAfter merge:")
# print("df2 rows:", len(df2))
# print("df2 unique runs:", df2["run"].nunique())

# print("\nDuplicate runs after merge:")
# print(df2[df2["run"].duplicated(keep=False)].sort_values("run"))

df2["run"] = df2["run"].fillna(df2["runnum"]).astype(int)

target_dict = {"Loop 2 10cm": "LH2",
               "10cm Dummy": "Dummy",
               "Loop 1 10cm": "LD2",
               "Carbon 3%": "C",
               "Copper 6%": "Cu",
               "Aluminum 1.5%": "Al",
               "Out of Beam": "NONE"}

comp = df2.copy()

comp["status"] = ""

# If runs exist in only one of rcdb json and the runlist, check the following,
comp.loc[comp["_merge"] == "left_only", "status"] += "CHECK_RCDB,"
comp.loc[comp["_merge"] == "right_only", "status"] += "CHECK_MISSING_REPLAY,"

# When information is there for both rcdb json and the runlist, check the following,
both = comp["_merge"] == "both"
rcdb_missing = (comp["rcdb_ebeam"].isna() |
                comp["rcdb_ibeam"].isna() |
                comp["rcdb_target"].isna() |
                comp["rcdb_hms_p"].isna() |
                comp["rcdb_hms_th"].isna() |
                comp["rcdb_shms_p"].isna() |
                comp["rcdb_shms_th"].isna())
comp.loc[both & rcdb_missing, "status"] += "RCDB_MISSING_INFO,"
both = (comp["_merge"] == "both") & (~rcdb_missing)

ebeam_tolerance = 0.01 # percent
comp.loc[both, "ebeam_rat"] = comp.loc[both, "ebeam"] * 1000 / comp.loc[both, "rcdb_ebeam"]
comp.loc[both & (abs(1 - abs(comp["ebeam_rat"])) > ebeam_tolerance ), "status"] += "CHECK_EBEAM,"

ibeam_tolerance = 8.0  #uA
comp.loc[both, "ibeam_comp"] = comp.loc[both, "current"] - comp.loc[both, "rcdb_ibeam"]
comp.loc[both & (abs(comp["ibeam_comp"]) > ibeam_tolerance), "status"] += "CHECK_CURRENT,"

hms_p_tolerance = 0.01
comp.loc[both, "hms_p_rat"] = comp.loc[both, "hms_p"] / comp.loc[both, "rcdb_hms_p"]
comp.loc[both & (abs(1-abs(comp["hms_p_rat"])) > hms_p_tolerance), "status"] += "CHECK_HMS_P,"

hms_th_tolerance = 0.01
comp.loc[both, "hms_th_rat"] = comp.loc[both, "hms_th"] / comp.loc[both, "rcdb_hms_th"]
comp.loc[both & (abs(1-abs(comp["hms_th_rat"])) > hms_th_tolerance), "status"] += "CHECK_HMS_TH,"

shms_p_tolerance = 0.01
comp.loc[both, "shms_p_rat"] = comp.loc[both, "shms_p"] / comp.loc[both, "rcdb_shms_p"]
comp.loc[both & (abs(1-abs(comp["shms_p_rat"])) > shms_p_tolerance), "status"] += "CHECK_SHMS_P,"

shms_th_tolerance = 0.01
comp.loc[both, "shms_th_rat"] = comp.loc[both, "shms_th"] / comp.loc[both, "rcdb_shms_th"]
comp.loc[both & (abs(1-abs(comp["shms_th_rat"])) > shms_th_tolerance), "status"] += "CHECK_SHMS_TH,"

# This is logic for checking prescales.  They have to match exactly.
for i in range(1, 7):
    comp[f"dps{i}"] = comp[f"ps{i}"] - comp[f"rcdb_ps{i}"]
    comp.loc[both & (comp[f"dps{i}"] != 0), "status"] += f"CHECK_PS{i},"

# This is logic for checking target.  They have to match exactly.
comp["rcdb_target_mapped"] = comp["rcdb_target"].map(target_dict)
comp.loc[both & (comp["rcdb_target_mapped"] != comp["target"]), "status"] += "CHECK_TARGET,"

# This is logic for checking duration.
duration_tolerance = 0.10
comp.loc[both, "duration_rat"] = comp.loc[both, "rf_duration"] / comp.loc[both, "rcdb_duration"]
comp.loc[both & (abs(1-abs(comp["duration_rat"])) > duration_tolerance), "status"] += "DURATION_MISMATCH,"

# Adding logic here to check run type
comp["num_active_ps"] = 0
for i in range(1, 7):
    comp.loc[comp[f"rcdb_ps{i}"] != -1, "num_active_ps"] +=1
comp.loc[both & (comp["num_active_ps"] > 1), "status"] += "CHECK_MULTIPLE_PS_USED,"

comp["run_type_check"] = ""
mask = both & (comp["num_active_ps"] == 1) & ((comp["rcdb_ps1"] != -1) | (comp["rcdb_ps2"] !=-1))
comp.loc[mask, "run_type_check"] = "SHMSDIS"
comp.loc[mask & (abs(comp["rcdb_shms_p"] - (-5.52)) < 0.01), "run_type_check"] = "HEE"
comp.loc[mask & (abs(comp["rcdb_shms_p"] - (-7.07)) < 0.01), "run_type_check"] = "HEE"

mask = both & (comp["num_active_ps"] == 1) & ((comp["rcdb_ps3"] != -1) | (comp["rcdb_ps4"] !=-1))
comp.loc[mask, "run_type_check"] = "HMSDIS"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (-5.39)) < 0.01), "run_type_check"] = "HEE"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (-3.70)) < 0.01), "run_type_check"] = "HEE"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (-3.318)) < 0.01), "run_type_check"] = "HEE"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (-5.44)) < 0.01), "run_type_check"] = "HEE"

mask = both & (comp["num_active_ps"] == 1) & ((comp["rcdb_ps5"] != -1) | (comp["rcdb_ps6"] !=-1))
comp.loc[mask & (comp["rcdb_shms_p"] > 0), "run_type_check"] = "PI+SIDIS"
comp.loc[mask & (comp["rcdb_shms_p"] < 0), "run_type_check"] = "PI-SIDIS"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (1.67)) < 0.01) & (abs(comp["rcdb_shms_p"] - (-5.52)) < 0.01), "run_type_check"] = "HEEP"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (-3.7)) < 0.01) & (abs(comp["rcdb_shms_p"] - (3.61)) < 0.01), "run_type_check"] = "HEEP"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (-3.318)) < 0.01) & (abs(comp["rcdb_shms_p"] - (4.01)) < 0.01), "run_type_check"] = "HEEP"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (2.28)) < 0.01) & (abs(comp["rcdb_shms_p"] - (-7.07)) < 0.01), "run_type_check"] = "HEEP"
comp.loc[mask & (abs(comp["rcdb_hms_p"] - (-5.44)) < 0.01) & (abs(comp["rcdb_shms_p"] - (3.99)) < 0.01), "run_type_check"] = "HEEP"

comp.loc[both & (comp["run_type_check"] != "") & (comp["run_type"] != comp["run_type_check"]), "status"] += "CHECK_RUN_TYPE,"

# Reading in the exceptions here
for run, info in exceptions.items():
    mask = comp["run"] == run
    for check in info["checks"]:
        comp.loc[mask, "status"] = (comp.loc[mask, "status"].str.replace(check + ",", "", regex=False))

comp.to_csv(outfile, index=False)

print("\nTOLERANCES")
print("-" * 60)
print(f"Beam energy ratio tolerance: {ebeam_tolerance:.3f}")
print(f"Beam current difference tolerance: {ibeam_tolerance:.1f} uA")
print(f"HMS momentum ratio tolerance: {hms_p_tolerance:.3f}")
print(f"HMS angle ratio tolerance: {hms_th_tolerance:.3f}")
print(f"SHMS momentum ratio tolerance: {shms_p_tolerance:.3f}")
print(f"SHMS angle ratio tolerance: {shms_th_tolerance:.3f}")
print(f"Run duration ratio tolerance: {duration_tolerance:.2f}")
print(f"Target: Exact match")
print(f"Prescales: Exact match")

minor_warn = ["RCDB_MISSING_INFO", "CHECK_CURRENT", "CHECK_RCDB", "DURATION_MISMATCH"]
print("\nMINOR WARNINGS")
print("-" * 60)

minor_warn = ["RCDB_MISSING_INFO",
              "CHECK_CURRENT",
              "CHECK_RCDB",
              "DURATION_MISMATCH",]

for check in minor_warn:
    runs = []

    for _, row in comp.iterrows():
        if check in row["status"]:
            runs.append(str(row["run"]))

    if runs:
        print(f"\n{check}:")
        print(", ".join(runs))

minor_count = comp["status"].apply(lambda s: any(check in s for check in minor_warn)).sum()
minor_pct = 100 * minor_count / len(comp)

print("\nKNOWN EXCEPTIONS")
print("-" * 60)

if exceptions:
    for run, info in sorted(exceptions.items()):
        print(f"Run {run}: {', '.join(info['checks'])} ({info['reason']})")
else:
    print("None")

print("\nSEVERE WARNINGS")
print("-" * 60)
for _, row in comp.iterrows():
    if row["status"] and not any(check in row["status"] for check in minor_warn):
        print(f"☢️  Run {row['run']}: {row['status']}")
severe_count = comp["status"].apply(lambda s: s != "" and not any(check in s for check in minor_warn)).sum()
if not severe_count:
    print("None")
severe_pct = 100 * severe_count / len(comp)

print("\n")
print("*" * 60)
print("SUMMARY")
print("*" * 60)
print(f"Total runs checked: {len(comp)}")
print(f"Runs with minor warnings: {minor_count} ({minor_pct:.1f}%)")
print(f"Runs with severe warnings: {severe_count} ({severe_pct:.1f}%)")


