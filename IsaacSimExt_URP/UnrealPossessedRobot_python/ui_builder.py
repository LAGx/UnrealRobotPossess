
import omni.timeline
import omni.ui as ui
from isaacsim.core.api.world import World
from isaacsim.core.prims import SingleXFormPrim
from isaacsim.core.utils.stage import create_new_stage, get_current_stage
from isaacsim.examples.extension.core_connectors import LoadButton, ResetButton
from isaacsim.gui.components.element_wrappers import CollapsableFrame, StateButton
from isaacsim.gui.components.ui_utils import get_style
from omni.usd import StageEventType
from pxr import Sdf, UsdLux

from .scene_controller import CustomSceneController
from .global_variables import set_scene_controller

class UIBuilder:
    def __init__(self):
        self.frames = []
        self.wrapped_ui_elements = []
        self._timeline = omni.timeline.get_timeline_interface()
        self._cuboid = None

        self._scene_controller = None
        self._toggle_test_cube_btn = None
        self._move_to_test_cube_btn = None

    def on_menu_callback(self):
        pass

    def on_timeline_event(self, event):
        pass

    def on_physics_step(self, step: float):
        if self._scene_controller:
            self._scene_controller.service_step(step)

    def on_stage_event(self, event):
        if event.type == int(StageEventType.OPENED):
            # If the user opens a new stage, the extension should completely reset
            self._reset_extension()

    def cleanup(self):
        if self._scene_controller:
            self._scene_controller.cleanup()

        self._scene_controller = None
        set_scene_controller(None)

        for ui_elem in self.wrapped_ui_elements:
            if hasattr(ui_elem, "cleanup"):
                ui_elem.cleanup()

    def build_ui(self):
        world_controls_frame = CollapsableFrame("World Controls", collapsed=False)

        with world_controls_frame:
            with ui.VStack(style=get_style(), spacing=5, height=0):
                self._load_btn = LoadButton(
                    "Load Button", "LOAD", setup_scene_fn=self._load_scene, setup_post_load_fn=self._setup_scene_controller
                )
                self._load_btn.set_world_settings(physics_dt=1 / 60.0, rendering_dt=1 / 60.0)
                self.wrapped_ui_elements.append(self._load_btn)

        test_actions_frame = CollapsableFrame("Test Actions")

        with test_actions_frame:
            with ui.VStack(style=get_style(), spacing=5, height=0):
                self._toggle_test_cube_btn = ui.Button(
                    "Toggle Test Cube",
                    clicked_fn=self._toggle_test_cube,
                )
                self._toggle_test_cube_btn.enabled = True

                self._move_to_test_cube_btn = ui.Button(
                    "Move To Test Cube",
                    clicked_fn=self._move_to_test_cube,
                )
                self._move_to_test_cube_btn.enabled = True

    def _load_scene(self):
        if self._scene_controller:
            self._scene_controller.cleanup()

        self._scene_controller = CustomSceneController()
        set_scene_controller(self._scene_controller)
        self._scene_controller.load_scene()

    def _setup_scene_controller(self):
        self._scene_controller.setup()
        self._scene_controller.enabled = True

    def _toggle_test_cube(self):
        self._scene_controller.toggle_target_cube()
    
    def _move_to_test_cube(self):
        self._scene_controller.move_to_target_cube()

    def _reset_extension(self):
        self.cleanup()
        self._reset_ui()

    def _reset_ui(self):
        pass
