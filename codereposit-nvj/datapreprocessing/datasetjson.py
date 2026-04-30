import os
import json


def create_dataset_json(groundtruthsplit_path, json_landmarks):
    output_file = os.path.join(groundtruthsplit_path, 'dataset.json')

    # Ensure the output directory exists before proceeding
    if not os.path.exists(groundtruthsplit_path):
        num_training = 0
        print(f"Error: Target directory {groundtruthsplit_path} does not exist. Please create it first.")
        return
    else:
        # Counts number of patients (based on amount of folders starting with 'ma')
        pat_path = os.path.join(groundtruthsplit_path, 'imagesTr') 
        patient_folders = [f for f in os.listdir(pat_path) 
                          if f.startswith('ma')]
        num_training = len(patient_folders)

    # Build the labels dictionary (always including background)
    # Use dictionary comprehension to merge background with your active labels
    labels_dict = {"background": 0}
    labels_dict.update(json_landmarks)

    # Create file structure
    dataset_data = {
        "channel_names": {
            "0": "CBCT"
        },
        "labels": labels_dict,
        "numTraining": num_training,
        "file_ending": ".nii.gz"
    }

    # Write to file
    try:
        with open(output_file, 'w') as f:
            json.dump(dataset_data, f, indent=4)
        print(f"\nCreated dataset.json at {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
