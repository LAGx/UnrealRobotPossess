import omni.usd
import numpy as np
from pxr import Usd, UsdGeom, Gf, Sdf

def get_stage():
    return omni.usd.get_context().get_stage()

def get_prim(path):
    stage = get_stage()
    prim = stage.GetPrimAtPath(path)
    if not prim.IsValid():
        raise RuntimeError(f"Prim not found or invalid: {path}")
    return prim

def get_world_pose_wxyz(path: str, time_code=Usd.TimeCode.Default()):
    """
    return (pos_np, quat_wxyz_np)
    pos_np: np.array([x,y,z], dtype=float64)
    quat_wxyz_np: np.array([w,x,y,z], dtype=float64)
    """
    prim = get_prim(path)
    xf_cache = UsdGeom.XformCache(time_code)
    m = xf_cache.GetLocalToWorldTransform(prim)  # Gf.Matrix4d

    t = Gf.Transform(m)
    pos = t.GetTranslation()     # Gf.Vec3d
    rot = t.GetRotation()        # Gf.Rotation
    q   = rot.GetQuat()          # Gf.Quatd (w + (xi + yj + zk))

    w = q.GetReal()
    x, y, z = q.GetImaginary()
    return np.array([pos[0], pos[1], pos[2]], dtype=np.float64), \
           np.array([w, x, y, z], dtype=np.float64)

# --- VISIBILITY ---
def set_visibility(path, visible=True):
    prim = get_prim(path)
    img = UsdGeom.Imageable(prim)
    if not img:
        raise RuntimeError(f"Prim is not UsdGeom.Imageable: {path}")
    if visible:
        img.MakeVisible()
    else:
        img.MakeInvisible()

def toggle_visibility(path):
    prim = get_prim(path)
    img = UsdGeom.Imageable(prim)
    current = img.ComputeVisibility(Usd.TimeCode.Default())  # 'inherited' or 'invisible'
    set_visibility(path, visible=(current == "invisible"))

def get_world_xform(prim_or_path, time_code=Usd.TimeCode.Default()) -> Gf.Matrix4d:
    if isinstance(prim_or_path, str):
        prim = get_prim(prim_or_path)
    else:
        prim = prim_or_path  # Usd.Prim
    xf_cache = UsdGeom.XformCache(time_code)
    return xf_cache.GetLocalToWorldTransform(prim)

def world_point_to_local(p_world: np.ndarray, prim_or_path) -> np.ndarray:
    M = get_world_xform(prim_or_path)
    M_inv = Gf.Matrix4d(M).GetInverse()
    v = M_inv.Transform(Gf.Vec3d(float(p_world[0]), float(p_world[1]), float(p_world[2])))
    return np.array([v[0], v[1], v[2]], dtype=np.float64)

def world_quat_to_local_wxyz(q_world_wxyz: np.ndarray, prim_or_path) -> np.ndarray:
    M = get_world_xform(prim_or_path)
    R = Gf.Transform(M).GetRotation().GetQuat()
    w_b = R.GetReal()
    x_b, y_b, z_b = R.GetImaginary()
    w_bi, x_bi, y_bi, z_bi = w_b, -x_b, -y_b, -z_b

    w, x, y, z = map(float, q_world_wxyz)
    # q_local = q_base_inv * q_world  (WXYZ)
    w_l = w_bi*w - x_bi*x - y_bi*y - z_bi*z
    x_l = w_bi*x + x_bi*w + y_bi*z - z_bi*y
    y_l = w_bi*y - x_bi*z + y_bi*w + z_bi*x
    z_l = w_bi*z + x_bi*y - y_bi*x + z_bi*w
    return np.array([w_l, x_l, y_l, z_l], dtype=np.float64)

