"""Module that implements command line interface for the package."""

from pathlib import Path

import click


@click.group()
def cli() -> None:
    pass


@cli.group()
def div_doh() -> None:
    pass


@div_doh.command(name="xml-report")
@click.option("--taxpayer-info", default=None, help="Config JSON that holds the tax-payer info.")
@click.option("--data-path", default=None, help="Directory that holds the input data.")
@click.option("--xml-path", default=None, help="Path to XML output report.")
def create_div_doh_xml_report(taxpayer_info: str, data_path: str, xml_path: str) -> None:
    from sp.xml_writer import DivDohXML

    writer = DivDohXML(
        personal_info_path=Path(taxpayer_info),
        input_path=Path(data_path),
        output_path=Path(xml_path),
    )
    writer.write()
