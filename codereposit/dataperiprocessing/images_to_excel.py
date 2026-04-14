import os
import SimpleITK as sitk
import pandas as pd

def get_image_info(file_path):
    """Reads metadata from a NIfTI file header."""
    if not file_path or not os.path.exists(file_path):
        return "Not Found", "Not Found"
    try:
        reader = sitk.ImageFileReader()
        reader.SetFileName(file_path)
        reader.ReadImageInformation()
        size = reader.GetSize()
        spacing = [round(s, 3) for s in reader.GetSpacing()]
        return str(size), str(tuple(spacing))
    except Exception as e:
        return f"Error: {e}", "Error"

def process_all_data(parent_path):
    # Dictionary to store all file paths found in the parent directory
    # Key: filename, Value: full path
    all_files = {}
    print("Indexing directory... this may take a moment.")
    for root, _, files in os.walk(parent_path):
        for f in files:
            if f.endswith(".nii.gz"):
                all_files[f] = os.path.join(root, f)

    # 1. Identify all unique patients based on the "_0000.nii.gz" suffix
    patient_ids = sorted([f.replace("_0000.nii.gz", "") for f in all_files if "_0000.nii.gz" in f])
    
    if not patient_ids:
        print("No patients found with the suffix '_0000.nii.gz'. Check your file names!")
        return

    data_list = []

    for p_id in patient_ids:
        print(f"Processing Patient: {p_id}")
        
        # Original Image Path
        img_name = f"{p_id}_0000.nii.gz"
        img_path = all_files.get(img_name)
        
        # Segmentation Path - Try both naming conventions
        seg_name_1 = f"{p_id}_landmark_map.nii.gz"
        seg_name_2 = f"{p_id}.nii.gz"
        
        # Priority: landmark_map first, then exact patient name
        seg_path = all_files.get(seg_name_1) or all_files.get(seg_name_2)
        
        # Get metadata
        img_size, img_spacing = get_image_info(img_path)
        seg_size, seg_spacing = get_image_info(seg_path)
        
        data_list.append({
            "Patient Name": p_id,
            "Image Size": img_size,
            "Image Spacing": img_spacing,
            "Segmentation Size": seg_size,
            "Segmentation Spacing": seg_spacing,
            "Image Found At": img_path,
            "Seg Found At": seg_path if seg_path else "NOT FOUND"
        })

    # Create Excel
    df = pd.DataFrame(data_list)
    output_path = os.path.join(parent_path, "comprehensive_patient_summary.xlsx")
    df.to_excel(output_path, index=False)
    print(f"\nDone! Excel created at: {output_path}")

# --- CONFIGURATION ---
# Point this to the VERY TOP folder that contains either 
# patient folders OR the imagesTr/labelsTr folders.
root_directory = r"R:\TM Internships\Dept of CMF\Nynke van Jaarsveld\Code\database\highres\groundtruth_split"

if __name__ == "__main__":
    process_all_data(root_directory)
