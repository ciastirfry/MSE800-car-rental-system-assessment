# ==============================================================================
# Pricing and payment strategies.
# Every step tells you plainly what it does.

# ==============================================================================

"""Pricing and payment strategies (Strategy pattern)."""  # Strategies let us swap logic without changing other code.

from __future__ import annotations  # Modern type hints.
from typing import Protocol, Dict  # Protocol defines an interface.
from datetime import datetime, timedelta  # For date math.

class PricingStrategy(Protocol):  # All pricing strategies must have the same method.
    def quote(self, daily_rate: float, start: str, end: str) -> tuple[float, Dict[str, float]]: ...  # Returns (total, details).

class WeekendMultiplierStrategy:  # A concrete pricing strategy.
    """Applies a higher multiplier on Saturday and Sunday."""  # Human description.
    def __init__(self, weekend_multiplier: float = 1.2) -> None:  # Set up with a default multiplier.
        self.weekend_multiplier = weekend_multiplier  # Save the multiplier.
    def quote(self, daily_rate: float, start: str, end: str) -> tuple[float, Dict[str, float]]:  # Work out the total price.
        s = datetime.fromisoformat(start)  # Turn start text into a real date.
        e = datetime.fromisoformat(end)  # Turn end text into a real date.
        if e < s:  # If the end is before the start...
            raise ValueError("End date must be on or after start date")  # ..we shout loudly because that cannot happen.
        days = (e - s).days + 1  # Count how many days are included (inclusive of both ends).
        total = 0.0  # Begin at zero dollars.
        weekend_days = 0  # Count weekends for the receipt.
        weekday_days = 0  # Count weekdays for the receipt.
        cur = s  # Start walking day by day from the start.
        for _ in range(days):  # Repeat once per day.
            if cur.weekday() >= 5:  # 5 = Saturday, 6 = Sunday.
                total += daily_rate * self.weekend_multiplier  # Weekend days cost more.
                weekend_days += 1  # Remember we saw a weekend day.
            else:  # Monday..Friday
                total += daily_rate  # Normal price on weekdays.
                weekday_days += 1  # Remember we saw a weekday.
            cur += timedelta(days=1)  # Move forward one day.
        details = {  # Build a friendly receipt/dictionary about the price.
            "weekday_days": float(weekday_days),  # Number of weekdays charged.
            "weekend_days": float(weekend_days),  # Number of weekend days charged.
            "daily_rate": float(daily_rate),  # The base daily price.
            "weekend_multiplier": float(self.weekend_multiplier),  # The extra weekend factor.
        }  # Done building the receipt.
        return round(total, 2), details  # Return total rounded to cents and the details.

class PaymentStrategy(Protocol):  # Payment interface.
    def pay(self, amount: float) -> bool: ...  # All payments try to pay and return True/False.

class CashPayment:  # Paying with cash (a pretend one for the console app).
    """Always succeeds (for our CLI demo)."""  # Human description.
    def pay(self, amount: float) -> bool:  # Try to pay the amount.
        return True  # In the demo we pretend it always works.

class CardPayment:  # Paying with a card (pretend).
    """Always succeeds (for our CLI demo)."""  # Human description.
    def pay(self, amount: float) -> bool:  # Try to pay the amount.
        return True  # In the demo we pretend it always works.
