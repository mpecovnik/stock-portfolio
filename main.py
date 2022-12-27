from pathlib import Path

from sp.xml_writer import DivDohXML

if __name__ == "__main__":

    xml_writer = DivDohXML(
        input_path=Path("/home/mpecovnik/Private/data/stock-portfolio/history"),
        output_path=Path("./div_doh_report.xsd"),
        personal_info_path=Path("./config.json"),
        years=[2022]
    )
    element = xml_writer.write()
