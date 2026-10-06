"""Turns a typed or dictated sentence ("today I saved 500") into a database change.

Tools like Wispr Flow just type the spoken words into the command bar, so this
module only has to understand clean text. It is rule-based on purpose: it is
predictable, free, works offline, and every result is explained in the reply.
"""
import re
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_SAVINGS_GOAL, EXPENSE_TYPES, INCOME_TYPES, today_ist
from app.models.business import Business
from app.models.conversation import Conversation
from app.models.savings import SavingsGoal
from app.models.transaction import Transaction
from app.services.budget_service import budget_for_category
from app.services.savings_service import (
    add_deposit,
    find_goal_by_name,
    get_or_create_default_goal,
    list_goals,
    serialize_goal,
)

EXAMPLES = (
    'Try: "today I saved 500", "sold goods for 2000 by UPI", '
    '"spent 3000 on inventory", or "how much did I spend this month".'
)

# ---------------------------------------------------------------- amounts

_UNITS = {"k": 1_000, "thousand": 1_000, "hundred": 100, "lakh": 100_000,
          "lakhs": 100_000, "lac": 100_000, "lacs": 100_000, "crore": 10_000_000}
_AMOUNT = re.compile(
    r"(?P<pre>₹|rs\.?|inr|rupees?)?\s*(?P<num>\d[\d,]*(?:\.\d+)?)\s*"
    r"(?P<unit>k|thousand|hundred|lakhs?|lacs?|crore)?(?![\w%])"
    r"(?P<post>\s*(?:₹|rs\b\.?|rupees?|inr\b))?",
    re.IGNORECASE,
)
_ORDINAL_OR_TIME = re.compile(r"^(?:(?:st|nd|rd|th)\b|\s?(?:am|pm)\b|:)", re.IGNORECASE)



# Dictation tools sometimes write numbers as words ("five hundred rupees").
_ONES = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
_TENS = {w: 10 * i for i, w in enumerate(
    "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
_SCALES = {"thousand": 1_000, "lakh": 100_000, "lakhs": 100_000, "lac": 100_000,
           "lacs": 100_000, "crore": 10_000_000}
_WORDS = set(_ONES) | set(_TENS) | set(_SCALES) | {"hundred", "and", "a"}
_NUM_RUN = re.compile(r"\b(?:(?:%s)\b[\s-]*)+" % "|".join(sorted(_WORDS - {"and", "a"}, key=len, reverse=True)
                                                       + ["and"]), re.IGNORECASE)
_CURRENCY_NEXT = re.compile(r"^\s*(?:rupees?|rs\b|inr\b|₹)", re.IGNORECASE)


def words_to_digits(text: str) -> str:
    def convert(m: re.Match) -> str:
        raw = m.group(0)
        if re.search(r"\d\s*$", text[:m.start()]):  # "1.5 lakh": the digits already carry the number
            return raw
        tokens = [t for t in re.split(r"[\s-]+", raw.lower()) if t]
        while tokens and tokens[-1] == "and":
            tokens.pop()
        while tokens and tokens[0] == "and":
            tokens.pop(0)
        if not tokens or "and" in tokens[:1]:
            return raw
        total = current = 0
        for w in tokens:
            if w in _ONES:
                current += _ONES[w]
            elif w in _TENS:
                current += _TENS[w]
            elif w == "hundred":
                current = (current or 1) * 100
            elif w in _SCALES:
                total += (current or 1) * _SCALES[w]
                current = 0
        value = total + current
        after = text[m.end():m.end() + 12]
        # "one item" must not become 1; only convert real amounts.
        if value < 10 and not _CURRENCY_NEXT.match(after):
            return raw
        trailing = " " if raw.endswith((" ", "-")) else ""
        return str(value) + trailing
    return _NUM_RUN.sub(convert, text)


def extract_amount(text: str) -> float | None:
    """First money-looking number. Prefers numbers marked with ₹/Rs/rupees."""
    text = words_to_digits(text)
    found: list[tuple[bool, float]] = []
    for m in _AMOUNT.finditer(text):
        tail = text[m.end("num"):m.end("num") + 4]
        if _ORDINAL_OR_TIME.match(tail):
            continue
        try:
            value = float(m.group("num").replace(",", ""))
        except ValueError:
            continue
        if m.group("unit"):
            value *= _UNITS[m.group("unit").lower()]
        marked = bool(m.group("pre") or m.group("post"))
        found.append((marked, value))
    if not found:
        return None
    for marked, value in found:
        if marked:
            return value
    return found[0][1]


def inr(n: float) -> str:
    """₹ with Indian digit grouping: 200000 -> ₹2,00,000."""
    whole, _, frac = ("%.2f" % abs(n)).partition(".")
    head, tail = whole[:-3], whole[-3:]
    if head:
        head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
        whole = head + "," + tail
    out = "₹" + whole + ("" if frac == "00" else "." + frac)
    return "-" + out if n < 0 else out


# ---------------------------------------------------------------- details

_METHODS = [
    ("UPI", r"\b(upi|gpay|google pay|phonepe|phone pe|paytm|bhim)\b"),
    ("Card", r"\b(card|debit|credit)\b"),
    ("Bank Transfer", r"\b(bank|neft|rtgs|imps|transfer|cheque|check)\b"),
    ("Cash", r"\bcash\b"),
]
_CATEGORIES = [
    ("Inventory", r"\b(inventory|stock|goods|supplies|rice|dal|wholesale|supplier|raw material)\b"),
    ("Rent", r"\b(rent)\b"),
    ("Electricity", r"\b(electricity|electric|current bill|power bill|eb bill)\b"),
    ("Transportation", r"\b(transport|transportation|delivery|petrol|diesel|fuel|freight|auto|travel)\b"),
    ("Marketing", r"\b(marketing|advertis\w*|ads?|promotion|pamphlet|banner)\b"),
    ("Salaries", r"\b(salary|salaries|wages?|staff|worker)\b"),
    ("Maintenance", r"\b(repair|maintenance|servicing)\b"),
]


def detect_method(lower: str) -> str:
    for name, pat in _METHODS:
        if re.search(pat, lower):
            return name
    return "Cash"


def detect_category(lower: str) -> str:
    for name, pat in _CATEGORIES:
        if re.search(pat, lower):
            return name
    return "Other"


def detect_date(lower: str) -> date:
    today = today_ist()
    if "day before yesterday" in lower:
        return today - timedelta(days=2)
    if "yesterday" in lower:
        return today - timedelta(days=1)
    return today


# ---------------------------------------------------------------- intents

_SAVE = r"\b(sav(?:e|ed|ing|ings)|set aside|put aside|kept aside|keep aside|deposit(?:ed)?)\b"
_SALE = r"\b(sold|sale|sales|sell|earned|earning|income|revenue|received|collected|got|customer|customers)\b"
_EXPENSE = r"\b(spent|spend|paid|pay|bought|buy|purchased?|expenses?|bill|cost)\b"
_QUERY = r"\b(how much|what is|what's|whats|show|total|balance|summary|how many)\b"
_NEW_GOAL = r"\b(create|new|start|add|make|set up|open)\b.*\bgoal\b"


def _earliest(lower: str) -> str | None:
    """Whichever verb comes first wins: 'saved 500 from sales' is a saving."""
    hits = []
    for intent, pat in (("SAVE", _SAVE), ("SALE", _SALE), ("EXPENSE", _EXPENSE)):
        m = re.search(pat, lower)
        if m:
            hits.append((m.start(), intent))
    return min(hits)[1] if hits else None


def _period(lower: str) -> tuple[str, date, date]:
    today = today_ist()
    if "yesterday" in lower:
        d = today - timedelta(days=1)
        return "yesterday", d, d
    if "week" in lower:
        return "in the last 7 days", today - timedelta(days=6), today
    if "today" in lower:
        return "today", today, today
    return "this month", today.replace(day=1), today


def _clean_description(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip().rstrip(".!?")
    return (text[:1].upper() + text[1:])[:255]


def _match_goal(db: Session, business_id: int, lower: str) -> SavingsGoal | None:
    goals = list_goals(db, business_id)
    for g in goals:
        if g.name.strip().lower() in lower:
            return g
    generic = {"fund", "savings", "goal", "the", "my", "for", "new"}
    words = set(re.findall(r"[a-z]+", lower))
    scored = []
    for g in goals:
        tokens = {t for t in re.findall(r"[a-z]+", g.name.lower()) if len(t) > 2 and t not in generic}
        score = len(tokens & words)
        if score:
            scored.append((score, g))
    scored.sort(key=lambda x: -x[0])
    if scored and (len(scored) == 1 or scored[0][0] > scored[1][0]):
        return scored[0][1]
    return None


# ---------------------------------------------------------------- handlers

def _result(ok: bool, intent: str, message: str, data=None, warning=None) -> dict:
    return {"ok": ok, "intent": intent, "message": message, "data": data, "warning": warning}


def _handle_save(db, business, text, lower, amount):
    if amount is None:
        return _result(False, "ADD_SAVINGS", 'How much did you save? Try "I saved 500".')
    goal = _match_goal(db, business.id, lower) or get_or_create_default_goal(db, business.id)
    when = detect_date(lower)
    add_deposit(db, goal, amount, when, _clean_description(text))
    db.commit()
    db.refresh(goal)
    data = {"kind": "savings", "goal": serialize_goal(goal), "amount": amount}
    msg = f"Saved {inr(amount)} to {goal.name}. Total there: {inr(float(goal.current_amount))}."
    if goal.name == DEFAULT_SAVINGS_GOAL:
        msg += ' Say "to Emergency Fund" to pick a specific goal.' if len(list_goals(db, business.id)) > 1 else ""
    return _result(True, "ADD_SAVINGS", msg, data)


def _handle_transaction(db, business, text, lower, amount, income: bool):
    intent = "ADD_SALE" if income else "ADD_EXPENSE"
    if amount is None:
        what = "sale" if income else "expense"
        return _result(False, intent, f'What was the {what} amount? Try "{what} of 500".')
    category = "Sales" if income else detect_category(lower)
    tx = Transaction(
        business_id=business.id,
        transaction_type="Sale" if income else "Expense",
        category=category,
        description=_clean_description(text),
        payment_method=detect_method(lower),
        amount=amount,
        transaction_date=detect_date(lower),
        status="Completed",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    data = {"kind": "transaction", "id": tx.id, "type": tx.transaction_type, "category": category,
            "method": tx.payment_method, "amount": amount, "date": tx.transaction_date.isoformat()}
    if income:
        msg = f"Recorded a sale of {inr(amount)} via {tx.payment_method}."
        return _result(True, intent, msg, data)
    article = "an" if category[0] in "AEIOU" else "a"
    msg = f"Recorded {article} {category.lower()} expense of {inr(amount)} via {tx.payment_method}."
    warning = None
    b = budget_for_category(db, business.id, category)
    if b and b["status"] == "Exceeded":
        warning = f"{b['name']} budget exceeded: {inr(b['spent'])} of {inr(b['limit'])}."
    elif b and b["status"] == "Warning":
        warning = f"{b['name']} budget is {b['percentage']:.0f}% used."
    return _result(True, intent, msg, data, warning)


def _handle_new_goal(db, business, text, lower, amount):
    m = re.search(r"\bgoal\b\s*(?:called|named|for|to buy|to get)?\s*(.*)", text, re.IGNORECASE)
    raw = m.group(1) if m else ""
    raw = re.split(r"\b(?:of|with|target|worth|by|for)\b|[₹\d]|\brs\b", raw, maxsplit=1, flags=re.IGNORECASE)[0]
    name = re.sub(r"[^\w\s&-]", "", raw).strip().title() or "New Goal"
    if amount is None:
        return _result(False, "CREATE_GOAL", f'What target amount for "{name}"? Try "create goal {name} of 50000".')
    if find_goal_by_name(db, business.id, name):
        return _result(False, "CREATE_GOAL", f'You already have a goal called "{name}".')
    goal = SavingsGoal(business_id=business.id, name=name, target_amount=amount, current_amount=0, monthly_contribution=0)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _result(True, "CREATE_GOAL", f'Created savings goal "{name}" with a target of {inr(amount)}.',
                   {"kind": "savings", "goal": serialize_goal(goal)})


def _handle_query(db, business, lower):
    label, start, end = _period(lower)

    def total(types):
        return float(db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.business_id == business.id,
            Transaction.transaction_type.in_(types),
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end).scalar() or 0)

    if re.search(r"\bsav", lower):
        goals = list_goals(db, business.id)
        total_saved = sum(float(g.current_amount) for g in goals)
        return _result(True, "QUERY_SAVINGS", f"You have saved {inr(total_saved)} across {len(goals)} goal(s).")
    if re.search(r"\b(spend|spent|expense|expenses)\b", lower):
        return _result(True, "QUERY_EXPENSES", f"You spent {inr(total(EXPENSE_TYPES))} {label}.")
    if re.search(_SALE, lower):
        return _result(True, "QUERY_SALES", f"Your sales are {inr(total(INCOME_TYPES))} {label}.")
    s, e = total(INCOME_TYPES), total(EXPENSE_TYPES)
    return _result(True, "QUERY_SUMMARY", f"{label.capitalize()}: sales {inr(s)}, expenses {inr(e)}, surplus {inr(s - e)}.")


# ---------------------------------------------------------------- entry point

def run_command(db: Session, business: Business, text: str) -> dict:
    text = " ".join(text.split())
    lower = text.lower()
    amount = extract_amount(text)

    try:
        if re.search(_NEW_GOAL, lower):
            result = _handle_new_goal(db, business, text, lower, amount)
        elif re.search(_QUERY, lower) and not (amount and _earliest(lower)):
            result = _handle_query(db, business, lower)
        else:
            intent = _earliest(lower)
            if intent == "SAVE":
                result = _handle_save(db, business, text, lower, amount)
            elif intent == "SALE":
                result = _handle_transaction(db, business, text, lower, amount, income=True)
            elif intent == "EXPENSE":
                result = _handle_transaction(db, business, text, lower, amount, income=False)
            else:
                result = _result(False, "UNKNOWN", "I couldn't understand that. " + EXAMPLES)
    except Exception:
        db.rollback()
        raise

    db.add(Conversation(
        business_id=business.id,
        user_message=text,
        assistant_response=result["message"],
        intent=result["intent"],
        success=result["ok"],
    ))
    db.commit()
    return result
