import json
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent

import pandas as pd
from pydantic import parse_obj_as

from .history import DividendHistory
from .model import BaseModel
from .report import DividendReport


class BaseInfo(BaseModel):
    tax_number: str
    tax_payer_type: str
    name: str
    address: str
    city: str
    post_number: str
    birth_date: str

    @staticmethod
    def attr_conversion(attr_name: str) -> str:
        DICT = {
            "tax_number": "taxNumber",
            "tax_payer_type": "taxpayerType",
            "name": "name",
            "address": "address1",
            "city": "city",
            "post_number": "postNumber",
            "birth_date": "birthDate",
        }

        return DICT[attr_name]


class DohDivInfo(BaseModel):
    period: str
    email_address: str
    phone_number: str
    resident_country: str
    is_resident: Optional[bool] = True
    locked: Optional[bool] = False
    self_report: Optional[bool] = False
    workflow_type: Optional[bool] = True

    @staticmethod
    def attr_conversion(attr_name: str) -> str:
        DICT = {
            "period": "Period",
            "email_address": "EmailAddress",
            "phone_number": "PhoneNumber",
            "resident_country": "ResidentCountry",
            "is_resident": "IsResident",
            "locked": "Locked",
            "self_report": "SelfReport",
            "workflow_type": "WfTypeU",
        }

        return DICT[attr_name]


class PersonalInfo(BaseModel):
    base_info: BaseInfo
    doh_div_info: DohDivInfo

    @classmethod
    def from_file(cls, path: Path) -> "PersonalInfo":
        return parse_obj_as(cls, json.loads(path.read_text()))


class DivDohXML(BaseModel):
    personal_info_path: Path
    input_path: Path
    output_path: Path
    write_csv_report: Optional[bool] = True

    @property
    def personal_info(self) -> PersonalInfo:
        return PersonalInfo.from_file(self.personal_info_path)

    def create_header(self, root: Element) -> Element:
        header = SubElement(root, "edp:Header")

        taxpayer_child = SubElement(header, "edp:taxpayer")

        for name, value in self.personal_info.base_info:
            SubElement(taxpayer_child, f"edp:{self.personal_info.base_info.attr_conversion(name)}").text = value

        workflow = SubElement(header, "edp:Workflow")
        SubElement(workflow, "edp:DocumentWorkflowID").text = "O"

        return root

    def load_report(self) -> pd.DataFrame:

        year = int(self.personal_info.doh_div_info.period)

        div_report = DividendReport(
            years=[year],
            history=DividendHistory(path=self.input_path),
        )

        report = div_report.create_report()

        if self.write_csv_report:
            path = self.output_path.parent / "report.csv"
            report.to_csv(path_or_buf=path, index=False)

        return report

    def create_doh_div_root(self, envelope: Element) -> Element:
        doh_div_root = SubElement(envelope, "body")
        doh_div_child = SubElement(doh_div_root, "Doh_Div")

        for name, value in self.personal_info.doh_div_info:
            if isinstance(value, bool):
                value = str(int(value))

            SubElement(doh_div_child, self.personal_info.doh_div_info.attr_conversion(name)).text = value

        return doh_div_root

    def add_dividend(self, dividend_root: Element, row: pd.Series) -> None:
        divident_item = SubElement(dividend_root, "Dividend")
        SubElement(divident_item, "Date").text = row.DATE
        SubElement(divident_item, "PayerIdentificationNumber").text = row.ISIN
        SubElement(divident_item, "PayerName").text = row.NAME

        if "Vanguard" in row.NAME:  # TODO
            address = "Europadamm 2-6, 41460 Neuss, Germany"
            country = "Germany"
            statement = "192/2006, 10. ??len"
        elif "iShares" in row.NAME:
            address = "2 Ballsbridge Park, Ballsbridge, Dublin, D04 YW83"
            country = "Ireland"
            statement = "96/2002, 10. ??len"
        else:
            raise ValueError

        SubElement(divident_item, "PayerAddress").text = address
        SubElement(divident_item, "PayerCountry").text = country
        SubElement(divident_item, "Type").text = "1"
        SubElement(divident_item, "Value").text = str(row.TOTAL)
        SubElement(divident_item, "ForeignTax").text = str(row.TAX)
        SubElement(divident_item, "SourceCountry").text = country
        SubElement(divident_item, "ReliefStatement").text = statement

    def write(self) -> None:
        root = Element(
            "Envelope",
            {
                "xmlns": "http://edavki.durs.si/Documents/Schemas/Doh_Div_3.xsd",
                "xmlns:edp": "http://edavki.durs.si/Documents/Schemas/EDP-Common-1.xsd",
            },
        )

        envelope = self.create_header(root=root)
        SubElement(envelope, "edp:AttachmentList")
        SubElement(envelope, "edp:Signatures")
        dividend_root = self.create_doh_div_root(envelope=envelope)

        report = self.load_report()

        for _, row in report.iterrows():
            self.add_dividend(dividend_root=dividend_root, row=row)

        tree = ElementTree(element=root)
        indent(tree)
        tree.write(self.output_path)
