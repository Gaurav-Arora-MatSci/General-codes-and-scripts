import numpy as np
import os

# Read the initial box size from the input file
with open('CONTCAR', 'r') as f:
    lines = f.readlines()
box = np.array([list(map(float, line.split())) for line in lines[2:5]])

# Define the range of shear strains to apply
shear_range = np.linspace(0.01, 0.1, num=20)

# Define the direction of shear strain (0 for xy-plane, 1 for xz-plane, 2 for yz-plane)
shear_direction = 1

# Loop over the shear strain range and apply box shearing
for i, shear in enumerate(shear_range):
    # Create the shear strain matrix based on the specified direction
    shear_matrix = np.eye(3)
    shear_matrix[shear_direction, (shear_direction + 1) % 3] = shear

    # Apply the shear strain matrix to the box vectors
    box_sheared = np.dot(shear_matrix, box.T).T

    # Create a new directory for each shear strain if it doesn't exist
    dirname = f"{i+1}-sheared_{shear:.3f}"
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # Update the file with the new box size and shear strain value
    lines[0] = f"Shear Strain = {shear:.2f}\n"
    lines[2:5] = [f"{box_sheared[j][0]:.16f} {box_sheared[j][1]:.16f} {box_sheared[j][2]:.16f}\n" for j in range(3)]
    with open(f'{dirname}/POSCAR', 'w') as f:
        f.writelines(lines)

    # Print the new box vectors and volume
    print("Shear Strain = {:.2f}%".format(shear*100))
    print(box_sheared)
