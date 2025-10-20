import json
import pandas as pd
from pathlib import Path

def read_json_file(json_path):
    """Load a JSON file into a Python dict."""
    with open(json_path, "r") as f:
        return json.load(f)

def check_run(run_data, nominal_df, key_mapping, ratio_tol=(0.99, 1.1), diff_tol=1.0):
    """
    Compare specified JSON keys to specified CSV columns.

    Parameters:
        run_data (dict): Parsed JSON for one run.
        nominal_df (DataFrame): Nominal values.
        key_mapping (dict): {json_key: csv_column}
        ratio_tol (tuple): Ratio tolerance range.
        diff_tol (float): Max-min tolerance.
    """
    errors = []
    avg_zero_flag = False
    value_undefined_flag = False

    # Normalize run number for matching
    run_number = int(float(run_data.get("RunNumber", -1)))
    nominal_df["run"] = nominal_df["run"].apply(lambda x: int(float(x)))

    # Get nominal row
    nominal_row = nominal_df[nominal_df["run"] == run_number]
    nominal_row = nominal_row.iloc[0] if not nominal_row.empty else {}

    # Loop over mapping
    for json_key, csv_col in key_mapping.items():
        if json_key not in run_data:
            errors.append(f"{json_key}: Key missing in JSON.")
            continue

        avg = run_data[json_key].get("average")
        min_val = run_data[json_key].get("minimum")
        max_val = run_data[json_key].get("maximum")

        # Ratio check only if nominal exists
        if csv_col in nominal_row:
            nominal = nominal_row[csv_col]
            if nominal != 0:
                ratio = avg / nominal
                if not (ratio_tol[0] <= ratio <= ratio_tol[1]):
                    #errors.append(f"{json_key}: obs/nom = {ratio:.3f}.")
                    errors.append(f"{json_key}: obs/nom = {ratio:.3f}. avg = {avg}.")                    
            else:
                errors.append(f"{json_key}: Nominal value is zero, cannot compute ratio.")
        else:
            errors.append(f"{json_key}: Nominal value missing in CSV column '{csv_col}'.")

        # Max-min check
        if min_val is not None and max_val is not None:
            if abs(max_val - min_val) > diff_tol:
                #errors.append(f"{json_key}: abs(Max-Min) = {abs(max_val - min_val):.3f}.")
                errors.append(f"{json_key}: abs(Max-Min) = {abs(max_val - min_val):.3f}. avg = {avg}")                

        # Zero-average check
        if avg == 0:
            avg_zero_flag = True
        if avg == -999:
            value_undefined_flag = True

    # Condense error messages for special flags
    if avg_zero_flag:
        errors = ["Average value is 0. Likely no EPICS entry in the data stream."]
    if value_undefined_flag:
        errors = ["Average value is -999. Likely undefined output from myData."]

    return (len(errors) == 0, errors)

def process_runs(json_dir, nominal_csv, output_csv, key_mapping, ratio_tol=(0.99, 1.1), diff_tol=1.0):
    """
    Process multiple JSON files and write summary for failing runs.

    Parameters:
        json_dir (str or Path): Directory containing JSON files.
        nominal_csv (str or Path): CSV with run-specific nominal values.
        output_csv (str): Path to save summary of failing runs.
        key_mapping (dict): Mapping of {json_key: csv_column}.
        ratio_tol (tuple): Ratio tolerance range.
        diff_tol (float): Max-min tolerance.
    """
    nominal_df = pd.read_csv(nominal_csv)
    results = []

    for json_file in sorted(Path(json_dir).glob("*.json")):
        run_data = read_json_file(json_file)
        passed, errors = check_run(run_data, nominal_df, key_mapping, ratio_tol, diff_tol)
        if not passed:
            results.append({
                "RunNumber": int(float(run_data.get("RunNumber", -1))),
                "Errors": "; ".join(errors)
            })

    if results:
        df_out = pd.DataFrame(results).sort_values(by="RunNumber").reset_index(drop=True)
        df_out.to_csv(output_csv, index=False)
        print(f"⚠️ Found {len(results)} failing runs. Summary saved to {output_csv}")
    else:
        print("✅ All runs passed the checks.")

# Example usage
if __name__ == "__main__":

    # -----------------------------------------    
    # **** Target BDS Position Comp. Block ****
    # ****     Uncomment the following     ****
    # -----------------------------------------

    # Mapping JSON keys to CSV columns
    key_mapping = {
        "hcBDSPOS": "BDSpos",
    }

    process_runs(
        json_dir="per_run_epics_readback_values_from_archiver",
        nominal_csv="target_check/rsidis_nominal_target_BDSpos_100625.csv",
        output_csv="tgt_BDS_failing_runs_epics_archiver_100625.csv",
        # json_dir="per_run_epics_readback_values_from_datastream",
        # nominal_csv="target_check/rsidis_nominal_target_BDSpos_100625.csv",
        # output_csv="tgt_BDS_failing_runs_epics_datastream_100625.csv",
        key_mapping=key_mapping,
        ratio_tol=(0.99, 1.01),
        diff_tol=50000
    )

    # -----------------------------------------    
    # **** Magnet Current Comparison Block ****
    # ****     Uncomment the following     ****
    # -----------------------------------------
    
    # # Mapping JSON keys to CSV columns
    # key_mapping = {
    #     # "ecDI_B_True_NMR": "ecDI_B_Set_NMR",
    #     "ecDI_I_coarse": "ecDI_Set_Current",
    #     "ecQ1_I_coarse": "ecQ1_Set_Current",
    #     "ecQ2_I_coarse": "ecQ2_Set_Current",
    #     "ecQ3_I_coarse": "ecQ3_Set_Current",
    #     "ecSHB_I_coarse": "ecSHB_Set_Current",
    #     "ecSDI_I_coarse": "ecSDI_Set_Current",
    #     "ecSQ1_I_coarse": "ecSQ1_Set_Current",
    #     "ecSQ2_I_coarse": "ecSQ2_Set_Current",
    #     "ecSQ3_I_coarse": "ecSQ3_Set_Current"
    #     # "ecQ1_Set_Current": "ecQ1_Set_Current",
    #     # "ecQ2_Set_Current": "ecQ2_Set_Current",
    #     # "ecQ3_Set_Current": "ecQ3_Set_Current",
    #     # "ecSHB_Set_Current": "ecSHB_Set_Current",
    #     # "ecSQ1_Set_Current": "ecSQ1_Set_Current",
    #     # "ecSQ2_Set_Current": "ecSQ2_Set_Current",
    #     # "ecSQ3_Set_Current": "ecSQ3_Set_Current",
    #     # "ecSDI_Set_Current": "ecSDI_Set_Current"        
    # }

    # process_runs(
    #     json_dir="per_run_epics_readback_values_from_archiver",
    #     nominal_csv="updated_rsidis_nominal_mag_currs_092625.csv",
    #     output_csv="failing_runs_epics_archiver_092925_including_NMR.csv",
    #     # json_dir="per_run_epics_readback_values_from_datastream",
    #     # nominal_csv="updated_rsidis_nominal_mag_currs_092625.csv",
    #     # output_csv="failing_runs_epics_datastream_092925.csv",                
    #     key_mapping=key_mapping,
    #     ratio_tol=(0.99, 1.01),
    #     diff_tol=1.0
    # )    
