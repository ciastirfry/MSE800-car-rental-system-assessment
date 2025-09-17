# ==============================================================================
# Input validation helpers.
# Every step tells you plainly what it does.

# ==============================================================================

"""Tiny input validator helpers."""

from __future__ import annotations
from datetime import datetime, date
from carrental.utils.ui import prompt_center  # use centered prompt

def prompt_date(label: str) -> str:  # Ask for a date like "2025-09-30" (today or future only).
    while True:
        val = prompt_center(label).strip()
        try:
            d = datetime.fromisoformat(val).date()
            if d < date.today():
                print("Date cannot be in the past. Use today or a future date.")
                continue
            return val
        except Exception:
            print("Invalid date, use YYYY-MM-DD")
        except Exception:
            print("Invalid date, use YYYY-MM-DD")
