import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Personal Expense Analysis",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Expense Analysis")
st.write("Track your spending and understand your expenses.")

if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount", "Description"]
    )

st.subheader("➕ Add a New Expense")

with st.form("expense_form"):
    expense_date = st.date_input("Date")
    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Education", "Bills", "Other"]
    )
    amount = st.number_input(
        "Amount (₹)", min_value=0.01, step=1.0
    )
    description = st.text_input("Description")
    submitted = st.form_submit_button("Add Expense")

if submitted:
    new_expense = pd.DataFrame([{
        "Date": pd.to_datetime(expense_date),
        "Category": category,
        "Amount": amount,
        "Description": description
    }])

    st.session_state.expenses = pd.concat(
        [st.session_state.expenses, new_expense],
        ignore_index=True
    )
    st.success("Expense added successfully!")

df = st.session_state.expenses.copy()

if not df.empty:
    total = df["Amount"].sum()
    average = df["Amount"].mean()
    highest = df["Amount"].max()

    st.subheader("📊 Expense Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Expenses", f"₹{total:.2f}")
    c2.metric("Average Expense", f"₹{average:.2f}")
    c3.metric("Highest Expense", f"₹{highest:.2f}")

    st.subheader("📋 All Expenses")
    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Category-wise Expenses")
    category_totals = df.groupby("Category")["Amount"].sum()
    st.bar_chart(category_totals)

    st.subheader("🥧 Expense Distribution")
    fig, ax = plt.subplots()
    category_totals.plot.pie(
        autopct="%1.1f%%", ax=ax, ylabel=""
    )
    st.pyplot(fig)
    plt.close(fig)

    if st.button("Clear All Expenses"):
        st.session_state.expenses = pd.DataFrame(
            columns=["Date", "Category", "Amount", "Description"]
        )
        st.rerun()
else:
    st.info("No expenses added yet. Enter your first expense above.")
