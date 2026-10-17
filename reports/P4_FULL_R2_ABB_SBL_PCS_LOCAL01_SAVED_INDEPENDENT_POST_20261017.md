# SBL PCS LOCAL01 保存证据人员独立后审

PASS_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST；129/129，失败0。

[
  {
    "schedule_index": 0,
    "fixture": "positive",
    "mode": "trace",
    "returned": true,
    "before": 2,
    "after": 2,
    "source_started": {
      "addMotion": 2,
      "collision": 107,
      "fixed_branch_project": 107,
      "freeGridMotions": 2,
      "isPathValid": 1,
      "mesh_load": 1,
      "native_fk": 107,
      "native_ik": 107,
      "state_rbs": 1,
      "vector_rbs": 215
    },
    "remaining_live_motions": 0
  },
  {
    "schedule_index": 1,
    "fixture": "positive",
    "mode": "plain",
    "returned": true,
    "before": 2,
    "after": 2,
    "source_started": null,
    "remaining_live_motions": 0
  },
  {
    "schedule_index": 2,
    "fixture": "negative",
    "mode": "trace",
    "returned": false,
    "before": 3,
    "after": 1,
    "source_started": {
      "addMotion": 3,
      "freeGridMotions": 2,
      "isPathValid": 1,
      "mesh_load": 1,
      "removeMotion": 2
    },
    "remaining_live_motions": 0
  },
  {
    "schedule_index": 3,
    "fixture": "negative",
    "mode": "plain",
    "returned": false,
    "before": 3,
    "after": 1,
    "source_started": null,
    "remaining_live_motions": 0
  }
]

实际四进程/四setup/四local，public13/solve/connect/writer/VI/formal均0。正例真实RBS非平凡true并保留child valid，负例真实分支不同不调RBS且递归删除child和grandchild；完整生命周期、q12/分支/角色/祖先、plain/trace、raw/EOF/reap/group、原生文件缺失及持久sidecar、加载scope与外费逐项核验。

费用上界8.19wall / 2.89CPU，累计869.8857053759941 / 811.528923。局部机制成功不是独立物理端到端路径或连续碰撞资格，checkSolution/connect/writer仍待另冻单solve。无新模型计算或科学运行；原失败、UNKNOWN、VI只读边界和正式预算未批准均保留。
