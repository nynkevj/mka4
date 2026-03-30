import os

LANDMARK_NAMES = [
    'B-Point.mrk.json', 'l-Condyl.mrk.json', 'r-Condyle.mrk.json', 'l-Coronoid.mrk.json', 'r-Coronoid.mrk.json',
    'l-Foramen Mentale.mrk.json', 'r-Foramen Mentale.mrk.json', 'Gnation.mrk.json', 'l-Gonion.mrk.json', 'r-Gonion.mrk.json', 
    'Menton.mrk.json', 'Pogonion.mrk.json', 'l-Sigmoid Notch.mrk.json', 'r-Sigmoid Notch.mrk.json', 'Anterior Nasal Spine.mrk.json',
    'Basion.mrk.json', 'Infraorbitale L.mrk.json', 'Infraorbitale R.mrk', 'Nasion.mrk.json', 'Point A.mrk.json',
    'Porion L.mrk.json', 'Porion R.mrk.json', 'Posterior Nasal Spine.mrk.json', 'Sella.mrk.json', 'Supraorbital L.mrk.json', 'Supraorbital R.mrk.json',
    '13.mrk.json', '16.mrk.json', '23.mrk.json', '26.mrk.json', '33.mrk.json', '36.mrk.json', '43.mrk.json', '46.mrk.json',
    'IsL1.mrk.json', 'IsL1L.mrk.json', 'IsL1R.mrk.json', 'IsU1.mrk.json', 'Inferior border L.mrk.json','Inferior border R.mrk.json',
    'Lingula L.mrk.json', 'Lingula R.mrk.json', 'Nasal notch L.mrk.json', 'Nasal notch R.mrk.json', 'M2-line L.mrk.json', 'M2-line R.mrk.json',
    'Zygomatic Process L.mrk.json', 'Zygomatic Process R.mrk.json'
]

class Patient:
    def __init__(self, folder_path):
        self.path = folder_path
        self.id = os.path.basename(folder_path)
        self.actual_files = self.find_json_filenames()

    def find_json_filenames(self):
        if not os.path.isdir(self.path):
            return []
        return [f for f in os.listdir(self.path) if f.endswith('.json')]

    def audit_landmarks(self, required_list):
        actual_set = set(self.actual_files)
        required_set = set(required_list)
        
        missing = required_set - actual_set
        extra = actual_set - required_set
        
        return sorted(list(missing)), sorted(list(extra))
    
if __name__ == "__main__":
    base_path = r"R:\TM Internships\Dept of CMF\Nynke van Jaarsveld\Code\database\groundtruth"
    
    required_set = set(LANDMARK_NAMES)
    all_missing_sets = []
    all_extra_sets = []
    patient_count = 0

    for folder_name in sorted(os.listdir(base_path)):
        full_path = os.path.join(base_path, folder_name)
        if os.path.isdir(full_path):
            patient = Patient(full_path)
            actual_set = set(patient.actual_files)
            
            # Calculate this patient's specific gaps
            missing = required_set - actual_set
            extra = actual_set - required_set
            
            all_missing_sets.append(missing)
            all_extra_sets.append(extra)
            patient_count += 1

    # THE "EASY CHECK" LOGIC:
    # Intersection (&) finds only items that exist in EVERY set provided
    if all_missing_sets:
        universally_missing = set.intersection(*all_missing_sets)
        universally_extra = set.intersection(*all_extra_sets)

        print("="*50)
        print(f"GLOBAL AUDIT (Across {patient_count} patients)")
        print("="*50)

        if universally_missing:
            print(f"\n ALWAYS MISSING ({len(universally_missing)}):")
            for m in sorted(universally_missing):
                print(f"  - {m}")
        else:
            print("\n No single file is missing from EVERY patient.")

        if universally_extra:
            print(f"\n ALWAYS EXTRA ({len(universally_extra)}):")
            for e in sorted(universally_extra):
                print(f"  + {e}")
        else:
            print("\n No single 'extra' file exists in EVERY patient.")
        print("="*50)