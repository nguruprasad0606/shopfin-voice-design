# ShopFin Backend

FastAPI + SQLAlchemy + SQLite. All data is stored in `shopfin.db` (created on first run).

## Run (PowerShell)

Use a 64-bit Python interpreter (for example Python 3.11 or 3.12 on Windows). The ARM64 build can fail while compiling optional `uvicorn[standard]` extras, so the project installs the base `uvicorn` package instead.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.utils.seed        # optional demo data
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  ·  Swagger: http://127.0.0.1:8000/docs

Demo login: `demo@shopfin.app` / `Demo@123` (never use in production).
Copy `.env.example` to `.env` and set a long random `SECRET_KEY` before deploying.

## Text / dictation commands

`POST /api/command/` with `{"text": "today I saved 500"}` runs the sentence and saves the result.
The frontend's bottom bar is a normal text box, so dictation tools such as Wispr Flow can type into it.

| You say | What is stored |
|---|---|
| today I saved 500 | +₹500 in **General Savings** (history row + goal balance) |
| saved 1000 for the emergency fund | +₹1000 in that goal (matched by name) |
| sold goods for 2000 by UPI | Sale, ₹2000, UPI |
| spent 3000 on inventory / paid rent 10000 | Expense with detected category and payment method |
| yesterday I paid 800 for electricity | same, dated yesterday |
| create a goal called New Freezer of 40000 | new savings goal |
| how much did I spend this month / what's my savings balance | answer, nothing stored |

Amounts understand `₹`, `Rs`, `rupees`, commas, `5k`, `2 lakh`. Every command is logged (`GET /api/command/history`).
Budget "spent" is calculated from this month's expense transactions, so it updates automatically.

## Database

All data lives in the database named by `DATABASE_URL` in `.env` (SQLite `shopfin.db` by default).
Tables: users, businesses (includes `opening_cash`), transactions, budget_categories, savings_goals,
savings_deposits, conversations, notifications. Dashboards are calculated from these tables, nothing is cached.
Tables are created on first start, and `app/database/migrate.py` adds new columns to an older `shopfin.db`
automatically. For PostgreSQL, install `psycopg[binary]` and use
`DATABASE_URL=postgresql+psycopg://user:password@localhost/shopfin`.

## Dashboard endpoints

| Endpoint | What it returns |
|---|---|
| `GET /api/dashboard/` | today's sales/expenses, available cash, total savings, today's sales update, 7-day chart |
| `GET /api/analytics/sales?days=30` | sales totals, comparisons, daily series, by method / category, recent |
| `GET /api/analytics/expenses?days=30` | same for expenses, plus monthly budget used |
| `GET /api/analytics/cash?days=30` | cash balances, money in/out with running balance, cash runway |
| `PUT /api/analytics/cash/opening` | set the opening cash (`{"amount": 20000}`) |
| `GET /api/budgets/overview` | budget totals, month-end projection, per-category status, unbudgeted spending |

Available cash = opening cash + all money in - all money out. Savings are shown separately (cash after savings).

## Tests

```powershell
python -m pytest
```
