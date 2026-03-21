"""Tests for custom template filters in core/templatetags/core_tags.py."""

from core.templatetags.core_tags import first_paragraph


def test_first_paragraph_single_block():
    text = "This is the first paragraph."
    assert first_paragraph(text) == "This is the first paragraph."


def test_first_paragraph_two_blocks():
    text = "First paragraph.\n\nSecond paragraph."
    assert first_paragraph(text) == "First paragraph."


def test_first_paragraph_strips_whitespace():
    text = "  First paragraph.  \n\nSecond paragraph."
    assert first_paragraph(text) == "First paragraph."


def test_first_paragraph_empty_string():
    assert first_paragraph("") == ""


def test_first_paragraph_none():
    assert first_paragraph(None) == ""


def test_first_paragraph_only_whitespace():
    assert first_paragraph("   ") == ""
