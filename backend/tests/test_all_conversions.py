import docx
import pytest
from pathlib import Path
from app.services.converter_engine import convert_pdf_sync

SAMPLE_PDF_PATH = Path("../sample-local-pdf_2_edited (2).pdf")
LIPA_PDF_PATH = Path("../Warehouse_Managment_LIPA.pdf")


@pytest.mark.skipif(not SAMPLE_PDF_PATH.exists(), reason="Local sample test PDF not present")
def test_sample_pdf_watermark_and_images_and_page_numbers(tmp_path):
    """
    Tests sample-local-pdf_2_edited (2).pdf:
    1. Watermark 'Watermark' in header with correct counter-clockwise upward diagonal rotation (rot=19800000).
    2. Building photo and signature in foreground (behindDoc = '0').
    3. Page numbers in footer (<w:fldSimple w:instr="PAGE"/>).
    4. No leaked trailing body numbers creating blank pages.
    """
    pdf_path = SAMPLE_PDF_PATH
    docx_path = tmp_path / "sample_test.docx"

    result = convert_pdf_sync(pdf_path, docx_path)
    assert result["success"] is True
    assert result["pages_converted"] == 3

    doc = docx.Document(str(docx_path))
    assert len(doc.sections) == 3

    # Check header DrawingML watermark & upward diagonal rotation (rot=19800000 = 330 deg)
    sec1 = doc.sections[0]
    hdr_xml = sec1.first_page_header._element.xml if sec1.different_first_page_header_footer else sec1.header._element.xml
    assert "WatermarkShape" in hdr_xml
    assert "Watermark" in hdr_xml
    assert 'rot="19800000"' in hdr_xml

    # Check footer has native PAGE number field
    ftr_xml = sec1.first_page_footer._element.xml if sec1.different_first_page_header_footer else sec1.footer._element.xml
    assert "w:fldSimple" in ftr_xml

    # Check images are in foreground
    for anchor in doc._element.xpath(".//wp:anchor"):
        assert anchor.get("behindDoc") == "0"


@pytest.mark.skipif(not LIPA_PDF_PATH.exists(), reason="Local LIPA test PDF not present")
def test_warehouse_lipa_pdf_emblem_and_contact_footer(tmp_path):
    """
    Tests Warehouse_Managment_LIPA.pdf:
    1. Circular emblem is in background (behindDoc = '1').
    2. Contact info is in footer with hyperlinked styling for web & email (color=0563C1, underline=single).
    3. NO page number fields injected into footer.
    """
    pdf_path = LIPA_PDF_PATH
    docx_path = tmp_path / "lipa_test.docx"

    result = convert_pdf_sync(pdf_path, docx_path)
    assert result["success"] is True
    assert result["pages_converted"] == 11

    doc = docx.Document(str(docx_path))
    sec1 = doc.sections[0]
    ftr_xml = sec1.footer._element.xml

    # Contact lines and hyperlinked web/email styling must be in footer XML
    assert "Fortress Ct" in ftr_xml
    assert "www.sublime-ent.com" in ftr_xml
    assert "globalsales@sublime-ent.com" in ftr_xml
    assert 'w:val="0563C1"' in ftr_xml
    assert 'w:val="single"' in ftr_xml

    # No fake page number field
    assert "w:fldSimple" not in ftr_xml

    # Circular background emblem must be behind text
    anchors = doc._element.xpath(".//wp:anchor")
    assert len(anchors) > 0
    for anchor in anchors:
        assert anchor.get("behindDoc") == "1"
