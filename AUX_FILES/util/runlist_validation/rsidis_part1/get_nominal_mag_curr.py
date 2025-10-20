import pandas as pd
import numpy as np
import subprocess
import csv
import re


def read_csv(filename):
    """
    Reads a csv file and returns a pandas dataframe
    """
    df = pd.read_csv(filename)
    return df

def get_hms_magnet_currents(hms_p):
    """
    Runs the go_magnets_HMS_current script with the given HMS momentum (hms_p)
    and returns:
        - Recommended NMR B (Tesla)
        - Corresponds to approx Iset (Amps)
        - Iset values for Q1, Q2, Q3 (Amps)
    """
    try:
        # Run the shell script, pass "n" to stdin to answer the prompt
        process = subprocess.run(
            ["go_magnets_HMS_current", str(hms_p)],
            input="n\n",
            text=True,
            capture_output=True,
            check=True
        )

        output = process.stdout

        # Regex for Recommended NMR B and approx Iset
        nmr_b_match = re.search(r"Recommended NMR B:\s*([\d\.E+-]+)", output)
        approx_iset_match = re.search(r"Corresponds to approx Iset:\s*([\d\.E+-]+)", output)

        # Regex for Q1, Q2, Q3 Iset
        q1_match = re.search(r"Magnet:\s*Q1\s*Iset:\s*([\d\.E+-]+)", output)
        q2_match = re.search(r"Magnet:\s*Q2\s*Iset:\s*([\d\.E+-]+)", output)
        q3_match = re.search(r"Magnet:\s*Q3\s*Iset:\s*([\d\.E+-]+)", output)

        if not (nmr_b_match and approx_iset_match and q1_match and q2_match and q3_match):
            raise ValueError("Could not parse all required values from script output.")

        # Convert to floats
        nmr_b = float(nmr_b_match.group(1))
        approx_iset = float(approx_iset_match.group(1))
        q1_iset = float(q1_match.group(1))
        q2_iset = float(q2_match.group(1))
        q3_iset = float(q3_match.group(1))

        return nmr_b, approx_iset, q1_iset, q2_iset, q3_iset

    except subprocess.CalledProcessError as e:
        print("Error running go_magnets_HMS_current:", e)
        print("stderr:", e.stderr)
        return None
    except Exception as e:
        print("Error parsing magnet currents:", e)
        return None

# def get_hms_magnet_currents(hms_p):
#     """
#     Runs the go_magnets_HMS_current script with the given HMS momentum (hms_p)
#     and returns the Iset values for Q1, Q2, and Q3 as floats.
#     """
#     try:
#         # Run the shell script, pass "n" to stdin to answer the prompt
#         process = subprocess.run(
#             ["go_magnets_HMS_current", str(hms_p)],
#             input="n\n",  # Send "n" and a newline to the script
#             text=True,
#             capture_output=True,
#             check=True
#         )

#         output = process.stdout

#         # Regex to find Iset values for Q1, Q2, Q3
#         q1_match = re.search(r"Magnet:\s*Q1\s*Iset:\s*([\d\.E+-]+)", output)
#         q2_match = re.search(r"Magnet:\s*Q2\s*Iset:\s*([\d\.E+-]+)", output)
#         q3_match = re.search(r"Magnet:\s*Q3\s*Iset:\s*([\d\.E+-]+)", output)

#         if not (q1_match and q2_match and q3_match):
#             raise ValueError("Could not parse Iset values from script output.")

#         q1_iset = float(q1_match.group(1))
#         q2_iset = float(q2_match.group(1))
#         q3_iset = float(q3_match.group(1))

#         return q1_iset, q2_iset, q3_iset

#     except subprocess.CalledProcessError as e:
#         print("Error running go_magnets_HMS_current:", e)
#         print("stderr:", e.stderr)
#         return None
#     except Exception as e:
#         print("Error parsing magnet currents:", e)
#         return None

def get_shms_magnet_currents(shms_p):
    """
    Runs the go_magnets_SHMS_current script with the given SHMS momentum (shms_p)
    and returns the Iset values for HB, Q1, Q2, Q3, and Dipole as floats.
    """
    try:
        # Run the shell script, pass "n" to stdin to answer the prompt
        process = subprocess.run(
            ["go_magnets_SHMS_current", str(shms_p)],
            input="n\n",  # Send "n" to the prompt
            text=True,
            capture_output=True,
            check=True
        )

        output = process.stdout

        # Regex patterns for each magnet
        hb_match      = re.search(r"Magnet:\s*HB.*?Iset:\s*([\d\.E+-]+)", output, re.DOTALL)
        q1_match      = re.search(r"Magnet:\s*Q1.*?Iset:\s*([\d\.E+-]+)", output, re.DOTALL)
        q2_match      = re.search(r"Magnet:\s*Q2.*?Iset:\s*([\d\.E+-]+)", output, re.DOTALL)
        q3_match      = re.search(r"Magnet:\s*Q3.*?Iset:\s*([\d\.E+-]+)", output, re.DOTALL)
        dipole_match  = re.search(r"Magnet:\s*Dipole.*?Iset:\s*([\d\.E+-]+)", output, re.DOTALL)

        if not all([hb_match, q1_match, q2_match, q3_match, dipole_match]):
            raise ValueError("Could not parse all Iset values from SHMS script output.")

        hb_iset     = float(hb_match.group(1))
        q1_iset     = float(q1_match.group(1))
        q2_iset     = float(q2_match.group(1))
        q3_iset     = float(q3_match.group(1))
        dipole_iset = float(dipole_match.group(1))

        return dipole_iset, hb_iset, q1_iset, q2_iset, q3_iset

    except subprocess.CalledProcessError as e:
        print("Error running go_magnets_SHMS_current:", e)
        print("stderr:", e.stderr)
        return None
    except Exception as e:
        print("Error parsing SHMS magnet currents:", e)
        return None

import pandas as pd
import numpy as np

def generate_magnet_csv(runlist_df, runnum, output_csv):
    """
    Processes specified run(s) from a Pandas DataFrame and either:
      - Saves results to a CSV if runnum == -1 (all runs)
      - Prints results to terminal if runnum != -1 (single run)

    Parameters:
        runlist_df (pd.DataFrame): DataFrame containing run info with columns 'run', 'hms_p', 'shms_p'
        runnum (int): Run number to process, or -1 for all runs
        output_csv (str): Path to save the output CSV file (only used if runnum == -1)
    """
    # Ensure DataFrame has required columns
    required_cols = {"run", "hms_p", "shms_p"}
    if not required_cols.issubset(runlist_df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_cols}")

    # Process all runs
    if runnum == -1:
        runs_to_process = runlist_df["run"].tolist()
        all_results = []

        for rnum in runs_to_process:
            row = runlist_df.loc[runlist_df["run"] == rnum]
            if row.empty:
                print(f"Skipping run {rnum}: Not found in DataFrame.")
                continue

            hms_p = float(row.iloc[0]["hms_p"])
            shms_p = float(row.iloc[0]["shms_p"])

            try:
                hms_currs = get_hms_magnet_currents(hms_p)
                shms_currs = get_shms_magnet_currents(shms_p)
                flat_list = np.hstack((int(rnum), hms_p, shms_p, hms_currs, shms_currs)).tolist()
                flat_list[0] = int(flat_list[0])  # Convert first element back to int
                all_results.append(flat_list)
                print(f"Processed run {rnum}")
            except Exception as e:
                print(f"Error processing run {rnum}: {e}")

        # Define header for CSV
        header = ["run", "hms_p", "shms_p",
                  "ecDI_B_Set_NMR","ecDI_Set_Current","ecQ1_Set_Current","ecQ2_Set_Current","ecQ3_Set_Current",
                  "ecSDI_Set_Current","ecSHB_Set_Current","ecSQ1_Set_Current","ecSQ2_Set_Current","ecSQ3_Set_Current"]

        # Save all runs to CSV
        df_out = pd.DataFrame(all_results, columns=header)
        df_out.to_csv(output_csv, index=False)
        print(f"✅ Output saved to {output_csv}")

    # Process single run
    else:
        row = runlist_df.loc[runlist_df["run"] == runnum]
        if row.empty:
            print(f"Run number {runnum} not found in DataFrame.")
            return

        hms_p = float(row.iloc[0]["hms_p"])
        shms_p = float(row.iloc[0]["shms_p"])

        try:
            hms_currs = get_hms_magnet_currents(hms_p)
            shms_currs = get_shms_magnet_currents(shms_p)
            flat_list = np.hstack((int(runnum), hms_p, shms_p, hms_currs, shms_currs)).tolist()
            flat_list[0] = int(flat_list[0])  # Convert first element back to int
            csv_string = ",".join(map(str, flat_list))
            print(csv_string)  # Print CSV-style row to terminal
        except Exception as e:
            print(f"Error processing run {runnum}: {e}")
    
# Example usage:
if __name__ == "__main__":
    runlist = read_csv("/home/cdaq/rsidis-2025/users/pdbforce/hallc_replay_rsidis/AUX_FILES/updated_parsed_runlist.csv")

    generate_magnet_csv(runlist, -1, "updated_rsidis_mag_currs_092625.csv")
    

    # shms_p_value = -7.07
    # currents = get_shms_magnet_currents(shms_p_value)
    # if currents:
    #     print(f"HB Iset: {currents[0]} A")
    #     print(f"Q1 Iset: {currents[1]} A")
    #     print(f"Q2 Iset: {currents[2]} A")
    #     print(f"Q3 Iset: {currents[3]} A")
    #     print(f"Dipole Iset: {currents[4]} A")
        
#     hms_p_value = 2.28
#     currents = get_hms_magnet_currents(hms_p_value)
#     if currents:
#         print(f"Q1 Iset: {currents[0]} A")
#         print(f"Q2 Iset: {currents[1]} A")
#         print(f"Q3 Iset: {currents[2]} A")
