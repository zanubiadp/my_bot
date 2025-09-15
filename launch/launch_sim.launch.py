import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command

def generate_launch_description():
    package_name = 'my_bot'

    # Use xacro to generate robot description at launch time
    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        "description",
        "robot.urdf.xacro"
    )

    robot_description_content = Command([
        'xacro ', xacro_file
    ])

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "use_sim_time": True,
            "robot_description": robot_description_content
        }]
    )

    # Launch Gazebo Sim (Ionic) with your custom world
    gazebo = ExecuteProcess(
        cmd=["gz", "sim", "-v", "4", os.path.join(
            get_package_share_directory(package_name),
            "worlds",
            "empty.world"
        )],
        output="screen"
    )

    # Spawn robot into Gazebo using gz service
    spawn = ExecuteProcess(
        cmd=[
            "gz", "service", "-s", "/world/empty/create",
            "--reqtype", "gz.msgs.EntityFactory",
            "--reptype", "gz.msgs.Boolean",
            "--timeout", "1000",
            "--req",
            f'sdf_filename: "{os.path.join(get_package_share_directory(package_name), "description", "robot.urdf")}", name: "my_bot", pose: {{ position: {{ x: 0, y: 0, z: 0.05 }} }}'
        ],
        output="screen"
    )

    # Bridge /cmd_vel and /odom
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry'
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn,
        bridge,
    ])