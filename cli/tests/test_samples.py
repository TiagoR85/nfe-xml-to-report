from pathlib import Path

import pytest
from lxml import etree

RAIZ = Path(__file__).resolve().parents[2]
SCHEMAS = RAIZ / "schemas" / "nfe_v4.00" / "nfe_v4.00.xsd"
VALIDOS = sorted((RAIZ / "samples" / "validos").glob("*.xml"))
INVALIDO_XSD = RAIZ / "samples" / "invalidos" / "xsd-violado.xml"


@pytest.fixture(scope="module")
def schema() -> etree.XMLSchema:
    return etree.XMLSchema(etree.parse(str(SCHEMAS)))


@pytest.mark.parametrize("xml", VALIDOS, ids=lambda p: p.name)
def test_sample_valido_passa_xsd(schema, xml):
    schema.assertValid(etree.parse(str(xml)))


def test_sample_xsd_violado_falha(schema):
    with pytest.raises(etree.DocumentInvalid):
        schema.assertValid(etree.parse(str(INVALIDO_XSD)))
