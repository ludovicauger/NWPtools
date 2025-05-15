PID=`squeue |grep auger | grep interact |gawk '{print $1}'`
NODE=`squeue |grep auger | grep interact | gawk '{print $8}'`
NODE=${NODE:7}

#export SLURMD_NODENAME="belenos223"
export SLURMD_NODENAME="belenos"${NODE}
export SLURM_CLUSTER_NAME="belenos"
export SLURM_CPUS_ON_NODE="128"
export SLURM_CPUS_PER_TASK="1"
export SLURM_EXPORT_ENV="NONE"
export SLURM_GET_USER_ENV="1"
export SLURM_GTIDS="0"
#export SLURM_JOBID="63027836"
export SLURM_JOBID=$PID
export SLURM_JOB_ACCOUNT="mrpa"
export SLURM_JOB_CPUS_PER_NODE="128(x150)"
export SLURM_JOB_GID="1780"
export SLURM_JOB_ID=$PID
export SLURM_JOB_NAME="_fp@G5SH"
export SLURM_JOB_NODELIST="belenos["$NODE"]"
export SLURM_JOB_NUM_NODES="150"
export SLURM_JOB_PARTITION="normal256"
export SLURM_JOB_QOS="normal"
export SLURM_JOB_UID=$PID
export SLURM_JOB_USER="auger"
export SLURM_LOCALID="0"
export SLURM_MEM_PER_NODE="50000"
export SLURM_NNODES="150"
export SLURM_NODEID="0"
export SLURM_NODELIST="belenos["$NODE"]"
export SLURM_NODE_ALIASES="(null)"
export SLURM_NPROCS="1"
export SLURM_NTASKS="1"
export SLURM_PRIO_PROCESS="0"
export SLURM_PROCID="0"
export SLURM_SUBMIT_DIR="/scratch/work/auger/exp/aromeCy46pdg_dev"
export SLURM_SUBMIT_HOST="belenostransfert6.belenoshpc.meteo.fr"
export SLURM_TASKS_PER_NODE="128(x150)"
export SLURM_TASK_PID=$PID
export SLURM_TOPOLOGY_ADDR="root_switch.CELL1.iswi1r4s0c1l1.belenos386"
export SLURM_TOPOLOGY_ADDR_PATTERN="switch.switch.switch.node"
export SLURM_WORKING_CLUSTER="belenos:slurm.master.belenoshpc.meteo.fr:6817:8704:109"
export OMP_NUM_THREADS=1

#/home/mf/dp/marp/verolive/public/mpi-tools/mpiauto/mpiauto --wrap --wrap-stdeo --wrap-stdeo-pack --verbose --init-timeout-restart 1 -nn 1 -nnp 1  ./getf
#/opt/softs/intel/2018.04/impi/2018.5.274/intel64/bin/mpiexec.hydra -np 1 -ppn 1 /scratch/work/auger/exp/aromeCy46pdg_dev/getf < /dev/null

