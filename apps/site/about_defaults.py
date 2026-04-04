"""Reusable About-page starter defaults and prompts."""

PLACEHOLDER_MARKERS = (
    "[Your Name]",
    "[Your Local Professional Body]",
    "[Your Professional Institute]",
    "[Add ",
    "[Describe ",
    "[Explain ",
)

CLOSING_INVITATION_DEFAULT = (
    "Get in touch about a project, a site, or an early-stage question."
)

PRACTICE_STRUCTURE_PROMPT = (
    '[Add truthful practice structure, for example "Solo practice" or "Small studio".]'
)

PROJECT_LEADERSHIP_PROMPT = (
    "[Explain how projects are led and where consultants or collaborators are involved.]"
)

PROFESSIONAL_STANDING_PROMPT = (
    "[Add the public registration or professional standing shown on this page.]"
)


def is_placeholder_text(value: str) -> bool:
    return bool(value) and any(marker in value for marker in PLACEHOLDER_MARKERS)


def public_text(value: str) -> str:
    return "" if is_placeholder_text(value) else value


def public_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip() and not is_placeholder_text(line)]
