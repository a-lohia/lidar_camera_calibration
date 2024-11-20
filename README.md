# This repository is attempting to implement LiDAR to camera calibration via Direct Linear Transform

> The goal is to solve the equation $\vec{x} = \text{P}\mathbf{X}$ for P, where $\vec{x}$ is the camera pixel coordinate, $\begin{pmatrix} u \\ v \end{pmatrix}$, $\mathbf{X}$ is a point in LIDAR space, $\begin{pmatrix} x \\ y \\ z \end{pmatrix}$, and $\text{P is the projection matrix P} = \textbf{K}R[I_3 | - X_0]$  

- $$\textbf{K} \text{ is the intrinsic camera parameter matrix}$$
- $$R \text{ is the rotation matrix}$$
- $$X_0 \text{ is the location of the camera in LiDAR space}$$



> [!IMPORTANT]
> This requires at least 6 points in space that are identified in the camera frame and the lidar. These points ***must not be coplanar*** (would result in a reduction of rank of the final matrix making solving for the parameters impossible).


