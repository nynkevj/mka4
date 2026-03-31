"""
Rearranges CBCT scans and corresponding multilabel segmentation maps into a new folder (groundtruth_split) according to the nnLandmark structure (see Github)
Train and test split is based on predefined split found in csv file


"""

import pandas as pd
import shutil
from pathlib import Path

def setup_folders(csv_path, source_base, overwrite=False):
    csv_path = Path(csv_path)
    source_base = Path(source_base)
    
    # Define folder with reorganized files
    target_base = source_base.parent / f'{source_base.name}_split'
    target_base.mkdir(parents=True, exist_ok=True)

    # Define the specific nnU-Net subfolders
    images_tr = target_base / "imagesTr"
    labels_tr = target_base / "labelsTr"
    images_ts = target_base / "imagesTs"
    labels_ts = target_base / "labelsTs"

    # Create directories if they don't exist
    for folder in [images_tr, labels_tr, images_ts, labels_ts]:
        folder.mkdir(parents=True, exist_ok=True)

    # Read the CSV
    df = pd.read_csv(csv_path)

    for index, row in df.iterrows():
        patient_name = str(row.iloc[0]) # First column
        split_type = str(row.iloc[1]).lower() # Second column (train/test)

        # Determine target folders based on split
        if "train" in split_type:
            img_dest_folder = images_tr
            lbl_dest_folder = labels_tr
        else:
            img_dest_folder = images_ts
            lbl_dest_folder = labels_ts

        # Define source and destination file paths
        # Source: source_base / patient_name / patientname_0000.nii
        src_img = source_base / patient_name / f"{patient_name}_0000.nii.gz"
        src_lbl = source_base / patient_name / f"{patient_name}.nii.gz"

        dst_img = img_dest_folder / f"{patient_name}_0000.nii.gz"
        dst_lbl = lbl_dest_folder / f"{patient_name}.nii.gz"

        # Copy logic with checks
        for src, dst in [(src_img, dst_img), (src_lbl, dst_lbl)]:
            if src.exists():
                if not dst.exists() or overwrite:
                    shutil.copy2(src, dst)
                    print(f"Copied: {src.name} to {dst.parent.name}")
                else:
                    print(f"Skipped: {src.name} already exists in correct training/test folder.")
            else:
                print(f"Warning: Source file not found: {src}")

    return target_base
