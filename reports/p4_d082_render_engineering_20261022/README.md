# D082 文档渲染环境恢复

Ubuntu22主机的glibc不能满足当前工作区所捆绑的LibreOffice/Poppler。保持原科学代码、报告内容、主机库及捆绑可执行文件原字节，只在`work/d082_render_runtime/`提取Ubuntu24的glibc与动态加载器，并用该加载器运行原捆绑`soffice.bin`、`pdfinfo`、`pdftoppm`。所需新版libstdc++直接使用捆绑Poppler内的版本。未使用用户安装的桌面LibreOffice，未安装主机系统包。

固定sysroot来源为`ubuntu@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac`，仅从临时Docker容器提取`/usr/lib/x86_64-linux-gnu/`，随后移除该容器。主机已有Noto CJK字体与`/etc/fonts/fonts.conf`用于中文排版。

两次有限工程尝试：

1. 使用隔离加载器后，原捆绑LibreOffice输出PDF；后续原捆绑Poppler仍通过主机加载器启动，报`GLIBC_2.38`缺失。原错误日志完整保留。
2. 同时将两个捆绑Poppler入口放入任务局部wrapper，统一使用隔离加载器；canonical `render_docx.py`任务局部副本运行退出0，生成18页PNG与PDF。只替换其`_resolve_soffice`选择逻辑，其余渲染及PDF转PNG流程保留。

实际渲染结果在`work/d082_recovery_20261022/render2/`，含`page-1.png`至`page-18.png`和报告PDF。最终可交付版本须由root完整逐页查看，内容改动后重新渲染。`recovery.json`保存本次输入SHA、隔离库/wrapper SHA和输出PDF SHA。

以后使用工作区依赖工具返回的捆绑Python运行轻量配方；下列命令会在sysroot不存在时从固定镜像准备它，否则复用任务局部文件：

```bash
/home/ubuntu2004/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  scripts/p4_d082/render_report_isolated.py \
  --docx reports/P4_D082闭链规划算法与完整虚拟仿真研究报告_20261022.docx \
  --output-dir work/d082_recovery_20261022/render3
```

各次后续渲染的完整日志和JSON记录自动保存在`work/d082_render_runtime/logs/render_<UTC>.*`，包含输入SHA、执行命令、页面数及原捆绑二进制身份。成功表示已产生页面图，视觉质量仍需逐页审查。

Git只纳入轻量配方、本目录小型错误/成功日志及JSON。不要提交`work/d082_render_runtime/sysroot/`、Docker镜像或任何捆绑二进制。该恢复属于文档渲染工程，不新增科学预算或实验次数。

最终排版交付为14页，21个可编辑OMML公式对象、7幅图。`final_visual_qa.json`绑定最终DOCX/PDF及全部14页SHA；前13页与已逐页查看版本逐像素一致，最终第14页另行检查。`final_render_record.json`保留实际渲染入口，原18页恢复稿仅为历史工程结果。
