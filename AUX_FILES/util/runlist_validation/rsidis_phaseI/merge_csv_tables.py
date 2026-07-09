import pandas as pd
import sys

def merge_csv(file1, file2, output_file, left_index, right_index, mode="replace"):
    """
    Merge two CSV files based on specified index columns.

    Modes:
    - "replace": right replaces matching rows in left
    - "add": right's columns are added as new columns to left
    """
# Read CSVs
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Ensure index columns exist
    if left_index not in df1.columns:
        raise ValueError(f"Column '{left_index}' not found in {file1}")
    if right_index not in df2.columns:
        raise ValueError(f"Column '{right_index}' not found in {file2}")

    # Force run number columns to string to avoid float issues
    df1[left_index] = df1[left_index].astype(str)
    df2[right_index] = df2[right_index].astype(str)

    if mode == "replace":
        df1.set_index(left_index, inplace=True)
        df2.set_index(right_index, inplace=True)
        df1.update(df2)
        df_combined = pd.concat([df1, df2[~df2.index.isin(df1.index)]])
        df_combined.reset_index(inplace=True)
        df_combined.sort_values(by=left_index, inplace=True)

    elif mode == "add":
        # Outer join to keep all runs
        df_combined = pd.merge(
            df1, df2,
            how="outer",
            left_on=left_index,
            right_on=right_index,
            suffixes=('', '_right')
        )

        # Unify run number column
        df_combined[left_index] = df_combined[left_index].fillna(df_combined[right_index])
        df_combined.drop(columns=[right_index], inplace=True)

        # Sort by unified run column
        df_combined.sort_values(by=left_index, inplace=True)

    else:
        raise ValueError("Invalid mode. Use 'replace' or 'add'.")

    # Save output
    df_combined.to_csv(output_file, index=False)
    print(f"✅ Merged CSV saved to {output_file} in '{mode}' mode.")

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print(f"Usage: python {sys.argv[0]} file1.csv file2.csv output.csv left_index right_index mode")
        print("mode: 'replace' or 'add'")
        sys.exit(1)

    file1, file2, output_file, left_index, right_index, mode = sys.argv[1:]
    merge_csv(file1, file2, output_file, left_index, right_index, mode)
