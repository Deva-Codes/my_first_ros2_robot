import os
from launch import LaunchDescription
from launch_ros.substitutions import FindPackageShare
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = FindPackageShare('my_package').find('my_package')
    urdf_file_path = os.path.join(pkg_share,'urdf','my_robot.urdf')
    world_file_path = os.path.join(pkg_share,'worlds','my_world.sdf')
    with open(urdf_file_path,'r') as infp:
        robot_desc = infp.read()

    start_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(FindPackageShare('ros_gz_sim').find('ros_gz_sim'),'launch','gz_sim.launch.py')

        ]),
        launch_arguments={'gz_args': f'-r {world_file_path}'}.items()
    )

    start_robot_state_publisher = Node(
        package = 'robot_state_publisher',
        executable = 'robot_state_publisher',
        name = 'robot_state_publisher',
        output = 'both',
        parameters = [{'robot_description': robot_desc}]
    )

    spawn_the_robot = Node(
        package= "ros_gz_sim", 
        executable = 'create',
        output = 'screen', 
        arguments =[ '-topic', 'robot_description', 
            '-name', 'my_first_robot' ,
               '-z','0.5' ] 
    )
    
    return LaunchDescription([
        start_gazebo,
        start_robot_state_publisher,
        spawn_the_robot
    ])


    