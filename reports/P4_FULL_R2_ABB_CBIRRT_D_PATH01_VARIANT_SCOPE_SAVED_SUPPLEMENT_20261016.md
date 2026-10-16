# P 碰撞变体与被动链机制保存审计补充

PASS_VARIANT_SCOPE_SAVED_SUPPLEMENT：1659/1659。

完整413节点中，native和aligned原始PQP均无collision、各47908查询；native保存TCP全部413节点不符合物理坐标一致性，aligned全部413节点符合。完整路径资格接纳只依冻结aligned策略。

四条原始完整边active_chain=0,0,1,1、passive branch均3；真实跨树桥保留原active0失败M2与原active1成功fallback M33。该单条路径给出原机制实际发生的见证，不构成PCS复杂场景优势或统计性能证据。全部原始失败保持。

{
  "native": {
    "nodes": 413,
    "native_collision_nodes": 0,
    "pose_pass_nodes": 0,
    "pose_mismatch_nodes": 413,
    "PQP_queries": 47908,
    "statuses": {
      "COLLISION_PHYSICAL_TCP_MISMATCH": 413
    },
    "maximum_saved_translation_error_mm": 0.003531998994674268,
    "maximum_saved_rotation_error": 6.824437533303751e-06
  },
  "aligned": {
    "nodes": 413,
    "native_collision_nodes": 0,
    "pose_pass_nodes": 413,
    "pose_mismatch_nodes": 0,
    "PQP_queries": 47908,
    "statuses": {
      "PASS": 413
    },
    "maximum_saved_translation_error_mm": 3.410605131648481e-13,
    "maximum_saved_rotation_error": 4.440892098500626e-16
  }
}
