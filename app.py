import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="RoseGold | Expense Analysis",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DATABASE
# ==========================================

DB_PATH = Path(__file__).parent / "expenses.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT
            )
        """)

def load_expenses():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC",
            conn
        )

initialize_database()

# ==========================================
# ROSE GOLD + BLACK CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #111014;
    color: #F8F1F3;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #1C181D;
    border-right: 1px solid #684451;
}

h1, h2, h3 {
    color: #E8B4C0 !important;
}

.main-heading {
    font-size: 34px;
    font-weight: 800;
    color: #E8B4C0;
}

.sub-heading {
    color: #BFAAB1;
    margin-bottom: 25px;
}

.metric-card {
    background: linear-gradient(145deg, #292129, #1B171D);
    border: 1px solid #966675;
    border-radius: 16px;
    padding: 22px;
    min-height: 115px;
    margin-bottom: 12px;
}

.metric-label {
    color: #D5A5B1;
    font-size: 14px;
    font-weight: 600;
}

.metric-value {
    color: #F2C5CF;
    font-size: 25px;
    font-weight: 800;
    margin-top: 12px;
}

.stButton button,
.stFormSubmitButton button {
    background-color: #B77A8B;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 600;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #D49BAA;
    color: #171217;
}

input, textarea {
    background-color: #29232B !important;
    color: white !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #684451;
    border-radius: 10px;
}

.footer {
    color: #A98D96;
    text-align: center;
    padding: 25px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.markdown(
    "<h1 style='color:#E8B4C0;'>🌸 RoseGold</h1>",
    unsafe_allow_html=True
)

st.sidebar.caption("PERSONAL FINANCE DASHBOARD")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Expense", "Transactions", "Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Your expenses are saved in your local database.")

# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-heading">Personal Expense Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-heading">Manage your money with elegance and clarity.</div>',
    unsafe_allow_html=True
)

# Load the latest data
df = load_expenses()

# ==========================================
# ADD EXPENSE PAGE
# ==========================================

if page == "Add Expense":

    st.markdown("## 🌸 Add a New Expense")
    st.write("Enter your expense details below.")

    with st.form("add_expense_form", clear_on_submit=True):

        expense_date = st.date_input(
            "Expense Date",
            value=date.today()
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Education",
                "Health",
                "Entertainment",
                "Other"
            ]
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            value=100.0,
            step=10.0
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Lunch, bus ticket, books..."
        )

        submitted = st.form_submit_button(
            "➕ Save Expense",
            use_container_width=True
        )

        if submitted:
            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO expenses
                    (expense_date, category, amount, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        expense_date.isoformat(),
                        category,
                        amount,
                        description.strip()
                    )
                )

            st.success("Expense saved successfully! 🌸")
            st.rerun()

# ==========================================
# TRANSACTIONS PAGE
# ==========================================

elif page == "Transactions":

    st.markdown("## 🧾 Transaction History")

    if df.empty:
        st.info("No expenses recorded yet. Go to Add Expense to enter your first transaction.")

    else:
        search = st.text_input(
            "Search transactions",
            placeholder="Search category or description..."
        )

        history = df.copy()

        if search:
            matches = (
                history["category"].str.contains(search, case=False, na=False)
                | history["description"].fillna("").str.contains(
                    search, case=False, na=False
                )
            )
            history = history[matches]

        display_df = history.rename(columns={
            "expense_date": "Date",
            "category": "Category",
            "amount": "Amount (₹)",
            "description": "Description",
            "id": "ID"
        })

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### ✏️ Edit or Delete an Expense")

        transaction_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select transaction",
            transaction_ids,
            format_func=lambda x: (
                f"#{x} — "
                f"{df.loc[df['id'] == x, 'category'].iloc[0]} — "
                f"₹{df.loc[df['id'] == x, 'amount'].iloc[0]:,.2f}"
            )
        )

        selected_row = df[df["id"] == selected_id].iloc[0]

        with st.form("edit_expense_form"):

            edit_date = st.date_input(
                "Date",
                value=pd.to_datetime(
                    selected_row["expense_date"]
                ).date()
            )

            categories = [
                "Food", "Travel", "Shopping", "Bills",
                "Education", "Health", "Entertainment", "Other"
            ]

            current_category = selected_row["category"]

            if current_category not in categories:
                categories.append(current_category)

            edit_category = st.selectbox(
                "Category",
                categories,
                index=categories.index(current_category)
            )

            edit_amount = st.number_input(
                "Amount (₹)",
                min_value=0.01,
                value=max(float(selected_row["amount"]), 0.01),
                step=10.0
            )

            edit_description = st.text_input(
                "Description",
                value=selected_row["description"] or ""
            )

            update_button = st.form_submit_button(
                "💾 Update Expense",
                use_container_width=True
            )

            if update_button:
                with get_connection() as conn:
                    conn.execute(
                        """
                        UPDATE expenses
                        SET expense_date = ?,
                            category = ?,
                            amount = ?,
                            description = ?
                        WHERE id = ?
                        """,
                        (
                            edit_date.isoformat(),
                            edit_category,
                            edit_amount,
                            edit_description.strip(),
                            int(selected_id)
                        )
                    )

                st.success("Expense updated successfully!")
                st.rerun()

        if st.button("🗑️ Delete Selected Expense"):
            with get_connection() as conn:
                conn.execute(
                    "DELETE FROM expenses WHERE id = ?",
                    (int(selected_id),)
                )

            st.success("Expense deleted successfully.")
            st.rerun()

# ==========================================
# DASHBOARD PAGE
# ==========================================

elif page == "Dashboard":

    st.markdown("## ✨ Financial Overview")

    if df.empty:
        st.info("No expenses yet. Select Add Expense to get started.")

        if st.button("➕ Add Your First Expense"):
            st.session_state["open_add_expense"] = True
            st.rerun()

    else:
        total = df["amount"].sum()
        average = df["amount"].mean()
        highest = df["amount"].max()
        transaction_count = len(df)

        c1, c2, c3, c4 = st.columns(4)

        cards = [
            (c1, "TOTAL EXPENSES", f"₹{total:,.2f}"),
            (c2, "AVERAGE EXPENSE", f"₹{average:,.2f}"),
            (c3, "HIGHEST EXPENSE", f"₹{highest:,.2f}"),
            (c4, "TRANSACTIONS", str(transaction_count))
        ]

        for col, label, value in cards:
            with col:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("## 📊 Spending Overview")

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown("### Category Breakdown")

            category_totals = df.groupby("category")["amount"].sum()

            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor("#1D191F")
            ax.set_facecolor("#1D191F")

            ax.pie(
                category_totals,
                labels=category_totals.index,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"color": "#F8E9ED"},
                colors=[
                    "#D49BAA", "#B77A8B", "#966675",
                    "#E8B4C0", "#704957", "#E6C4CD",
                    "#C58A9A", "#8A5969"
                ]
            )

            ax.axis("equal")
            st.pyplot(fig)
            plt.close(fig)

        with chart2:
            st.markdown("### Monthly Expenses")

            monthly = df.copy()
            monthly["Month"] = pd.to_datetime(
                monthly["expense_date"]
            ).dt.to_period("M").astype(str)

            monthly_totals = monthly.groupby("Month")["amount"].sum()

            st.bar_chart(
                monthly_totals,
                color="#D49BAA"
            )

        st.markdown("## 🕒 Recent Transactions")

        recent = df.head(5).rename(columns={
            "expense_date": "Date",
            "category": "Category",
            "amount": "Amount (₹)",
            "description": "Description",
            "id": "ID"
        })

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# ANALYTICS PAGE
# ==========================================

elif page == "Analytics":

    st.markdown("## 📈 Expense Analytics")

    if df.empty:
        st.info("No data available. Add expenses to see your analytics.")

    else:
        category_totals = (
            df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.markdown("### Category-wise Spending")

        st.bar_chart(
            category_totals,
            color="#D49BAA"
        )

        st.markdown("### Monthly Spending")

        monthly = df.copy()
        monthly["Month"] = pd.to_datetime(
            monthly["expense_date"]
        ).dt.to_period("M").astype(str)

        monthly_totals = monthly.groupby("Month")["amount"].sum()

        st.line_chart(
            monthly_totals,
            color="#D49BAA"
        )

# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="footer">
        🌸 RoseGold | Personal Expense Analysis
        <br>
        Manage your expenses with elegance.
    </div>
    """,
    unsafe_allow_html=True
)