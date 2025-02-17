#This code is used to create 100, 110 and 111 dumbell around a atom which is input by a user. It takes "CONTCAR_pe" as input file with cartesian coordinates. USer can predefine the type of 
#interstitial needed in line 56 and 57. List of atom to be deleted or around which dumbell needs to be added is defined in line 83 and type is defined in 84. Please keep in mind tha atom ids
#added in this code is one less than what is defined by Ovito.

import numpy as np
import os

def read_contcar(filename="CONTCAR"):
    """Reads the CONTCAR file and extracts atomic positions."""
    with open(filename, "r") as file:
        lines = file.readlines()

    scale = float(lines[1].strip())
    lattice_vectors = np.array([list(map(float, line.split())) for line in lines[2:5]]) * scale
    atom_types = lines[5].split()
    atom_counts = list(map(int, lines[6].split()))
    total_atoms = sum(atom_counts)
    coordinate_type = lines[7].strip().lower()

    if "cart" not in coordinate_type:
        raise ValueError("Only Cartesian coordinates are supported in CONTCAR.")

    start_index = 8
    positions = np.array([list(map(float, lines[start_index + i].split()[:3])) for i in range(total_atoms)])

    return lattice_vectors, atom_types, atom_counts, positions

def write_contcar(lattice_vectors, atom_types, atom_counts, positions, filename="UPDATED_CONTCAR"):
    """Writes a CONTCAR file."""
    with open(filename, "w") as file:
        file.write("CONTCAR updated\n")
        file.write("1.0\n")
        for vec in lattice_vectors:
            file.write(f"{vec[0]:.6f} {vec[1]:.6f} {vec[2]:.6f}\n")
        file.write(" ".join(atom_types) + "\n")
        file.write(" ".join(map(str, atom_counts)) + "\n")
        file.write("Cartesian\n")
        for pos in positions:
            file.write(f"{pos[0]:.6f} {pos[1]:.6f} {pos[2]:.6f}\n")

def generate_dumbbell_positions(deleted_atom_position):
    """Generates dumbbell positions."""
    base_pos = np.array(deleted_atom_position)

    dumbbells = {
        "100": [base_pos + [-0.75, 0, 0], base_pos + [0.75, 0, 0]],
        "110": [base_pos + [-0.75 / np.sqrt(2), -0.75 / np.sqrt(2), 0],
                base_pos + [0.75 / np.sqrt(2), 0.75 / np.sqrt(2), 0]],
        "111": [base_pos + [-0.75 / np.sqrt(3), -0.75 / np.sqrt(3), -0.75 / np.sqrt(3)],
                base_pos + [0.75 / np.sqrt(3), 0.75 / np.sqrt(3), 0.75 / np.sqrt(3)]]
    }

    return dumbbells

def write_dumbbell_contcars(lattice_vectors, atom_types, atom_counts, new_positions, deleted_atom, dir_counter, deleted_atom_index):
    """Writes dumbbell CONTCARs with user types in numbered directories."""
    dumbbell_positions = generate_dumbbell_positions(deleted_atom)

    #dumbbell_type1 = input("Enter the element symbol for the first dumbbell atom: ")
    #dumbbell_type2 = input("Enter the element symbol for the second dumbbell atom: ")
    dumbbell_type1 = 'Cr'
    dumbbell_type2 = 'Cr'
        
    dir_name = f"{dir_counter}-atom-id{deleted_atom_index}"
    os.makedirs(dir_name, exist_ok=True)

    for direction, positions in dumbbell_positions.items():
        new_positions_with_dumbbell = np.concatenate([new_positions, positions])

        atom_types_with_dumbbell = atom_types[:]
        atom_counts_with_dumbbell = atom_counts[:]

        atom_counts_with_dumbbell.extend([1, 1])
        atom_types_with_dumbbell.extend([dumbbell_type1, dumbbell_type2])

        filename = f"UPDATED_CONTCAR_dumbbell_{direction}"
        filepath = os.path.join(dir_name, filename)
        write_contcar(lattice_vectors, atom_types_with_dumbbell, atom_counts_with_dumbbell, new_positions_with_dumbbell, filepath)
        print(f"{filename} written to {dir_name} successfully.")


def main():
    contcar_file = "CONTCAR_pe"

    atom_ids_to_delete = [61,60,19,117,116,55,97,56,112,31,11,46,105,67,65]  # Example list of atom IDs
    atom_types_to_delete = ["Mn", "Mn", "Cr", "V", "V", "Mn", "V", "Mn", "V", "Cr", "Cr", "Mn", "V", "Mn", "Mn"] # Example list of atom types

    dir_counter = 1

    for i, atom_id in enumerate(atom_ids_to_delete):
        atom_type_to_delete = atom_types_to_delete[i]
        lattice_vectors, atom_types, atom_counts, positions = read_contcar(contcar_file)

        if atom_id < 1 or atom_id > len(positions):
            print(f"Invalid atom ID {atom_id}. Skipping.")
            continue

        deleted_atom_index = atom_id - 1
        deleted_atom = positions[deleted_atom_index]

        new_positions = np.delete(positions, deleted_atom_index, axis=0)

        try:
            atom_type_index = atom_types.index(atom_type_to_delete)
            atom_counts[atom_type_index] -= 1
        except ValueError:
            print(f"Atom type {atom_type_to_delete} not found. Skipping.")
            continue

        print(f"Deleted atom coordinates: {deleted_atom}")

        dir_name = f"{dir_counter}-atom-id{deleted_atom_index}"
        os.makedirs(dir_name, exist_ok=True)

        write_contcar(lattice_vectors, atom_types, atom_counts, new_positions, os.path.join(dir_name, "UPDATED_CONTCAR_removed"))
        print(f"UPDATED_CONTCAR_removed written to {dir_name} successfully.")

        write_dumbbell_contcars(lattice_vectors, atom_types, atom_counts, new_positions, deleted_atom, dir_counter, deleted_atom_index)

        dir_counter += 1


if __name__ == "__main__":
    main()
