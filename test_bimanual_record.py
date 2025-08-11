from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features

# Bimanual Follower Robot & Teleoperator Robot Config and Class import
from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100LeaderConfig
from lerobot.teleoperators.bi_so100_follower import BiSO100FollowerConfig, BiSO100FollowerConfig

from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import _init_rerun
from lerobot.record import record_loop

NUM_EPISODES = 1
FPS = 60
EPISODE_TIME_SEC = 20
RESET_TIME_SEC = 10
TASK_DESCRIPTION = "New Classify Objects into the Pocket"
REPO_ID = "nobana/test_bimanual"

# Setup Port
LEFT_ARM_PORT_FOLLOWER = "/dev/ttyFL"
RIGHT_ARM_PORT_FOLLOWER = "/dev/ttyFR"
LEFT_ARM_PORT_LEADER = "/dev/ttyTL"
RIGHT_ARM_PORT_LEADER = "/dev/ttyTR"

# Create the robot and teleoperator configurations
# Setup Camera
camera_config = {
    "left_front": OpenCVCameraConfig(index_or_path=6, width=640, height=480, fps=30),
    "right_front": OpenCVCameraConfig(index_or_path=8, width=640, height=480, fps=30),
    "top": OpenCVCameraConfig(index_or_path=2, width=640, height=480, fps=30),
}

# Setup Follower Robot using BiSO100FollowerConfig
robot_config = BiSO100FollowerConfig(
    left_arm_port=LEFT_ARM_PORT_FOLLOWER,
    right_arm_port=RIGHT_ARM_PORT_FOLLOWER,
    id="follower_robot_arms",
    cameras=camera_config,
)

# Setup Leader Robot using BiSO100LeaderConfig
teleop_config = BiSO100LeaderConfig(
    left_arm_port=LEFT_ARM_PORT_LEADER,
    right_arm_port=RIGHT_ARM_PORT_LEADER,
    id="leader_robot_arms",
)

# Initialize the robot and teleoperator
robot = BiSO100FollowerConfig(robot_config)
teleop = BiSO100LeaderConfig(teleop_config)

# Configure the dataset features
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

# Create the dataset
dataset = LeRobotDataset.create(
    repo_id=REPO_ID,
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
    # Example for dataset.root
    # root=DATASET_ROOT,
)

# Initialize the keyboard listener and return visualization
_, events = init_keyboard_listener()
_init_rerun(session_name="recording")

# Connect the robot and teleoperator
robot.connect()
teleop.connect()

episode_idx = 0
while episode_idx < NUM_EPISODES and not events["stop_recording"]:
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
log_say("Stop recoding")
robot.disconnect()
teleop.disconnect()
dataset.push_to_hub()