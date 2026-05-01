#!/bin/bash -l
#SBATCH --job-name=MP3-50
#SBATCH --time=72:00:00
#SBATCH --partition=DC,batch
#SBATCH --account=me
#SBATCH --constraint=ubuntu
#SBATCH --nodes=2
#SBATCH --qos=batchplus
#SBATCH --ntasks-per-node=64
#SBATCH --mail-type=end
##SBATCH --mail-user=garora@villanova.edu

echo "========== Job started at: $(date) =========="

# ------------------------------
# 1. Load modules and VASP env
# ------------------------------
module purge
export VASP=/opt/VASP/vasp.6.3.2/bin/vasp_gam
export I_MPI_F90=ifx

# Intel compilers
source /opt/intel/oneapi/setvars.sh
#mpiexec.hydra -np 64 /opt/VASP/vasp.6.3.2/bin/vasp_gam

VASP_CMD="mpiexec.hydra -np 128 /opt/VASP/vasp.6.3.2/bin/vasp_gam"



for d in calc-{0..199}; do
    [ -d "$d" ] || continue
    cd "$d" || continue

    if [ ! -f OUTCAR ]; then
        echo "$d - no OUTCAR, starting fresh"
        $VASP_CMD

    elif grep -q "reached required accuracy" OUTCAR; then
        echo "$d - converged, skipping"
        cd ..
        continue

    elif grep -q "rerun with smaller EDIFF" OUTCAR; then
        echo "$d - restarting from CONTCAR"
        cp CONTCAR POSCAR
        $VASP_CMD

    else
        now=$(date +%s)
        mtime=$(stat -c %Y OUTCAR)
        diff=$(( now - mtime ))
        if [ "$diff" -lt 120 ]; then
            echo "$d - still running"
        else
            echo "$d - check manually"
        fi
	rm PROCAR *.xml DOSCAR EIGENVAL *.h5
    fi

    cd ..
done

#bash run_multiple_jobs.sh
