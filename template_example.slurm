#! /bin/bash

#SBATCH --job-name=TEST
#SBATCH --account=xyz@h100
#SBATCH --output={{ output_file }}
#SBATCH --error={{ output_file }}
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:2
#SBATCH --constraint=h100
#SBATCH --hint=nomultithread

module purge

cd ${SLURM_SUBMIT_DIR}

source ~/ceph/activate_venv_pytorch2.4.sh

echo "{{ params }}"
echo "{{ cli }}"

srun hostname
srun python3 blabla.py --batch_size {{ batch_size }} {{ fsdp_cli }}
