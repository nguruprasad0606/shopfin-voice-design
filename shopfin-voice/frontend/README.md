# ShopFin (frontend)

React, TypeScript, Vite, Tailwind, React Router, Recharts, Framer Motion.
Talks to the FastAPI backend through `/api` (Vite proxies it to http://127.0.0.1:8000).

## Run

Start the backend first (see `../backend/README.md`), then:

```
npm install
npm run dev
```

Open http://localhost:5173 and log in with `demo@shopfin.app` / `Demo@123` after seeding.

## Command bar

The text box fixed at the bottom of every page runs commands such as "today I saved 500".
The bar is focused automatically (also after you change page), so you can start dictating straight away.
With Wispr Flow: hold its hotkey, speak, release, then press Enter. Pages refresh automatically.
Spoken numbers work either way: "500" or "five hundred rupees".

Built pages: Dashboard, Transactions, Sales, Expenses, Cash Flow, Budget, Savings, Reports. Settings is still a placeholder.

## Business dashboards

- **Dashboard**: today's sales, today's expenses, available cash, total savings, a "Today's sales update" strip, 7-day chart and budget usage. Re-checks every 30 seconds.
- **Sales / Expenses**: today vs yesterday, last 7 days, this month vs last month, daily chart, split by payment method and category, recent entries. 7 / 30 / 90 day range.
- **Cash Flow**: available cash, cash in hand vs UPI/card/bank, cash after savings, money in/out with a running balance, how many days the cash will last, and an editable opening cash.
- **Budget**: total budget, spent, remaining, expected spend by month end, a safe daily spend, per-category progress with editable limits, and spending that has no budget.
