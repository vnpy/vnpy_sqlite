import os
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT: Path = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# vnpy.trader.utility 导入时按当前目录决定 .vntrader 位置，vnpy.trader.setting 导入时读取 vt_setting.json。
# 必须在第一次 import vnpy 之前切到带空 .vntrader 的临时目录，避免读写用户真实配置。
ORIGINAL_CWD: str = os.getcwd()
TRADER_TEMP_DIR: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
VNTRADER_DIR: Path = Path(TRADER_TEMP_DIR.name).joinpath(".vntrader")
VNTRADER_DIR.mkdir()
os.chdir(TRADER_TEMP_DIR.name)

DATABASE_FILENAME: str = "test_sqlite.db"

from vnpy.trader.setting import SETTINGS  # noqa: E402

# vnpy.trader.logger 导入时按 log.file 创建日志目录，需在它被导入前关闭。
SETTINGS["log.file"] = False
SETTINGS["log.console"] = False
# sqlite_database 在导入时读取 database.database，并用 get_file_path 写到当前 .vntrader。
SETTINGS["database.name"] = "sqlite"
SETTINGS["database.database"] = DATABASE_FILENAME


@pytest.fixture(scope="session")
def vntrader_dir() -> Path:
    return VNTRADER_DIR


def pytest_unconfigure(config: pytest.Config) -> None:
    os.chdir(ORIGINAL_CWD)
    try:
        module = sys.modules.get("vnpy_sqlite.sqlite_database")
        if module is not None and not module.db.is_closed():
            module.db.close()
    finally:
        TRADER_TEMP_DIR.cleanup()
