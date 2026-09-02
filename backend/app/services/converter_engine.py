import os
import time
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
import fitz
from pdf2docx import Converter
import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from app.core.config import settings
from app.core.exceptions import ConversionException, FileValidationException

logger = logging.getLogger("pdf2docx.engine")


def extract_pdf_watermark(pdf_path: Path) -> Optional[Dict[str, Any]]:
    """
    Scans PDF pages for rotated/diagonal background text blocks (e.g. 'Watermark', 'Confidential', 'Draft').
    Returns watermark metadata and the list of page indices where it is present.
    """
    try:
        doc_pdf = fitz.open(str(pdf_path))
        wm_pages = []
        wm_meta = None

        for p_no, page in enumerate(doc_pdf):
            data = page.get_text("dict")
            for b in data.get("blocks", []):
                for l in b.get("lines", []):
                    dx, dy = l.get("dir", (1, 0))
                    # Rotated / diagonal line (|dy| > 0.1)
                    if abs(dy) > 0.1:
                        for s in l.get("spans", []):
                            txt = s.get("text", "").strip()
                            if len(txt) > 1 and s.get("size", 0) >= 16:
                                if not wm_meta:
                                    c = s.get("color", 0)
                                    r = (c >> 16) & 0xFF
                                    g = (c >> 8) & 0xFF
                                    b_val = c & 0xFF
                                    hex_col = f"{r:02x}{g:02x}{b_val:02x}".upper() if c != 0 else "2562EB"
                                    font_name = s.get("font", "DejaVu Sans")
                                    if "-" in font_name:
                                        font_name = font_name.split("-")[0]
                                    wm_meta = {
                                        "text": txt,
                                        "size": s.get("size", 42),
                                        "font": font_name,
                                        "color": hex_col,
                                    }
                                if p_no not in wm_pages:
                                    wm_pages.append(p_no)
        doc_pdf.close()
        if wm_meta:
            wm_meta["pages_present"] = wm_pages
            return wm_meta
        return None
    except Exception as e:
        logger.warning(f"Watermark pre-scan encountered an issue: {e}")
        return None


def apply_word_post_processing(
    docx_path: Path,
    watermark_info: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Applies essential post-processing to the generated Word DOCX:
    1. Forces default View to 'Print Layout' in word/settings.xml so Word never opens in Web/Draft mode.
    2. Normalizes paragraph spacing and moves body page numbers to Word footers.
    3. Retains floating user image layering in front of text (behindDoc="0").
    4. Auto-fits table columns for cross-suite layout parity (Word + WPS Office).
    5. Injects modern DrawingML watermark into the header (Page 1 only if detected only on Page 1).
    6. Injects dynamic native Page Numbers (<w:fldSimple w:instr="PAGE"/>) into the footer.
    """
    try:
        doc = docx.Document(str(docx_path))

        # 1. Force Print Layout view mode by default in settings.xml
        try:
            settings_elm = doc.settings.element
            view_xml = f'<w:view {nsdecls("w")} w:val="print"/>'
            settings_elm.insert(0, parse_xml(view_xml))
        except Exception as view_err:
            logger.warning(f"Failed to set print layout view setting: {view_err}")

        # 2. Normalize paragraph spacing & remove standalone body page number paragraphs
        try:
            from docx.shared import Pt
            for p in list(doc.paragraphs):
                txt_clean = p.text.strip()
                if txt_clean.isdigit() and len(txt_clean) <= 3:
                    p._element.getparent().remove(p._element)
                else:
                    pf = p.paragraph_format
                    if pf.space_before and pf.space_before.pt > 6:
                        pf.space_before = Pt(round(pf.space_before.pt * 0.45, 1))
                    pf.space_after = Pt(0)
                    pf.line_spacing = 1.0
        except Exception as spacing_err:
            logger.warning(f"Failed to normalize paragraph spacing: {spacing_err}")

        # 3. Ensure user images overlay IN FRONT of text (behindDoc="0")
        try:
            for anchor in doc._element.xpath(".//wp:anchor"):
                anchor.set("behindDoc", "0")
        except Exception as anchor_err:
            logger.warning(f"Failed to adjust drawing Z-order: {anchor_err}")

        # 4. Optimize table layout and autofit for cross-suite compatibility (Microsoft Word & WPS Office)
        try:
            from docx.shared import Inches
            for t in doc.tables:
                t.autofit = True
                tblPr = t._element.xpath("w:tblPr")
                if tblPr:
                    tblPr[0].append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="autofit"/>'))
                for row in t.rows:
                    if len(row.cells) >= 3:
                        row.cells[0].width = Inches(1.2)
                        row.cells[1].width = Inches(4.5)
                        row.cells[2].width = Inches(1.5)
        except Exception as tbl_err:
            logger.warning(f"Failed to optimize table layout: {tbl_err}")

        # 5. Inject Modern DrawingML Watermark if detected
        if watermark_info and doc.sections:
            watermark_text = watermark_info.get("text", "Watermark")
            watermark_font = watermark_info.get("font", "DejaVu Sans")
            watermark_color = watermark_info.get("color", "2562EB")
            wm_pages = watermark_info.get("pages_present", [0])

            drawingml_xml = (
                f'<w:p {nsdecls("w")} xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
                f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                f'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">\n'
                f'  <w:pPr>\n'
                f'    <w:pStyle w:val="Header"/>\n'
                f'  </w:pPr>\n'
                f'  <w:r>\n'
                f'    <w:drawing>\n'
                f'      <wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="251658240" '
                f'behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">\n'
                f'        <wp:simplePos x="0" y="0"/>\n'
                f'        <wp:positionH relativeFrom="page">\n'
                f'          <wp:align>center</wp:align>\n'
                f'        </wp:positionH>\n'
                f'        <wp:positionV relativeFrom="page">\n'
                f'          <wp:align>center</wp:align>\n'
                f'        </wp:positionV>\n'
                f'        <wp:extent cx="5486400" cy="1371600"/>\n'
                f'        <wp:effectExtent l="0" t="0" r="0" b="0"/>\n'
                f'        <wp:wrapNone/>\n'
                f'        <wp:docPr id="9999" name="WatermarkShape"/>\n'
                f'        <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">\n'
                f'          <a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">\n'
                f'            <wps:wsp>\n'
                f'              <wps:cNvSpPr txBox="1"/>\n'
                f'              <wps:spPr>\n'
                f'                <a:xfrm rot="18900000">\n'
                f'                  <a:off x="0" y="0"/>\n'
                f'                  <a:ext cx="5486400" cy="1371600"/>\n'
                f'                </a:xfrm>\n'
                f'                <a:prstGeom prst="rect">\n'
                f'                  <a:avLst/>\n'
                f'                </a:prstGeom>\n'
                f'                <a:noFill/>\n'
                f'                <a:ln>\n'
                f'                  <a:noFill/>\n'
                f'                </a:ln>\n'
                f'              </wps:spPr>\n'
                f'              <wps:txbx>\n'
                f'                <w:txbxContent>\n'
                f'                  <w:p>\n'
                f'                    <w:pPr>\n'
                f'                      <w:jc w:val="center"/>\n'
                f'                    </w:pPr>\n'
                f'                    <w:r>\n'
                f'                      <w:rPr>\n'
                f'                        <w:rFonts w:ascii="{watermark_font}" w:hAnsi="{watermark_font}" w:cs="{watermark_font}"/>\n'
                f'                        <w:b/>\n'
                f'                        <w:sz w:val="96"/>\n'
                f'                        <w:szCs w:val="96"/>\n'
                f'                        <w:color w:val="{watermark_color}"/>\n'
                f'                      </w:rPr>\n'
                f'                      <w:t>{watermark_text}</w:t>\n'
                f'                    </w:r>\n'
                f'                  </w:p>\n'
                f'                </w:txbxContent>\n'
                f'              </wps:txbx>\n'
                f'              <wps:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr">\n'
                f'                <a:noFill/>\n'
                f'              </wps:bodyPr>\n'
                f'            </wps:wsp>\n'
                f'          </a:graphicData>\n'
                f'        </a:graphic>\n'
                f'      </wp:anchor>\n'
                f'    </w:drawing>\n'
                f'  </w:r>\n'
                f'</w:p>'
            )

            sec1 = doc.sections[0]
            # If watermark was only on Page 1 in PDF, use different_first_page_header_footer
            if wm_pages == [0]:
                sec1.different_first_page_header_footer = True
                f_header = sec1.first_page_header
                for p in list(f_header.paragraphs):
                    p._element.getparent().remove(p._element)
                f_header._element.append(parse_xml(drawingml_xml))

                for p in list(sec1.header.paragraphs):
                    p._element.getparent().remove(p._element)
            else:
                header = sec1.header
                for p in list(header.paragraphs):
                    p._element.getparent().remove(p._element)
                header._element.append(parse_xml(drawingml_xml))
                for sec in doc.sections[1:]:
                    sec.header.is_linked_to_previous = True

            logger.info(f"Injected modern DrawingML watermark '{watermark_text}' ({watermark_color}) on pages {wm_pages}")

        # 6. Inject Native Page Number Field into Word Footers
        try:
            footer_page_xml = (
                f'<w:p {nsdecls("w")}>\n'
                f'  <w:pPr>\n'
                f'    <w:pStyle w:val="Footer"/>\n'
                f'    <w:jc w:val="center"/>\n'
                f'  </w:pPr>\n'
                f'  <w:fldSimple w:instr="PAGE"/>\n'
                f'</w:p>'
            )
            for sec in doc.sections:
                fp_ftr = sec.first_page_footer
                for p in list(fp_ftr.paragraphs):
                    p._element.getparent().remove(p._element)
                fp_ftr._element.append(parse_xml(footer_page_xml))

                ftr = sec.footer
                for p in list(ftr.paragraphs):
                    p._element.getparent().remove(p._element)
                ftr._element.append(parse_xml(footer_page_xml))
        except Exception as ftr_err:
            logger.warning(f"Failed to inject footer page numbers: {ftr_err}")

        doc.save(str(docx_path))
        return True
    except Exception as e:
        logger.warning(f"Failed in post-processing Word DOCX: {e}")
        return False


def parse_page_range(range_str: Optional[str], total_pages: int) -> List[int]:
    """
    Parses a user-supplied page range string (e.g. '1-3, 5, 8') into a sorted,
    deduplicated list of 0-indexed page indices.
    
    If range_str is empty or None, returns all pages [0, 1, ..., total_pages - 1].
    """
    if not range_str or not range_str.strip():
        return list(range(total_pages))

    indices = set()
    parts = range_str.split(",")

    for part in parts:
        clean_part = part.strip()
        if not clean_part:
            continue
        if "-" in clean_part:
            subparts = clean_part.split("-")
            if len(subparts) != 2:
                raise FileValidationException(
                    message=f"Invalid page range token: '{clean_part}'. Expected format 'X-Y'.",
                    code="INVALID_PAGE_RANGE",
                )
            try:
                start_p = int(subparts[0].strip())
                end_p = int(subparts[1].strip())
            except ValueError:
                raise FileValidationException(
                    message=f"Invalid page numbers in range: '{clean_part}'.",
                    code="INVALID_PAGE_RANGE",
                )
            if start_p < 1 or end_p < 1 or start_p > end_p:
                raise FileValidationException(
                    message=f"Invalid range bounds '{clean_part}': Start page must be >= 1 and <= End page.",
                    code="INVALID_PAGE_RANGE",
                )
            if end_p > total_pages:
                raise FileValidationException(
                    message=f"Page number {end_p} exceeds total document pages ({total_pages}).",
                    code="PAGE_OUT_OF_BOUNDS",
                    details={"total_pages": total_pages, "requested_page": end_p},
                )
            for p in range(start_p, end_p + 1):
                indices.add(p - 1)
        else:
            try:
                single_p = int(clean_part)
            except ValueError:
                raise FileValidationException(
                    message=f"Invalid page number token: '{clean_part}'.",
                    code="INVALID_PAGE_RANGE",
                )
            if single_p < 1 or single_p > total_pages:
                raise FileValidationException(
                    message=f"Page number {single_p} is out of bounds (document has {total_pages} pages).",
                    code="PAGE_OUT_OF_BOUNDS",
                    details={"total_pages": total_pages, "requested_page": single_p},
                )
            indices.add(single_p - 1)

    if not indices:
        raise FileValidationException(
            message="Parsed page range is empty.",
            code="EMPTY_PAGE_RANGE",
        )

    return sorted(list(indices))


def convert_pdf_sync(
    pdf_path: Path,
    docx_path: Path,
    pages: Optional[List[int]] = None,
    password: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str, int], None]] = None,
) -> dict:
    """
    Synchronous conversion engine function.
    Converts PDF layout to DOCX format page-by-page, invoking progress_callback after each page.
    Automatically preserves background diagonal watermarks and enforces Print Layout view.
    """
    start_time = time.time()
    unlocked_pdf_path: Optional[Path] = None

    effective_pdf_path = pdf_path

    # Step 1: If password is provided, decrypt to a temporary unencrypted PDF
    if password:
        try:
            doc = fitz.open(str(pdf_path))
            if doc.is_encrypted:
                auth_success = doc.authenticate(password)
                if auth_success == 0:
                    raise FileValidationException(
                        message="Incorrect password for encrypted PDF.",
                        code="INVALID_PASSWORD",
                    )
                unlocked_pdf_path = pdf_path.parent / f"unlocked_{pdf_path.name}"
                doc.save(str(unlocked_pdf_path))
                effective_pdf_path = unlocked_pdf_path
            doc.close()
        except Exception as e:
            if isinstance(e, FileValidationException):
                raise
            raise ConversionException(
                message=f"Failed to decrypt password-protected PDF: {e}",
                code="DECRYPTION_ERROR",
            )

    # Pre-scan for background watermarks before conversion
    watermark_info = extract_pdf_watermark(effective_pdf_path)

    cv: Optional[Converter] = None
    try:
        cv = Converter(str(effective_pdf_path))
        doc_page_count = len(cv.fitz_doc)
        
        target_pages = pages if pages is not None else list(range(doc_page_count))
        total_target_count = len(target_pages)

        if total_target_count == 0:
            raise ConversionException(
                message="No pages selected for conversion.",
                code="NO_PAGES_SELECTED",
            )

        cv_settings = cv.default_settings

        if progress_callback:
            progress_callback(0, total_target_count, "Initializing layout analyzer", 5)

        # Step 1: Load specific page indexes
        cv.load_pages(pages=target_pages)

        # Step 2: Parse document layout structure (margins, sections, headers)
        cv.parse_document(**cv_settings)

        # Step 3: Reconstruct page by page
        for idx, page in enumerate(cv.pages):
            page_num = idx + 1
            percent = 10 + int((idx / total_target_count) * 75)
            if progress_callback:
                progress_callback(
                    page_num,
                    total_target_count,
                    f"Reconstructing page {page_num} of {total_target_count}",
                    percent,
                )
            page.parse(**cv_settings)

        if progress_callback:
            progress_callback(
                total_target_count,
                total_target_count,
                "Packaging Word document layout and styles",
                90,
            )

        # Step 4: Make DOCX
        cv.make_docx(str(docx_path), **cv_settings)

        # Step 5: Post-processing (Force Print Layout view + Watermark injection)
        if docx_path.exists():
            apply_word_post_processing(docx_path, watermark_info=watermark_info)

        duration = round(time.time() - start_time, 2)
        docx_size = docx_path.stat().st_size if docx_path.exists() else 0

        if progress_callback:
            progress_callback(
                total_target_count,
                total_target_count,
                "Conversion completed successfully",
                100,
            )

        logger.info(
            f"Successfully converted {total_target_count} page(s) to {docx_path.name} in {duration}s ({docx_size} bytes)"
        )

        return {
            "success": True,
            "pages_converted": total_target_count,
            "duration_seconds": duration,
            "docx_size_bytes": docx_size,
        }

    except Exception as e:
        logger.error(f"Conversion failed for {pdf_path.name}: {e}", exc_info=True)
        if isinstance(e, (FileValidationException, ConversionException)):
            raise
        raise ConversionException(
            message=f"Layout reconstruction failed: {str(e)}",
            code="CONVERSION_ERROR",
            details={"error_detail": str(e)},
        )
    finally:
        if cv:
            try:
                cv.close()
            except Exception:
                pass
        # Clean up unencrypted temporary PDF if one was created
        if unlocked_pdf_path and unlocked_pdf_path.exists():
            try:
                unlocked_pdf_path.unlink(missing_ok=True)
            except Exception:
                pass


async def convert_pdf_async(
    pdf_path: Path,
    docx_path: Path,
    pages: Optional[List[int]] = None,
    password: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str, int], None]] = None,
    timeout_seconds: Optional[int] = None,
) -> dict:
    """
    Executes conversion asynchronously in a separate thread/process with a timeout watchdog.
    """
    timeout = timeout_seconds or settings.CONVERSION_TIMEOUT_SECONDS

    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(
                None,
                convert_pdf_sync,
                pdf_path,
                docx_path,
                pages,
                password,
                progress_callback,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        raise ConversionException(
            message=f"Conversion timed out after {timeout} seconds.",
            code="CONVERSION_TIMEOUT",
            details={"timeout_seconds": timeout},
        )
