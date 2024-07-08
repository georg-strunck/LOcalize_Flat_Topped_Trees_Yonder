import os
import shutil

# Define the main folder, the destination folder, and the exclusion string
main_folder = "LOFTY_datasets\syssifoss\original_data_structure"  # Replace with your main folder path
destination_folder = "LOFTY_datasets\syssifoss\laz_data"  # Replace with your destination folder path
exclusion_string = "TLS"

# Function to copy .laz files from the source to destination folder
def copy_laz_files(src_folder, dest_folder, exclusion_string):
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.lower().endswith(".laz") and exclusion_string not in file:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(dest_folder, file)
                shutil.copy2(source_file, destination_file)
                print(f"Copied {file} to {destination_file}")

# Create the destination folder if it doesn't exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Copy .laz files (excluding those containing the exclusion string) from subfolders
copy_laz_files(main_folder, destination_folder, exclusion_string)

print("Copying .laz files (excluding those with '", exclusion_string, "' in name) complete.")