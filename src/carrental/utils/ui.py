# ==============================================================================
# Console drawing helpers (pretty boxes, prompts).
# This file is the 'explained like I am 10' version with simple comments.
# Every step tells you plainly what it does.

# ==============================================================================

"""Console UI helpers: centered boxes, left-aligned content."""

from __future__ import annotations
import os, shutil
from typing import List
import getpass

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def term_width(default: int = 80) -> int:
    try:
        return shutil.get_terminal_size((default, 24)).columns
    except Exception:
        return default

def center_line(text: str, width: int | None = None) -> str:
    w = width or term_width()
    t = text.strip()
    left = max((w - len(t)) // 2, 0)
    return (" " * left) + t

def _split_lines(items: List[str]) -> List[str]:
    out: List[str] = []
    for s in items:
        out.extend(s.splitlines())
    return out

def boxed(lines: List[str], title: str | None = None, padding: int = 0) -> str:
    """Draw a centered box; keep content LEFT-ALIGNED inside the box for neat columns."""
    width = term_width()
    lines = _split_lines(lines)
    content_max = max((len(line) for line in lines), default=0)
    inner_width = min(max(content_max, 20), width - 10)  # content width with side margins
    box_width = inner_width + 4  # borders + 1 space each side
    left_pad = max((width - box_width) // 2, 0)  # center the whole box
    pad_prefix = " " * left_pad

    top = pad_prefix + "┌" + "─" * (box_width - 2) + "┐"
    bottom = pad_prefix + "└" + "─" * (box_width - 2) + "┘"

    parts: List[str] = [top]

    if title:
        t = title.strip()
        t_pad = max((inner_width - len(t)) // 2, 0)  # title remains centered
        parts.append(pad_prefix + f"│ {' ' * t_pad}{t}{' ' * (inner_width - len(t) - t_pad)} │")

    for _ in range(padding):
        parts.append(pad_prefix + f"│ {' ' * inner_width} │")

    for line in lines:
        clipped = line[: inner_width]
        rpad = inner_width - len(clipped)
        parts.append(pad_prefix + f"│ {clipped}{' ' * rpad} │")  # LEFT aligned content

    for _ in range(padding):
        parts.append(pad_prefix + f"│ {' ' * inner_width} │")

    parts.append(bottom)
    return "\n".join(parts)

def box_text(text: str, title: str | None = None) -> str:
    return boxed(text.splitlines(), title=title)

def prompt_center(label: str) -> str:
    w = term_width()
    inner = min(max(48, len(label) + 2), w - 10)
    left = max((w - inner) // 2, 0)
    return input((" " * left) + label.strip() + " ")

def prompt_center_hidden(label: str) -> str:
    w = term_width()
    inner = min(max(48, len(label) + 2), w - 10)
    left = max((w - inner) // 2, 0)
    return getpass.getpass((" " * left) + label.strip() + " ")

def title_box(title: str = "Fred's Car Rental") -> str:
    return boxed([""], title=title, padding=1)
