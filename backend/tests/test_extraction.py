"""Extraction tests that need no external deps (CSV via stdlib, unknown type)."""
from app.modules.documents.extraction import extract_text


def test_csv_extraction():
    data = b"name,qty\ncoconut,12\nwater,30\n"
    out = extract_text(data, "harvest.csv")
    assert "coconut, 12" in out
    assert "name, qty" in out


def test_unknown_type_returns_empty():
    assert extract_text(b"...", "notes.bin") == ""
