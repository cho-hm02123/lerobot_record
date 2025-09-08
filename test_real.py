import os
import time
import numpy as np
import cv2
from pathlib import Path
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.realsense.configuration_realsense import RealSenseCameraConfig
from lerobot.cameras.realsense.camera_realsense import RealSenseCamera
from lerobot.cameras.configs import ColorMode, Cv2Rotation

from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features, build_dataset_frame
from lerobot.constants import HF_LEROBOT_HOME
import logging

from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy

from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say, get_safe_torch_device
from lerobot.utils.visualization_utils import _init_rerun
from lerobot.record import record_loop

# Create a `RealSenseCameraConfig` specifying your camera’s serial number and enabling depth.
config = RealSenseCameraConfig(
    serial_number_or_name="233722071057",
    fps=15,
    width=640,
    height=480,
    color_mode=ColorMode.RGB,
    use_depth=True,
    rotation=Cv2Rotation.NO_ROTATION
)

# Create a `RealSenseCameraConfig` specifying your camera’s serial number and enabling depth.
camera_config = {
    "grip": OpenCVCameraConfig(index_or_path=2, width=640, height=480, fps=30),
    "realsense": config
}

robot_config = SO101FollowerConfig(
    port="/dev/ttyFR",
    id="follwer_robot_arm",
    cameras=camera_config
)

teleop_config = SO101LeaderConfig(
    port="/dev/ttyTR",
    id="leader_robot_arm",
)

# Initialize the robot and teleoperator
robot = SO101Follower(robot_config)
teleop = SO101Leader(teleop_config)

robot.connect()
teleop.connect()

while True:
    observation = robot.get_observation()
    action = teleop.get_action()
    robot.send_action(action)    

    if "realsense" in observation and observation["realsense"] is not None:
        frame_top = observation["realsense"]


        frame_rgb_top = cv2.cvtColor(frame_top, cv2.COLOR_BGR2RGB)
        frame_rgb_top = cv2.resize(frame_rgb_top, (640, 380))
        cv2.imshow("Top Camera", frame_rgb_top)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # # RealSense 카메라 데이터 처리
    # if "realsense" in observation and observation["realsense"] is not None:
    #     realsense_data = observation["realsense"]
        
    #     # 딕셔너리가 아닌 NumPy 배열로 반환되는 경우
    #     if isinstance(realsense_data, np.ndarray):
    #         if realsense_data.ndim == 2:
    #             # 2차원 배열은 깊이 이미지로 간주합니다.
    #             depth_image = realsense_data
    #             print("깊이 이미지 형태:", depth_image.shape)
    #             normalized_depth = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    #             cv2.imshow("RealSense Depth", normalized_depth)

    #         elif realsense_data.ndim == 3:
    #             # 3차원 배열은 RGB 이미지로 간주합니다.
    #             rgb_image = realsense_data
    #             print("RGB 이미지 형태:", rgb_image.shape)
    #             rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
    #             cv2.imshow("RealSense RGB", rgb_image)

    #     # 딕셔너리로 반환되는 경우 (기존 방식)
    #     elif isinstance(realsense_data, dict):
    #         if "depth" in realsense_data and realsense_data["depth"] is not None:
    #             depth_image = realsense_data["depth"]
    #             print("깊이 이미지 형태:", depth_image.shape)
    #             normalized_depth = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    #             cv2.imshow("RealSense Depth", normalized_depth)

    #         if "rgb" in realsense_data and realsense_data["rgb"] is not None:
    #             rgb_image = realsense_data["rgb"]
    #             rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
    #             cv2.imshow("RealSense RGB", rgb_image)

    # # OpenCV 카메라 데이터 처리
    # if "grip" in observation and observation["grip"] is not None:
    #     grip_image = observation["grip"]
    #     grip_image = cv2.cvtColor(grip_image, cv2.COLOR_BGR2RGB)
    #     cv2.imshow("Grip Camera", grip_image)

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

cv2.destroyAllWindows()

