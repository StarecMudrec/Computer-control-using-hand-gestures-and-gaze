import yaml
import numpy as np

with open("calibration_matrix.yaml", "r") as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

mtx = np.array(data['camera_matrix'])
dist = np.array(data['dist_coeff'])
rms = data['rms']