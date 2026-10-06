"""[ENGINEERING] 可见GUI入口，复用已验证的原场景/物理桥/记录器。

只切换显示方式；本入口无headless选项，未找到显示服务器时拒绝启动。
"""
import os
from task01_cube04_headless import main

if __name__ == '__main__':
    if not os.environ.get('DISPLAY'):
        raise RuntimeError('可见GUI需要DISPLAY；禁止静默退回headless。')
    main(visible_gui=True)
