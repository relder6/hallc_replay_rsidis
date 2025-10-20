import csv
import pandas as pd

def load_targets(filename):
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None

def get_target_spec(encoder, targets_df):
    tolerance = 50000
    result = targets_df[(targets_df['BDSpos'] - encoder).abs() < tolerance]
    if not result.empty:
        return result[['name', 'mass', 'BDSpos']].iloc[0].to_dict()
    return {'name': 'UNKNOWN', 'mass': 0.0, 'BDSpos': None}

def get_BDSpos(name, targets_df):
    result = targets_df[targets_df['name'] == name]
    if not result.empty:
        return result['BDSpos'].iloc[0]
    return None

def get_target_by_name(name, targets_df):
    result = targets_df[targets_df['name'] == name]
    if not result.empty:
        return result[['name', 'mass', 'BDSpos']].iloc[0].to_dict()
    return None

def main():
    targets_df = load_targets('target_info.csv')
    if targets_df is not None:
        encoder = 31648860
        target_spec = get_target_spec(encoder, targets_df)
        print(target_spec)

        name = 'LD2'
        BDSpos = get_BDSpos(name, targets_df)
        print(BDSpos)

        target = get_target_by_name(name, targets_df)
        print(target)

if __name__ == "__main__":
    main()
