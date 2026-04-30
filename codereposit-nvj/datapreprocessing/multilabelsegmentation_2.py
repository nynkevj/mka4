"""
File computes multilabel segmentation maps (.nii.gz) where each landmark is signified by a 3x3 voxel block with a certain label. 
Labels are consistent throughout the patient population.

"""

import os
import json
import numpy as np
import SimpleITK as sitk
from concurrent.futures import ProcessPoolExecutor

class OptimizedPatient:
    def __init__(self, folder_path, predefined_landmarks):
        self.path = folder_path
        self.id = os.path.basename(folder_path)
        self.predefined_landmarks = predefined_landmarks
        self.rev_landmarks = {v: k for k, v in predefined_landmarks.items()}
        
        self.cbct_path = self.find_file('0000.nii.gz')
        self.landmark_json_paths = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.endswith('.json')]
        self.landmark_indices = {}

    def find_file(self, suffix):
        for file in os.listdir(self.path):
            if file.endswith(suffix):
                return os.path.join(self.path, file)
        return None

    def draw_cube_vectorized(self, seg_array, center_idx, label_value):
        """
        Draws a 3x3x3 cube in NumPy. 
        Note: SimpleITK (x,y,z) -> NumPy (z,y,x)
        """
        x, y, z = center_idx
        
        z_min, z_max = max(z-1, 0), min(z+2, seg_array.shape[0])
        y_min, y_max = max(y-1, 0), min(y+2, seg_array.shape[1])
        x_min, x_max = max(x-1, 0), min(x+2, seg_array.shape[2])

        # Check if any voxel in this 3x3x3 area is already labeled with something else
        region = seg_array[z_min:z_max, y_min:y_max, x_min:x_max]
        existing_labels = np.unique(region)
        existing_labels = existing_labels[existing_labels != 0] # Ignore background
        existing_labels = existing_labels[existing_labels != label_value] # Ignore self

        if existing_labels.size > 0:
            current_name = self.rev_landmarks.get(label_value, "Unknown")
            for other_label in existing_labels:
                other_name = self.rev_landmarks.get(other_label, "Unknown")
                print(f"OVERLAP WARNING: '{current_name}' is overwriting '{other_name}' in patient {self.id}")


        seg_array[z_min:z_max, y_min:y_max, x_min:x_max] = label_value

    def process(self, do_crop=False, margin=10):
        if not self.cbct_path:
            return self.id, {}

        # Load CBCT
        sitk_img = sitk.ReadImage(self.cbct_path)
        img_array = sitk.GetArrayFromImage(sitk_img) # Shape: (z, y, x)
        
        # Create blank segmentation array
        seg_array = np.zeros_like(img_array, dtype=np.uint8)

        # Parse JSONs and draw
        for json_path in self.landmark_json_paths:
            with open(json_path, 'r') as f:
                data = json.load(f)
                for markup in data.get('markups', []):
                    for point in markup.get('controlPoints', []):
                        label_name = point.get('label')
                        coords = point.get('position')
                        label_val = self.predefined_landmarks.get(label_name)
                        
                        if label_val and coords:
                            # Transform physical (x,y,z) to index (x,y,z)
                            idx = sitk_img.TransformPhysicalPointToIndex(coords)
                            self.landmark_indices[label_name] = list(idx)
                            
                            self.draw_cube_vectorized(seg_array, idx, label_val)

        # Convert back to SITK
        seg_img = sitk.GetImageFromArray(seg_array)
        seg_img.CopyInformation(sitk_img)

        if do_crop:
            if not self.landmark_indices:
                print(f"SKIPPING CROP: No landmarks {self.predefined_landmarks} found for patient {self.id}.")
                return self.id, {}
            
            crop_dir = os.path.join(self.path, "cropped_files")
            os.makedirs(crop_dir, exist_ok=True)

            # Calculate Bounding Box
            indices = np.array(list(self.landmark_indices.values())) # (N, 3) -> [x, y, z]
            min_coords = np.maximum(0, indices.min(axis=0) - margin).astype(int)
            max_coords = np.minimum(np.array(sitk_img.GetSize()) - 1, indices.max(axis=0) + margin).astype(int)
            
            crop_size = (max_coords - min_coords + 1).tolist()
            start_index = min_coords.tolist() # This is our offset [x_start, y_start, z_start]

            # Perform the Crop
            seg_img = sitk.RegionOfInterest(seg_img, crop_size, start_index)
            sitk_img = sitk.RegionOfInterest(sitk_img, crop_size, start_index)

            # --- KEY STEP: Update indices to be relative to the cropped volume ---
            # New index = Old index - crop start index
            for label in self.landmark_indices:
                old_idx = np.array(self.landmark_indices[label])
                new_idx = old_idx - min_coords
                self.landmark_indices[label] = new_idx.tolist()

            # Save cropped versions in the new folder
            sitk.WriteImage(seg_img, os.path.join(crop_dir, f"{self.id}_landmark_map.nii.gz"))
            sitk.WriteImage(sitk_img, os.path.join(crop_dir, f"{self.id}_0000.nii.gz"))
            
        else:
            # If not cropping, save landmark map in the main patient folder as before
            sitk.WriteImage(seg_img, os.path.join(self.path, f"{self.id}_landmark_map.nii.gz"))

        return self.id, self.landmark_indices
    

def run_pipeline(base_path, predefined_landmarks, do_crop=False):
    patient_folders = [os.path.join(base_path, d) for d in os.listdir(base_path) if d.startswith('ma')]
    all_indices = {}

    # # Use ProcessPoolExecutor for parallel core utilization
    # with ProcessPoolExecutor(max_workers=1) as executor:
    #     futures = [executor.submit(worker, folder, predefined_landmarks, do_crop) for folder in patient_folders]
        
    #     for future in futures:
    #         p_id, indices = future.result()
    #         all_indices[p_id] = indices

    for folder in patient_folders:
        p_id, indices = worker(folder, predefined_landmarks, do_crop)
        all_indices[p_id] = indices

    return all_indices

def worker(folder, landmarks, do_crop):
    """Module-level worker function for multiprocessing"""
    p = OptimizedPatient(folder, landmarks)
    return p.process(do_crop=do_crop)