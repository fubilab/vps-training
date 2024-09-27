import os

def find_missing_files(folder1, folder2):
    filenames1 = set(os.path.splitext(file)[0] for file in os.listdir(folder1))
    filenames2 = set(os.path.splitext(file)[0] for file in os.listdir(folder2))

    missing_files = filenames1 - filenames2
    return list(missing_files)

def delete_missing_files(folder1, folder2):
    missing_files_list = find_missing_files(folder1, folder2)
    for filename in missing_files_list:
        file_path = os.path.join(folder1, filename + ".png")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")
        else:
            print(f"File {file_path} not found in folder1.")

# Example usage
folder1_path = "/home/aziza/dsacstar/datasets/scene_2/primary/"
folder2_path = "/home/aziza/dsacstar/datasets/scene_2/poses/"
delete_missing_files(folder1_path, folder2_path)

