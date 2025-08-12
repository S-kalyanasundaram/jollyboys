import streamlit as st
from pymongo import MongoClient
import pandas as pd

# ---------------- MongoDB Connection ----------------
client = MongoClient("mongodb://localhost:27017/")  # Change if needed
db = client["mydatabase"]                           # Change DB name
collection = db["jollyboys"]                        # Change collection name

# Page settings
st.set_page_config(page_title="Jollyboys Savings Dashboard", layout="wide")

# Custom CSS for cards
st.markdown("""
    <style>
        .card {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .card h3 {
            margin-bottom: 10px;
            font-size: 16px;
            color: gray;
        }
        .card p {
            font-size: 22px;
            font-weight: bold;
            color: #1a73e8;
        }
        .dashboard-section {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Load all data from MongoDB into DataFrame
data = list(collection.find({}, {'_id': 0}))  # Exclude Mongo _id
df = pd.DataFrame(data)

# ---- Clean column names ----
df.rename(columns=lambda x: str(x).strip(), inplace=True)

# ---- Convert all numeric columns automatically ----
for col in df.columns:
    if col != "user_id" and col != "NAME" and col != "DESIGNATION":
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ---- Debug: Uncomment if you want to check column names ----
# st.write(df.columns.tolist())
# st.write(df.head())

# Login input
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
        st.markdown(
            '<div class="dashboard-section">'
            '<div class="section-title">👥 Group Dashboard</div>',
            unsafe_allow_html=True
        )

        sum_2024_credited = df["2024_Credited"].sum()
        sum_2024_balance = df["2024_balance"].sum()
        sum_2025_balance = df["2025_balance"].sum()
        sum_total_fine = df["total_FINE"].sum()
        sum_Loan_Amount = df["Loan_Amount"].sum()
        sum_PROFIT_AMOUNT = df["PROFIT_AMOUNT"].sum()
        sum_Loan_Completed = df["Loan_Completed"].sum()

        loan_amount = sum_Loan_Amount
        current_amount = (
            sum_2024_balance + sum_2025_balance + sum_total_fine +
            sum_Loan_Completed + sum_PROFIT_AMOUNT - sum_Loan_Amount
        )

        col6, col7, col8, col9, col10 = st.columns(5)
        with col6:
            st.markdown(f'<div class="card"><h3>Loan Amount</h3><p>₹{loan_amount}</p></div>', unsafe_allow_html=True)
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
