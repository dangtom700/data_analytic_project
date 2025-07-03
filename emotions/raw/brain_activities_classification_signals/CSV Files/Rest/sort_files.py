import os
import random


# Define the source and target directories
source_dir = "./"
target_dir = "./rest_data_random"

for i in range(600):
    # Get a list of all files in the source directory
    files = os.listdir(source_dir)

    # Pick a random file
    file = random.choice(files)

    # Get the full path of the selected file
    source_file = os.path.join(source_dir, file)

    # Get the full path of the target file
    target_file = os.path.join(target_dir, file)

    # Move the file
    os.rename(source_file, target_file)