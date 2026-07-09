# compare_runs.py
def read_run_list(file_path):
    """Read a text file with one run number per line and return a set of runs."""
    with open(file_path, 'r') as f:
        # Strip whitespace and ignore empty lines
        return {line.strip() for line in f if line.strip()}

def compare_runs(left_file, right_file, output_file):
    """Find runs in left_file but not in right_file and save to output_file."""
    left_runs = read_run_list(left_file)
    right_runs = read_run_list(right_file)

    diff_runs = sorted(left_runs - right_runs)  # runs only in left

    with open(output_file, 'w') as f:
        for run in diff_runs:
            f.write(run + '\n')

    print(f"✅ Found {len(diff_runs)} runs in {left_file} but not in {right_file}. Saved to {output_file}.")

if __name__ == "__main__":
    # Example usage
    left_file = "prob_runs_from_092925.txt"
    right_file = "prob_runs_from_092525.txt"
    output_file = "prob_runs_after_readback_comp.txt"

    compare_runs(left_file, right_file, output_file)
