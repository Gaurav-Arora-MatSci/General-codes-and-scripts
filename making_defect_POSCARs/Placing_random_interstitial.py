#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np

for i in range (100):
    def read_poscar(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Extract lattice vectors
        lattice = np.zeros((3, 3))
        for i in range(2, 5):
            lattice[i-2] = [float(x) for x in lines[i].split()]

        # Extract atomic positions and types
        elements = lines[5].split()
        counts = [int(x) for x in lines[6].split()]
        num_atoms = sum(counts)

        positions = []
        for i in range(8, 8 + num_atoms):
            positions.append([float(x) for x in lines[i].split()])

        return lattice, elements, counts, positions

    def write_poscar(filename, lattice, elements, counts, positions):
        with open(filename, 'w') as f:
            # Write header
            f.write("Generated POSCAR\n")

            # Write scaling factor
            f.write("1.0\n")

            # Write lattice vectors
            for i in range(3):
                f.write("{:.8f} {:.8f} {:.8f}\n".format(lattice[i][0], lattice[i][1], lattice[i][2]))


            # Write element symbols and counts
            f.write(" ".join(elements) + "\n")
            f.write(" ".join(str(count) for count in counts) + "\n")

            # Write atomic positions in direct format
            f.write("Direct\n")
            for position in positions:
                f.write("{:.8f} {:.8f} {:.8f}\n".format(position[0], position[1], position[2]))

    def random_atom_position(lattice, positions):
        while True:
            # Generate random position within simulation cell in fractional coordinates
            atom_position_frac = np.random.random(3)

            # Convert fractional coordinates to Cartesian coordinates using lattice vectors
            atom_position_cartesian = np.dot(atom_position_frac, lattice)

            # Check distance from existing atoms
            min_distance = min(np.linalg.norm(atom_position_cartesian - p) for p in positions)
            if min_distance >= 1.0:
                return atom_position_frac

    # Read POSCAR file
    filename = "CONTCAR"
    lattice, elements, counts, positions = read_poscar(filename)

    # Generate random atom position in fractional coordinates
    new_atom_position_frac = random_atom_position(lattice, positions)

    # Update atom counts and positions
    elements.append("Cr")
    counts.append(1)
    positions.append(new_atom_position_frac)

    # Write updated POSCAR file
    new_filename = str(i) + "-POSCAR.vasp"
    write_poscar(new_filename, lattice, elements, counts, positions)

    print("Updated POSCAR file saved as", new_filename)


# In[ ]:





# In[ ]:




