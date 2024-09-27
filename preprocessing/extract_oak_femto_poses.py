import pandas as pd
import os
import shutil
from scipy.spatial.transform import Rotation as R
import numpy as np

# Read the content from your text file
#data = json.loads(open('/home/aziza/lab/orbbec/2024-06-12_19-20-57_map/poses.json','r'))
data = pd.read_json(path_or_buf='/home/aziza/lab/final_test/oak/1/data.jsonl', lines=True)
images30fps = "/home/aziza/lab/final_test/oak/1/fps30/"
images_for_poses = "/home/aziza/lab/final_test/oak/1/rgb/"
# Create a directory to save the individual pose files
output_dir = '/home/aziza/lab/final_test/oak/1/poses/'
os.makedirs(output_dir, exist_ok=True)

def quat_to_matrix(quaternion, translation_vector):
    rotation = R.from_quat(quaternion)
    rotation_matrix = rotation.as_matrix()
    # Initialize the 4x4 transformation matrix
    transformation_matrix = np.eye(4)
    # Set the rotation part
    transformation_matrix[:3, :3] = rotation_matrix
    # Set the translation part
    transformation_matrix[:3, 3] = translation_vector
    return transformation_matrix

def clean_pose(pose):

    #print(pose['orientation'], pose['position'])
    transl = [float(pose['position']['x']), float(pose['position']['y']), float(pose['position']['z'])]
    rotation = []
    for key in ['x', 'y', 'z', 'w']:
        rotation.append(float(pose['orientation'][key]))

    matrix = quat_to_matrix(rotation, transl)
    #print(matrix)
    return matrix



gt_to_frame = 0

for i, row in data.iterrows():
    if not pd.isna(row.loc['groundTruth']):
        gt_to_frame = 1
        pose = row.get('groundTruth')
        pose = clean_pose(pose)

    if gt_to_frame == 1 and len(str(row['frames'])) > 3 and len(row['frames']) == 3:
            frame = row['frames'][2]['number']
            gt_to_frame = 0

            # Save the pose data to the file
            filename = os.path.join(output_dir, f'{frame}.txt')
            with open(filename, 'w') as pose_file:
                for pose_row in pose:
                    pose_file.write(' '.join(map(str, pose_row)) + '\n')

            src_file = os.path.join(images30fps, f'{frame}.png')
            dest_file = os.path.join(images_for_poses, f'{frame}.png')
            shutil.copy(src_file, dest_file)








