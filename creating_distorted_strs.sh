#!/bin/bash/

lower_strain=-0.8
high_strain=1.2
counter=1

for i in $(seq "$lower_strain" 0.1 "$high_strain"); do
  echo "$i"
  yes y | atomsk POSCAR -def x "$i"% 0 -def y "$i"% 0 -def z "$i"% 0 "stress_$i.cfg"

  for dist in $(seq 0.1 0.1 0.4); do # Loop for distortion values
      for j in {1..5}; do # Loop for 10 structures per distortion
          counter=$((counter + 1))
          echo "$counter:###############################################"
          yes y | atomsk "stress_$i.cfg" -disturb "$dist" -wrap "${counter}-${j}_strain_${i}_dist_${dist}.lmp"
      done
  done
done
