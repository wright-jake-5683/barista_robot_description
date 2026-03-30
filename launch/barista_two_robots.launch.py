import os
import random
from launch.actions import TimerAction
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_prefix
from launch_ros.parameter_descriptions import ParameterValue


# this is the function launch system will look for
def generate_launch_description():
    package_description = "barista_robot_description"
    
    install_dir = get_package_prefix(package_description)
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_barista_bot_gazebo = get_package_share_directory('barista_robot_description')
    

    # Set the path to the WORLD model files. Is to find the models inside the models folder in my_box_bot_gazebo package
    gazebo_models_path = os.path.join(pkg_barista_bot_gazebo, 'models')
    # os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

##### RVIZ ################################################################################################################################################# RVIZ ############################################################################################################################################

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'multi_robot_urdf_vis.rviz')
    
    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', rviz_config_dir])


##### Robot State Publishers & Spawn Nodes ##############################################################################################################

    ####### DATA INPUT ##########
    xacro_file = 'barista_robot_model.urdf.xacro'

    # Position and orientation
    # [X, Y, Z]
    position_1 = [0.0, 0.0, 0.2]
    position_2 = [1.0, 1.0, 1.2]
    # [Roll, Pitch, Yaw]
    orientation = [0.0, 0.0, 0.0]
    
    # Base Name or robot
    barista_bot_1_name = "rick"
    barista_bot_2_name = "morty"

    print("Fetching XACRO File ==>")
    robot_model_path = os.path.join(get_package_share_directory('barista_robot_description'))
    xacro_path = os.path.join(robot_model_path, 'xacro', xacro_file)

    barista_bot_1_description = ParameterValue(
        Command([
            'xacro ',
            xacro_path,
            ' robot_name:=', barista_bot_1_name,
            ' gazebo_color:=Gazebo/Blue',
            ' color:=blue'
        ]),
        value_type=str
    )

    barista_bot_2_description = ParameterValue(
        Command([
            'xacro ',
            xacro_path,
            ' robot_name:=', barista_bot_2_name,
            ' gazebo_color:=Gazebo/Red',
            ' color:=blue'' color:=red'
        ]),
        value_type=str
    )
    

    # Robot State Publishers
    rsp_barista_bot_1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace="rick",
        name='robot_state_publisher_node_barista_bot_1',
        emulate_tty=True,
        parameters=[
            {'robot_description': barista_bot_1_description}, 
            {'use_sim_time': True},
            {'frame_prefix': 'rick/'} 
        ],
        remappings=[
            ('/rick/joint_states', '/rick/joint_states'),  # keep joint states namespaced
            ('tf', '/tf'),          # publish TF globally
            ('tf_static', '/tf_static')   # publish static TF globally
        ],
        output="screen"
    )
    rsp_barista_bot_2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace="morty",
        name='robot_state_publisher_node_barista_bot_2',
        emulate_tty=True,
        parameters=[
            {'robot_description': barista_bot_2_description}, 
            {'use_sim_time': True},
            {'frame_prefix': 'morty/'}
        ],
        remappings=[
            ('/morty/joint_states', '/morty/joint_states'),  # keep joint states namespaced
            ('tf', '/tf'),          # publish TF globally
            ('tf_static', '/tf_static')   # publish static TF globally
        ],
        output="screen"
    )

    # Spawn Robots in Gazebo
    spawn_robot_barista_bot_1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity_barista_bot_1',
        namespace="rick",
        output='screen',
        arguments=['-entity',
                   barista_bot_1_name,
                   '-x', str(position_1[0]), '-y', str(position_1[1]), '-z', str(position_1[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
                   '-topic', '/rick/robot_description'
                   ]
    )
    spawn_robot_barista_bot_2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity_barista_bot_2',
        namespace="morty",
        output='screen',
        arguments=['-entity',
                   barista_bot_2_name,
                   '-x', str(position_2[0]), '-y', str(position_2[1]), '-z', str(position_2[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
                   '-topic', '/morty/robot_description'
                   ]
    )



##### Gazebo Launch Config ############################################################################################################################
    
    # Declare a new launch argument for the world file
    world_file_arg = DeclareLaunchArgument(
                'world',
                default_value=[os.path.join(pkg_barista_bot_gazebo, 'worlds', 'barista_bot_empty.world'), ''],
                description='SDF world file'
    )

    # Define the launch arguments for the Gazebo launch file
    gazebo_launch_args = {
        'verbose': 'false',
        'pause': 'false',
        'world': LaunchConfiguration('world')
    }

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments=gazebo_launch_args.items()
        
    )

    delayed_spawn_1 = TimerAction(
        period=5.0,   # wait 5 seconds
        actions=[spawn_robot_barista_bot_1]
    )
    delayed_spawn_2 = TimerAction(
        period=5.0,   # wait 5 seconds
        actions=[spawn_robot_barista_bot_2]
    )  

##### World Static TF Publisher ##########################################################################################################################
    rick_static_tf_pub = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher_world_rick_odom',
            output='screen',
            emulate_tty=True,
            arguments=['0', '0', '0', '0', '0', '0', 'world', 'rick/odom']
    )

    morty_static_tf_pub = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher_world_morty_odom',
            output='screen',
            emulate_tty=True,
            arguments=['1', '1', '0', '0', '0', '0', 'world', 'morty/odom']
    )

    # create and return launch description object
    return LaunchDescription(
        [            
            world_file_arg,
            gazebo,
            rsp_barista_bot_1,
            rsp_barista_bot_2,
            delayed_spawn_1,
            delayed_spawn_2,
            rick_static_tf_pub,
            morty_static_tf_pub,
            rviz_node
        ]
    )