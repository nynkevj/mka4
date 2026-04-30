"""
EMC MKA
Project: Automatization of landmark placement for presurgical CMF planning
Focus: Configuring recently published nnLandmark model (https://github.com/MIC-DKFZ/nnLandmark) for EMC dataset
Author: Nynke van Jaarsveld (n.vanjaarsveld@student.tudelft.nl)


Main preprocessing file 

Input: folder with patient specific folders named (ma_patientnumber) with CBCT files and json files containing landmark coordinates per patient (found in GROUNDTRUTH_PATH)
    Make sure all of the json files have the same landmark labels, otherwise run reset_jsonlabel.py to be found in periprocessing folder
Output: Multilabel segmentation map per patient in format suitable for NN Landmark (to be found in groundtruth_split_path (same parent folder as GROUNDTRUTH_PATH))

"""
from multilabelsegmentation_2 import run_pipeline
from datasplit import setup_folders
from spacingjson import create_spacing_file 
from all_landmarks_voxel_json import landmarks_json
from datasetjson import create_dataset_json


GROUNDTRUTH_PATH = r"R:\\TM Internships\\Dept of CMF\\Nynke van Jaarsveld\\Code\\database-nvj\\lowres_1lm\\groundtruth"
SPLIT_PATH = r"R:\\TM Internships\\Dept of CMF\\Bram Roumen\\Master Thesis - CMF\\Thesis\\nnUNet\\Landmarking\\gt_labels\\patient_data_part_two\\train_test_split.csv"
JSON_LANDMARK_LABELS = {'13': 1}
# JSON_LANDMARK_LABELS = {'13': 1, '16': 2, '23': 3, '26': 4, '33': 5, '36': 6, '43': 7, '46': 8, 'anteriornasalspine': 9,
#                         'bpoint': 10, 'basion': 11, 'gnation': 12, 'inferiorborderl': 13, 'inferiorborderr': 14, 'infraorbitalel': 15,
#                           'infraorbitaler': 16, 'isl1': 17, 'isl1l': 18, 'isl1r': 19, 'isu1': 20, 'lingulal': 21, 'lingular': 22,
#                             'm2linel': 23, 'm2liner': 24, 'menton': 25, 'nasalnotchl': 26, 'nasalnotchr': 27, 'nasion': 28,
#                               'pogonion': 29, 'pointa': 30, 'porionl': 31, 'porionr': 32, 'posteriornasalspine': 33, 'sella': 34,
#                                 'zygomaticprocessl': 35, 'zygomaticprocessr': 36, 'lcondyl': 37, 'lcoronoid': 38, 'lforamenmentale': 39,
#                                   'lgonion': 40, 'lsigmoidnotch': 41, 'rcondyle': 42, 'rcoronoid': 43, 'rforamenmentale': 44, 'rgonion': 45,
#                                     'rsigmoidnotch': 46}


def main():
    ### MULTI LABEL SEGMENTATION
    ## Creates 3x3 multilabel segmentation maps based on json files with landmark coordinates in an empty CBCT template
    # Crop option creates new CBCT and multilabel segmentation maps with 10 voxel margin around selected landmarks 
    crop_cbct_landmarks = True
    central_landmark_index = run_pipeline(GROUNDTRUTH_PATH, JSON_LANDMARK_LABELS, crop_cbct_landmarks)


    ### NN LANDMARK FILE REORGANIZATION
    ## Reorganizes the original CBCT images and multilabel segmentation maps into images and labels respectively
    ## Train and test split is based on split defined in csv file in SPLIT_PATH

    # Reorganization
    overwrite_split = True
    groundtruth_split_path = setup_folders(SPLIT_PATH, GROUNDTRUTH_PATH, overwrite_split, crop_cbct_landmarks)

    # Create spacing.json (see NNLandmark Github)
    create_spacing_file(GROUNDTRUTH_PATH, groundtruth_split_path)

    # Create all_landmarks_voxel.json (see NNLandmark Github)
    landmarks_json(groundtruth_split_path, central_landmark_index)

    # Create dataset.json (see NNLandmark Github)
    create_dataset_json(groundtruth_split_path, JSON_LANDMARK_LABELS)


if __name__ == "__main__":
    main()
