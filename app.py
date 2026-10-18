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

# Upload your expense CSV file
uploaded_file = st.file_uploader(
    "Upload your expenses.csv file",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Check required columns
    required = ["Date", "Category", "Amount"]
    if not all(col in df.columns for col in required):
        st.error("Your CSV must contain Date, Category, and Amount columns.")
    else:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Date", "Category", "Amount"])

        if df.empty:
            st.warning("No valid transactions found in the CSV.")
        else:
            total = df["Amount"].sum()
            average = df["Amount"].mean()
            highest = df["Amount"].max()
            transactions_count=len(df)

            st.subheader("📊 Expense Summary")
            c1, c2, c3 ,c4= st.columns(4)
            c1.metric("Total Expenses", f"₹{total:,.2f}")
            c2.metric("Average Expense", f"₹{average:,.2f}")
            c3.metric("Highest Expense", f"₹{highest:,.2f}")
            c4.metric("Transactions", transaction_count)


            st.subheader("🥧 Expenses by Category")
            category_totals = df.groupby("Category")["Amount"].sum()
            fig1, ax1 = plt.subplots()
            ax1.pie(
                category_totals,
                labels=category_totals.index,
                autopct="%1.1f%%"
            )
            ax1.axis("equal")
            st.pyplot(fig1)
            plt.close(fig1)

            st.subheader("📅 Monthly Expenses")
            monthly = (
                df.dropna(subset=["Date"])
                .groupby(df["Date"].dt.to_period("M"))["Amount"]
                .sum()
            )
            monthly.index = monthly.index.astype(str)
            st.bar_chart(monthly)

            st.subheader("🧾 Transaction History")
            st.dataframe(df, use_container_width=True)

else:
    st.info("Upload your expenses.csv file above to view your dashboard.")
