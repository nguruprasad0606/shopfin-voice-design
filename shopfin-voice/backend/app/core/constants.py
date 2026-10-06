from datetime import date, datetime, timedelta, timezone

# Money coming in / going out. Every report, dashboard and budget calculation
# uses these two sets so the rules live in exactly one place.
INCOME_TYPES = ("Sale", "Customer Payment", "Other Income")
EXPENSE_TYPES = ("Expense", "Purchase", "Supplier Payment")
ALL_TYPES = INCOME_TYPES + EXPENSE_TYPES

PAYMENT_METHODS = ("Cash", "UPI", "Card", "Bank Transfer")
STATUSES = ("Completed", "Pending")

DEFAULT_SAVINGS_GOAL = "General Savings"

IST = timezone(timedelta(hours=5, minutes=30))


def today_ist() -> date:
    """Shop owners think in Indian time, not server time."""
    return datetime.now(IST).date()
