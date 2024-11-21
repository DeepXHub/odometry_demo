# Odometry Demo

Odometry Demo by DeepX team for AI tinkerers meetup (Palo Alto, 20th November 2024).

![CleanShot 2024-11-20 at 16 20 07@2x](https://github.com/user-attachments/assets/f5e8807a-ed02-400e-8111-20a184e94d12)


The **Lucas-Kanade Optical Flow** (calcOpticalFlowPyrLK) and **Affine Transformation Estimation** (estimateAffinePartial2D) serve complementary purposes in this simple visual odometry pipeline. 

**Lucas-Kanade Optical Flow**:
* Tracks individual keypoints (features) between consecutive frames.
* Provides the correspondence between keypoints in the previous and current frames (e.g., where a feature in frame 1 appears in frame 2).
* Outputs the displacement of keypoints but not the overall motion of the camera or object.

**Affine Transformation**:
* Computes the overall motion model (translation, rotation, scaling) based on the displacement of keypoints tracked by Lucas-Kanade.
* Outputs a transformation matrix that summarizes the motion of the camera (or scene) between frames.
* Provides a robust estimation of motion even when some keypoints are noisy or lost.
  
**Step-by-Step Breakdown**:
1. Tracking Keypoints with Lucas-Kanade:
* Tracks how individual features move between consecutive frames.
This step outputs two sets of keypoints:
* tracked_prev: Keypoints in the previous frame.
* tracked_next: Corresponding keypoints in the current frame.
2. Estimating Motion with Affine Transformation:
* Takes the tracked keypoints (tracked_prev and tracked_next) and computes the overall motion model between the two frames.
This summarizes the relative translation, rotation, and scaling, which is used to update the camera trajectory.


![CleanShot 2024-11-20 at 16 20 52@2x](https://github.com/user-attachments/assets/f45d40c9-6191-4be8-be33-16b91fac768d)

**Analogy**:
Imagine you're tracking a car's path using landmarks:
* Lucas-Kanade is like identifying and following individual landmarks (e.g., "this tree moved from here to there").
* Affine transformation is like estimating the car's movement (e.g., "the car moved forward and slightly rotated") based on the movement of the landmarks.

Both are essential:
* Lucas-Kanade gives you the **local movement of points**.
* Affine transformation combines these movements into a **global motion model**.

![CleanShot 2024-11-20 at 16 25 47@2x](https://github.com/user-attachments/assets/03d33cc6-f4ea-43ff-83a8-119746d53d57)

![CleanShot 2024-11-20 at 16 26 13@2x](https://github.com/user-attachments/assets/647c0cd7-6b77-4dd7-89a5-49f1e54054e1)

![CleanShot 2024-11-20 at 16 26 49@2x](https://github.com/user-attachments/assets/9247ed53-226d-4229-a8a0-49c0a3b3850c)





