import numpy as np
import omni.usd
from enum import Enum
from isaacsim.core.api.objects import DynamicCuboid, FixedCuboid, GroundPlane
from isaacsim.core.prims import SingleArticulation, SingleXFormPrim
from isaacsim.core.utils import distance_metrics
from isaacsim.core.utils.numpy.rotations import euler_angles_to_quats, quats_to_rot_matrices
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.robot_motion.motion_generation import ArticulationMotionPolicy, RmpFlow
from isaacsim.robot_motion.motion_generation.interface_config_loader import (
    get_supported_robot_policy_pairs,
    load_supported_motion_policy_config,
)
from isaacsim.storage.native import get_assets_root_path

from pathlib import Path
from . import scene_utility

def _plugin_root():
    return Path(__file__).resolve().parent

USD_PATH = (_plugin_root() / "../data/PrimaryStage.usd").resolve().as_posix()

class SceneHandName(Enum):
    FANUC = "fanuc"
    FESTO = "festo"
    RIZON = "rizon"

class CustomSceneController:
    def __init__(self):
        self._crx10ial_rmpflow = None
        self._festo_cobot_rmpflow = None
        self._flexiv_rizon4_rmpflow = None

        self._crx10ial_articulation = None
        self._festo_cobot_articulation = None
        self._flexiv_rizon4_articulation = None

        self._crx10ial_articulation_rmpflow = None
        self._festo_cobot_articulation_rmpflow = None
        self._flexiv_rizon4_articulation_rmpflow = None

        self.test_cube_prim_path = None
        self._jobs = []
        self._art_root = {}

    def load_scene(self):
        omni.usd.get_context().open_stage(USD_PATH)

        robot_crx10ial_prim_path = "/World/crx10ial"
        self._crx10ial_articulation = SingleArticulation(robot_crx10ial_prim_path)
        self._art_root[self._crx10ial_articulation] = robot_crx10ial_prim_path

        robot_festo_cobot_prim_path = "/World/festo_cobot"
        self._festo_cobot_articulation = SingleArticulation(robot_festo_cobot_prim_path)
        self._art_root[self._festo_cobot_articulation] = robot_festo_cobot_prim_path
        
        robot_flexiv_rizon4_prim_path = "/World/flexiv_rizon4"
        self._flexiv_rizon4_articulation = SingleArticulation(robot_flexiv_rizon4_prim_path)
        self._art_root[self._flexiv_rizon4_articulation] = robot_flexiv_rizon4_prim_path

        self.test_cube_prim_path = "/World/_TestTarget"
        scene_utility.set_visibility(self.test_cube_prim_path, False)

    def setup(self):
        self._crx10ial_articulation.initialize()
        self._festo_cobot_articulation.initialize()
        self._flexiv_rizon4_articulation.initialize()

        crx10ial_rmp_config = load_supported_motion_policy_config("Fanuc_CRX10IAL", "RMPflow")
        self._crx10ial_rmpflow = RmpFlow(**crx10ial_rmp_config)
        self._crx10ial_articulation_rmpflow = ArticulationMotionPolicy(self._crx10ial_articulation, self._crx10ial_rmpflow)

        festo_cobot_rmp_config = load_supported_motion_policy_config("FestoCobot", "RMPflow")
        self._festo_cobot_rmpflow = RmpFlow(**festo_cobot_rmp_config)
        self._festo_cobot_articulation_rmpflow = ArticulationMotionPolicy(self._festo_cobot_articulation, self._festo_cobot_rmpflow)

        flexiv_rizon4_rmp_config = load_supported_motion_policy_config("Rizon4", "RMPflow")
        self._flexiv_rizon4_rmpflow = RmpFlow(**flexiv_rizon4_rmp_config)
        self._flexiv_rizon4_articulation_rmpflow = ArticulationMotionPolicy(self._flexiv_rizon4_articulation, self._flexiv_rizon4_rmpflow)

    def cleanup(self):
        pass

    def toggle_target_cube(self):
        scene_utility.toggle_visibility(self.test_cube_prim_path)

    def move_to_target_cube(self):
        translation_target, orientation_target = scene_utility.get_world_pose_wxyz(self.test_cube_prim_path)
        
        print("move_to_target_cube translation_target " + str(translation_target))
        print("move_to_target_cube orientation_target " + str(orientation_target))

        self.move_hand_to_pos(SceneHandName.FANUC, translation_target, orientation_target)
        self.move_hand_to_pos(SceneHandName.FESTO, translation_target, orientation_target)
        self.move_hand_to_pos(SceneHandName.RIZON, translation_target, orientation_target)

    # Entry point for ROS
    def move_hand_to_pos_from_str_safe(self, hand_name_str: str, translation_target, orientation_target):
        try:
            hand_name: SceneHandName = SceneHandName[hand_name_str.lower()]
            self.move_hand_to_pos(hand_name, translation_target, orientation_target)
        except Exception as e:
            print(f"[URP][ROS2] stop error: {e}")

    def move_hand_to_pos(self, hand_name: SceneHandName, translation_target, orientation_target):
        print(f"[info] move_hand_to_pos: {hand_name}: {translation_target} - {orientation_target}")

        if hand_name == SceneHandName.FANUC:
            self.enqueue_job(self.goto_position_job(translation_target, orientation_target, self._crx10ial_articulation, self._crx10ial_rmpflow))
        elif hand_name == SceneHandName.FESTO:
            self.enqueue_job(self.goto_position_job(translation_target, orientation_target, self._festo_cobot_articulation, self._festo_cobot_rmpflow))
        elif hand_name == SceneHandName.RIZON:
            self.enqueue_job(self.goto_position_job(translation_target, orientation_target, self._flexiv_rizon4_articulation, self._flexiv_rizon4_rmpflow))

    def goto_position_job(
        self,
        translation_target, # np.array([x,y,z])
        orientation_target, # np.array([w,x,y,z])
        articulation,
        rmpflow,
        translation_thresh=0.01,
        orientation_thresh=0.1,
        timeout=500,
    ):
        articulation_motion_policy = ArticulationMotionPolicy(articulation, rmpflow, 1 / 60)

        art_root_path = self._art_root.get(articulation, None)
        if art_root_path is None:
            print("[URP] ERROR: no root path for articulation")
            return False

        world_trans_goal = translation_target
        world_orient_goal = orientation_target

        local_trans_goal = scene_utility.world_point_to_local(world_trans_goal, art_root_path)
        local_orient_goal = scene_utility.world_quat_to_local_wxyz(world_orient_goal, art_root_path)

        rmpflow.set_end_effector_target(local_trans_goal, local_orient_goal)

        for i in range(timeout):
            ee_trans, ee_rot = rmpflow.get_end_effector_pose(
                articulation_motion_policy.get_active_joints_subset().get_joint_positions()
            )

            trans_dist = distance_metrics.weighted_translational_distance(ee_trans, translation_target)
            rotation_target = quats_to_rot_matrices(orientation_target)
            rot_dist = distance_metrics.rotational_distance_angle(ee_rot, rotation_target)

            done = trans_dist < translation_thresh and rot_dist < orientation_thresh

            if done:
                return True

            rmpflow.update_world()
            action = articulation_motion_policy.get_next_articulation_action(1 / 60)
            articulation.apply_action(action)
            yield ()

        return False

    def open_gripper_franka(self, articulation):
        open_gripper_action = ArticulationAction(np.array([0.04, 0.04]), joint_indices=np.array([7, 8]))
        articulation.apply_action(open_gripper_action)

        while not np.allclose(articulation.get_joint_positions()[7:], np.array([0.04, 0.04]), atol=0.001):
            yield ()

        return True

    def close_gripper_franka(self, articulation, close_position=np.array([0, 0]), atol=0.001):
        open_gripper_action = ArticulationAction(np.array(close_position), joint_indices=np.array([7, 8]))
        articulation.apply_action(open_gripper_action)

        while not np.allclose(articulation.get_joint_positions()[7:], np.array(close_position), atol=atol):
            yield ()

        return True

    def service_step(self, dt: float):
        if not self._jobs:
            return

        alive = []
        for job in self._jobs:
            try:
                next(job)
                alive.append(job)
            except StopIteration:
                pass

        self._jobs = alive

    def enqueue_job(self, gen):
        if gen is not None:
            self._jobs.append(gen)