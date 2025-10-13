
# Copyright Yurii (Kvark) Maruda. Free, open source sample.


EXTENSION_TITLE = "UnrealPossessedRobot"

EXTENSION_DESCRIPTION = ""


_scene_controller = None

def set_scene_controller(sc):
    global _scene_controller
    _scene_controller = sc

def get_scene_controller():
    return _scene_controller