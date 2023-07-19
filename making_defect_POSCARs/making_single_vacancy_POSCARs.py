#!/usr/bin/env python
# coding: utf-8

# ## This code reads the POSCAR file and delete one atom a time to make POSCARs for calculting single vacancy formation energy. This code needs a directory with name output_directory to make all POSCAR files.

# In[10]:


import os
from itertools import accumulate

def read_poscar(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Extracting data from POSCAR
    lattice_constant = float(lines[1])
    lattice_vectors = [list(map(float, line.split())) for line in lines[2:5]]
    elements = lines[5].split()
    element_counts = list(map(int, lines[6].split()))
    total_atoms = sum(element_counts)
    atom_coords = [list(map(float, line.split()[:3])) for line in lines[8:8+total_atoms]]

    return lattice_constant, lattice_vectors, elements, element_counts, atom_coords

def write_poscar(file_path, lattice_constant, lattice_vectors, elements, element_counts, atom_coords):
    with open(file_path, 'w') as f:
        # Writing header
        f.write("Generated by Python\n")
        f.write(f"{lattice_constant:.10f}\n")
        for vector in lattice_vectors:
            f.write(f"{vector[0]:.10f} {vector[1]:.10f} {vector[2]:.10f}\n")
        f.write(' '.join(elements) + '\n')
        f.write(' '.join(map(str, element_counts)) + '\n')
        f.write("Direct\n")

        # Writing atom coordinates
        for coord in atom_coords:
            f.write(f"{coord[0]:.10f} {coord[1]:.10f} {coord[2]:.10f}\n")

def delete_atom(poscar_file_path, output_dir):
    # Read original POSCAR file
    lattice_constant, lattice_vectors, elements, element_counts, atom_coords = read_poscar(poscar_file_path)

    start_indices = list(accumulate(element_counts))  # Starting indices of each element
    total_atoms = sum(element_counts)
    
    for i in range(total_atoms):
        element_index = next(j for j, start_index in enumerate(start_indices) if i < start_index)  # Find element index for the atom at index i

        # Create new atom coordinates by excluding the atom at index i
        new_atom_coords = atom_coords[:i] + atom_coords[i+1:]

        # Adjust the element counts
        new_element_counts = element_counts[:]
        new_element_counts[element_index] -= 1

        # Create a new POSCAR file name
        file_name = f"POSCAR_{i}.vasp"
        output_path = os.path.join(output_dir, file_name)

        # Write new POSCAR file
        write_poscar(output_path, lattice_constant, lattice_vectors, elements, new_element_counts, new_atom_coords)

# Example usage
delete_atom('POSCAR', 'output_directory')

