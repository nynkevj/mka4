import os
import json
import nibabel as nib

def create_nnlandmark_spacing_file(base_dir):
    gt_dir = os.path.join(base_dir, 'groundtruth')
    output_dir = os.path.join(base_dir, 'groundtruth_split')
    output_file = os.path.join(output_dir, 'spacing.json')

    # Ensure the output directory exists before proceeding
    if not os.path.exists(output_dir):
        print(f"Error: Target directory {output_dir} does not exist. Please create it first.")
        return
    
    # Dictionary to hold our final JSON structure
    master_spacing = {}

    if not os.path.exists(gt_dir):
        print(f"Error: Directory {gt_dir} does not exist.")
        return

    # Iterate through each case subfolder
    for case_id in os.listdir(gt_dir):
        case_path = os.path.join(gt_dir, case_id)
        
        if os.path.isdir(case_path):
            img_name = f"{case_id}_0000.nii.gz"
            mask_name = f"{case_id}_landmark_map.nii.gz"

            img_path = os.path.join(case_path, img_name)
            mask_path = os.path.join(case_path, mask_name)

            try:
                # Load spacing
                img_nifti = nib.load(img_path)
                img_spacing = [float(s) for s in img_nifti.header.get_zooms()[:3]]

                mask_nifti = nib.load(mask_path)
                anno_spacing = [float(s) for s in mask_nifti.header.get_zooms()[:3]]

                # Store in the required format
                master_spacing[case_id] = {
                    "image_spacing": img_spacing,
                    "annotation_spacing": anno_spacing
                }
                print(f"Processed {case_id}: Spacing {anno_spacing}")

            except Exception as e:
                print(f"Skipping {case_id} due to error: {e}")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write the JSON file
    with open(output_file, 'w') as f:
        json.dump(master_spacing, f, indent=2)

    print(f"\nDone! File saved to: {output_file}")

# Execute
base_path = r'R:\\TM Internships\\Dept of CMF\\Nynke van Jaarsveld\\Code\\database\\highres'
create_nnlandmark_spacing_file(base_path)