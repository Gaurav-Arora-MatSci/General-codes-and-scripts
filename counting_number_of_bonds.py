# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: NERSC Python
#     language: python
#     name: python3
# ---

# ## This code reads the POSCARs present in the format POSCAR-0, POSCAR-1 and so on and then calculates the number of bonds for 1st NN shell and 2nd NN shell. The cut off distances for these shells can be adjusted in the code. User should 

# +
from ase.io import read
from ase.neighborlist import neighbor_list
from itertools import combinations, combinations_with_replacement
import pandas as pd
import numpy as np
import sys
import os

# --- Configuration ---
START_INDEX = 0
END_INDEX = 100
FILE_PREFIX = 'POSCAR-'     # Files like POSCAR-0, POSCAR-1, ...
RANGE_1_MAX = 2.9           # 1st Shell
RANGE_2_MAX = 3.5           # 2nd Shell
OUTPUT_FILE = 'bond_and_angle_statistics.xlsx'
# ---------------------

# ============================================================
# MANUALLY DEFINE ELEMENT ORDER (IMPORTANT)
# ============================================================
TARGET_ELEMENTS = ['Cr', 'Ta', 'Ti', 'W']   # <-- ENTER CORRECT ORDER HERE
# ============================================================

# Generate bond keys (order preserved by hand-defined TARGET_ELEMENTS)
base_pairs = ["-".join(sorted(p)) for p in combinations_with_replacement(TARGET_ELEMENTS, 2)]
keys_1st = [f"{p}_1stNN" for p in base_pairs]
keys_2nd = [f"{p}_2ndNN" for p in base_pairs]

data_frames = []

print(f"Analyzing POSCAR files {START_INDEX} to {END_INDEX} in current folder...")

# ============================================================
# Process POSCAR files
# ============================================================
for i in range(START_INDEX, END_INDEX + 1):
    filename = f"{FILE_PREFIX}{i}"

    if not os.path.exists(filename):
        continue

    if i % 50 == 0:
        print(f"Processing file: {filename}")

    try:
        atoms = read(filename, format='vasp')
        symbols = atoms.get_chemical_symbols()

        # --- Bond / Neighbor Logic ---
        idx_i, idx_j, dists = neighbor_list('ijd', atoms, RANGE_2_MAX)

        counts = {key: 0 for key in keys_1st + keys_2nd}
        counts.update({'Folder': filename, 'Frame_ID': i})

        # Map for angle calculation
        center_map = {idx: [] for idx in range(len(atoms))}

        for k in range(len(idx_i)):
            u, v, d = idx_i[k], idx_j[k], dists[k]

            if d < RANGE_1_MAX:
                center_map[u].append(v)

            if u >= v:
                continue

            base_bond = "-".join(sorted((symbols[u], symbols[v])))

            if d < RANGE_1_MAX:
                counts[f"{base_bond}_1stNN"] += 1
            elif d <= RANGE_2_MAX:
                counts[f"{base_bond}_2ndNN"] += 1

        # --- Angle Logic ---
        angle_values = []
        for center_idx in range(len(atoms)):
            neighbors = center_map[center_idx]
            if len(neighbors) < 2:
                continue

            for n1, n2 in combinations(neighbors, 2):
                if all(symbols[x] in TARGET_ELEMENTS for x in [center_idx, n1, n2]):
                    angle = atoms.get_angle(n1, center_idx, n2, mic=True)
                    angle_values.append(angle)

        counts['Avg_Angle'] = np.mean(angle_values) if angle_values else 0
        data_frames.append(counts)

    except Exception as e:
        print(f"Error in {filename}: {e}")

# ============================================================
# Export
# ============================================================
if data_frames:
    df_final = pd.DataFrame(data_frames)

    meta = ['Folder', 'Frame_ID', 'Avg_Angle']
    cols = meta + [c for c in df_final.columns if c not in meta]
    df_final = df_final[cols]

    df_final.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved results to {OUTPUT_FILE}")

# -


