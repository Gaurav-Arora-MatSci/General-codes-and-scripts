#/bin/bash/

input_file="CONTCAR"
for ((i=1;i<=128;i++))
do
        atomsk $input_file -remove-atoms $i POSCAR
        mkdir $i-removed_atom_str
        mv POSCAR $i-removed_atom_str
done
