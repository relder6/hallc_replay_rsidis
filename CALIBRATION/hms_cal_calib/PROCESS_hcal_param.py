#!/usr/bin/env python3

# -----------------------------
# This tool was developed by R. Elder in Nov. 2025. Its purpose is to replace zeroes and negatives in
# the output .param file with the outlier/zero/negative subtracted average of other gains.  It expects
# to be ran in the <spec>_cal_calib folder, which should also contain the outputted .param from the
# main calibration script.  This script will output a new file, moveme.param.  Be careful if copying/
# pasting, replay and calibration scripts can be sensitive to extra/removed spacing.
# -----------------------------

import sys
import os
import re
import numpy as np

# -----------------------------
# Input/output
# -----------------------------
input_filename = sys.argv[1] if len(sys.argv) > 1 else input("Input parameter file: ")
output_filename = "moveme.param"

if not os.path.exists(input_filename):
    print(f"ERROR: '{input_filename}' not found.")
    sys.exit(1)

# -----------------------------
# Read the file
# -----------------------------
with open(input_filename, "r") as f:
    lines = f.readlines()

# -----------------------------
# Extract numbers from pos/neg
# -----------------------------
def extract_numbers(lines, key):
    values = []
    capture = False
    for line in lines:
        if line.startswith(key):
            capture = True
        if capture:
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            values.extend([float(n) for n in numbers])
            if not line.rstrip().endswith(","):
                capture = False
    return values

pos_values = extract_numbers(lines, "hcal_pos_gain_cor")
neg_values = extract_numbers(lines, "hcal_neg_gain_cor")

# -----------------------------
# Compute replacement average
# -----------------------------
combined = np.array([v for v in pos_values + neg_values if v > 0])
q1, q3 = np.percentile(combined, [25, 75])
iqr = q3 - q1
filtered = combined[(combined >= q1 - 1.5*iqr) & (combined <= q3 + 1.5*iqr)]
replacement_avg = round(np.mean(filtered), 2)

# -----------------------------
# Replace zeros and negatives
# -----------------------------
pos_fixed = [v if v > 0 else replacement_avg for v in pos_values]
neg_fixed = [v if v > 0 else replacement_avg for v in neg_values]

# -----------------------------
# Replace numbers in text, preserving exact spacing/comma structure
# -----------------------------
def replace_numbers_in_line(line, values_iter):
    def repl(match):
        width = len(match.group(0))
        return f"{next(values_iter):{width}.2f}"
    return re.sub(r"[-+]?\d*\.\d+|\d+", repl, line)

# -----------------------------
# Write output file, preserves only first commented line
# -----------------------------
with open(output_filename, "w") as out:
    pos_iter = iter(pos_fixed)
    neg_iter = iter(neg_fixed)
    current = None
    header_written = False

    for line in lines:
        if line.startswith(";"):
            if not header_written:
                out.write(line)
                header_written = True
            continue
        
        if line.startswith("hcal_pos_gain_cor"):
            current = "pos"
            out.write(replace_numbers_in_line(line, pos_iter))
        elif line.startswith("hcal_neg_gain_cor"):
            current = "neg"
            out.write(replace_numbers_in_line(line, neg_iter))
        elif current == "pos":
            out.write(replace_numbers_in_line(line, pos_iter))
        elif current == "neg":
            out.write(replace_numbers_in_line(line, neg_iter))
        else:
            out.write(line)

print(f"Wrote file to {output_filename}.")
