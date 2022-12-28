import shutil

from click.testing import CliRunner

from sp._testing.env import HISTORY_DATA_ROOT, TEST_DATA_ROOT
from sp.cli import cli


def test_cli_write_doh_div_xml() -> None:

    base_path = TEST_DATA_ROOT / "test_xml_writer" / "test_write"

    config_path = base_path / "test_config.json"
    output_path = base_path / "output"
    output_xml = output_path / "output.xml"

    output_path.mkdir(exist_ok=True)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "div-doh",
            "xml-report",
            "--taxpayer-info",
            str(config_path),
            "--data-path",
            str(HISTORY_DATA_ROOT),
            "--xml-path",
            str(output_xml),
        ],
    )
    assert result.exit_code == 0

    shutil.rmtree(output_path)
