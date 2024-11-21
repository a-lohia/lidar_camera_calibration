# This repository implements LiDAR to camera calibration via Direct Linear Transform

## btw this is not renering properly on GitHub (if you want to see the equations open in vscode)

```math 
\text{The goal is to solve the equation } \vec{x} = \text{P}\mathbf{X} \text{ for P}
```


```math 
\vec{x} \text{ is the camera pixel coordinate (homogeneous coordinates)}  \begin{pmatrix} u \\ v \\ 1 \end{pmatrix} \\  

\mathbf{X} \text{ is a point in LIDAR space (homogeneous coordinates)} \begin{pmatrix} x \\ y \\ z \\ 1 \end{pmatrix} \\

\text{P is the projection matrix, P: } \R^{4} \rightarrow \R^{3} \text{, P} = \textbf{K}R[I_3 | - X_0] \\
\textbf{K} \text{ is the intrinsic camera parameter matrix} \\
R \text{ is the rotation matrix} \\
X_0 \text{ is the location of the camera in LiDAR space}
```

> [!IMPORTANT]
> This requires at least 6 points in space that are identified in the camera frame and the lidar. These points ***must not be coplanar*** (would result in a reduction of rank of the final matrix making solving for the parameters impossible).

```math
\begin{align*}
    \vec{x_i} &= \text{P}\mathbf{X_i} \\
    \vec{x_i} &= \begin{bmatrix} - A^T -\\ - B^T - \\ - C^T - \end{bmatrix}\mathbf{X_i} \\
    \begin{pmatrix} u_i \\ v_i \\ w_i \end{pmatrix}&= \begin{bmatrix} A^T\mathbf{X_i}\\ B^T\mathbf{X_i} \\ C^T\mathbf{X_i} \end{bmatrix} \\ \text{divide by w to normalize into 2d pixel}
    \begin{pmatrix} \frac{u_i}{w_i} \\ \frac{v_i}{w_i} \\ 1 \end{pmatrix} &= \begin{bmatrix} \frac{A^T\mathbf{X_i}}{C^T\mathbf{X_i}} \\ \frac{B^T\mathbf{X_i}}{C^T\mathbf{X_i}} \\ 1 \end{bmatrix} \\ \text{now we have a system of two equations}
     \begin{pmatrix} x_i \\ y_i \\ 1 \end{pmatrix} &= \begin{bmatrix} \frac{A^T\mathbf{X_i}}{C^T\mathbf{X_i}} \\ \frac{B^T\mathbf{X_i}}{C^T\mathbf{X_i}} \\ 1 \end{bmatrix} \\
    \begin{align*}
        x_i &= \frac{A^T\mathbf{X_i}}{C^T\mathbf{X_i}} \\
        y_i &= \frac{B^T\mathbf{X_i}}{C^T\mathbf{X_i}}
    \end{align*} \\

    \begin{align*}
        x_i \cdot C^T\mathbf{X_i} - A^T\mathbf{X_i} &= 0\\
        y_i \cdot C^T\mathbf{X_i} - B^T\mathbf{X_i} &= 0
    \end{align*} \\

    \begin{align*}
        - \mathbf{X_i}^TA \phantom{\mathbf{X_i}^TB} + x_i \cdot \mathbf{X_i}^TC &= 0\\
        \phantom{\mathbf{X_i}^TA} - \mathbf{X_i}^TB + y_i \cdot \mathbf{X_i}^TC &= 0
    \end{align*} \\ \text{2 equations, 12 unknowns, }

    \begin{pmatrix} \mathbf{-X_i}^T & \vec{0} & x_i\mathbf{X_i}^T \\ \vec{0} & \mathbf{-X_i}^T & x_i\mathbf{X_i}^T \end{pmatrix}
    \begin{bmatrix} A^T \\ B^T \\ C^T\end{bmatrix} &= 0 \\
    \text{for each equation we have one camera pixel and one lidar point} \\ \text{In order to solve generally, we can stack more correspondance eqns.} \\
    \begin{pmatrix} 
        \mathbf{-X_1}^T & \vec{0} & x_1\mathbf{X_1}^T \\ 
        \vec{0} & \mathbf{-X_1}^T & x_1\mathbf{X_1}^T \\
        \dots & \dots & \dots \\
        \mathbf{-X_i}^T & \vec{0} & x_i\mathbf{X_i}^T \\ 
        \vec{0} & \mathbf{-X_i}^T & x_i\mathbf{X_i}^T \\
        \dots & \dots & \dots \\
        \mathbf{-X_I}^T & \vec{0} & x_I\mathbf{X_I}^T \\ 
        \vec{0} & \mathbf{-X_I}^T & x_I\mathbf{X_I}^T \\
    \end{pmatrix}
    \begin{bmatrix} A^T \\ B^T \\ C^T\end{bmatrix} &= 0 \\

    \mathbf{A}\vec{p} = \vec{0} 
\end{align*}

\\\mathbf{A}\text{ is an (Ix12) matrix and } \vec{p} \text{ is a (12x1) vector. Solve using SVD}
```