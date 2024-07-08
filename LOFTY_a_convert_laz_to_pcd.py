import os
import laspy
import open3d as o3d
import numpy as np

# Make sure you are in the right working directory and that the relative paths are relative to that, not the folder th code is in
print("Current working directory:", os.getcwd())

# Define the source folder with .laz files and the destination folder for .pcd files
source_folder = os.path.abspath("../LOFTY_datasets/biodivX")
destination_folder = os.path.abspath("../LOFTY_datasets/biodivX")
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




# import laspy
# import numpy as np
# import os

# def lofty_convert_laz_to_pcd(input_file_path, output_file_path):

#     # Load the .laz file
#     in_laz = laspy.read(input_file_path)

#     # Access the point cloud data
#     points = np.vstack((in_laz.x, in_laz.y, in_laz.z)).T

#     # Create a new .pcd file
#     header = """\
#     # .PCD v.7 - Point Cloud Data file format
#     VERSION .7
#     FIELDS x y z
#     SIZE 4 4 4
#     TYPE F F F
#     COUNT 1 1 1
#     WIDTH {}
#     HEIGHT 1
#     VIEWPOINT 0 0 0 1 0 0 0
#     POINTS {}
#     DATA ascii
#     """.format(len(points), len(points))

#     # Write the header and point cloud data to the .pcd file
#     with open(output_file_path, "w") as pcd_file:
#         pcd_file.write(header)
#         np.savetxt(pcd_file, points, fmt="%f %f %f")

#     return print(f".laz to .pcd conversion complete. Output saved as {output_file_path}")

# ## Single file conversion manually
# # Replace with the path to your .laz file
# input_laz_file = "LOFTY_datasets\syssifoss\BR04\TLS\TLS-on_BR04_2019-07-04.laz"
# # Replace with the desired output .pcd file path
# output_pcd_file = os.path.splitext(os.path.basename(input_laz_file))[0] + '.pcd'
# # Run conversion
# lofty_convert_laz_to_pcd(input_laz_file, output_pcd_file)


