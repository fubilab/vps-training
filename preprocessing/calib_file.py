content = "565" #"" # "571.879"

import os
folder_path = "/home/aziza/lab/final_test/oak/1/rgb/"
for filename in os.listdir(folder_path):
    if os.path.isfile(os.path.join(folder_path, filename)):
        filename_2 = os.path.splitext(filename)[0]
        #print(filename_without_extension)
        with open("/home/aziza/lab/final_test/oak/1/calibration/" + filename_2 + ".txt", "w") as file:
            file.write(content)

