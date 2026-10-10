import os
import json
import sqlite3
import hashlib
import hmac
import secrets
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_FILE = "users.db"
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate",
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AUTHENTICATION DATABASE
# ============================================================

def init_auth_database():
    """Create the users table if it does not exist."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def hash_password(password, salt=None):
    """Hash a password rather than storing it as plain text."""
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000,
    ).hex()

    return salt, password_hash


def register_user(name, email, password):
    """Create a new account."""
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "Please complete all fields."

    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    salt, password_hash = hash_password(password)

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                """
                INSERT INTO users
                    (name, email, salt, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    salt,
                    password_hash,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
        return True, "Account created! You can now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def authenticate_user(email, password):
    """Check the email and password."""
    email = email.strip().lower()

    with sqlite3.connect(DB_FILE) as conn:
        user = conn.execute(
            """
            SELECT id, name, email, salt, password_hash
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if not user:
        return None

    user_id, name, saved_email, salt, saved_hash = user
    _, entered_hash = hash_password(password, salt)

    if hmac.compare_digest(entered_hash, saved_hash):
        return {
            "id": user_id,
            "name": name,
            "email": saved_email,
        }

    return None


def logout():
    """End the current login session."""
    st.session_state.logged_in = False
    st.session_state.pop("user", None)
    # The radio key must be changed before its widget is created.
    st.session_state.auth_mode = "Login"
    st.rerun()


def show_auth_page():
    """Display Sign Up and Login screens."""
    st.markdown(
        "<h1 style='text-align:center;'>📊 Financial Report Generator</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;'>"
        "Analyze company performance, financial risks, and trends."
        "</p>",
        unsafe_allow_html=True,
    )

    st.write("")
    _, center, _ = st.columns([1, 1.4, 1])

    with center:
        # Set the radio's state BEFORE creating the widget.
        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "Login"

        if st.session_state.pop("switch_to_login", False):
            st.session_state.auth_mode = "Login"

        mode = st.radio(
            "Welcome",
            ["Login", "Sign Up"],
            horizontal=True,
            key="auth_mode",
        )

        if mode == "Sign Up":
            with st.form("signup_form"):
                name = st.text_input("Full name")
                email = st.text_input("Email address")
                password = st.text_input(
                    "Password",
                    type="password",
                    help="Use at least 8 characters.",
                )
                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                )
                submitted = st.form_submit_button(
                    "Create Account",
                    use_container_width=True,
                )

            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(name, email, password)
                    if success:
                        st.success(message)
                        # Change radio state on the next run, before st.radio.
                        st.session_state.switch_to_login = True
                        st.rerun()
                    else:
                        st.error(message)

        else:
            with st.form("login_form"):
                email = st.text_input("Email address")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button(
                    "Login",
                    use_container_width=True,
                )

            if submitted:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        st.caption(
            "Demo authentication. Use a unique password and do not "
            "reuse your personal account password."
        )


# ============================================================
# FINANCIAL DATA
# ============================================================

FINANCIAL_COLUMNS = [
    "Company",
    "Sector",
    "Revenue",
    "Expenses",
    "Total Assets",
    "Total Debt",
    "Current Assets",
    "Current Liabilities",
]


def get_sample_data():
    """Provide sample data for trying the app."""
    return pd.DataFrame(
        [
            {
                "Company": "Alpha Technologies",
                "Sector": "Technology",
                "Revenue": 12_500_000,
                "Expenses": 8_750_000,
                "Total Assets": 18_000_000,
                "Total Debt": 4_500_000,
                "Current Assets": 6_200_000,
                "Current Liabilities": 3_100_000,
            },
            {
                "Company": "Bright Retail",
                "Sector": "Retail",
                "Revenue": 9_800_000,
                "Expenses": 8_500_000,
                "Total Assets": 12_000_000,
                "Total Debt": 6_500_000,
                "Current Assets": 2_800_000,
                "Current Liabilities": 3_500_000,
            },
            {
                "Company": "Green Energy",
                "Sector": "Energy",
                "Revenue": 15_800_000,
                "Expenses": 11_000_000,
                "Total Assets": 25_000_000,
                "Total Debt": 7_000_000,
                "Current Assets": 8_000_000,
                "Current Liabilities": 4_000_000,
            },
            {
                "Company": "Care Medical",
                "Sector": "Healthcare",
                "Revenue": 11_200_000,
                "Expenses": 9_300_000,
                "Total Assets": 14_500_000,
                "Total Debt": 6_000_000,
                "Current Assets": 3_600_000,
                "Current Liabilities": 3_000_000,
            },
            {
                "Company": "Future Manufacturing",
                "Sector": "Manufacturing",
                "Revenue": 21_000_000,
                "Expenses": 17_500_000,
                "Total Assets": 32_000_000,
                "Total Debt": 9_000_000,
                "Current Assets": 9_500_000,
                "Current Liabilities": 5_000_000,
            },
        ]
    )


def prepare_data(data):
    """Validate and calculate financial metrics."""
    data = data.copy()

    missing = [column for column in FINANCIAL_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    for column in FINANCIAL_COLUMNS[2:]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    if data[FINANCIAL_COLUMNS[2:]].isna().any().any():
        raise ValueError("Financial columns contain blank or non-numeric values.")

    if (data[FINANCIAL_COLUMNS[2:]] < 0).any().any():
        raise ValueError("Financial amounts cannot be negative.")

    if (data["Current Liabilities"] == 0).any():
        raise ValueError("Current Liabilities must be greater than zero.")

    if (data["Total Assets"] == 0).any():
        raise ValueError("Total Assets must be greater than zero.")

    data["Company"] = data["Company"].astype(str).str.strip()
    data["Sector"] = data["Sector"].astype(str).str.strip()

    if (data["Company"] == "").any() or (data["Sector"] == "").any():
        raise ValueError("Company and Sector values cannot be blank.")

    data["Profit"] = data["Revenue"] - data["Expenses"]
    data["Profit Margin (%)"] = np.where(
        data["Revenue"] > 0,
        data["Profit"] / data["Revenue"] * 100,
        0,
    )
    data["Current Ratio"] = data["Current Assets"] / data["Current Liabilities"]
    data["Debt Ratio (%)"] = data["Total Debt"] / data["Total Assets"] * 100
    data["Asset Turnover"] = np.where(
        data["Total Assets"] > 0,
        data["Revenue"] / data["Total Assets"],
        0,
    )
    return data


def risk_label(row):
    """Create a simple rule-based risk label."""
    score = 0
    if row["Profit Margin (%)"] < 5:
        score += 1
    if row["Current Ratio"] < 1:
        score += 1
    if row["Debt Ratio (%)"] > 60:
        score += 1
    if row["Profit"] < 0:
        score += 1

    if score >= 3:
        return "High Risk"
    if score >= 1:
        return "Medium Risk"
    return "Low Risk"


def add_risk_assessment(data):
    data = data.copy()
    data["Risk Level"] = data.apply(risk_label, axis=1)
    return data


def money(value):
    return f"₹{value:,.0f}"


# ============================================================
# REPORT AND AI FUNCTIONS
# ============================================================

def build_financial_summary(data):
    total_revenue = data["Revenue"].sum()
    total_expenses = data["Expenses"].sum()
    total_profit = data["Profit"].sum()
    overall_margin = total_profit / total_revenue * 100 if total_revenue else 0

    return {
        "report_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "number_of_companies": int(len(data)),
        "total_revenue": float(total_revenue),
        "total_expenses": float(total_expenses),
        "total_profit": float(total_profit),
        "overall_profit_margin_percent": round(overall_margin, 2),
        "high_risk_companies": int((data["Risk Level"] == "High Risk").sum()),
        "medium_risk_companies": int((data["Risk Level"] == "Medium Risk").sum()),
        "low_risk_companies": int((data["Risk Level"] == "Low Risk").sum()),
    }


def generate_ai_insights(data):
    """Generate insights with local Ollama, if available."""
    if not REQUESTS_AVAILABLE:
        return "Install the requests package to enable local AI insights."

    summary = build_financial_summary(data)
    company_data = data[
        [
            "Company",
            "Sector",
            "Revenue",
            "Expenses",
            "Profit",
            "Profit Margin (%)",
            "Current Ratio",
            "Debt Ratio (%)",
            "Risk Level",
        ]
    ].to_dict(orient="records")

    prompt = f"""
You are a financial analysis assistant.

Analyze the following financial data:
{json.dumps(company_data, indent=2)}

Overall summary:
{json.dumps(summary, indent=2)}

Write a beginner-friendly report containing:
1. Overall financial performance
2. Profitability observations
3. Liquidity concerns
4. Debt and financial risk observations
5. Practical recommendations

Use only the supplied data. Do not invent missing information.
Explain that the results are estimates and not financial advice.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        result = response.json().get("response", "").strip()
        if not result:
            return "The AI service returned an empty response."
        return result
    except requests.exceptions.ConnectionError:
        return (
            "Could not connect to Ollama. Start Ollama locally and "
            f"download the model with `ollama pull {OLLAMA_MODEL}`. "
            "Then restart this analysis."
        )
    except requests.exceptions.Timeout:
        return "The AI request timed out. Try again or use a smaller dataset."
    except Exception as exc:
        return f"AI analysis could not be completed: {exc}"


def create_report_text(data):
    summary = build_financial_summary(data)
    lines = [
        "AUTOMATED FINANCIAL REPORT",
        "=" * 40,
        f"Generated: {summary['report_generated']}",
        f"Companies analyzed: {summary['number_of_companies']}",
        "",
        "FINANCIAL SUMMARY",
        "-" * 40,
        f"Total Revenue: {money(summary['total_revenue'])}",
        f"Total Expenses: {money(summary['total_expenses'])}",
        f"Total Profit: {money(summary['total_profit'])}",
        f"Overall Profit Margin: {summary['overall_profit_margin_percent']}%",
        "",
        "RISK SUMMARY",
        "-" * 40,
        f"High Risk: {summary['high_risk_companies']}",
        f"Medium Risk: {summary['medium_risk_companies']}",
        f"Low Risk: {summary['low_risk_companies']}",
        "",
        "COMPANY DETAILS",
        "-" * 40,
    ]

    for _, row in data.iterrows():
        lines.extend(
            [
                f"Company: {row['Company']}",
                f"Sector: {row['Sector']}",
                f"Revenue: {money(row['Revenue'])}",
                f"Expenses: {money(row['Expenses'])}",
                f"Profit: {money(row['Profit'])}",
                f"Profit Margin: {row['Profit Margin (%)']:.2f}%",
                f"Current Ratio: {row['Current Ratio']:.2f}",
                f"Debt Ratio: {row['Debt Ratio (%)']:.2f}%",
                f"Risk Level: {row['Risk Level']}",
                "",
            ]
        )

    lines.append(
        "Note: This report is based on supplied data and is not "
        "professional financial advice."
    )
    return "\n".join(lines)


# ============================================================
# PAGE: HOME
# ============================================================

def page_home(data):
    st.title("📊 Financial Report Generator")
    st.write(
        "Welcome to your company financial reporting and risk analysis dashboard."
    )
    summary = build_financial_summary(data)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Companies", summary["number_of_companies"])
    c2.metric("Total Revenue", money(summary["total_revenue"]))
    c3.metric("Total Profit", money(summary["total_profit"]))
    c4.metric("Profit Margin", f"{summary['overall_profit_margin_percent']:.2f}%")

    st.subheader("What you can do")
    st.markdown(
        """
        - Upload company financial data from a CSV file.
        - View profitability, liquidity, and debt metrics.
        - Compare companies and business sectors.
        - Identify companies with potential financial risks.
        - Try an experimental machine-learning risk classifier.
        - Generate AI-assisted insights using local Ollama.
        - Download financial reports as CSV, JSON, or TXT.
        """
    )
    st.info(
        "Start with the sample dataset, or upload your own data "
        "from the Data Upload page."
    )


# ============================================================
# PAGE: DATA UPLOAD
# ============================================================

def page_data_upload():
    st.title("📁 Data Upload")
    st.write("Upload a CSV containing company financial information.")
    st.markdown("Required columns:")
    st.code(", ".join(FINANCIAL_COLUMNS))

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Load Sample Data", use_container_width=True):
            st.session_state.financial_data = get_sample_data()
            st.success("Sample data loaded.")
            st.rerun()

    with c2:
        sample_csv = get_sample_data().to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Sample CSV",
            data=sample_csv,
            file_name="sample_financial_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if uploaded_file is not None:
        try:
            raw_data = pd.read_csv(uploaded_file)
            st.subheader("Preview uploaded data")
            st.dataframe(raw_data.head(10), use_container_width=True)

            if st.button("Use Uploaded Data", type="primary"):
                validated_data = prepare_data(raw_data)
                st.session_state.financial_data = validated_data[FINANCIAL_COLUMNS].copy()
                st.success("Uploaded data is now active.")
                st.rerun()
        except Exception as exc:
            st.error(f"Could not read or validate the uploaded file: {exc}")


# ============================================================
# PAGE: DASHBOARD
# ============================================================

def page_dashboard(data):
    st.title("📈 Financial Dashboard")
    summary = build_financial_summary(data)

    a, b, c, d = st.columns(4)
    a.metric("Revenue", money(summary["total_revenue"]))
    b.metric("Expenses", money(summary["total_expenses"]))
    c.metric("Profit", money(summary["total_profit"]))
    d.metric("Profit Margin", f"{summary['overall_profit_margin_percent']:.2f}%")

    st.subheader("Company financial metrics")
    st.dataframe(
        data[
            [
                "Company",
                "Sector",
                "Revenue",
                "Expenses",
                "Profit",
                "Profit Margin (%)",
                "Current Ratio",
                "Debt Ratio (%)",
                "Risk Level",
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True,
    )

    chart = px.bar(
        data,
        x="Company",
        y=["Revenue", "Expenses", "Profit"],
        barmode="group",
        title="Revenue, Expenses and Profit by Company",
    )
    st.plotly_chart(chart, use_container_width=True)


# ============================================================
# PAGE: COMPANY ANALYSIS
# ============================================================

def page_company_analysis(data):
    st.title("🏢 Company Analysis")
    selected_company = st.selectbox(
        "Select a company",
        data["Company"].astype(str).tolist(),
    )
    row = data[data["Company"] == selected_company].iloc[0]

    st.subheader(selected_company)
    a, b, c = st.columns(3)
    a.metric("Revenue", money(row["Revenue"]))
    b.metric("Expenses", money(row["Expenses"]))
    c.metric("Profit", money(row["Profit"]))

    d, e, f = st.columns(3)
    d.metric("Profit Margin", f"{row['Profit Margin (%)']:.2f}%")
    e.metric("Current Ratio", f"{row['Current Ratio']:.2f}")
    f.metric("Debt Ratio", f"{row['Debt Ratio (%)']:.2f}%")

    st.write("**Sector:**", row["Sector"])
    st.write("**Risk level:**", row["Risk Level"])

    if row["Profit"] < 0:
        st.warning("This company has expenses greater than revenue.")
    if row["Current Ratio"] < 1:
        st.warning(
            "Current liabilities exceed current assets. Review short-term liquidity."
        )
    if row["Debt Ratio (%)"] > 60:
        st.warning("The debt-to-assets ratio is relatively high.")

    company_metrics = pd.DataFrame(
        {
            "Metric": ["Revenue", "Expenses", "Profit"],
            "Amount": [row["Revenue"], row["Expenses"], row["Profit"]],
        }
    )
    fig = px.bar(
        company_metrics,
        x="Metric",
        y="Amount",
        title=f"Financial Performance: {selected_company}",
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE: SECTOR ANALYSIS
# ============================================================

def page_sector_analysis(data):
    st.title("🏭 Sector Analysis")
    sector_data = (
        data.groupby("Sector", as_index=False)
        .agg(
            {
                "Revenue": "sum",
                "Expenses": "sum",
                "Profit": "sum",
                "Total Assets": "sum",
                "Total Debt": "sum",
            }
        )
    )
    sector_data["Profit Margin (%)"] = np.where(
        sector_data["Revenue"] > 0,
        sector_data["Profit"] / sector_data["Revenue"] * 100,
        0,
    )

    st.dataframe(sector_data.round(2), use_container_width=True, hide_index=True)

    fig = px.bar(
        sector_data,
        x="Sector",
        y="Profit",
        color="Sector",
        title="Total Profit by Sector",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        sector_data,
        x="Sector",
        y="Profit Margin (%)",
        title="Profit Margin by Sector",
    )
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# PAGE: VISUALIZATIONS
# ============================================================

def page_visualizations(data):
    st.title("📉 Financial Visualizations")
    fig1 = px.scatter(
        data,
        x="Revenue",
        y="Profit",
        size="Total Assets",
        color="Risk Level",
        hover_name="Company",
        title="Revenue vs Profit",
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        data,
        x="Company",
        y="Profit Margin (%)",
        color="Risk Level",
        title="Profit Margin by Company",
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(
        data,
        x="Total Assets",
        y="Total Debt",
        color="Sector",
        hover_name="Company",
        title="Total Assets vs Total Debt",
    )
    st.plotly_chart(fig3, use_container_width=True)

    risk_counts = (
        data["Risk Level"].value_counts()
        .rename_axis("Risk Level")
        .reset_index(name="Companies")
    )
    fig4 = px.pie(
        risk_counts,
        names="Risk Level",
        values="Companies",
        title="Distribution of Risk Levels",
    )
    st.plotly_chart(fig4, use_container_width=True)


# ============================================================
# PAGE: RISK ASSESSMENT
# ============================================================

def page_risk_assessment(data):
    st.title("⚠️ Financial Risk Assessment")
    st.write(
        "Risk levels are assigned using simple financial thresholds. "
        "They are indicators for review, not guarantees of default."
    )

    st.dataframe(
        data[
            [
                "Company",
                "Profit Margin (%)",
                "Current Ratio",
                "Debt Ratio (%)",
                "Risk Level",
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True,
    )

    high_risk = data[data["Risk Level"] == "High Risk"]
    if not high_risk.empty:
        st.error("Companies flagged as High Risk")
        st.dataframe(
            high_risk[["Company", "Sector", "Risk Level"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.success("No companies are currently flagged as High Risk.")

    st.subheader("How risk is estimated")
    st.markdown(
        """
        - Profit margin below 5% adds a risk indicator.
        - Current ratio below 1 adds a liquidity risk indicator.
        - Debt ratio above 60% adds a leverage risk indicator.
        - Negative profit adds a profitability risk indicator.

        **High Risk:** 3 or more indicators  
        **Medium Risk:** 1–2 indicators  
        **Low Risk:** no indicators
        """
    )


# ============================================================
# PAGE: MACHINE LEARNING PREDICTIONS
# ============================================================

def page_ml_predictions(data):
    st.title("🤖 ML Risk Predictions")
    if not SKLEARN_AVAILABLE:
        st.error("Scikit-learn is not installed. Run `pip install scikit-learn`.")
        return

    if len(data) < 5:
        st.warning(
            "At least five company records are recommended for this demo. "
            "More real, labeled records are needed for a useful model evaluation."
        )
        return

    st.warning(
        "This demo trains on rule-generated labels from the same financial "
        "dataset. Results are educational and do not demonstrate independently "
        "validated predictive accuracy."
    )

    feature_columns = [
        "Revenue",
        "Expenses",
        "Total Assets",
        "Total Debt",
        "Current Assets",
        "Current Liabilities",
        "Profit Margin (%)",
        "Current Ratio",
        "Debt Ratio (%)",
    ]
    X = data[feature_columns].replace([np.inf, -np.inf], np.nan).fillna(0)
    y = data["Risk Level"]

    if y.nunique() < 2:
        st.info(
            "The current dataset contains only one risk class. "
            "Add companies with different financial profiles."
        )
        return

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X, y)
    predictions = model.predict(X)

    results = data[["Company", "Sector", "Risk Level"]].copy()
    results["ML Risk Prediction"] = predictions
    results["Matches Rule Label"] = results["Risk Level"] == results["ML Risk Prediction"]

    st.subheader("Predictions")
    st.dataframe(results, use_container_width=True, hide_index=True)
    st.metric(
        "Training-set label agreement",
        f"{accuracy_score(y, predictions) * 100:.1f}%",
    )
    st.caption(
        "Training-set agreement is not test accuracy. A reliable model "
        "requires more records and evaluation on unseen data."
    )

    importance = pd.DataFrame(
        {
            "Feature": feature_columns,
            "Importance": model.feature_importances_,
        }
    ).sort_values("Importance", ascending=False)
    fig = px.bar(
        importance,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Feature Importance in the Demo Model",
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE: AI INSIGHTS
# ============================================================

def page_ai_insights(data):
    st.title("🧠 AI Financial Insights")
    st.write(
        "Generate an explanation of the financial metrics using a locally running Ollama model."
    )
    st.caption(
        f"Configured model: {OLLAMA_MODEL}. "
        "AI output may be inaccurate; verify financial conclusions."
    )

    if st.button("Generate AI Insights", type="primary"):
        with st.spinner("Generating financial insights..."):
            st.session_state.ai_insights = generate_ai_insights(data)

    if st.session_state.get("ai_insights"):
        st.markdown(st.session_state.ai_insights)
        st.download_button(
            "Download AI Insights",
            data=st.session_state.ai_insights,
            file_name="ai_financial_insights.txt",
            mime="text/plain",
        )


# ============================================================
# PAGE: FINANCIAL SUMMARY
# ============================================================

def page_financial_summary(data):
    st.title("📝 Financial Summary")
    summary = build_financial_summary(data)
    st.subheader("Overall Summary")

    a, b = st.columns(2)
    a.write("**Companies analyzed:**")
    a.write(summary["number_of_companies"])
    a.write("**Total revenue:**")
    a.write(money(summary["total_revenue"]))
    a.write("**Total expenses:**")
    a.write(money(summary["total_expenses"]))

    b.write("**Total profit:**")
    b.write(money(summary["total_profit"]))
    b.write("**Overall profit margin:**")
    b.write(f"{summary['overall_profit_margin_percent']:.2f}%")
    b.write("**High-risk companies:**")
    b.write(summary["high_risk_companies"])

    st.subheader("Company-level summary")
    st.dataframe(
        data[
            [
                "Company",
                "Sector",
                "Revenue",
                "Expenses",
                "Profit",
                "Profit Margin (%)",
                "Risk Level",
            ]
        ].round(2),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# PAGE: EXPORT REPORTS
# ============================================================

def page_export_reports(data):
    st.title("📥 Export Reports")
    summary = build_financial_summary(data)
    st.subheader("Download financial data")

    csv_bytes = data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Financial Data (CSV)",
        data=csv_bytes,
        file_name="financial_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )

    json_text = json.dumps(
        {
            "summary": summary,
            "companies": data.to_dict(orient="records"),
        },
        indent=2,
        default=str,
    )
    st.download_button(
        "Download Report (JSON)",
        data=json_text,
        file_name="financial_report.json",
        mime="application/json",
        use_container_width=True,
    )

    report_text = create_report_text(data)
    st.download_button(
        "Download Report (TXT)",
        data=report_text,
        file_name="financial_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.subheader("Preview report")
    st.text(report_text)


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():
    init_auth_database()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "financial_data" not in st.session_state:
        st.session_state.financial_data = get_sample_data()

    if "ai_insights" not in st.session_state:
        st.session_state.ai_insights = ""

    if not st.session_state.logged_in:
        show_auth_page()
        return

    user = st.session_state.user

    # Prepare financial metrics and risk levels.
    try:
        data = prepare_data(st.session_state.financial_data)
        data = add_risk_assessment(data)
    except Exception as exc:
        st.error(f"Could not process the financial data: {exc}")
        st.info(
            "Open Data Upload and load the sample data or upload a corrected CSV."
        )
        return

    with st.sidebar:
        st.title("📊 Financial Reports")
        st.write(f"Welcome, **{user['name']}**")
        st.caption(user["email"])

        if st.button("🚪 Logout", use_container_width=True):
            logout()

        st.divider()
        page = st.radio(
            "Navigation",
            [
                "Home",
                "Data Upload",
                "Dashboard",
                "Company Analysis",
                "Sector Analysis",
                "Visualizations",
                "Risk Assessment",
                "ML Predictions",
                "AI Insights",
                "Financial Summary",
                "Export Reports",
            ],
        )
        st.divider()
        st.caption("Automated Financial Report Generator")
        st.caption("Demo version")

    if page == "Home":
        page_home(data)
    elif page == "Data Upload":
        page_data_upload()
    elif page == "Dashboard":
        page_dashboard(data)
    elif page == "Company Analysis":
        page_company_analysis(data)
    elif page == "Sector Analysis":
        page_sector_analysis(data)
    elif page == "Visualizations":
        page_visualizations(data)
    elif page == "Risk Assessment":
        page_risk_assessment(data)
    elif page == "ML Predictions":
        page_ml_predictions(data)
    elif page == "AI Insights":
        page_ai_insights(data)
    elif page == "Financial Summary":
        page_financial_summary(data)
    elif page == "Export Reports":
        page_export_reports(data)


if __name__ == "__main__":
    main()
