from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument , IncludeLaunchDescription
import os
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch import LaunchDescription




def generate_launch_description():
    pkg_my_package =get_package_share_directory('my_package')#path to the package
    ekf_config_file_path = os.path.join(pkg_my_package,"config","ekf1.yaml")

    gazebo_models_path,ignore = os.path.split(pkg_my_package) # just in case if you have any model file in your package
    os.environ["GZ_SIM_RESOURCE_PATH"] += os.pathsep + gazebo_models_path

    rviz_launch_arg = DeclareLaunchArgument( # gives you choice to launch the rviz or not during launching
        'rviz',
        default_value="true",
        description="weather to open the rviz or not"
    )
    world_arg = DeclareLaunchArgument(# gives you the choice to launch the world you want during launching
        'world',
        default_value="empty.sdf",
        description="the world you want to launch"
    )
    model_arg = DeclareLaunchArgument( # gives the choice to launch the model you want during launching
        'model',
        default_value="my_robot.urdf"
        , description="the robot modle you want to launch")
    
    model_path = PathJoinSubstitution([pkg_my_package,'urdf', LaunchConfiguration('model')])#path to your robot
    
    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_package,'launch','world.launch.py'),),
            launch_arguments={
                'world': LaunchConfiguration('world'),
            }.items())
    
    rviz_node = Node(
                package = 'rviz2', 
                executable = "rviz2",
                arguments = ['-d' , os.path.join(pkg_my_package,'rviz',"my_robot.rviz")], 
                condition = IfCondition(LaunchConfiguration('rviz'
                )), 
                parameters = [{'use_sim_time':True}]
                
    )
    spawn_urdf_node = Node(
        package="ros_gz_sim", 
        executable='create', 
        arguments = [
            '-name', 'my_robot',
            '-topic' , 'robot_description',
             "-x", "0.0", "-y", "0.0", "-z", "0.5", "-Y", "0.0" 
            
        ], 
        output = "screen", 
        parameters = [
            {"use_sim_time": True},
        ]

    )
   
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': Command(['xacro', ' ', model_path]),
             'use_sim_time': True},
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static')
        ]
    )
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
    )

    gz_image_bridge_node = Node(
        package = "ros_gz_image",
        executable="image_bridge",
        arguments=[
            "/camera/image",
        ], 
        output = "screen", 
        parameters = [{"use_sim_time":True, "camera.image.compressed.jpeg_quality":75},],
    )
    relay_camera_info_node = Node(
        package = 'topic_tools',
        executable= 'relay',
        name = 'relay_camera_info',
        output = "screen",
        arguments=['camera/camera_info', 'camera/image/camera_info'], 
        parameters=[{'use_sim_time':True}]
    )
    relay_wide_camera_info_node = Node(
        package='topic_tools',
        executable='relay',
        arguments=['camera/wide_angle_camera_info', 'camera/wide_angle_image/camera_info']
    )
    ros2_bridge_node = Node(
        package = "ros_gz_bridge",
        executable = "parameter_bridge",
        arguments = [
             "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model",
            "/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V",
            #"/camera/image@sensor_msgs/msg/Image@gz.msgs.Image",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo",
            "/imu@sensor_msgs/msg/Imu@gz.msgs.IMU",
            "/navsat@sensor_msgs/msg/NavSatFix@gz.msgs.NavSat",
            "/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",
            "/scan/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked",

        ], 
        output = "screen", 
        parameters=[{"use_sim_time":True},]
    )
    ekf_node = Node(
        package= "robot_localization",
        executable = 'ekf_node',
        name = 'ekf_filter_node',
        output = "screen",
        parameters = [ekf_config_file_path,{"use_sim_time": True}]
    )
    return LaunchDescription([
        world_arg,
        model_arg,
        #use_sim_time_arg,
        rviz_launch_arg,
        robot_state_publisher_node,
        spawn_urdf_node,
        world_launch,
        rviz_node, ros2_bridge_node,
        gz_image_bridge_node, 
        #relay_camera_info_node,
        #relay_wide_camera_info_node,
        #ekf_node
        ]

    )




        
    
       
        
    
    

