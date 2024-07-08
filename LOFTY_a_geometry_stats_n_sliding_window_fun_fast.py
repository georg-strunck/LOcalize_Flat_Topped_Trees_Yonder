import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import time
from tqdm import tqdm  # For progress bar

def lofty_get_pcd_length_width_height(pcd_in, Print=True):
    t_0 = time.time()
    pcd_arr = np.asarray(pcd_in.points)
    # Calculate the extents along each axis
    x_extent = np.ptp(pcd_arr[:, 0])
    y_extent = np.ptp(pcd_arr[:, 1])
    z_extent = np.ptp(pcd_arr[:, 2])
    x_min = min(pcd_arr[:, 0])
    y_min = min(pcd_arr[:, 1])
    z_min = min(pcd_arr[:, 2])
    if Print:
        print('The point cloud has a maximum extent in \nWidth/x of\t', x_extent, '[m] \nLength/y of\t', y_extent, '[m] \nHeight/z of\t', z_extent, '[m]')
        print('\nMin point: \nNorthing:\t', min(pcd_arr[:, 0]),'[m]\nEasting:\t', min(pcd_arr[:, 1]),'[m]\nHeight:\t\t', min(pcd_arr[:, 2]),'[m]')
        print('Geometry information retrieved in ', time.time()-t_0, '[s]')
    return [x_extent, y_extent, z_extent, x_min, y_min, z_min]

def lofty_get_sliding_window_bboxes2d(whole_pcd, overlap=0, kernel_size=3, debug=False):
    '''
    This function takes a given pointcloud and returns a list containing the window corners for each window frameof a sliding window method.
    The window slides over the pointcloud horizontally (eg, only 2d).
    whole_pcl:      the input pointcloud in open3d pcd format
    overlap:        The overlap each column and row will have with the previous window. 
                    Ranging from 0 to 0.9.
                    The default is set to 0, meaning no overlap and perfectly aligned.
    kernel_size:    Size in [m] of the sliding window for both width and length. Default is set to 3[m]                    
    debug:          Include print statements and visualizations. Default is False.  
    
    Returns:
    windows_sizes:  List of lists: [[window1_start_x, window1_start_y, window1_end_x, window1_end_y]]  
    '''
    
    # Get geometry info of pcd
    [x_extent, y_extent, z_extent, x_min, y_min, z_min] = lofty_get_pcd_length_width_height(whole_pcd, Print=False)
    
    t_0 = time.time()
    # Define start and stop of sliding window area
    start_x = x_min
    start_y = y_min
    end_x = x_min + x_extent
    end_y = y_min + y_extent
    # Initiate empty list containing the cornerpoints of each window
    window_sizes = []
    # First slide along x direction first and then y:
    # Slide y
    while start_y < end_y+kernel_size-overlap*kernel_size:
        # Slide x
        while start_x < end_x+kernel_size-overlap*kernel_size:
            # Append the box to the window list
            window_sizes.append([start_x, start_y, start_x+kernel_size, start_y+kernel_size])            
            # Slide to next x location
            start_x += kernel_size - overlap*kernel_size
        # Reset start_x
        start_x = x_min
        # Slide to next y location
        start_y += kernel_size - overlap*kernel_size
    # if debug:
    print(len(window_sizes), ' 2D Bounding boxes created in ', time.time()-t_0, '[s]')
    return window_sizes

def lofty_create_bboxes_from_2d_array(pcd_in, bboxes2D, z_margin=1, visualize=False):
    '''
    This function draws the boudning boxes for each window location as defined by the sliding window approach.
    pcd_in:     pointcloud on which the bounding boxes will be drawn
    bboxes2d:   List containing a list of [start_x, start_y, end_x, end_y] for each window frame
    '''
    # Get min max height of scene
    [x_extent, y_extent, z_extent, x_min, y_min, z_min] = lofty_get_pcd_length_width_height(pcd_in)
    
    t_0 = time.time()
    # Set the z-coordinates of the bboxes3d
    bbox3d_z_min  = z_min - z_margin
    bbox3d_z_max  = z_min + z_extent + z_margin
    
    # Create list of egeometries to plot
    bboxes3d_list = []
    colors = [(np.random.random(), np.random.random(), np.random.random()) for _ in range(len(bboxes2D))]
    for frame_id, frame in enumerate(tqdm(bboxes2D, desc="Creating 3D bounding boxes", unit="bboxes")):
        # Define the minimum and maximum points of box
        min_point = [frame[0], frame[1], bbox3d_z_min]
        max_point = [frame[2], frame[3], bbox3d_z_max]
        bbox3d = o3d.geometry.AxisAlignedBoundingBox(min_bound=min_point, max_bound=max_point)
        cropped_pcd = pcd_in.crop(bbox3d)
        if len(cropped_pcd.points) > 10:
            bbox3d.color = colors[frame_id]
            bboxes3d_list.append(bbox3d)
    print(len(bboxes3d_list), ' 3D Bounding boxes corner points created in ', time.time()-t_0, '[s]')
    if visualize:
        t_0 = time.time()
        geometries = bboxes3d_list
        geometries.append(pcd_in)
        o3d.visualization.draw_geometries(geometries)
        print('3D Bounding boxes visualized in ', time.time()-t_0, '[s]')
    
    return bboxes3d_list
    
# def lofty_get_cropped_pcd_list(pcd_in, bboxes3d_list):
#     '''
#     Splitting up the input pointcloud into a list of multiple smaller pointclouds
#     '''

def lofty_calc_canopy_flatness_per_window(pcd_in, bboxes3d_list, downsampling_factor, min_points_in_cloud=7000, inliers=100, scaled=0, k_margin_points_z=10, 
                                          visualize=False, kernel_size=3, show_n_perc_best_kernels=10, colormap="cool"):
    '''
    1. Calculating the vertical distance of the #inliers closest points to the k_margin_points_z highest point in the cropped pointcloud.
    2. Storing that value per window/bbox and normalizing. The window with smallest distance (=horizontal spread) is the flattest.
    pcd_in:
    bboxes3d_list:      List of 3D corners for all bounding boxes
    min_points_in_cloud:Minimum of points that are required to be present in subset pointcloud. 
                        This value HAS to be tuned using a kernel size of 10[m]!!!
    inliers:            How many points in the vicinity should be considered for the flatness estimation. 
    scaled:             If not 0, it gives the percentage of points of the cropped pointcloud that will be used for the distance estimation 
                        (instead of 'inliers' variable).
                        Recommended to be used instead of manual inliers because it scales with the downsampling
    k_margin_points_z:  How many points on the top of the cropped bbox are considered as outliers.
    visualize:          Option to turn the plotting on/off. Plotting takes a very long time, whereas the calculations are rather fast.
    kernel_size:        Kernel size of the planes to be painted in the visualization
    show_n_perc_best_kernels:   For visualization, choose only the 10% best kernel planes of the pointcloud and skip the others. 
        	                    This improves the speed of the visualization and also enhances the heatmap colouring for easier understanding.
    '''
    t_0 = time.time()
    landingsite_flatness = []
    landingsite_center_position = []
    
    # for bbox3d in bboxes3d_list:
    for idx, bbox3d in enumerate(tqdm(bboxes3d_list, desc="Processing Kernels, individual RANSAC plane fitting", unit="kernel")):
        # Crop pcd to bounding box
        subset_pcd = pcd_in.crop(bbox3d)
        # Check if enough points in subset of pointcloud. min points based on quadratic rule using the kernel length.
        if len(subset_pcd.points) > min_points_in_cloud*(kernel_size**2)/(10**2)/downsampling_factor:
        # if scaled!=0 and len(subset_pcd.points)>inliers:
            if scaled<1:
                print('Attention! The \'scaled\' percentage you entered is smaller than 1\%.\nWas this your intention or did you mean to write as \%, eg 30\% instead of 0.3?')
            inliers = int(len(subset_pcd.points)*scaled/100)
            # print('Using scaled inliers. Inliers variable now set to:', inliers)
        # # Check if there are enough points in the box, else skip
        # if len(subset_pcd.points) > inliers:
            # Get the z-coordinates of all points
            z_coordinates = np.asarray(subset_pcd.points)[:, 2]
            # Create an indices list defining the height of the points in ascending order --> highest point will be last entry
            ids_sorted_by_height = np.argsort(z_coordinates)
            # Get the height
            
            # Calculate the vertical distances from the reference point to all points
            vertical_distances = np.abs(z_coordinates - z_coordinates[ids_sorted_by_height[-k_margin_points_z]])
            # Sort the points based on vertical distances and get the indices
            ids_sorted_by_dist = np.argsort(vertical_distances)
            # Calculate the average distance of the #inliers closest points and do not include the 0 point itself
            avg_dist = np.mean(vertical_distances[ids_sorted_by_dist[1:inliers]])
            
            # Store the center position of the box and the height of the point
            bbox_center = bbox3d.get_center()
            center_pos = [bbox_center[0], bbox_center[1], np.mean(z_coordinates[ids_sorted_by_height[-inliers]])]
            landingsite_center_position.append(center_pos)
            # Store the avg_dist
            landingsite_flatness.append(avg_dist)
        else:
            landingsite_center_position.append(bbox3d.get_center())#+bbox3d.get_center()[2]/2)
            landingsite_flatness.append(10)
    
    # Set outlier kernel to worst inlier kernel distance to reduce spread
    biggest_dist = max(np.asarray(landingsite_flatness)[np.asarray(landingsite_flatness)!=10])
    landingsite_flatness = [biggest_dist if value == 10 else value for value in landingsite_flatness]
    
    print('Flattest kernels found in ', time.time()-t_0, '[s]')
    print('Finished calculations. Visualizing now...')
    if visualize:
        t_0 = time.time()
        # Create list containing id's of the #% best kernels for better visualization
        ids_best_landing_flatness = np.argsort(landingsite_flatness)[0:int(len(landingsite_flatness)*show_n_perc_best_kernels/100)]
        # Create a colormap (e.g., "coolwarm" for a blue-to-red colormap)
        colormap = plt.get_cmap(colormap)
        # Generate a list of colors based on the normalized values
        best_land_dist = [landingsite_flatness[i] for i in ids_best_landing_flatness]
        colors = [colormap(value) for value in ((np.array(best_land_dist) - min(best_land_dist)) / (max(best_land_dist) - min(best_land_dist)))]
        # Create empty list for geometries of planes
        flat_planes = []
        for color_id, id in enumerate(ids_best_landing_flatness):
            mi_plane = o3d.geometry.TriangleMesh.create_box(width=kernel_size, height=kernel_size, depth=0.01)
            mi_plane.translate(landingsite_center_position[id] - mi_plane.get_center() + [0, 0, 1])
            mi_plane.paint_uniform_color(colors[color_id][:3])
            flat_planes.append(mi_plane)
        geometries = flat_planes
        geometries.append(pcd_in)
        o3d.visualization.draw_geometries(geometries)
        print('Landing planes on flat canopies visualization took', time.time()-t_0, '[s]')
        
    return landingsite_flatness, landingsite_center_position
    
    
pcd = o3d.io.read_point_cloud("../LOFTY_datasets/biodivX/07-prec-300-10-default-Project_2024-04-25_16-47-dense_poin.pcd")#("ALS-on_KA10_2019-07-05_300m.pcd")

my_kernel = 4
skip_points = 5
show_perc_best_kern = 5 #before 10
pcd = pcd.uniform_down_sample(every_k_points=skip_points)
bboxes2d_list = lofty_get_sliding_window_bboxes2d(pcd, kernel_size=my_kernel)
bboxes3d_list = lofty_create_bboxes_from_2d_array(pcd, bboxes2d_list, visualize=False)
# Nice colors for plotting are "cool"tab20c"Set1"YlGnBu"hot"
# See https://matplotlib.org/stable/users/explain/colors/colormaps.html for more colormaps
lofty_calc_canopy_flatness_per_window(pcd, bboxes3d_list, downsampling_factor=skip_points, visualize=True, kernel_size=my_kernel, 
                                      show_n_perc_best_kernels=show_perc_best_kern, colormap='cool', inliers=300, scaled=20) 