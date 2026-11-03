"""全局配置。

所有可调参数集中在这里，方便以后修改，不用满项目找常量。
配置优先级：环境变量 > backend/.env 文件 > 这里的默认值。
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
CONTENT_DIR = BACKEND_DIR / "content"
DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "dsquest.db"
RUN_DIR = BACKEND_DIR / "data" / "runs"


def _load_dotenv() -> None:
    """极简 .env 读取器，避免为了一个功能引入额外的依赖。"""
    env_file = BACKEND_DIR / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        # 已经存在的环境变量优先，不被文件覆盖
        os.environ.setdefault(key, value)


_load_dotenv()


def _find_compiler() -> str:
    """优先使用环境变量指定，否则在 PATH 里找 g++ / clang++。"""
    explicit = os.environ.get("DSQ_COMPILER", "").strip()
    if explicit and Path(explicit).exists():
        return explicit
    for name in ("g++", "clang++"):
        found = shutil.which(name)
        if found:
            return found
    return ""


def _find_c_compiler() -> str:
    explicit = os.environ.get("DSQ_C_COMPILER", "").strip()
    if explicit and Path(explicit).exists():
        return explicit
    for name in ("gcc", "clang"):
        found = shutil.which(name)
        if found:
            return found
    return ""


class Settings:
    # --- 服务 ---
    host: str = os.environ.get("DSQ_HOST", "127.0.0.1")
    port: int = int(os.environ.get("DSQ_PORT", "8000"))

    # --- 判题 ---
    cpp_compiler: str = _find_compiler()
    c_compiler: str = _find_c_compiler()
    compile_timeout_s: float = float(os.environ.get("DSQ_COMPILE_TIMEOUT", "25"))
    default_time_limit_ms: int = int(os.environ.get("DSQ_TIME_LIMIT_MS", "2000"))
    default_memory_limit_mb: int = int(os.environ.get("DSQ_MEMORY_LIMIT_MB", "256"))
    max_output_bytes: int = 64 * 1024
    # 一次提交最多跑多少个测试点，防止内容写错导致卡死
    max_test_cases: int = 30

    # --- DeepSeek ---
    api_key: str = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    api_base: str = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model: str = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    ai_timeout_s: float = float(os.environ.get("DSQ_AI_TIMEOUT", "60"))
    ai_max_tokens: int = int(os.environ.get("DSQ_AI_MAX_TOKENS", "1200"))
    # 每天允许的 AI 调用次数上限（省钱保险丝）
    ai_daily_limit: int = int(os.environ.get("DSQ_AI_DAILY_LIMIT", "30"))

    @property
    def ai_enabled(self) -> bool:
        return bool(self.api_key)


settings = Settings()
