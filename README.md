# LeRobot Dataset Recording

This guide explains how to record datasets using the LeRobot framework.

### Recording Single Arm Datasets

To record a single arm dataset, run the following command:
    ```
    python test_record.py
    ```

### Recording Bi-manual Datasets

There are two ways to record bi-manual datasets:

1. **Run the Python script:**
    ```
    python test_bimanual_record.py
    ```
    
2. **Use the command line:**
    You can use the following command to record without modifying the Python cose:
   ```bash
   python -m lerobot.record   --robot.type=bi_so100_follower   --robot.left_arm_port=/dev/ttyFL   --robot.right_arm_port=/dev/ttyFR   --robot.id=follower_robot   --robot.cameras='{
    "left_front": {"type": "opencv", "index_or_path": 6, "width": 640, "height": 480, "fps": 30},
    "right_front": {"type": "opencv", "index_or_path": 8, "width": 640, "height": 480, "fps": 30},
    "top": {"type": "opencv", "index_or_path": 2, "width": 640, "height": 480, "fps": 30}
      }'   --teleop.type=bi_so100_leader   --teleop.left_arm_port=/dev/ttyTL   --teleop.right_arm_port=/dev/ttyTR   --teleop.id=leader_robot   --display_data=true   --dataset.repo_id=local/record-test                     dataset.push_to_hub=false   --dataset.root=./my_local_dataset2   --dataset.num_episodes=5   --dataset.single_task="Grab the marker_from_the_drawer"
  ```

---

**Caution:** Please ensure you set the correct port for your specific robot arm and camera devices.
  
