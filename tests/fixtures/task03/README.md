# TASK03 immutable model fixture

These are **byte-identical**, expanded historical model inputs, not a new robot model.
They are copied from the local ignored `results/20261006_TASK01_single_cube_geometry_probe01/raw/`
to make the offline test reproducible from a Git checkout. No geometry, joints, tool,
collision, ACM/SRDF or acceptance condition has been changed. The archived 293 state
records and config remain at their original tracked paths and are not rewritten.

| File | SHA256 |
| --- | --- |
| robot.urdf | a9d6a364c89b9e72e51da962d16ee44de45595429339b51004a59211b312939b |
| robot.srdf | 11b89277bfa5fb7bcedfa35f8285507e88d2c793df6ba8e04daf12c8eb8d023a |

The source description is the predecessor
`dreamerToTOE/dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a`,
`ros_ws/src/fr3_dual_side_suction_description/urdf/dual_fr3_side_suction.urdf.xacro`
and `dual_side_suction.xacro`, with existing `franka_description` 2.8.1 FR3 macros.
The model snapshot is tied to the archived geometry run, not an assertion that the
current accepted Task26 foundation or draft benchmark is this historical topology.

FR3 description dependency declares Apache 2.0; its LICENSE is retained as
`FRANKA_LICENSE`. See the original xacro/source attribution. Mesh binaries are **not**
copied here; `package://franka_description/...` remains unchanged. If the description
package is unavailable, MoveIt reports unresolved mesh resources but still computes
kinematics; do not turn that into collision evidence. Our final test environment
resolves this package from the already installed predecessor workspace.

No Isaac scene, physics callback, ROS node, control code or paper-author algorithm
is copied into this fixture. The old bilateral-to-TARGET geometry is superseded as
an execution benchmark, but its joint/FK records remain useful mathematical oracles.
