import pandas as pd
import os

# Read the content from your text file
#data = json.loads(open('/home/aziza/lab/orbbec/2024-06-12_19-20-57_map/poses.json','r'))
data = pd.read_json(path_or_buf='/home/aziza/lab/oak/2024-06-27_16-50-43_map/poses.jsonl', lines=True)
#print(data)
# Extract the poses from the "rgb" key
frame_id = data['frameId']
#print(frame_id)

poses = data['poses'].values


# Create a directory to save the individual pose files
output_dir = '/home/aziza/lab/oak/2024-06-27_16-50-43_map/poses/'
os.makedirs(output_dir, exist_ok=True)

# Loop through each pose
for i, pose in enumerate(poses, start=0):
    # Create a filename based on the frame ID
    filename = os.path.join(output_dir, f'{frame_id[i]}.txt')

    rgb_pose = pose['primary']
    print(rgb_pose)

    # Save the pose data to the file
    with open(filename, 'w') as pose_file:
        for row in rgb_pose:
            pose_file.write(' '.join(map(str, row)) + '\n')

    print(f"Saved pose {frame_id[i]} to {filename}")

print("All poses extracted and saved successfully!")
