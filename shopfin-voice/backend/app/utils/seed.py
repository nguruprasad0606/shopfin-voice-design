from datetime import timedelta

from app.core.constants import today_ist
from app.core.security import hash_password
from app.database.database import Base, SessionLocal, engine
from app.database import base  # noqa: F401  (registers every model)
from app.models.budget import BudgetCategory
from app.models.business import Business
from app.models.savings import SavingsGoal
from app.models.transaction import Transaction
from app.models.user import User
from app.services.savings_service import add_deposit

DEMO_EMAIL = "demo@shopfin.app"
DEMO_PASSWORD = "Demo@123"


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == DEMO_EMAIL).first():
            print("Demo data already exists.")
            return

        user = User(name="Guru", email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD))
        db.add(user)
        db.flush()
        business = Business(user_id=user.id, name="Sri Lakshmi General Store",
                            owner_name="Guru", business_type="Retail Shop", currency="INR",
                            opening_cash=20000)
        db.add(business)
        db.flush()

        today = today_ist()
        month_start = today.replace(day=1)

        def ago(days):  # keep seeded expenses inside the current month so budgets show usage
            return max(today - timedelta(days=days), month_start)

        rows = [
            ("Sale", "Sales", "Daily shop sale", "UPI", 8500, today),
            ("Sale", "Sales", "Counter sale", "Cash", 6200, today - timedelta(days=1)),
            ("Sale", "Sales", "Festival rush", "Cash", 12400, today - timedelta(days=2)),
            ("Sale", "Sales", "Counter sale", "Card", 5800, today - timedelta(days=3)),
            ("Sale", "Sales", "Wholesale orders", "Bank Transfer", 45000, today - timedelta(days=4)),
            ("Expense", "Inventory", "Stock purchase", "UPI", 3000, today),
            ("Expense", "Inventory", "Rice and dal stock", "Bank Transfer", 21000, ago(2)),
            ("Expense", "Electricity", "Electricity bill", "Bank Transfer", 800, ago(1)),
            ("Expense", "Rent", "Monthly shop rent", "Bank Transfer", 10000, ago(3)),
            ("Expense", "Transportation", "Delivery transport", "Cash", 1500, ago(2)),
        ]
        for typ, cat, desc, method, amount, dt in rows:
            db.add(Transaction(business_id=business.id, transaction_type=typ, category=cat,
                               description=desc, payment_method=method, amount=amount,
                               transaction_date=dt))

        for name, limit in [("Inventory", 30000), ("Rent", 10000), ("Electricity", 5000),
                            ("Transportation", 3000), ("Marketing", 2000)]:
            db.add(BudgetCategory(business_id=business.id, name=name, limit=limit))

        emergency = SavingsGoal(business_id=business.id, name="Emergency Fund",
                                target_amount=50000, current_amount=0, monthly_contribution=5000)
        equipment = SavingsGoal(business_id=business.id, name="New Equipment",
                                target_amount=80000, current_amount=0, monthly_contribution=5000)
        db.add_all([emergency, equipment])
        db.flush()
        add_deposit(db, emergency, 30000, today - timedelta(days=20), "Opening balance")
        add_deposit(db, equipment, 20000, today - timedelta(days=20), "Opening balance")

        db.commit()
        print("Demo data created.")
        print(f"Email: {DEMO_EMAIL}\nPassword: {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
