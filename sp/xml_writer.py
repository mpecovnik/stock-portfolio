import json
from pathlib import Path
from typing import List
from xml.etree.ElementTree import Element, SubElement

import pandas as pd
from pydantic import parse_obj_as

from .history import DividendHistory
from .model import BaseModel
from .report import DividendReport


class PersonalInfo(BaseModel):
    tax_number: int
    tax_payer_type: str
    name: str
    address: str
    city: str
    post_number: int
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

    @classmethod
    def from_file(cls, path: Path) -> "PersonalInfo":
        return parse_obj_as(cls, json.loads(path.read_text()))


class DivDohXML(BaseModel):
    personal_info_path: Path
    input_path: Path
    output_path: Path
    years: List[int]

    def create_header(self, root: Element) -> Element:
        child = SubElement(root, "edp:Header")
        taxpayer_child = SubElement(child, "edp:taxpayer")

        personal_info = PersonalInfo.from_file(self.personal_info_path)
        for name, value in personal_info:
            SubElement(taxpayer_child, f"edp:{personal_info.attr_conversion(name)}", attrib={"text": value})

        return root

    def load_report(self) -> pd.DataFrame:
        div_report = DividendReport(
            years=self.years,
            history=DividendHistory(path=self.input_path),
        )

        return div_report.create_report()

    def write(self) -> Element:
        root = Element(
            "Envelope",
            {
                "xmlns": "http://edavki.durs.si/Documents/Schemas/Doh_Div_3.xsd",
                "xmlns:edp": "http://edavki.durs.si/Documents/Schemas/EDP-Common-1.xsd",
            },
        )

        envelope = self.create_header(root)
        SubElement(envelope, "edp:AttachmentList")
        SubElement(envelope, "edp:Signatures")
        body = SubElement(envelope, "body")
        SubElement(body, "edp:bodyContent")

        return root
