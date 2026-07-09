import json
import pandas as pd
from datetime import datetime
from pathlib import Path


def read_json_file(json_path):
    """Reads a JSON file and returns a Python dictionary."""
    with open(json_path, "r") as f:
        return json.load(f)
    
def parse_time(time_str):
    """
    Convert time of format 'HH:MM:SS MM/DD/YY TZ' to 'YYYY-MM-DD HH:MM:SS'.
    Ignores timezone for duration calculation.
    """
    try:
        dt = datetime.strptime(time_str, "%H:%M:%S %m/%d/%y %Z")
    except ValueError:
        dt = datetime.strptime(time_str, "%H:%M:%S %m/%d/%y")
    return dt

def process_runs(data, run_filter):
    """
    Process only the runs in run_filter from JSON data and return a list of dicts.
    Adds fail log entries for runs in run_filter that are missing in JSON.
    """
    results = []
    fail_log = []
    duration_threshold = 120  # sec

    for run_number in run_filter:
        run_number_int = int(run_number)

        # Check if run exists in JSON
        if str(run_number_int) not in data:
            fail_log.append(f"{run_number_int},missing in RCDB JSON")
            continue

        run_info = data[str(run_number_int)]

        start_str = run_info.get("run_info", {}).get("start_time")
        stop_str = run_info.get("run_info", {}).get("stop_time")
        hwp = run_info.get("beam", {}).get("half_wave_plate", "")
        hms_p = run_info.get("spectrometers", {}).get("hms_momentum", "")
        shms_p = run_info.get("spectrometers", {}).get("shms_momentum", "")

        # Skip runs with no start time at all
        if not start_str:
            fail_log.append(f"{run_number_int},missing start time")
            continue

        # Parse start time
        start_dt = parse_time(start_str)
        start_fmt = start_dt.strftime("%Y-%m-%d %H:%M:%S")

        # Handle stop time if available
        if stop_str:
            stop_dt = parse_time(stop_str)
            stop_fmt = stop_dt.strftime("%Y-%m-%d %H:%M:%S")
            duration_sec = int((stop_dt - start_dt).total_seconds())

            # # Handle very short run
            # if duration_sec <= duration_threshold:
            #     fail_log.append(f"{run_number_int},shorter than {duration_threshold} sec")
        else:
            stop_fmt = "-999"
            duration_sec = "-999"
            fail_log.append(f"{run_number_int},missing stop time")

        results.append({
            "run_number": run_number_int,
            "start_time": start_fmt,
            "stop_time": stop_fmt,
            "duration_seconds": duration_sec,
            "IHWP": hwp,
            "hms_p": hms_p,
            "shms_p": shms_p
        })

    return results, fail_log

def get_runlist(run_list_csv):
    """Reads a list of runs from run list CSV"""
    df = pd.read_csv(run_list_csv)    
    run_list = df["run"].astype(int).tolist()
    return run_list

def save_to_csv(data, output_csv):
    """Save processed run data to CSV."""
    df = pd.DataFrame(data)
    df.sort_values(by="run_number", inplace=True)
    df.to_csv(output_csv, index=False)
    print(f"✅ Output saved to {output_csv}")

def save_to_log(message, output_log):
    """Save processed run fail log to log file."""
    open(output_log, "w").write("\n".join(message) + "\n")
    print(f"✅ Fail log saved to {output_log}")    


def main(json_path, run_list, output_csv):
    """
    Main function to read JSON, process only selected runs, and save CSV.
    
    Parameters:
        json_path (str): Path to JSON file.
        run_list (list[int]): List of run numbers to process.
        output_csv (str): Path to output CSV file.
    """
    data = read_json_file(json_path)
    processed, faillog = process_runs(data, run_list)
    save_to_csv(processed, output_csv)
    output_log = output_csv.replace(".csv", ".faillog")
    save_to_log(faillog, output_log)


# Example usage
if __name__ == "__main__":
    # Example: process only these runs
    runs_to_process = get_runlist("/home/cdaq/rsidis-2025/users/pdbforce/hallc_replay_rsidis/AUX_FILES/parsed_runlist.csv")
    main("rundb_coin.json", runs_to_process, "run_start_stop_log.csv")
