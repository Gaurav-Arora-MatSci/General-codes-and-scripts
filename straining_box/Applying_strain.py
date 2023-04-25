import numpy as np
import os

# Read the initial box size from the input file
with open('CONTCAR', 'r') as f:
    lines = f.readlines()
box = np.array([list(map(float, line.split())) for line in lines[2:5]])

# Define the range of strains to apply
strain_range = np.linspace(-0.08, 0.08, num=25)

# Loop over the strain range and apply box scaling
for i, strain in enumerate(strain_range):
    # Calculate the new volume after applying the strain
    V1 = np.linalg.det(box) * (1 + strain)

    # Calculate the new length of each box vector
    L1 = V1**(1/3)

    # Calculate the scaling factor for each box vector
    s = L1 / np.linalg.norm(box, axis=0)

    # Apply the scaling factor to each box vector
    box_new = s[:, np.newaxis] * box.T

    # Create a new directory for each strain if it doesn't exist
    dirname = f"{i+1}-strained_{strain:.3f}"
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Update the file with the new box size and strain value
    lines[0] = f"{strain:.3f}\n"
    lines[2:5] = [f"{box_new[i][0]} {box_new[i][1]} {box_new[i][2]}\n" for i in range(3)]
    with open(f'{dirname}/POSCAR', 'w') as f:
        f.writelines(lines)

    # Print the new box vectors and volume
    print("Strain = {:.2f}%".format(strain*100))
    print(box_new.T)
    print("Volume = {:.4f}".format(V1))
