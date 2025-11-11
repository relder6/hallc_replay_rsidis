import csv
import os

def hms_dir(run_number):
    return f"/work/hallc/c-rsidis/replay/pass0/REPORT_OUTPUT/HMS/PRODUCTION/replay_hms_coin_production_{run_number}_-1.report"

def shms_dir(run_number):
    return f"/work/hallc/c-rsidis/replay/pass0/REPORT_OUTPUT/SHMS/PRODUCTION/replay_shms_coin_production_{run_number}_-1.report"

def coin_dir(run_number):
    return f"/work/hallc/c-rsidis/replay/pass0/REPORT_OUTPUT/COIN/PRODUCTION/replay_coin_production_{run_number}_-1.report"

# Mapping: variable -> (line_index, char_start, char_end)
HMS_MAP = {
    "BCM1_Q": (36,22,32),
    "BCM1_I": (29,22,29),
    "BCM2_Q": (37,22,32),
    "BCM2_I": (30,22,29),
    "BCM4A_Q": (38,22,32),
    "BCM4A_I": (31,23,29),
    "BCM4B_Q": (39,22,32),
    "BCM4B_I": (32,23,29),
    "BCM4C_Q": (40,22,32),
    "BCM4C_I": (33,23,29),
    "h_esing_Eff": (336,37,43),
    "h_hadron_Eff": (337,37,43),
    "ps1" : (47,12,15),
    "ps2" : (48,12,15),
    "ps3" : (49,12,15),
    "ps4" : (50,12,15),
    "ps5" : (51,12,15),
    "ps6" : (52,12,15),
    "pTRIG3" : (111,10,20),
    "pTRIG4" : (112,10,18),
    "phys_triggers": (78,32,41),
    "hEL_REAL": (87,11,19),
    "electr_deadtime": (160,42,50),
}

SHMS_MAP = {
    "BCM1_Q": (36,22,31),
    "BCM1_I": (29,22,29),
    "BCM2_Q": (37,22,31),
    "BCM2_I": (30,22,29),
    "BCM4A_Q": (38,22,31),
    "BCM4A_I": (31,23,30),
    "BCM4B_Q": (39,22,31),
    "BCM4B_I": (32,23,30),
    "BCM4C_Q": (40,22,31),
    "BCM4C_I": (33,23,30),
    "p_esing_Eff": (367,35,41),
    "p_hadron_Eff": (368,35,41),
    "ps1" : (47,13,15),
    "ps2" : (48,13,15),
    "ps3" : (49,13,15),
    "ps4" : (50,13,15),
    "ps5" : (51,13,15),
    "ps6" : (52,13,15),
    "pTRIG1" : (106,10,20),
    "pTRIG2" : (107,10,20),
    "phys_triggers": (75,32,41),
    "hEL_REAL": (102,11,21),
    "electr_deadtime": (157,42,50),
}

COIN_MAP = {
    "BCM1_Q": (46,26,33),
    "BCM1_I": (39,26,33),
    "BCM2_Q": (47,26,33),
    "BCM2_I": (40,26,33),
    "BCM4A_Q": (48,26,33),
    "BCM4A_I": (41,27,34),
    "BCM4B_Q": (49,26,33),
    "BCM4B_I": (42,27,34),
    "BCM4C_Q": (50,26,33),
    "BCM4C_I": (43,27,34),
    "h_esing_Eff": (626,36,43),
    "h_hadron_Eff": (627,36,43),
    "p_esing_Eff": (485,35,41),
    "p_hadron_Eff": (486,35,41),
    "ps1" : (89,12,15),
    "ps2" : (90,12,15),
    "ps3" : (91,12,15),
    "ps4" : (92,12,15),
    "ps5" : (93,12,15),
    "ps6" : (94,12,15),
    "phys_triggers": (75,32,41),
    "hEL_REAL": (84,11,19),
    "electr_deadtime": (256,60,68)
}

run_type_map = {
    "HMS": HMS_MAP,
    "SHMS": SHMS_MAP,
    "COIN": COIN_MAP,
}

def parse_report_file(report_path, mapping):
    props = {}
    if not os.path.exists(report_path):
        # If file doesn't exist, return empty dict
        return props

    with open(report_path, "r") as f:
        lines = f.readlines()
        for var, (line_idx, start, end) in mapping.items():
            try:
                segment = lines[line_idx][start:end].strip()
                # Try to convert to float if possible
                props[var] = float(segment)
#                if (var == "ps1" or var == "ps2" or var =="ps3" or var == "ps4" or var == "ps5" or var =="ps6"):
#                    props[var] = segment
            except (IndexError, ValueError):
                props[var] = None
    return props


def find_special_report_file(run_number):
    if os.path.exists(coin_dir(run_number)):
        return coin_dir(run_number), run_type_map["COIN"]
    elif os.path.exists(hms_dir(run_number)):
        return hms_dir(run_number), run_type_map["HMS"]
    else:
        return shms_dir(run_number), run_type_map["SHMS"]


def load_extra_info(run_number, run_type):
#    if run_type in ("PI-SIDIS", "PI+SIDIS", "HOLE", "HEEP"):

    # Load extra variables from output_get_good_coin_ev_<run>.csv
    
    extra_path = f"/work/hallc/c-rsidis/cmorean/replay_pass0a/REPORT_OUTPUT/COIN/PRODUCTION/output_get_good_coin_ev_{run_number}_-1.csv"
    keep_cols = ["coin", "randoms", "ransubcoin", "normyield", "normyield_err" ,"ctmean", "ctsigma"]

    if not os.path.exists(extra_path):
        # If file not found, return -999 placeholders
        print(f"file get_good_coin_events for run: {run_number} not found - {run_type} run")
        return {col: -999 for col in keep_cols}
        
    with open(extra_path, newline="") as f:
        reader = csv.DictReader(f)
        try:
            row = next(reader)  # should only be one row
            return {col: float(row[col]) for col in keep_cols}
        except (StopIteration, KeyError, ValueError):
            # If empty or malformed, return -999 placeholders
            return {col: -999 for col in keep_cols}


def load_fan_data(run_number, fan_csv_path):
    
#    Reads fan_freq.csv and r eturns mean and stdev for the given run_number.

    import csv
    if not os.path.exists(fan_csv_path):
        return {"fan_mean": -999, "fan_stdev": -999}

    with open(fan_csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if str(row["run"]) == str(run_number):
                try:
                    return {
                        "fan_mean": float(row.get("mean", -999)),
                        "fan_stdev": float(row.get("stdev", -999))
                    }
                except ValueError:
                    return {"fan_mean": -999, "fan_stdev": -999}

    # If run not found
    return {"fan_mean": -999, "fan_stdev": -999}

def load_ihwp_table(ihwp_csv_path):
    ihwp_map = {}
    if not os.path.exists(ihwp_csv_path):
        print(f"⚠️ IHWP file not found: {ihwp_csv_path}")
        return ihwp_map

    with open(ihwp_csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            run = row.get("run_number")
            if run:
                ihwp_map[str(run)] = {
                    "IHWP": row.get("IHWP", ""),
                    "start_time": row.get("start_time", ""),
                    "stop_time": row.get("stop_time", "")
                }
    return ihwp_map


# === New Kinematic Conversion Table ===
KINEMATIC_TABLE = [
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.9, "thpq": 2.0,   "hms_p": 1.531, "hms_th": 29.045, "shms_p": 6.538, "shms_th": 7.865},
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.67, "thpq": 2.0,   "hms_p": 1.531, "hms_th": 29.045, "shms_p": 4.868, "shms_th": 7.865},
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.67, "thpq": 5.2, "hms_p": 1.531, "hms_th": 29.045, "shms_p": 4.868, "shms_th": 11.075},
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.67, "thpq": 8.5, "hms_p": 1.531, "hms_th": 29.045, "shms_p": 4.868, "shms_th": 14.375},
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.5,  "thpq": 2.0,   "hms_p": 1.531, "hms_th": 29.045, "shms_p": 3.632, "shms_th": 7.865},
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.5,  "thpq": 5.2, "hms_p": 1.531, "hms_th": 29.045, "shms_p": 3.632, "shms_th": 11.075},
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.5,  "thpq": 8.5, "hms_p": 1.531, "hms_th": 29.045, "shms_p": 3.632, "shms_th": 14.375},
    {"ebeam": 8.5831, "x": 0.25, "Q2": 3.3, "z": 0.36, "thpq": 2.0,   "hms_p": 1.531, "hms_th": 29.045, "shms_p": 2.615, "shms_th": 7.865},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.9,  "thpq": -0.8, "hms_p": 3.642, "hms_th": 16.75, "shms_p": 6.538, "shms_th": 7.51},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.9,  "thpq": 2.0,    "hms_p": 3.642, "hms_th": 16.75, "shms_p": 6.538, "shms_th": 10.305},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.67, "thpq": 2.0,    "hms_p": 3.642, "hms_th": 16.75, "shms_p": 4.868, "shms_th": 10.305},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.67, "thpq": -0.8, "hms_p": 3.642, "hms_th": 16.75, "shms_p": 4.868, "shms_th": 7.51},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.5,  "thpq": -0.8, "hms_p": 3.642, "hms_th": 16.75, "shms_p": 3.632, "shms_th": 7.51},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.5,  "thpq": 2.0,    "hms_p": 3.642, "hms_th": 16.75, "shms_p": 3.632, "shms_th": 10.305},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.5,  "thpq": 5.2,  "hms_p": 3.642, "hms_th": 16.75, "shms_p": 3.632, "shms_th": 13.505},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.5,  "thpq": 8.5,  "hms_p": 3.642, "hms_th": 16.75, "shms_p": 3.632, "shms_th": 16.81},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.36, "thpq": 2.0,    "hms_p": 3.642, "hms_th": 16.75, "shms_p": 2.615, "shms_th": 10.305},
    {"ebeam": 10.6716, "x": 0.25, "Q2": 3.3, "z": 0.36, "thpq": -0.2,    "hms_p": 3.642, "hms_th": 16.75, "shms_p": 3.632, "shms_th": 8.11},
]


def find_kinematics(ebeam, hms_p, hms_th, shms_p, shms_th, tol=0.01):
    
    # Returns matching (x, Q2, z, thpq) for the given kinematic settings.
    
    for row in KINEMATIC_TABLE:
        if (
            abs(row["ebeam"] - abs(float(ebeam))) < tol and
            abs(row["hms_p"] - abs(float(hms_p))) < tol and
            abs(row["hms_th"] - abs(float(hms_th))) < tol and
            abs(row["shms_p"] - abs(float(shms_p))) < tol and
            abs(row["shms_th"] - abs(float(shms_th))) < tol
        ):
            return {
                "x": row["x"],
                "Q2": row["Q2"],
                "z": row["z"],
                "thpq": row["thpq"]
            }
    return {"x": -999, "Q2": -999, "z": -999, "thpq": -999}

def compute_corr_coeff(f, I):
    # Fit coefficients:
    alpha2, alpha1, alpha0 = -4.63644107e-06, 1.30424412e-04, 7.98013139e-05
    beta2, beta1, beta0 = 4.37559009e-04, -1.09899399e-02, -5.56375520e-03
    gamma2, gamma1, gamma0 = -9.31940585e-03, 1.15703945e-01, 1.43953881e+02

    if any(v in (-999, None) for v in [f, I]):
        return -999

    try:
        Y_fI = ((alpha2*I**2 + alpha1*I + alpha0)*f**2 +
                (beta2*I**2 + beta1*I + beta0)*f +
                (gamma2*I**2 + gamma1*I + gamma0))
        Y_f0 = (alpha0*f**2 + beta0*f + gamma0)
        if Y_fI == 0:
            return -999
        return round(Y_f0 / Y_fI, 6)
    except Exception:
        return -999



def collect_run_info(input_csv, output_csv, run_type_map):
    keep_columns = ["run", "ebeam", "target", "hms_p", "hms_th", "shms_p", "shms_th", "run_type"] 
    results = []

    ihwp_map = load_ihwp_table("updated_merged_run_start_stop_log_100625.csv")

    with open(input_csv, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            run_number = row["run"]
            run_type = row["run_type"]

            # Figure out report path depending on run type
            if run_type in ("PI-SIDIS", "PI+SIDIS", "HOLE", "HEEP"):
                report_path = coin_dir(run_number)
                mapping = run_type_map["COIN"]
            elif run_type == ("HMSDIS" or "HEE"):
                report_path = hms_dir(run_number)
                mapping = run_type_map["HMS"]
            elif run_type == "SHMSDIS":
                report_path = shms_dir(run_number)
                mapping = run_type_map["SHMS"]
            else:
                report_path, mapping = find_special_report_file(run_number)

            # Extract variables
            props = {}
            if report_path and os.path.exists(report_path):
                props = parse_report_file(report_path, mapping)

                if mapping is run_type_map["COIN"]:
                    props["comp_livetime"] = 1.0
                else:
                    phys_triggers = props.get("phys_triggers")
                    ps1, ps2, ps3, ps4, ps5, ps6 = props.get("ps1"), props.get("ps2"), props.get("ps3"), props.get("ps4"), props.get("ps5"), props.get("ps6")
                    ps_values = [props.get(f"ps{i}", 1) for i in range(1, 7)]
                    pTRIG1 = props.get("pTRIG1")
                    pTRIG2 = props.get("pTRIG2")
                    pTRIG3 = props.get("pTRIG3")
                    pTRIG4 = props.get("pTRIG4")

                    props["comp_livetime"] = -999

                    if phys_triggers not in (None, -999):

                        ps_product = 1
                        for ps in ps_values:
                            if ps in (None,-999):
                                ps = 1
                            ps_product *= ps

                        # Determine livetime based on spectrometer type
                        if mapping is run_type_map["HMS"]:
                            if pTRIG3 and ps3 > 0:
                                props["comp_livetime"] = round((-1 * ps_product * phys_triggers) / pTRIG3, 5)
                            elif pTRIG4 and ps4 > 0:
                                props["comp_livetime"] = round((-1 * ps_product * phys_triggers) / pTRIG4, 5)

                        elif mapping is run_type_map["SHMS"]:
                            if pTRIG1 and ps1 > 0:
                                props["comp_livetime"] = round((-1 * ps_product * phys_triggers) / pTRIG1, 5)
                            elif pTRIG2 and ps2 > 0:
                                props["comp_livetime"] = round((-1 * ps_product * phys_triggers) / pTRIG2, 5)

                        if props["comp_livetime"] > 1:
                            props["comp_livetime"] = 1.0


                if mapping is run_type_map["HMS"]:
                    props["pEff"] = -999
                if mapping is run_type_map["SHMS"]:
                    props["hEff"] = -999
            else:
                if report_path:  # file path expected but missing
                    print(f"⚠️ Report file not found: {report_path}")
                props = {var: -999 for var in mapping.keys()}

            # Load extra info from output_get_good_coin_ev
            extra_props = load_extra_info(run_number,run_type)
            props.update(extra_props)

            # Load fan speed table
            fan_props = load_fan_data(run_number, "fan_freq_pass0.csv") 
            props.update(fan_props)

            # Merge input row with extracted props
            merged = {col: row[col] for col in keep_columns if col in row}
            merged.update(props)

            # Include IHWP value
            #merged["IHWP"] = ihwp_map.get(str(run_number), "")

            ihwp_info = ihwp_map.get(str(run_number),{})
            merged["IHWP"]=ihwp_info.get("IHWP",-999)
            merged["start_time"] = ihwp_info.get("start_time", -999)
            merged["stop_time"] = ihwp_info.get("stop_time", -999)

            kin = find_kinematics(
                float(row["ebeam"]),
                float(row["hms_p"]),
                float(row["hms_th"]),
                float(row["shms_p"]),
                float(row["shms_th"]),
            )
            merged.update(kin)

            # Include fan speed and boiling corrections for LH2 and only boiling correction for LD2
            f = merged.get("fan_mean", -999)
            I = merged.get("BCM2_I", -999)
            target = merged.get("target", "")
            
            if target == "LH2":
                merged["boil_corr"] = compute_corr_coeff(f,I)
            elif target == "LD2":
                 merged["boil_corr"] = round(1 + 0.03493 * (I / 100), 6)
            else:
                merged["boil_corr"] = 1.0
   
            results.append(merged)

            

    # Write results to CSV
    fieldnames = keep_columns + ["x","Q2","z","thpq","BCM1_Q","BCM1_I","BCM2_Q","BCM2_I","BCM4A_Q","BCM4A_I","BCM4B_Q","BCM4B_I","BCM4C_Q","BCM4C_I","h_esing_Eff","h_hadron_Eff","p_esing_Eff","p_hadron_Eff","ps1","ps2","ps3","ps4","ps5","ps6","comp_livetime","electr_deadtime",
#get_good_coin_events variables:
"coin", "randoms", "ransubcoin", "normyield", "normyield_err", "ctmean","ctsigma",
#fan speed variables:
"fan_mean", "fan_stdev", "boil_corr",
#start and stop times
"IHWP", "start_time", "stop_time"]

    for row in results:
        for key in fieldnames:
            if key not in row or row[key] in ("", None):
                row[key] = -999

                    
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)





# ========= MAIN =========
if __name__ == "__main__":
    collect_run_info("updated_parsed_runlist_110425.csv", "run_info_pass0.csv", run_type_map)
