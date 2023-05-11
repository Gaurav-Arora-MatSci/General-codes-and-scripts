import os
import sys
import numpy as np
from pymatgen.io.vasp.outputs import Vasprun

try:
    path = sys.argv[1]
except IndexError:
    path = '.'

vrun = Vasprun(os.path.join(path, 'vasprun.xml'))
structures = vrun.structures
print(f'Total structures are {len(structures)}')

# Define the timesteps for which you want to dump the structures
timestep_ = 2 #2fs
first_str_time = 100 #100th fs
last_str_time = 1000 #1000th fs
interval = 100 #100 fs
timesteps = np.arange(int((first_str_time)/timestep_), int(((last_str_time)/timestep_)+1), int(interval/timestep_))  # Modify this list according to your desired timesteps
#print(timesteps)

output_folder = os.path.join(path, 'Extracted_POSCARs')
os.makedirs(output_folder, exist_ok=True)

for index, timestep in enumerate(timesteps, start=1):
    if timestep < len(structures):
        structure = structures[timestep]
        poscar_file = os.path.join(output_folder, f'{index}-POSCAR_{timestep*timestep_}-fs.vasp')
        structure.to(fmt="poscar", filename=poscar_file)
        print(f"Structure at timestep {timestep} saved to {poscar_file}")
    else:
        print(f"No structure available for timestep {timestep}")
