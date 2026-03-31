"""
EMC MKA
Project: Automatization of landmark placement within presurgical CMF planning
Focus: Configuring recently published nnLandmark model (https://github.com/MIC-DKFZ/nnLandmark) for EMC dataset
Author: Nynke van Jaarsveld (n.vanjaarsveld@student.tudelft.nl)


Main preprocessing file 

Input: CBCT files and json files containing landmark coordinates per patient (found in GROUNDTRUTH_PATH)
Output: Multilabel segmentation map per patient in format suitable for NN Landmark (to be found in groundtruth_split_path (same parent folder as GROUNDTRUTH_PATH))

"""

from multilabelsegmentation import multilabelsegmentation
from datasplit import setup_folders
from spacingjson import create_spacing_file 
from all_landmarks_voxel_json import landmarks_json

GROUNDTRUTH_PATH = r"R:\\TM Internships\\Dept of CMF\\Nynke van Jaarsveld\\Code\\database\\highres\\groundtruth"
SPLIT_PATH = r"R:\\TM Internships\\Dept of CMF\\Bram Roumen\\Master Thesis - CMF\\Thesis\\nnUNet\\Landmarking\\gt_labels\\patient_data_part_two\\train_test_split.csv"

### MULTI LABEL SEGMENTATION
## Creates 3x3 multilabel segmentation maps based on json files with landmark coordinates in an empty CBCT template

overwrite_multilabel_segmentation = False
central_landmark_index = multilabelsegmentation(GROUNDTRUTH_PATH, overwrite_multilabel_segmentation)

### NN LANDMARK FILE REORGANIZATION
## Reorganizes the original CBCT images and multilabel segmentation maps into images and labels respectively
## Train and test split is based on split defined in csv file in SPLIT_PATH

# Reorganization
overwrite_split = False
groundtruth_split_path = setup_folders(SPLIT_PATH, GROUNDTRUTH_PATH, overwrite_split)

# Create spacing.json (see NNLandmark Github)
create_spacing_file(GROUNDTRUTH_PATH, groundtruth_split_path)

# Create all_landmarks_voxel.json (see NNLandmark Github)
landmarks_json(groundtruth_split_path, central_landmark_index)
