# Copyright Yurii (Kvark) Maruda. Free, open source sample.

#        enable_extension("isaacsim.ros2.bridge")
#        enable_extension("isaacsim.ros2.sim_control")

#PS C:\dev\ros2_iron> $env:ROS_DOMAIN_ID = "44"
#PS C:\dev\ros2_iron> $env:RMW_IMPLEMENTATION = "rmw_fastrtps_cpp"

'''
/urp/move_hand_to_pos 
name: PoseStamped, 
package: geometry_msgs, 
subfolder: msg

$yaml = @" header: frame_id: 'fanuc'  
position: {x: 0.25, y: 0.00, z: 0.50} 
orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}"

ros2 topic pub /urp/move_hand_to_pos geometry_msgs/TransformStamped "$yaml" --once

FastDDS + FastCDR
'''

from .extension import *
