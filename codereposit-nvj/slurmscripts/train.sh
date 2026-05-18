#!/bin/bash

# --- Slurm Settings ---
#SBATCH --mail-user=n.vanjaarsveld@student.tudelft.nl
#SBATCH --mail-type=END,FAIL
#SBATCH --job-name=nnLandmark_train
#SBATCH --output=log/output/nnL_%j.out
#SBATCH --error=log/error/nnL_%j.err
#SBATCH --partition=hm
#SBATCH --time=48:00:00  

#SBATCH --gres=gpu:1
#SBATCH --exclude=gpu-hm-001
#SBATCH --ntasks=1
#SBATCH --mem=128G  
#SBATCH --cpus-per-task=8 

# --- Environment Setup ---
module purge
module load Python/3.11.5-GCCcore-13.2.0
module load CUDA
source ~/venv/bin/activate

# --- Path Configuration ---
export nnLM_raw="/data/scratch/r107583/nnLM_raw"
export nnLM_preprocessed="/data/scratch/r107583/nnLM_preprocessed"
export nnLM_results="/data/scratch/r107583/nnLM_results"
export nnUNet_n_proc_DA=4


# --- Training Configuration ---

echo "Date: $(date)"

nnLM_train \
    003 \
    3d_lowres \
    0 \


echo "Fold finished at $(date)"