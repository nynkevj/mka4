import os
import json

def landmarks_json(path, indices):
    # Saving all_landmarks_voxels.json with indices of central landmark of all patients
    json_out_path = os.path.join(path, "all_landmarks_voxels.json")
    with open(json_out_path, 'w') as f:
        json.dump(indices, f, indent=2)
    
    print(f"\nCreated all_landmarks_voxels.json at: {json_out_path}")