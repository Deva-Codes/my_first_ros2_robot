import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node 
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_name = "my_package"
    urdf_file_name = "my_robot.urdf"
    urdf_file_path = os.path.join(get_package_share_directory(pkg_name),'urdf',urdf_file_name)
    rviz_file_name = "my_robot.rviz"
    rviz_file_path = os.path.join(get_package_share_directory(pkg_name),'rviz',rviz_file_name)



    model_arg = DeclareLaunchArgument(
        'model',
        default_value=urdf_file_path,
        description="path to your urdf file"    )
    
    model_config = LaunchConfiguration('model')
    robot_description_content = Command(['cat ',model_config])
    
    rsp_node = Node(
        package = 'robot_state_publisher',
        executable = 'robot_state_publisher', 
        name = 'rsp_node',
        output = "screen",
        parameters = [{"robot_description":robot_description_content}]

    )
    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
      #  arguments=['-d',rviz_file_path]
    )
    jsp_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )
    return LaunchDescription(
        [ model_arg,
         rsp_node,
         jsp_gui_node,
         rviz_node,
         ]
    )
