# Odometry demo for AI Tinkerers meetup 20th November 2024, by Vitalii, Taras and team (c) DeepX, Covijn Ltd 

import cv2
import numpy as np
import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from tqdm import tqdm

class VisualOdometry():
    def __init__(self):
        self.lk_params = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
        self.trajectory = [(0, 0)]  # Initial position in the trajectory
        self.prev_frame = None  # To store the previous frame for tracking
        self.prev_keypoints = None  # To store keypoints from the previous frame
        self.gf_params = dict(maxCorners=500, qualityLevel=0.05, minDistance=30, blockSize=7)
        self.redetect_threshold = 10  # Minimum keypoints to maintain tracking

    def detect_keypoints(self, frame):
        return cv2.goodFeaturesToTrack(frame, **self.gf_params)

    def track_keypoints(self, prev_frame, next_frame, prev_keypoints):
        if prev_keypoints is None:
            return None, None
        next_keypoints, status, err = cv2.calcOpticalFlowPyrLK(prev_frame, next_frame, prev_keypoints, None, **self.lk_params)
        if next_keypoints is None or status is None:
            return None, None
        return prev_keypoints[status == 1], next_keypoints[status == 1]

    def update_camera_trajectory(self, tracked_prev, tracked_next):
        if tracked_prev is None or tracked_next is None or len(tracked_prev) < 3:
            self.trajectory.append(self.trajectory[-1])  # Use the previous position
            return
        transformation, _ = cv2.estimateAffinePartial2D(tracked_prev, tracked_next)
        if transformation is not None:
            dx, dy = transformation[0, 2], transformation[1, 2]
            last_position = self.trajectory[-1]
            new_position = (last_position[0] + dx, last_position[1] + dy)
            self.trajectory.append(new_position)
        else:
            self.trajectory.append(self.trajectory[-1])

    def process_frame(self, frame, draw_keypoints=True):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.prev_frame is None:
            self.prev_frame = gray
            self.prev_keypoints = self.detect_keypoints(gray)
            return

        tracked_prev, tracked_next = self.track_keypoints(self.prev_frame, gray, self.prev_keypoints)
        self.update_camera_trajectory(tracked_prev, tracked_next)

        # Re-detect keypoints if the count drops below the threshold
        if tracked_next is None or len(tracked_next) < self.redetect_threshold:
            self.prev_keypoints = self.detect_keypoints(gray)
        else:
            self.prev_keypoints = tracked_next.reshape(-1, 1, 2)

        self.prev_frame = gray

        if draw_keypoints and self.prev_keypoints is not None:
            for point in self.prev_keypoints:
                x, y = point.ravel()
                cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)  # Red dots for keypoints

def plot_trajectory(predicted_path, frame_size):
    predicted_path = np.array(predicted_path)
    plt.figure(figsize=(8, 6))
    plt.plot(predicted_path[:, 0], predicted_path[:, 1], label='Camera Trajectory', color='green', linewidth=2)
    plt.legend()
    plt.title("Estimated Camera Trajectory")
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_arr = np.asarray(bytearray(buf.read()), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    plt.close()
    return cv2.resize(img, frame_size)

def track_movement(input_path, output_folder, skip_frames=1):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error opening video file")
        return

    ret, first_frame = cap.read()
    if not ret:
        print("Failed to read the first frame.")
        return

    frame_height, frame_width = first_frame.shape[:2]
    prefix = datetime.now().strftime('%y-%m-%d_%H-%M-%S_')
    output_file = f"{prefix}{os.path.basename(input_path)}"
    output_path = os.path.join(output_folder, output_file)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 20, (frame_width * 2, frame_height))
    vo = VisualOdometry()
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_idx = 0
    while frame_idx < frame_count:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break

        vo.process_frame(frame, draw_keypoints=True)
        trajectory_image = plot_trajectory(vo.trajectory, (frame_width, frame_height))
        combined_frame = np.vstack((frame, trajectory_image))
        out.write(combined_frame)
        cv2.imshow('Trajectory Visualization', combined_frame)

        frame_idx += skip_frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Output video saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python odo.py <input_video>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_folder = "results"
    os.makedirs(output_folder, exist_ok=True)
    track_movement(input_path, output_folder, skip_frames=5)
