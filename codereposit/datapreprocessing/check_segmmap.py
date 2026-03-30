import SimpleITK as sitk
import numpy as np

pat = 'ma_003'

image_path = fr"R:\TM Internships\Dept of CMF\Nynke van Jaarsveld\Code\database\groundtruth\{pat}\{pat}_landmark_map.nii.gz"

segm_map = sitk.ReadImage(image_path)

segm_array = sitk.GetArrayFromImage(segm_map)

if __name__ == "__main__":
    print(f'Multilabel segmentation map patient {pat} contains following labels {np.unique(segm_array)}')