import os
import shutil

def sync_lowres_images():
    # Define your paths
    source_dir = r"R:\TM Internships\Dept of CMF\Bram Roumen\Master Thesis - CMF\Thesis\nnUNet\Images\Low Res Images\imagesTr"
    dest_base = r"R:\TM Internships\Dept of CMF\Nynke van Jaarsveld\Code\database\lowres\groundtruth"

    if not os.path.exists(source_dir):
        print(f"Error: Source directory not found: {source_dir}")
        return

    # Count for tracking
    copied_count = 0

    # Iterate through files in the Bram Roumen source folder
    for filename in os.listdir(source_dir):
        # We only care about the {pat_no}_0000.nii.gz files
        if filename.endswith("_0000.nii.gz"):
            # Extract patient ID (everything before the first underscore)
            # Example: 'ma01_0000.nii.gz' -> 'ma01'
            pat_no = filename.replace('_0000.nii.gz', '')
            
            source_file = os.path.join(source_dir, filename)
            target_folder = os.path.join(dest_base, pat_no)
            target_file = os.path.join(target_folder, filename)

            # Check if the target patient folder exists
            if os.path.exists(target_folder):
                try:
                    # shutil.copy2 preserves metadata (timestamps, etc.)
                    # It will automatically overwrite the file if it already exists
                    shutil.copy2(source_file, target_file)
                    print(f"Updated: {filename} -> {pat_no} subfolder")
                    copied_count += 1
                except Exception as e:
                    print(f"Failed to copy {filename}: {e}")
            else:
                print(f"Warning: Destination folder for {pat_no} does not exist. Skipping.")

    print(f"\nTask Complete. Total files updated: {copied_count}")

if __name__ == "__main__":
    sync_lowres_images()