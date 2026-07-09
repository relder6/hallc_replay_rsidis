# Reads two CSV files.
# Matches rows based on user given indices in both files.
# Compares a user-configurable list of common variables (e.g., ["hms_p", "shms_p"]).
# If any variable mismatch occurs → write a fail log 

import pandas as pd

def compare_csvs(left_csv, right_csv, run_col_left, run_col_right, variables, faillog_path):
    # Read both CSV files
    left_df = pd.read_csv(left_csv)
    right_df = pd.read_csv(right_csv)

    # Ensure run columns are integers for matching
    left_df[run_col_left] = left_df[run_col_left].astype(int)
    right_df[run_col_right] = right_df[run_col_right].astype(int)

    faillog_entries = []

    # Loop through runs in left_df
    for _, left_row in left_df.iterrows():
        run_number = left_row[run_col_left]

        # Find matching run in right_df
        match = right_df[right_df[run_col_right] == run_number]
        if match.empty:
            faillog_entries.append(f"{run_number},Run not found in right table")
            continue

        right_row = match.iloc[0]
        mismatches = []

        # Compare variables
        for var in variables:
            if var not in left_df.columns or var not in right_df.columns:
                mismatches.append(f"{var} : Missing in one of the tables")
                continue

            left_val = left_row[var]
            right_val = right_row[var]

            # Compare with tolerance for floats
            try:
                if pd.isna(left_val) or pd.isna(right_val) or float(left_val) != float(right_val):
                    mismatches.append(f"{var} : left = {left_val} right = {right_val}")
            except ValueError:
                # Non-numeric comparison
                if str(left_val) != str(right_val):
                    mismatches.append(f"{var} : left = {left_val} right = {right_val}")

        if mismatches:
            faillog_entries.append(f"{run_number}," + "; ".join(mismatches))

    # Save fail log
    with open(faillog_path, "w") as f:
        f.write("run,message\n")
        for entry in faillog_entries:
            f.write(entry + "\n")

    print(f"✅ Fail log saved to {faillog_path}")


if __name__ == "__main__":
    # Example usage
    left_csv =  "merged_run_start_stop_log.csv"  # First file
    right_csv = "/home/cdaq/rsidis-2025/users/pdbforce/hallc_replay_rsidis/AUX_FILES/parsed_runlist.csv" # Second file
    index_col_left = "run_number"
    index_col_right = "run"
    variables_to_compare = ["hms_p", "shms_p"]  # User-configurable
    faillog_path = "compare_csv_vars.faillog"

    compare_csvs(left_csv, right_csv, index_col_left, index_col_right, variables_to_compare, faillog_path)
