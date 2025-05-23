#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    
    # adapt if needed
    debug = False
    respawn = True

    default_config_file = os.path.join(
        get_package_share_directory('stcamera_launch'),
        'config',
        'default.yaml'
    )
    default_tf_frame = 'optical_frame'

    # launch configuration variables
    config_file = LaunchConfiguration('config_file')
    namespace_value = LaunchConfiguration('namespace_value')
    node_name = LaunchConfiguration('node_name')
    tf_frame = LaunchConfiguration('tf_frame')
    persistance_file = LaunchConfiguration('persistance_file')

    # launch arguments
    declare_config_file_cmd = DeclareLaunchArgument(
        'config_file',
        default_value=default_config_file,
        description='Camera parameters structured in a .yaml file.'
    )
    declare_namespace_value_cmd = DeclareLaunchArgument(
        'namespace_value',
        default_value='multispectral',
        description='Namespace.'
    )
    declare_node_name_cmd = DeclareLaunchArgument(
        'node_name',
        default_value='multispectral',
        description='Name of the node.'
    )

    declare_tf_frame_cmd = DeclareLaunchArgument(
        'tf_frame',
        default_value=default_tf_frame,
        description='Camera TF frame to be declared in image message headers. Namespaced using the "namespace_value" parameter'
    )

    declare_persistance_file_cmd = DeclareLaunchArgument(
        'persistance_file',
        default_value='',
        description='GenApi persistance file of the camera to use'
    )

    # log format
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '{time} [{name}] [{severity}] {message}'

    # see https://navigation.ros.org/tutorials/docs/get_backtrace.html
    if (debug == True):
        launch_prefix = ['xterm -e gdb -ex run --args']
    else:
        launch_prefix = ''

    robot_name = os.getenv('ROBOT_NAME', 'UNDEFINED_ROBOT')
    
    # node
    stcamera_node = Node(
        package='stcamera_launch',        
        namespace=namespace_value,
        executable='stcamera_launch',
        output='screen',
        respawn=respawn,
        respawn_delay=10,
        emulate_tty=True,
        prefix=launch_prefix,
        parameters=[
            config_file,
            {
            "tf_frame": tf_frame,
            "node_name": node_name,
            "robot_name": robot_name,
            "persistance_file": persistance_file
            }
        ]
    )

    monitor_node = Node(
            package='payload_health_monitor',
            executable='monitor',
            name='monitor',
            namespace=namespace_value,  # Namespace
            output='screen',  # Output
            parameters=[{
                "topic_name":"image_raw",
                "datatype": "image",
                "main_node_name": "st_camera_lifecycle_node",
                "startup_time":200
                }]  # Parameters
    )

    # Define LaunchDescription variable and return it
    ld = LaunchDescription()

    ld.add_action(declare_config_file_cmd)
    ld.add_action(declare_namespace_value_cmd)
    ld.add_action(declare_node_name_cmd)
    ld.add_action(declare_tf_frame_cmd)
    ld.add_action(declare_persistance_file_cmd)

    ld.add_action(stcamera_node)
    ld.add_action(monitor_node)

    return ld
