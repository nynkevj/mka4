#!/bin/bash

# --- Slurm Settings ---
#SBATCH --mail-user=n.vanjaarsveld@student.tudelft.nl
#SBATCH --mail-type=END,FAIL
#SBATCH --job-name=nnLandmark_pandp   
#SBATCH --output=log/output/nnL_%j.out
#SBATCH --error=log/error/nnL_%j.err
#SBATCH --partition=hm
#SBATCH --time=24:00:00  
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --mem=128G

# --- Environment Setup ---
module purge
module load Python/3.11.5-GCCcore-13.2.0
module load CUDA/12.1.1

# Activate your virtual environment (ensure nnLandmark is installed here)
source ~/venv/bin/activate

# --- Path Configuration (Crucial for nnLandmark) ---
export nnLM_raw="/data/scratch/r107583/nnLM_raw"
export nnLM_preprocessed="/data/scratch/r107583/nnLM_preprocessed"
export nnLM_results="/data/scratch/r107583/nnLM_results"

# Create these directories if they don't exist
mkdir -p $nnLM_raw $nnLM_preprocessed $nnLM_results

# --- Execution ---
echo "Starting nnLandmark Training at $(date)"

nnLM_plan_and_preprocess \
     -d 005 \
     -c 3d_lowres \
     --verify_dataset_integrity

nnLM_plan_experiment \
    -d 005 \
    -pl nnUNetPlannerResEncM

echo "Finished at $(date)"