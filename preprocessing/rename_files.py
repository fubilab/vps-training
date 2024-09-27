import os
import glob

# Specify the directory where your files are located
directory = '/home/aziza/dsacstar/datasets/scene_2/primary/'
files = glob.glob(os.path.join(directory, '*.png'))
prefix = "primary_"

for file in files:
   or_name = os.path.basename(file)
   name = or_name.replace(prefix, "").replace(".png", "")
   id = int(name)
   new_name = f"{id}.png"
   print(new_name)
   new_file_name = file.replace(os.path.basename(file), new_name)
   print(new_file_name)
   os.rename(os.path.join(directory, or_name), os.path.join(directory, new_file_name))
