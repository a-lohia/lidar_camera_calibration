# This repository is attempting to implement LiDAR to camera calibration via Direct Linear Transform

>The goal is to solve the equation $x = \text{P}\bold{X}$ for P, where $x$ is the camera pixel coordinate, $\begin{pmatrix} u \\ v \end{pmatrix}$, $\bold{X}$ is a point in LIDAR space, $\begin{pmatrix} x \\ y \\ z \end{pmatrix}$, and $\text{P is the projection matrix P} = \text{K}R[I_3 | - X_o]$  

> [!IMPORTANT]
> This requires at least 6 points in space that are identified in the camera frame and the lidar. These points ***must not be coplanar***.