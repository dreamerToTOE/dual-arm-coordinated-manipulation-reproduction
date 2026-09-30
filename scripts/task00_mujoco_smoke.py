#!/usr/bin/env python3
"""TASK00: verify the existing MuJoCo environment can advance one physics step."""

import sys

import mujoco


MODEL_XML = """
<mujoco>
  <worldbody>
    <body name="test">
      <joint name="hinge" type="hinge"/>
      <geom type="sphere" size="0.01" mass="1"/>
    </body>
  </worldbody>
</mujoco>
"""


def main() -> None:
    model = mujoco.MjModel.from_xml_string(MODEL_XML)
    data = mujoco.MjData(model)
    mujoco.mj_step(model, data)
    print("python=", sys.version.split()[0])
    print("mujoco=", mujoco.__version__)
    print("smoke_step_time=", data.time)


if __name__ == "__main__":
    main()
