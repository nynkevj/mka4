""" 
In de ground truth database verschilt de naamgeving van landmark labels soms per patient in de json files. Zo heette landmark 13 in sommige gevallen 
13 en in andere gevallen 13-1. De json filenames waren daarentegen wel grotendeels hetzelfde voor iedere patient. 

De code verandert de json landmark label naar de json filename voor consistentie en latere aanpassingen.

"""

import os
import json

class Patient:
    def __init__(self, folder_path):
        self.path = folder_path
        self.id = os.path.basename(folder_path)
        self.json_files = self.find_json_filenames()
    

    def find_json_filenames(self):
        if not os.path.isdir(self.path):
            return []
        return [f for f in os.listdir(self.path) if f.endswith('.json')]
    
    def rewrite_jsonlabel(self):
        files_changed = 0

        for json_file in self.json_files:
            json_path = os.path.join(self.path, json_file)

            new_json_label = self.clean_name(json_file)
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                needs_update = False
                for markup in data.get('markups', []):
                    for point in markup.get('controlPoints', []):
                        if point.get('label') != new_json_label:
                            point['label'] = new_json_label
                            needs_update = True

                if needs_update:
                    with open(json_path, "w") as f:
                        json.dump(data, f, indent=2)
                        files_changed += 1
                    print(f'Label in file {json_file} updated to {new_json_label}')

            except json.JSONDecodeError:
                print(f"Error: {json_file} is not a valid JSON or is empty.")
                continue # Skip this file and move to the next one

        return files_changed

    def clean_name(self, name_init):
        name_init_mrk = os.path.splitext(name_init)
        name_init = os.path.splitext(name_init_mrk[0])
        name_lower = name_init[0].lower().replace(" ", "")
        name_post = name_lower.replace("-", "")
        
        return name_post
    

if __name__ == "__main__":
    base_path = r"R:\TM Internships\Dept of CMF\Nynke van Jaarsveld\Code\database\groundtruth"
    
    # Change to true if you want labels in json files to be adapted to json file name
    update_json_labels = True

    for folder_name in sorted(os.listdir(base_path)):
        full_path = os.path.join(base_path, folder_name)
    
        if os.path.isdir(full_path):
            patient = Patient(full_path)
            print(f"Processing Patient: {patient.id}")

            if update_json_labels:
                changed = patient.rewrite_jsonlabel()
                print(f"{changed} json labels were updated")
            else:
                print(f"Just looking at {len(patient.json_files)} files.")