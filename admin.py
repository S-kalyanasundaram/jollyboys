import streamlit as st
from pymongo import MongoClient
import pandas as pd
import math
from bson import ObjectId

# ---------------- MongoDB Connection ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # <-- replace
collection = db["jollyboys"]  # <-- replace

st.title("💼 Admin Payment & Loan Manager (Monthly Update)")

# ---------------- Fetch All Users ----------------
users = list(collection.find({}, {"user_id": 1, "NAME": 1}))
if not users:
    st.warning("No users found in the database. Check DB/collection names.")
    st.stop()

user_options = {u["NAME"]: u["user_id"] for u in users if "NAME" in u and "user_id" in u}
selected_user = st.selectbox("Select User", list(user_options.keys()))

if selected_user:
    user_id = user_options[selected_user]
    user_data = collection.find_one({"user_id": user_id})

    st.subheader(f"Editing: {selected_user}")

    # ---------------- Select Month ----------------
    months = [
        "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY ", "JUNE",
        "JULY", "AUGUEST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
    ]
    selected_month = st.selectbox("Select Month to Update", months)

    month_payment = st.number_input(
        f"Enter Payment for {selected_month} (2025)",
        value=float(user_data.get(selected_month, 0) or 0),
        min_value=0.0
    )

    # ---------------- Loan Details ----------------
    # Define defaults to avoid NameError
    interest_amount = 0
    period_month = 0
    loan_completed = ""

    loan_amount = float(user_data.get("Loan_Amount") or 0)

    if loan_amount > 0:
        st.write("This user has taken a loan.")
        
        interest_amount = loan_amount / 100
        st.number_input(
            "Interest Amount (per month)",
            value=interest_amount,
            format="%.2f",
            disabled=True
        )
        period_month = st.number_input(
            "Period (Months)", value=float(user_data.get("PERIOD_MONTH") or 0), min_value=0.0
        )
        loan_completed = st.text_input(
            "Loan Completed", value=str(user_data.get("Loan_Completed") or "")
        )
    else:
        st.write("No loan for this user.")

    # ---------------- Fine ----------------
    st.write("### Fine")
    fine_2025 = st.number_input(
        "2025 Fine", value=float(user_data.get("2025_FINE") or 0), min_value=0.0
    )

    # ---------------- Update Button ----------------
    if st.button("💾 Update User Data"):
        # Calculate balance for 2025 with updated month
        all_months = [m for m in months]
        balance_2025 = sum(
            month_payment if m == selected_month else (user_data.get(m) or 0)
            for m in all_months
        )

        profit_amount = interest_amount * period_month if period_month else 0
        total_fine = (user_data.get("2024_FINE") or 0) + fine_2025
        total_balance = (user_data.get("2024_balance") or 0) + balance_2025

        # Prepare update dictionary
        update_data = {
            selected_month: month_payment,
            "Loan_Amount": loan_amount,
            "PERIOD_MONTH": period_month,
            "Loan_Completed": loan_completed,
            "2025_FINE": fine_2025,
            "INTEREST_AMOUNT": interest_amount,
            "2025_balance": balance_2025,
            "PROFIT_AMOUNT": profit_amount,
            "total_FINE": total_fine,
            "Total": total_balance
        }

        # Update in MongoDB
        collection.update_one({"user_id": user_id}, {"$set": update_data})
        st.success(f"✅ {selected_month} payment updated successfully!")

    # ---------------- Show Updated Data ----------------
    updated_user = collection.find_one({"user_id": user_id}, {"_id": 0})

    clean_user = {}
    for k, v in updated_user.items():
        if isinstance(v, ObjectId):
            clean_user[k] = str(v)
        elif v is None or (isinstance(v, float) and math.isnan(v)):
            clean_user[k] = 0
        else:
            clean_user[k] = v

    st.json(clean_user)
