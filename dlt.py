import numpy as np

def dlt(cam_data: list, lidar_data: list) -> np.ndarray:
    """
    input cam_data: at least 6 camera points (u, v) which correspond to LiDAR
    input lidar_data: at least 6 LiDAR points (x, y, z) which correspond to camera

    output projection_matrix: projects LiDAR points to camera space
    """

    #proj_mat = #

    #return proj_mat