import shutil
import xml.etree.ElementTree as etree
from pathlib import Path

import pytest

from sp._testing.env import HISTORY_DATA_ROOT, TEST_DATA_ROOT
from sp.xml_writer import DivDohXML


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_write(input_path: Path) -> None:

    base_path = TEST_DATA_ROOT / "test_xml_writer" / "test_write"

    compare_path = base_path / "compare.xml"
    config_path = base_path / "test_config.json"
    output_path = base_path / "output"
    output_xml = output_path / "output.xml"

    output_path.mkdir(exist_ok=True)

    xml_writer = DivDohXML(
        input_path=input_path,
        output_path=output_xml,
        personal_info_path=config_path,
    )
    xml_writer.write()

    test_xml = etree.ElementTree(file=output_xml).getroot()
    compare_xml = etree.ElementTree(file=compare_path).getroot()

    assert etree.tostring(test_xml) == etree.tostring(compare_xml)

    shutil.rmtree(output_path)
