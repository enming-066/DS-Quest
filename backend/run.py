"""启动脚本：python backend/run.py

注意：backend/vendor 是本项目自带的依赖目录（FastAPI 等），
所以不需要你额外 pip install，只要用对解释器即可。
"""

from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
for extra in (BACKEND_DIR / "vendor", BACKEND_DIR):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

# --reload 时 uvicorn 会另起子进程，子进程要靠 PYTHONPATH 找到 app 包
os.environ["PYTHONPATH"] = os.pathsep.join(
    [str(BACKEND_DIR / "vendor"), str(BACKEND_DIR), os.environ.get("PYTHONPATH", "")]
)

if __name__ == "__main__":
    import uvicorn

    from app.config import settings

    url = f"http://{settings.host}:{settings.port}"
    print(f"\n  DS Quest 启动中……  {url}\n")
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload="--reload" in sys.argv,
        log_level="info",
    )
