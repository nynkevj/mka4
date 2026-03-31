"""
File computes multilabel segmentation maps (.nii.gz) where each landmark is signified by a 3x3 voxel block with a certain label. 
Labels are consistent throughout the patient population.

"""

import os
import json
import SimpleITK as sitk


# Labels for multilabel segmentation map for each patient - to be divided in two parts?
JSON_LANDMARK_LABELS = {'13': 1, '16': 2, '23': 3, '26': 4, '33': 5, '36': 6, '43': 7, '46': 8, 'anteriornasalspine': 9,
                         'bpoint': 10, 'basion': 11, 'gnation': 12, 'inferiorborderl': 13, 'inferiorborderr': 14, 'infraorbitalel': 15,
                           'infraorbitaler': 16, 'isl1': 17, 'isl1l': 18, 'isl1r': 19, 'isu1': 20, 'lingulal': 21, 'lingular': 22,
                             'm2linel': 23, 'm2liner': 24, 'menton': 25, 'nasalnotchl': 26, 'nasalnotchr': 27, 'nasion': 28,
                               'pogonion': 29, 'pointa': 30, 'porionl': 31, 'porionr': 32, 'posteriornasalspine': 33, 'sella': 34,
                                 'zygomaticprocessl': 35, 'zygomaticprocessr': 36, 'lcondyl': 37, 'lcoronoid': 38, 'lforamenmentale': 39,
                                   'lgonion': 40, 'lsigmoidnotch': 41, 'rcondyle': 42, 'rcoronoid': 43, 'rforamenmentale': 44, 'rgonion': 45,
                                     'rsigmoidnotch': 46}

class Patient:
    def __init__(self, folder_path):
        """
        """
        self.path = folder_path
        self.id = os.path.basename(folder_path)
        self.cbct_path = self.find_cbct()
        self.landmark_paths = self.find_landmarks()
        self.landmark_indices = {}

    def find_cbct(self):
        """ 
        Internal helper to find the .nii file for this patient 
        """

        for file in os.listdir(self.path):
            if file.endswith('0000.nii.gz'):
                return os.path.join(self.path, file)
        return None
    
    def find_landmarks(self):
        """
        Internal helper to find all landmark files for this patient and returns them in list of paths
        """

        paths_la = []
        for file in os.listdir(self.path):
            if file.endswith('.json'):
                file_path = os.path.join(self.path, file)
                paths_la.append(file_path)
        return paths_la        

    def blank_segm_map(self):
        """
        Create empty template for multilabel segmentation map based on dimensions CBCT image
        """
        if not self.cbct_path:
            print(f"No CBCT found for patient: {self.id}")
            return None
        
        # print(f"Processing CBCT for patient: {self.id}")
        
        # Load the image to get metadata (spacing, origin, direction, size)
        sitk_img = sitk.ReadImage(self.cbct_path)
        
        # Create an empty (zeros) image with the same metadata
        blank_map = sitk.Image(sitk_img.GetSize(), sitk.sitkUInt8)
        blank_map.SetSpacing(sitk_img.GetSpacing())
        blank_map.SetOrigin(sitk_img.GetOrigin())
        blank_map.SetDirection(sitk_img.GetDirection())
        
        return blank_map
    
    def segm_map(self):
        """
        Create multi-label segmentation map where each individual landmark is signified by its own 3x3 voxel label
        """
        segmentation = self.blank_segm_map()
        if segmentation is None:
            return None

        unknown_labels = set()
        overlaps = {} 

        for json_path in self.landmark_paths:
            self.json_file_handling(json_path, segmentation, unknown_labels, overlaps)

        return segmentation

    def json_file_handling(self, json_path, segmentation, unknown_labels, overlaps):
        """
        Opens and reads json file to extract name and coordinates of landmark 
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            for markup in data.get('markups', []):
                for point in markup.get('controlPoints', []):
                    self.coord_to_segm(point, segmentation, unknown_labels, overlaps)
                    
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f" Error reading JSON {json_path}: {e}")

    def coord_to_segm(self, point, segmentation, unknown_labels, overlaps):
        """
        Handles spatial logic for a single landmark point
        """
        label_name = point.get('label')
        label_value = JSON_LANDMARK_LABELS.get(label_name)

        # Validate label - check whether JSON name coincides with a name mentioned in JSON_LANDMARK_LABELS (global)
        if label_value is None:
            if label_name not in unknown_labels:
                print(f" Warning: '{label_name}' NOT in {JSON_LANDMARK_LABELS}. Skipping...")
                unknown_labels.add(label_name)
            return

        coords = point.get('position')
        if not coords:
            return

        # Convert JSON landmark coordinates into 3x3 voxel labeled segmentation
        try:
            center_idx = segmentation.TransformPhysicalPointToIndex(coords)

            # Store central landmark indices for all_landmarks_voxel.json file
            self.landmark_indices[label_name] = list(center_idx)
            
            # Draw 3x3x3 block
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    for z in [-1, 0, 1]:
                        idx = (center_idx[0] + x, center_idx[1] + y, center_idx[2] + z)
                        
                        if self.is_inside_img(segmentation, idx):
                            self.overlap_check(idx, label_value, label_name, segmentation, overlaps)

        except Exception:
            print(f" Point {label_name} is outside image volume for {self.id}")

    def overlap_check(self, idx, label_value, label_name, segmentation, overlaps):
        """
        Checks whether pixel had already been assigned a label (thus if there is overlap).
        NB: if there is overlap the pixel will be overwritten by the new label!
        """
        existing_val = segmentation.GetPixel(idx)
        
        if existing_val != 0 and existing_val != label_value:
            # Reverse lookup for the existing label name
            existing_name = next((k for k, v in JSON_LANDMARK_LABELS.items() if v == existing_val), "Unknown")
            pair = tuple(sorted((label_name, existing_name)))
            
            if pair not in overlaps:
                print(f"OVERLAP WARNING: '{label_name}' vs '{existing_name}' in patient {self.id}")
                overlaps[pair] = True

        segmentation.SetPixel(idx, label_value)

    def is_inside_img(self, img, index):
        """
        Checks whether index of landmark is within size of template segmentation map
        """
        size = img.GetSize()
        return all(0 <= index[i] < size[i] for i in range(3))
    
    def load_indices_from_segm(self, file_path):
        """
        If multilabel segmentation map already exists, this function loads the image and 
        extracts the central voxel indices for every label found.
        """
        img = sitk.ReadImage(file_path)
        stats = sitk.LabelShapeStatisticsImageFilter()
        stats.Execute(img)

        reverse_labels = {v: k for k, v in JSON_LANDMARK_LABELS.items()}

        for label_value in stats.GetLabels():
            if label_value in reverse_labels:
                label_name = reverse_labels[label_value]
                
                # Get the centroid in physical coordinates, then convert to index
                centroid_physical = stats.GetCentroid(label_value)
                center_idx = img.TransformPhysicalPointToIndex(centroid_physical)
                
                self.landmark_indices[label_name] = list(center_idx)


def multilabelsegmentation(base_path, overwrite):
    all_landmark_indices = {}
    
    # Get list of patient folders
    patient_folders = [item for item in os.listdir(base_path) if item.startswith('ma')]

    for folder in patient_folders:
        full_path = os.path.join(base_path, folder)
        p = Patient(full_path)
        output_path = os.path.join(p.path, f"{p.id}_landmark_map.nii.gz")

        # Check if we need to process or if we can just load
        if overwrite or not os.path.exists(output_path):
            print(f"Processing Patient: {p.id}")
            segmented_blocks = p.segm_map()
            sitk.WriteImage(segmented_blocks, output_path)
            all_landmark_indices[p.id] = p.landmark_indices
        else:
            print(f"Skipping creation of multilabel segmentation maps for {p.id}, file already exists.")
            p.load_indices_from_segm(output_path)
            
        all_landmark_indices[p.id] = p.landmark_indices 

    return all_landmark_indices

