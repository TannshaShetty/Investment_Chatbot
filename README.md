# Investment_Chatbot
import streamlit as st
import subprocess
import sys
import google.generativeai as genai


# Ensure necessary packages are installed
def install_packages():
    packages = ['streamlit']
    for package in packages:
        subprocess.call([sys.executable, "-m", "pip", "install", package])


install_packages()

# Initialize session state if not present
if 'wallet_balance' not in st.session_state:
    st.session_state.wallet_balance = 0
if 'goal_data' not in st.session_state:
    st.session_state.goal_data = {}


# Function to add funds
def add_funds():
    st.session_state.wallet_balance += 100  # Example increment


# Sidebar Navigation
st.sidebar.title("Investment Tracker")
nav_option = st.sidebar.radio("Navigation", ['Wallet', 'Set Goal', 'Your Investments'])

# Wallet Page
if nav_option == 'Wallet':
    st.title("💰 Wallet")
    st.subheader("Manage Your Balance")
    st.write(f"**Current Balance:** ${st.session_state.wallet_balance}")
    if st.button("➕ Add Funds"):
        add_funds()
        st.success("Funds added successfully!")
        st.rerun()

# Set Goal Page
elif nav_option == 'Set Goal':
    st.title("🎯 Set Your Investment Goal")
    percentage_profit = st.number_input("📈 Enter target profit percentage:", min_value=0.0, step=0.1)
    time_span = st.number_input("⏳ Enter time span (months):", min_value=1, step=1)

    if st.button("Submit Goal"):
        api = "AIzaSyC15hBMiMRDoF42JRuiHrCfrmC2VM6IKF8"

        prompt = """
        Find 3 stocks from moneycontrol.com which are having dividend yield and TTM PE less than Sector PE
        """

        genai.configure(api_key=api)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        stock_data = response.text

        st.session_state.goal_data = {
            "Profit Percentage": percentage_profit,
            "Time Span (days)": time_span,
            "Stock Analysis": stock_data
        }
        st.success("Investment goal set successfully!")
        st.rerun()

# Your Investments Page
elif nav_option == 'Your Investments':
    st.title("📊 Your Investments")
    if st.session_state.goal_data:
        st.write("### 📝 Goal Details")
        st.write(f"**📈 Profit Percentage:** {st.session_state.goal_data['Profit Percentage']}%")
        st.write(f"**⏳ Time Span:** {st.session_state.goal_data['Time Span (days)']} days")
        if "Stock Analysis" in st.session_state.goal_data:
            st.write("### 📊 Stock Analysis")
            st.write(st.session_state.goal_data["Stock Analysis"])
    else:
        st.warning("No investment goals set yet. Set a goal to start tracking your investments!")
![image](https://github.com/user-attachments/assets/06285a99-9298-4de9-ba93-b78e17162a59)
