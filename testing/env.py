from pathlib import Path

ENV_ROOT = Path(__file__).absolute()
REPO_ROOT = ENV_ROOT.parents[1]
TEST_ROOT = REPO_ROOT / "test"
TEST_DATA_ROOT = TEST_ROOT / "_data"
