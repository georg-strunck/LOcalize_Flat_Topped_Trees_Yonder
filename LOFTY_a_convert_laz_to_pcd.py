import os
import laspy
import open3d as o3d
import numpy as np

# Make sure you are in the right working directory and that the relative paths are relative to that, not the folder th code is in
print("Current working directory:", os.getcwd())

# Define the source folder with .laz files and the destination folder for .pcd files
source_folder = os.path.abspath("../LOFTY_datasets/biodivX_finals")
destination_folder = os.path.abspath("../LOFTY_datasets/biodivX_finals")
# Print the paths to verify
print("Source folder path:", source_folder)
print("Destination folder path:", destination_folder)

# Create the destination folder if it doesn't exist
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Function to convert .laz files to .pcd and save in the destination folder
def convert_laz_to_pcd(src_folder, dest_folder):
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.lower().endswith(".laz"):
                source_file = os.path.join(root, file)

                # Load the .laz file
                in_laz = laspy.read(source_file)

                # Access the point cloud data
                x = in_laz.x
                y = in_laz.y
                z = in_laz.z

                # Create a PointCloud object
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(np.vstack((x, y, z)).T)

                # Save the PointCloud as a .pcd file in the destination folder
                output_file = os.path.splitext(file)[0] + ".pcd"
                destination_file = os.path.join(dest_folder, output_file)
                o3d.io.write_point_cloud(destination_file, pcd)

                print(f"Converted {file} to {output_file}")

# Convert .laz files to .pcd and save in the destination folder
convert_laz_to_pcd(source_folder, destination_folder)

print("Batch conversion of .laz files to .pcd files complete.")


