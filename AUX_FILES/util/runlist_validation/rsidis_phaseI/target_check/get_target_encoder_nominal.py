import csv
import pandas as pd

def load_targets(filename):
    """
    Loads target data from a CSV file into a Pandas DataFrame.
    
    Args:
        filename (str): The name of the CSV file to load.
    
    Returns:
        pd.DataFrame: The loaded target data.
    """
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

def get_target_spec(name, targets_df):
    """
    Retrieves the target specification for a given target name.
    
    Args:
        name (str): The name of the target.
        targets_df (pd.DataFrame): The DataFrame containing target data.
    
    Returns:
        dict: The target specification, or None if not found.
    """
    result = targets_df[targets_df['name'] == name]
    if not result.empty:
        return result[['name', 'mass', 'BDSpos']].iloc[0].to_dict()
    return None

def process_run_data(run_data_filename, targets_df, output_filename):
    """
    Processes run data from a CSV file, extracting target information and writing it to an output CSV file.
    
    Args:
        run_data_filename (str): The name of the CSV file containing run data.
        targets_df (pd.DataFrame): The DataFrame containing target data.
        output_filename (str): The name of the output CSV file.
    """
    with open(run_data_filename, 'r') as run_data_file:
        reader = csv.DictReader(run_data_file)
        output_data = []
        for row in reader:
            target_name = row['target']
            target_spec = get_target_spec(target_name, targets_df)
            if target_spec is not None:
                output_data.append({
                    'run': row['run'],
                    'target': target_name,
                    'BDSpos': target_spec['BDSpos'],
                    'mass': target_spec['mass']
                })
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(output_filename, index=False)

def main():
    """
    The main entry point of the program.
    """
    targets_df = load_targets('target_info.csv')
    if targets_df is not None:
        process_run_data('/home/cdaq/rsidis-2025/users/pdbforce/hallc_replay_rsidis/AUX_FILES/updated_parsed_runlist_100625.csv', targets_df, 'output.csv')

if __name__ == "__main__":
    main()
