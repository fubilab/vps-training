import os
import numpy as np
from PIL import Image
# Define your image directory
image_directory = "/home/aziza/dsacstar/datasets/scene_2/train/rgb/"


# Initialize variables for accumulating sums
sum_rgb = np.zeros(3)
sum_sq_rgb = np.zeros(3)
num_images = 0

# Iterate through images in the directory
for filename in os.listdir(image_directory):
    if filename.endswith(".png"):
        print(filename)
        img_path = os.path.join(image_directory, filename)
        img = Image.open(img_path)
        pixels = np.array(img.getdata()) / 255.0  # Normalize pixel values
        sum_rgb += np.sum(pixels, axis=0)
        sum_sq_rgb += np.sum(pixels ** 2, axis=0)
        num_images += pixels.shape[0]

# Calculate mean and std
mean_rgb = sum_rgb / num_images
var_rgb = (sum_sq_rgb / num_images) - (mean_rgb ** 2)
std_rgb = np.sqrt(var_rgb)

print("Mean (R, G, B):", mean_rgb)
print("Std (R, G, B):", std_rgb)
