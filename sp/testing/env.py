from pathlib import Path

ENV_ROOT = Path(__file__).absolute()
REPO_ROOT = ENV_ROOT.parents[2]
TEST_ROOT = REPO_ROOT / "test"
TEST_DATA_ROOT = TEST_ROOT / "_data"
HISTORY_DATA_ROOT = TEST_DATA_ROOT / "history"


PRECISION_GUARD = 1e-9
