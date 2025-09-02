import time
import logging

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features

from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower

from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import _init_rerun
from lerobot.record import record_loop

NUM_EPISODES = 1
FPS = 60
EPISODE_TIME_SEC = 20
RESET_TIME_SEC = 10
TASK_DESCRIPTION = "New Classify Objects into the Pocket"

def sync_robot_to_teleop_gradually(robot, teleop, max_step, delay):
    try:
        # Get current position and goal position
        target_action = teleop.get_action()
        current_obs = robot.get_observation()

        # Compute diff
        position_diffs = {}
        max_diff = 0

        for key in target_action:
            motor_key = key.replace('.pos', '') + '.pos'
            if motor_key in current_obs:
                diff = target_action[key] - current_obs[motor_key]
                position_diffs[key] = diff
                max_diff = max(max_diff, abs(diff))
        
        # If the difference is small, move at once
        if max_diff <= max_step:
            robot.send_action(target_action)
            time.sleep(delay)
            return
        
        steps = int(max_diff / max_step) + 1

        # Gradually move
        for step in range(steps):
            interpolated_action = {}
            for key, total_diff in position_diffs.items():
                motor_key = key.replace('.pos', '') + '.pos'
                current_val = current_obs[motor_key]
                step_ratio = min(1.0, (step + 1) / steps)
                interpolated_action[key] = current_val + total_diff * step_ratio
            
            robot.send_action(interpolated_action)
            time.sleep(delay)

            if step < steps - 1:
                current_obs = robot.get_observation()
        
        log_say("Position synchronization complete")
    
    except Exception as e:
        logging.warning(f"Position sync failed: {e}")     
            

# Create the robot and teleoperator configurations
camera_config = {
    "grip": OpenCVCameraConfig(index_or_path=0, width=640, height=480, fps=30),
    "top": OpenCVCameraConfig(index_or_path=6, width=640, height=480, fps=30),
    "depth": OpenCVCameraConfig(index_or_path=4, width=640, height=480, fps=30),
}

robot_config = SO101FollowerConfig(
    port="/dev/ttyACM0", id="follwer_robot_arm", cameras=camera_config
)

teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM1",
    id="leader_robot_arm",
)

# Initialize the robot and teleoperator
robot = SO101Follower(robot_config)
teleop = SO101Leader(teleop_config)

# Configure the dataset features
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

# Create the dataset
dataset = LeRobotDataset.create(
    repo_id="nobana/test1",
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
)

# Initialize the keyboard listener and rerun visualization
_, events = init_keyboard_listener()
_init_rerun(session_name="recording")

# Connect the robot and teleoperator
robot.connect()
teleop.connect()

episode_idx = 0
while episode_idx < NUM_EPISODES and not events["stop_recording"]:

    log_say("Synchronizing positions...")
    sync_robot_to_teleop_gradually(robot, teleop, max_step = 15, delay = 0.03)

    log_say(f"Recording episode {episode_idx + 1} of {NUM_EPISODES}")

    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        teleop=teleop,
        dataset=dataset,
        control_time_s=EPISODE_TIME_SEC,
        single_task=TASK_DESCRIPTION,
        display_data=True,
    )

    print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
    print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')

    # Reset the environment if not stopping or re-recording
    if not events["stop_recording"] and (episode_idx < NUM_EPISODES - 1 or events["rerecord_episode"]):
        log_say("Reset the environment")
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            teleop=teleop,
            dataset=dataset,
            control_time_s=RESET_TIME_SEC,
            single_task=TASK_DESCRIPTION,
            display_data=True,
        )

    if events["rerecord_episode"]:
        log_say("Re-recording episode")
        events["rerecord_episode"] = False
        events["exit_early"] = False
        dataset.clear_episode_buffer()
        continue

    dataset.save_episode()
    episode_idx += 1

# Clean up
log_say("Stop recording")
robot.disconnect()
teleop.disconnect()
dataset.push_to_hub()
