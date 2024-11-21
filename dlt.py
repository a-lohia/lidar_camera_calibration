# Written by Arya Lohia and Matthew Rao for Carnegie Mellon Racing. Fall 2024

import numpy as np

# TODO: Add support for least squares regression when using redundant points
def dlt(cam_data: list, lidar_data: list) -> np.ndarray:
    """
    Implements a direct linear transform for 6 lidar points to 6 camera pixels.

    input cam_data: at least 6 camera points (u, v) which correspond to LiDAR
    input lidar_data: at least 6 LiDAR points (x, y, z) which correspond to camera

    output projection_matrix: projects LiDAR points to camera space
    """
    assert cam_data.shape[0] == 6

    mat = []

    for i in range(cam_data.shape[0]):
        X, Y, Z = lidar_data[i]
        u, v = cam_data[i]

        mat.append([-X, -Y, -Z, -1, 0, 0, 0, 0, u*X, u*Y, u*Z, u])
        mat.append([0, 0, 0, 0, -X, -Y, -Z, -1, v*X, v*Y, v*Z, v])
        
    mat = np.stack(mat)
    
    _, _, Vt = np.linalg.svd(mat)

    return Vt[-1].reshape(3, 4)