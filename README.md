# lerobot_record
If you want to record 'Single arm dataset', run test_record.py

If you want to record 'Bi manual datasets', run test_bimanual_record.py

If you want to use Bi manual through the command without modifying the Python code, use the following command

python -m lerobot.record   --robot.type=bi_so100_follower   --robot.left_arm_port=/dev/ttyFL   --robot.right_arm_port=/dev/ttyFR   --robot.id=follower_robot   --robot.cameras='{
    "left_front": {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
    "right_front": {"type": "opencv", "index_or_path": 8, "width": 640, "height": 480, "fps": 30},
    "top": {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30}
  }'   --teleop.type=bi_so100_leader   --teleop.left_arm_port=/dev/ttyTL   --teleop.right_arm_port=/dev/ttyTR   --teleop.id=leader_robot   --display_data=true   --dataset.repo_id=local/record-test   --dataset.push_to_hub=false   --dataset.root=./my_local_dataset2   --dataset.num_episodes=5   --dataset.single_task="Grab the marker_from_the_drawer"

Caution: Set the port for you (robot arm, camera)
