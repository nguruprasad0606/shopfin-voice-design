from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.database import Base, engine
from app.database import base  # noqa: F401
from app.database.migrate import ensure_columns

from app.routers import (
    auth,
    users,
    dashboard,
    transactions,
    budgets,
    savings,
    command,
    insights,
    analytics,
    reports,
)

Base.metadata.create_all(bind=engine)
ensure_columns()

app = FastAPI(
    title=settings.app_name,
    description="AI Financial Copilot for Small Businesses",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted({settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"}),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "SHOPFIN",
        "message": "ShopFin API is running",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(savings.router, prefix="/api/savings", tags=["Savings"])
app.include_router(command.router, prefix="/api/command", tags=["Command"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Business dashboards"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
