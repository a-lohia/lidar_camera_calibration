# Written by Arya Lohia and Matthew Rao for Carnegie Mellon Racing. Fall 2024
# Test DLT from lidar to camera

from dlt import dlt
import numpy as np
import cv2

img_path =  "camera_fusion/homography_result.jpg"
path_to_cam_points = "data/fused_image_points/test_2.npy"
cam_points = np.load(path_to_cam_points)

lidar_points = np.array([
    [2.4312069416046143, 1.3126771450042725, 0.34171435236930847],
    [2.2233331203460693, 1.9558364152908325, -0.1295785903930664],
    [2.911242961883545, 3.705608606338501, -0.33062195777893066],
    [4.554427623748779, 3.7121224403381348, 0.0686786100268364],
    [3.3457372188568115, 0.6525140404701233, 0.2768925726413727],
    [2.342090606689453, 1.3372682332992554, -0.38275590538978577]
])

dlt_mat = dlt(cam_data=cam_points, lidar_data=lidar_points)

test_points = np.array([
    [2.1892471313476562, 2.1655070781707764, 0.16980226337909698],
    [4.535505771636963, 3.7224624156951904, 0.07677774876356125],
    [3.4350616931915283, 0.717289388179779, 0.14139263331890106]
])
test_points = np.hstack((test_points, np.ones((test_points.shape[0], 1))))

image = cv2.imread(img_path)
color = (0, 0, 255)

for i in range(test_points.shape[0]):
    print(dlt_mat @ test_points[i])

    x, y, z = dlt_mat @ test_points[i]   

    # divide by z to get the euclidean normed coordinates
    u, v = int(x/z), int(y/z)

    print(u,v)

    # Draw a circle at the transformed point
    cv2.circle(image, (u, v), 10, color, -1)

cv2.imshow("Fused Image", image)

cv2.waitKey(0)
cv2.destroyAllWindows()
