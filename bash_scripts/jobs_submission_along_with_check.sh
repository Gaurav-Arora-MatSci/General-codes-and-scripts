#!/bin/bash

dir=500
file=job.log
string_rerun="please rerun with smaller EDIFF, or copy CONTCAR"
string_accuracy="reached required accuracy - stopping structural energy minimisation"
string_f="150 F="

for ((i=0; i<dir; i+=1))
do
    cd $i-structure

    if [ ! -f "$file" ]; then
        sbatch submit_vasp.sh
    else
        last_line=$(tail -n 1 "$file")
        if echo "$last_line" | grep -q "$string_rerun"; then
            cp CONTCAR POSCAR
            sbatch submit_vasp.sh
        elif echo "$last_line" | grep -q "$string_accuracy"; then
            # Do nothing
            :
        elif echo "$last_line" | grep -q "$string_f"; then
            cp CONTCAR POSCAR
            sbatch submit_vasp.sh
        else
            sbatch submit_vasp.sh
        fi
    fi

    cd ..
done

