"""Tests for shared template filters in core/templatetags/core_tags.py."""


from apps.core.templatetags.core_tags import (
    NAV_TEXT_MAX_CHARS,
    _compute_monogram,
    first_paragraph,
    nav_needs_monogram,
)

# ---------------------------------------------------------------------------
# first_paragraph filter (existing tests)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# nav_needs_monogram filter
# ---------------------------------------------------------------------------

def test_nav_needs_monogram_short_name():
    # 12 chars, 2 words — both within thresholds → full text
    assert nav_needs_monogram("Atelier Nord") is False


def test_nav_needs_monogram_single_word():
    assert nav_needs_monogram("Strand") is False  # 6 chars, 1 word


def test_nav_needs_monogram_char_threshold_exceeded():
    # 19 chars, 2 words — char count alone fails the test
    assert nav_needs_monogram("Strand Architecture") is True


def test_nav_needs_monogram_word_count_exceeded():
    # 3 words triggers monogram even if char count would otherwise pass
    assert nav_needs_monogram("Studio of Form") is True  # 14 chars, 3 words


def test_nav_needs_monogram_at_threshold():
    name = "A" * NAV_TEXT_MAX_CHARS
    assert nav_needs_monogram(name) is False


def test_nav_needs_monogram_above_threshold():
    name = "A" * (NAV_TEXT_MAX_CHARS + 1)
    assert nav_needs_monogram(name) is True


def test_nav_needs_monogram_empty():
    assert nav_needs_monogram("") is False


def test_nav_needs_monogram_none():
    assert nav_needs_monogram(None) is False


# ---------------------------------------------------------------------------
# _compute_monogram — standard cases
# ---------------------------------------------------------------------------

def test_monogram_two_founder_names():
    # v3: "Architects" is kept → 3 tokens B, W, A → BWA
    assert _compute_monogram("Beaumont Whitfield Architects") == "BWA"


def test_monogram_three_founders():
    # 4 tokens (no descriptor stripping) → first 3 = BWK
    assert _compute_monogram("Beaumont Whitfield Kellerman Architects") == "BWK"


def test_monogram_four_plus_tokens_first_three():
    # 5 tokens (descriptor kept) → first 3 = BWK
    assert _compute_monogram("Beaumont Whitfield Kellerman Adeyemi Architects") == "BWK"


def test_monogram_keeps_descriptor_words():
    # v3: profession word initial counts → Hopkins, Architects → HA
    assert _compute_monogram("Hopkins Architects") == "HA"


def test_monogram_strips_stop_words():
    # "Foster and Partners" → strip "and" (stop word); keep "Partners" → FP
    assert _compute_monogram("Foster and Partners") == "FP"


def test_monogram_strips_ampersand():
    # "Skidmore, Owings & Merrill" — '&' is stop word; no split on comma so
    # "Skidmore," is one token (comma stays). Initials: S, O, M → SOM
    # Note: comma is not a token boundary in the spec; this tests real behaviour.
    result = _compute_monogram("Skidmore Owings & Merrill")
    assert result == "SOM"


def test_monogram_strips_plus():
    # '+' is a token boundary; residual '+' token filtered by stop-word list (defensive)
    # ["Foster", "Partners"] → both kept → FP
    assert _compute_monogram("Foster + Partners") == "FP"


def test_monogram_hyphen_single_initial_only():
    # Hyphen is NOT a token boundary; "Zaha-Hadid" is one token → initial "Z"
    # v3: "Architects" kept → [Zaha-Hadid, Architects] → ZA
    assert _compute_monogram("Zaha-Hadid Architects") == "ZA"


def test_monogram_preserves_particle():
    # "De" is NOT in stop list (conservative policy); "Architects" kept → DGA
    assert _compute_monogram("De Graaf Architects") == "DGA"


def test_monogram_short_acronym_not_triggered():
    # "OMA" is ≤ 24 chars; monogram path would yield "O" but the template
    # never calls compute_monogram — this test verifies the function itself
    # returns "O" even if called directly (full text path prevents it in template).
    assert _compute_monogram("OMA") == "O"


def test_monogram_empty_string():
    assert _compute_monogram("") == ""


def test_monogram_none_equivalent():
    assert _compute_monogram("") == ""


def test_monogram_descriptor_words_kept():
    # v3: no descriptor filtering → both tokens survive → AS
    assert _compute_monogram("Architecture Studio") == "AS"


def test_monogram_normalises_whitespace():
    # v3: both tokens kept → SA
    assert _compute_monogram("  Strand   Architecture  ") == "SA"


def test_monogram_uppercase():
    result = _compute_monogram("strand architecture")
    assert result == result.upper()
