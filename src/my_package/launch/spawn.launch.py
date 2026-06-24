import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = "my_package"
    urdf_name = "my_robot.urdf"
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    urdf_path = os.path.join(get_package_share_directory(pkg_name), 'urdf', urdf_name)
    os.environ["GZ_SIM_RESOURCE_PATH"] = os.path.join(get_package_share_directory(pkg_name), '..')
    model_arg = DeclareLaunchArgument('model', default_value=urdf_path, description="Path to URDF")

    gazebo =  IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_ros_gz_sim,'launch','gz_sim.launch.py')),
        launch_arguments={'gz_args':'-r empty.sdf'}.items()

    )
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )
    spawn_urdf_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "/robot_description",
            "-name", "my_robot",
            "-allow_renaming", "true"
        ],
        output="screen"
    )
    return LaunchDescription([
        model_arg,
        gazebo,
        rsp_node,
        spawn_urdf_node
    ])


