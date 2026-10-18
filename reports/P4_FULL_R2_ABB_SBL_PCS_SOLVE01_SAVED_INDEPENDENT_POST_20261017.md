# SBL PCS SOLVE01 保存证据独立后审

PASS_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST；111/111，失败0。

{
  "native_exact": true,
  "planner_status": "Exact solution",
  "solution_count": 1,
  "milestone_count": 6,
  "source_started": {
    "mesh_load": 1,
    "identify": 36,
    "native_fk": 2384,
    "native_ik": 2650,
    "collision": 2117,
    "addMotion": 50,
    "checkSolution": 34,
    "isPathValid": 15,
    "state_rbs": 34,
    "vector_rbs": 3104,
    "fixed_branch_project": 2074,
    "removeMotion": 27,
    "save2file": 1,
    "state_reconstruct": 6,
    "vector_reconstruct": 768,
    "freeGridMotions": 2
  },
  "return_histograms": {
    "native_ik": {
      "false": 271,
      "true": 2379
    },
    "collision": {
      "0": 2090,
      "1": 27
    },
    "checkSolution": {
      "false": 33,
      "true": 1
    },
    "fixed_branch_project": {
      "true": 2059,
      "false": 15
    },
    "vector_rbs": {
      "true": 2622,
      "false": 482
    },
    "state_rbs": {
      "true": 12,
      "false": 22
    },
    "isPathValid": {
      "false": 13,
      "true": 2
    },
    "vector_reconstruct": {
      "true": 767,
      "false": 1
    },
    "state_reconstruct": {
      "true": 5,
      "false": 1
    }
  },
  "registered_motion_lifetimes": 50,
  "uninitialized_connect_lifetimes": 14,
  "writer_attempts": 6,
  "writer_unknown_connect_attempts": 0,
  "writer_final_bytes_qualified": true,
  "native_file_count": 5
}

外费上界7.05wall/5.01CPU，累计876.935705375994/816.538923。真实单solve、raw、双EOF/回收/空group、全部生命周期与unknown connect、原生最终文件/sidecar/元数据分支及外费核验。EXACT仍待另冻完整独立物理路径资格；无新模型或科学运行，不证明CCD或正式性能。
