import os
import json
import numpy as np
import SimpleITK as sitk

# Landmark groups
landmarks_groups = {
    "group_left_mandible": [
        "l-Condyl.mrk",
        "l-Coronoid.mrk",
        "l-Gonion.mrk",
        "l-Sigmoid Notch.mrk"
    ],

    "group_right_mandible": [
        "r-Condyle.mrk",
        "r-Coronoid.mrk",
        "r-Gonion.mrk",
        "r-Sigmoid Notch.mrk"
    ],

    "group_anterior_mandible": [
        "B-Point.mrk",
        "Gnation.mrk",
        "l-Foramen Mentale.mrk",
        "Menton.mrk",
        "Pogonion.mrk",
        "r-Foramen Mentale.mrk"
    ],
    
    "group_dentition": [
        "B3L.mrk",
        "B3R.mrk",
        "IsL1.mrk",
        "IsL1L.mrk",
        "IsL1R.mrk"
    ]
}

class PatientData:
    """
    A class used to represent Patient Data for cropping CBCT images.
    """   
    def __init__(self, path_to_patients):
        """
        Initialize PatientData with the directory path to the patients' data.
        """
        self.path_to_patients = path_to_patients
        self.patient_dirs = self.dir_to_patients()

    def dir_to_patients(self):
        """
        Returns a list of directories for each patient.
        """
        patient_dirs = []
        for patient in os.listdir(self.path_to_patients)[:1]:
            path_to_patient = os.path.join(self.path_to_patients, patient)
            patient_dirs.append(path_to_patient)
        return patient_dirs
    
    def dir_to_landmarks(self, path_to_patient):
        """
        Returns a list of directories for each landmark file for a given patient.
        """
        landmark_dirs = []
        for file in os.listdir(path_to_patient):
            if file.endswith('.json'):
                landmark_dirs.append(os.path.join(path_to_patient, file))
        return landmark_dirs
    
    def group_landmarks(self, landmark_dirs):
        """
        Groups landmarks based on predefined landmark groups.
        """
        grouped_landmarks = {group_name: [] for group_name in landmarks_groups.keys()}
        for landmark_dir in landmark_dirs:
            basename_without_extension = os.path.splitext(os.path.basename(landmark_dir))[0]
            for group_name, group in landmarks_groups.items():
                if basename_without_extension in group:
                    grouped_landmarks[group_name].append(landmark_dir)
        return grouped_landmarks
    
    def dir_to_cbct(self, path_to_patient):
        """
        Returns a list of directories for each CBCT file for a given patient.
        """
        cbct_dir = []
        for file in os.listdir(path_to_patient):
            if file.endswith('_0000.nii.gz'):
                cbct_dir.append(os.path.join(path_to_patient, file))
        return cbct_dir

    def load_landmarks(self, paths_to_landmark_files):
        """
        Loads landmarks from given files and returns a list of all landmark coordinates.
        """
        all_landmark_coordinates = []
        for path_to_landmark_file in paths_to_landmark_files:
            with open(path_to_landmark_file, 'r') as f:
                data = json.load(f)
            landmark_coordinates = [point['position'] for point in data['markups'][0]['controlPoints']]
            all_landmark_coordinates.extend(landmark_coordinates)
        return all_landmark_coordinates

    def get_crop_coordinates(self, landmarks):
        """
        Calculates and returns the minimum and maximum coordinates from a list of landmarks.
        """
        landmarks_array = np.array(landmarks)
        min_coords = landmarks_array.min(axis=0)
        max_coords = landmarks_array.max(axis=0)
        return min_coords, max_coords

    def calculate_bounding_box_with_margin(self, binary_img, margin_mm):
        """
        Calculates and returns the bounding box of a binary image with a given margin.
        """
        label_stats = sitk.LabelShapeStatisticsImageFilter()
        label_stats.Execute(binary_img)
        
        # Get initial bounding box [x_start, y_start, z_start, x_size, y_size, z_size]
        bounding_box = list(label_stats.GetBoundingBox(1))
        img_size = binary_img.GetSize()
        margin = [margin_mm / spacing for spacing in binary_img.GetSpacing()]

        new_box = [0, 0, 0, 0, 0, 0]

        for i in range(3):
            start = max(0, int(bounding_box[i] - margin[i]))
            
            end = min(img_size[i], int(bounding_box[i] + bounding_box[i+3] + margin[i]))
            
            new_box[i] = start
            new_box[i+3] = end - start

        return new_box

    def crop_cbct(self, path_to_cbct, landmarks):
        """
        Crops a CBCT image based on given landmarks and returns the cropped image.
        """
        cbct_img = sitk.ReadImage(path_to_cbct[0])

        # Create a binary image where the voxels at the landmark points are set to 1
        binary_img = sitk.Image(cbct_img.GetSize(), sitk.sitkUInt8)
        binary_img.CopyInformation(cbct_img)

        img_size = binary_img.GetSize()
        for landmark in landmarks:
            index = list(binary_img.TransformPhysicalPointToIndex(landmark))

            for i in range(3):
                index[i] = max(0, min(img_size[i] -1, index[i]))

            binary_img[tuple(index)] = 1

        # Calculate the bounding box with a margin of 10 mm
        bounding_box = self.calculate_bounding_box_with_margin(binary_img, 10)

        # Extract the region of interest
        roi_filter = sitk.RegionOfInterestImageFilter()
        roi_filter.SetIndex(bounding_box[:3])
        roi_filter.SetSize(bounding_box[3:])
        cropped_cbct_img = roi_filter.Execute(cbct_img)

        return cropped_cbct_img
    
def save_cropped_cbct(cbct_name, cropped_cbct, patient_dir):
    """
    Saves the cropped CBCT image to the patient's directory.
    """
    cropped_dir = os.path.join(patient_dir, "cropped_cbct")
    print(cropped_dir)
    os.makedirs(cropped_dir, exist_ok=True)
    sitk.WriteImage(cropped_cbct, os.path.join(cropped_dir, f"{cbct_name}.nii.gz"))


if __name__ == "__main__":
    path_to_patients = "R:\\TM Internships\\Dept of CMF\\Nynke van Jaarsveld\\Code\\database\\groundtruth"
    patient_data = PatientData(path_to_patients)
    for patient_dir in patient_data.patient_dirs:
        landmark_dirs = patient_data.dir_to_landmarks(patient_dir)
        grouped_landmarks = patient_data.group_landmarks(landmark_dirs)
        cbct_dir = patient_data.dir_to_cbct(patient_dir)
        for group_name, landmark_paths in grouped_landmarks.items():
            landmark_coordinates = patient_data.load_landmarks(landmark_paths)
            if not landmark_coordinates:
                print(f"Skipping {group_name} - no files found for this patient.")
                continue
            min_coords, max_coords = patient_data.get_crop_coordinates(landmark_coordinates)
            print(f'Group: {group_name}, min_coords: {min_coords}, max_coords: {max_coords}')
            cropped_cbct = patient_data.crop_cbct(cbct_dir, landmark_coordinates)
            save_cropped_cbct(group_name, cropped_cbct, patient_dir)
            