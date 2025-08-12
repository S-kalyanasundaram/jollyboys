import streamlit as st
from pymongo import MongoClient
import pandas as pd
import math
from bson import ObjectId
import os
mongo_uri = os.getenv("MONGO_URI")
admin_key = os.getenv("ADMIN_KEY")

# ---------------- MongoDB Connection ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]  # DB name
collection = db["jollyboys"]  # Collection name

# ---------------- Page Settings ----------------
st.set_page_config(page_title="Jollyboys Savings Dashboard", layout="wide")

# ---------------- Custom CSS ----------------
st.markdown("""
    <style>
        .card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .card h3 { margin-bottom: 10px; font-size: 16px; color: gray; }
        .card p { font-size: 22px; font-weight: bold; color: #1a73e8; }
        .dashboard-section {
            background-color: white; padding: 20px;
            border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section-title { font-size: 18px; font-weight: bold; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# ---------------- Load Data ----------------
data = list(collection.find({}, {'_id': 0}))
df = pd.DataFrame(data)
df.rename(columns=lambda x: str(x).strip(), inplace=True)

for col in df.columns:
    if col not in ["user_id", "NAME", "DESIGNATION"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ---------------- User Section ----------------
st.markdown("## 💰 Jollyboys Savings Dashboard")
user_id = st.text_input("Enter your User ID:")

if user_id:
    if user_id in df["user_id"].values:
        user_data = df[df["user_id"] == user_id].iloc[0]

        # --- User Dashboard ---
        st.markdown(
            f'<div class="dashboard-section">'
            f'<div class="section-title">🔑 User Dashboard - {user_data["NAME"]} ({user_data["DESIGNATION"]})</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="card"><h3>2024 Credited</h3><p>₹{user_data["2024_Credited"]}</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="card"><h3>Fine Amount</h3><p>₹{user_data["total_FINE"]}</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="card"><h3>2024 Balance</h3><p>₹{user_data["2024_balance"]}</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="card"><h3>2025 Balance</h3><p>₹{user_data["2025_balance"]}</p></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="card"><h3>Total</h3><p>₹{user_data["Total"]}</p></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # --- Group Dashboard ---
        st.markdown('<div class="dashboard-section"><div class="section-title">👥 Group Dashboard</div>', unsafe_allow_html=True)
        sum_2024_balance = df["2024_balance"].sum()
        sum_2025_balance = df["2025_balance"].sum()
        sum_total_fine = df["total_FINE"].sum()
        sum_Loan_Amount = df["Loan_Amount"].sum()
        sum_PROFIT_AMOUNT = df["PROFIT_AMOUNT"].sum()
        sum_Loan_Completed = df["Loan_Completed"].sum()

        current_amount = sum_2024_balance + sum_2025_balance + sum_total_fine + sum_Loan_Completed + sum_PROFIT_AMOUNT - sum_Loan_Amount

        col6, col7, col8, col9, col10 = st.columns(5)
        with col6:
            st.markdown(f'<div class="card"><h3>Loan Amount</h3><p>₹{sum_Loan_Amount}</p></div>', unsafe_allow_html=True)
        with col7:
            st.markdown(f'<div class="card"><h3>Sum of 2024 Balance</h3><p>₹{sum_2024_balance}</p></div>', unsafe_allow_html=True)
        with col8:
            st.markdown(f'<div class="card"><h3>Sum of 2025 Balance</h3><p>₹{sum_2025_balance}</p></div>', unsafe_allow_html=True)
        with col9:
            st.markdown(f'<div class="card"><h3>Sum of Total Fine</h3><p>₹{sum_total_fine}</p></div>', unsafe_allow_html=True)
        with col10:
            st.markdown(f'<div class="card"><h3>Current Amount</h3><p>₹{current_amount}</p></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ User ID not found. Please check and try again.")

# ---------------- Admin Login / Logout ----------------
st.markdown("---")
if not st.session_state.is_admin:
    if st.button("🔑 Admin Login"):
        st.session_state.show_login = True
        st.rerun()

if st.session_state.show_login and not st.session_state.is_admin:
    secret_key = st.text_input("Enter Admin Secret Key:", type="password")
    if st.button("Submit Key"):
        if secret_key == "mysecret123":  # Change your secret here
            st.session_state.is_admin = True
            st.session_state.show_login = False
            st.rerun()
        else:
            st.error("❌ Wrong secret key.")

# ---------------- Admin Panel ----------------
if st.session_state.is_admin:
    st.success("✅ Admin Access Granted")
    if st.button("🚪 Logout"):
        st.session_state.is_admin = False
        st.rerun()

    st.markdown("### 💼 Admin Payment & Loan Manager (Monthly Update)")

    users = list(collection.find({}, {"user_id": 1, "NAME": 1}))
    user_options = {u["NAME"]: u["user_id"] for u in users}
    selected_user = st.selectbox("Select User", list(user_options.keys()))

    if selected_user:
        user_id = user_options[selected_user]
        user_data = collection.find_one({"user_id": user_id})

        months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY ", "JUNE",
                  "JULY", "AUGUEST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
        selected_month = st.selectbox("Select Month to Update", months)

        month_payment = st.number_input(
            f"Enter Payment for {selected_month} (2025)",
            value=float(user_data.get(selected_month, 0) or 0),
            min_value=0.0
        )

        loan_amount = float(user_data.get("Loan_Amount") or 0)
        interest_amount = 0
        period_month = 0
        loan_completed = ""

        if loan_amount > 0:
            st.write("This user has taken a loan.")
            interest_amount = loan_amount / 100
            st.number_input("Interest Amount (per month)", value=interest_amount, format="%.2f", disabled=True)
            period_month = st.number_input("Period (Months)", value=float(user_data.get("PERIOD_MONTH") or 0), min_value=0.0)
            loan_completed = st.text_input("Loan Completed", value=str(user_data.get("Loan_Completed") or ""))
        else:
            st.write("No loan for this user.")

        fine_2025 = st.number_input("2025 Fine", value=float(user_data.get("2025_FINE") or 0), min_value=0.0)

        if st.button("💾 Update User Data"):
            all_months = [m for m in months]
            balance_2025 = sum(
                month_payment if m == selected_month else (user_data.get(m) or 0)
                for m in all_months
            )

            profit_amount = interest_amount * period_month if period_month else 0
            total_fine = (user_data.get("2024_FINE") or 0) + fine_2025
            total_balance = (user_data.get("2024_balance") or 0) + balance_2025

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

            collection.update_one({"user_id": user_id}, {"$set": update_data})
            st.success(f"✅ {selected_month} payment updated successfully!")

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
