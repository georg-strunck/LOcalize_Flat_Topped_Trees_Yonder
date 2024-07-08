import open3d as o3d
import numpy as np
import os

# Function to find all .laz file paths in a folder and its subfolders
def find_laz_files(root_dir):
    laz_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".pcd"):
                laz_files.append(os.path.join(root, file))
    return laz_files

def show_all_pcd_in_folder(root_folder):
    # Find all .pcd file paths
    laz_file_paths = find_laz_files(root_folder)

    # Open each pcd file in folder
    for path in laz_file_paths:
        filename = path
        print(os.path.basename(filename))
        # Load the point cloud data from a .pcd file
        point_cloud = o3d.io.read_point_cloud(filename)
        # Visualize the point cloud
        o3d.visualization.draw_geometries([point_cloud])
        # print(np.asarray(point_cloud.points))
        
def show_pcd_of_name(file):
    filename = file
    # Load the point cloud data from a .pcd file
    point_cloud = o3d.io.read_point_cloud(filename)
    # Visualize the point cloud
    o3d.visualization.draw_geometries([point_cloud])
    # print(np.asarray(point_cloud.points))

# Make sure you are in the right working directory and that the relative paths are relative to that, not the folder th code is in
print("Current working directory:", os.getcwd())
# Define the root folder where you want to search for .pcd files
root_folder_or_file = "../LOFTY_datasets/biodivX/07-prec-300-10-default-Project_2024-04-25_16-47-dense_poin.pcd"  # Replace with your root folder path

# Open single file
show_pcd_of_name(root_folder_or_file)

# Open all pcd files in folder
# show_all_pcd_in_folder(root_folder_or_file)