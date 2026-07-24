from pathlib import Path

import aion


def test_create_pdf_report_fallback(tmp_path):
    out = tmp_path / "report.pdf"
    created = aion.pdf.create_pdf_report("Title", ["Line 1", "Line 2"], str(out))
    created_path = Path(created)
    assert created_path.exists()
    assert created_path.suffix in {".pdf", ".txt"}
