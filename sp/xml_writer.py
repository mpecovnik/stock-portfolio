import json
from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import Element, ElementTree, SubElement

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
            "email_address": "EmailAdress",
            "phone_number": "PhoneNumber",
            "resident_country": "ResidentCountry",
            "is_resident": "isResident",
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

    @property
    def personal_info(self) -> PersonalInfo:
        return PersonalInfo.from_file(self.personal_info_path)

    def create_header(self, root: Element) -> Element:
        child = SubElement(root, "edp:Header")
        taxpayer_child = SubElement(child, "edp:taxpayer")

        for name, value in self.personal_info.base_info:
            SubElement(
                taxpayer_child, f"edp:{self.personal_info.base_info.attr_conversion(name)}", attrib={"text": value}
            )

        return root

    def load_report(self) -> pd.DataFrame:

        year = int(self.personal_info.doh_div_info.period)

        div_report = DividendReport(
            years=[year],
            history=DividendHistory(path=self.input_path),
        )

        return div_report.create_report()

    def create_doh_div_root(self, envelope: Element) -> Element:
        doh_div_root = SubElement(envelope, "body")
        doh_div_child = SubElement(doh_div_root, "Doh_Div")

        for name, value in self.personal_info.doh_div_info:
            if isinstance(value, bool):
                value = str(value).lower()
            SubElement(doh_div_child, self.personal_info.doh_div_info.attr_conversion(name), attrib={"text": value})

        return doh_div_root

    def add_dividend(self, dividend_root: Element, row: pd.Series) -> None:
        divident_item = SubElement(dividend_root, "DividendItem")
        SubElement(divident_item, "Date", attrib={"text": row.DATE})
        SubElement(divident_item, "PayerIdentificationNumber", attrib={"text": row.ISIN})
        SubElement(divident_item, "PayerName", attrib={"text": row.Name})

        if "Vanguard" in row.Name:  # TODO
            address = "Europadamm 2-6, 41460 Neuss, Germany"
            country = "Germany"
            statement = "192/2006, 10. člen"
        elif "iShares" in row.Name:
            address = "2 Ballsbridge Park, Ballsbridge, Dublin, D04 YW83"
            country = "Ireland"
            statement = "96/2002, 10. člen"
        else:
            raise ValueError

        SubElement(divident_item, "PayerAddress", attrib={"text": address})
        SubElement(divident_item, "PayerCountry", attrib={"text": country})
        SubElement(divident_item, "Type", attrib={"text": "1"})
        SubElement(divident_item, "Value", attrib={"text": str(row["Total (EUR)"])})
        SubElement(divident_item, "ForeignTax", attrib={"text": str(row["Withholding tax"])})
        SubElement(divident_item, "SourceCountry", attrib={"text": country})
        SubElement(divident_item, "ReliefStatement", attrib={"text": statement})

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
        doh_div_root = self.create_doh_div_root(envelope=envelope)
        dividend_root = SubElement(doh_div_root, "Dividend")

        report = self.load_report()

        for _, row in report.iterrows():
            self.add_dividend(dividend_root=dividend_root, row=row)

        tree = ElementTree(element=root)
        tree.write(self.output_path)
