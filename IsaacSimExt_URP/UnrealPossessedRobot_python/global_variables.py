
# Copyright Yurii (Kvark) Maruda. Free, open source sample.


#        enable_extension("isaacsim.ros2.bridge")
#        enable_extension("isaacsim.ros2.sim_control")

#PS C:\dev\ros2_iron> $env:ROS_DOMAIN_ID = "44"
#PS C:\dev\ros2_iron> $env:RMW_IMPLEMENTATION = "rmw_fastrtps_cpp"


EXTENSION_TITLE = "UnrealPossessedRobot"

EXTENSION_DESCRIPTION = ""


_scene_controller = None

def set_scene_controller(sc):
    global _scene_controller
    _scene_controller = sc

def get_scene_controller():
    return _scene_controller