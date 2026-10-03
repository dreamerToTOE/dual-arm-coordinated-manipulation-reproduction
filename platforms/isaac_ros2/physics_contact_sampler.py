"""[ENGINEERING] Isaac 4.5 碰撞接触力采样，不包含吸盘 D6 约束反力。

调用方在同一物理步完成后传入 PhysicsSnapshot 和真实 physics dt。
接触/摩擦缓冲区必须立即复制：两次 API 调用可能复用 count/start 缓冲。
力矩参考点是 sensor 刚体原点，不冒充任意模型的质心或 TCP。
"""

import math

import numpy as np


class PhysicsContactSampler:
    def __init__(self, view, sensor_paths, filter_paths):
        self.view = view
        self.sensor_paths = tuple(sensor_paths)
        self.filter_paths = tuple(filter_paths)
        if view.sensor_count != len(self.sensor_paths) or view.filter_count != len(self.filter_paths):
            raise ValueError("Contact view dimensions do not match the explicit path mapping")
        if tuple(view.sensor_paths) != self.sensor_paths:
            raise ValueError("Contact view sensor ordering changed")
        if tuple(tuple(paths) for paths in view.filter_paths) != tuple(
                self.filter_paths for _ in self.sensor_paths):
            raise ValueError("Contact view filter ordering changed; explicit paths required")

    @staticmethod
    def _slice(counts, starts, sensor, other, capacity):
        count, start = int(counts[sensor, other]), int(starts[sensor, other])
        if count < 0 or start < 0 or start + count > capacity:
            raise RuntimeError("Contact buffer range invalid or capacity exhausted")
        return slice(start, start + count)

    def capture(self, snapshot, dt):
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("Real physics dt must be positive; dt=1 returns impulses, not Newtons")
        if not self.view.check():
            raise RuntimeError("Invalid live contact view")
        origins = {body.prim_path: np.asarray(body.position_m) for body in snapshot.bodies}
        matrix = np.array(self.view.get_contact_force_matrix(dt), copy=True)
        normal, points, directions, distances, counts, starts = [
            np.array(value, copy=True) for value in self.view.get_contact_data(dt)]
        friction, friction_points, friction_counts, friction_starts = [
            np.array(value, copy=True) for value in self.view.get_friction_data(dt)]
        pairs = []
        for sensor, sensor_path in enumerate(self.sensor_paths):
            if sensor_path not in origins:
                raise ValueError(f"Missing same-step physics origin for {sensor_path}")
            origin = origins[sensor_path]
            for other, other_path in enumerate(self.filter_paths):
                n = self._slice(counts, starts, sensor, other, len(normal))
                f = self._slice(friction_counts, friction_starts, sensor, other, len(friction))
                normal_vectors = normal[n].reshape(-1, 1) * directions[n]
                normal_sum = normal_vectors.sum(axis=0)
                friction_sum = friction[f].sum(axis=0)
                moment = (np.cross(points[n] - origin, normal_vectors).sum(axis=0) +
                          np.cross(friction_points[f] - origin, friction[f]).sum(axis=0))
                total = normal_sum + friction_sum
                values = np.concatenate((normal_sum, friction_sum, total, moment, matrix[sensor, other]))
                if not np.isfinite(values).all():
                    raise ValueError("Nonfinite collision contact data")
                pairs.append({
                    "sensor_path": sensor_path, "other_path": other_path,
                    "normal_contact_count": int(counts[sensor, other]),
                    "friction_anchor_count": int(friction_counts[sensor, other]),
                    "normal_force_world_n": normal_sum.tolist(),
                    "friction_force_world_n": friction_sum.tolist(),
                    "collision_force_world_n": total.tolist(),
                    "collision_torque_about_sensor_origin_world_nm": moment.tolist(),
                    "force_matrix_world_n": matrix[sensor, other].tolist(),
                    "matrix_vs_normal_error_n": float(np.linalg.norm(matrix[sensor, other] - normal_sum)),
                })
        return {"stamp_ns": snapshot.stamp_ns, "physics_step": snapshot.physics_step,
                "physics_dt_s": dt, "frame_id": snapshot.frame_id,
                "source": "PhysX collision impulses / physics_dt; NOT suction constraint wrench",
                "pairs": pairs}
