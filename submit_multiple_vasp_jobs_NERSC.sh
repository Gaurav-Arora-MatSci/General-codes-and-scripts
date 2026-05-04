#!/bin/bash
#SBATCH -N 4
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -t 10:00:00
#SBATCH --output=slurm-%A.out
#SBATCH --job-name=1NNMP5
#SBATCH --account=m4349
##SBATCH --account=m4599

# --- Write job info immediately ---
echo "Job ID      : $SLURM_JOB_ID"   >  JOBID
echo "Job Name    : $SLURM_JOB_NAME" >> JOBID
echo "Submit Dir  : $SLURM_SUBMIT_DIR" >> JOBID
echo "Start Time  : $(date)"         >> JOBID

log_file="job.log_${SLURM_JOB_ID}"
start=$(date +%s.%N)

module load vasp/6.4.3-cpu
VASP_CMD="srun -n512 -c2 --cpu_bind=cores stdbuf --output=L vasp_gam"


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
            echo "$d - still running, skipping"
            cd ..
            continue
        elif [ -s CONTCAR ]; then
            echo "$d - continuing from CONTCAR"
            cp CONTCAR POSCAR
            $VASP_CMD
        else
            echo "$d - check manually"
        fi
    fi

    rm -f PROCAR *.xml DOSCAR EIGENVAL *.h5
    cd ..
done


#srun -n768 -c2 --cpu_bind=cores stdbuf --output=L vasp_std > "$log_file"

echo "Done."

duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=$(printf "%.2f seconds" $duration)
echo $execution_time >> JOBID

