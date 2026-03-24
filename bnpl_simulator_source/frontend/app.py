import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="BNPL Simulator",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Helper Functions
def api_get(endpoint: str):
    """Make GET request to API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def api_post(endpoint: str, data: dict):
    """Make POST request to API"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def api_put(endpoint: str, data: dict):
    """Make PUT request to API"""
    try:
        response = requests.put(f"{API_BASE_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

# Sidebar Navigation
st.sidebar.markdown('<div class="main-header">BNPL Simulator</div>', unsafe_allow_html=True)
page = st.sidebar.selectbox(
    "Choose a feature:",
    [
        "🏠 Dashboard",
        "👤 User Management", 
        "💳 Checkout & Loans",
        "📊 Affordability Analysis",
        "💰 Financing Comparison",
        "⚠️ Stress Testing",
        "🎯 Advanced Features"
    ]
)

# Initialize session state
if 'current_user_id' not in st.session_state:
    st.session_state.current_user_id = None
if 'selected_loan_id' not in st.session_state:
    st.session_state.selected_loan_id = None

# Dashboard Page
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">BNPL Simulator Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🏦 Loan Management</h4>
            <p>Process checkouts, manage loans, and track payments</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🔍 Affordability Analysis</h4>
            <p>Get personalized affordability scores and recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>💰 Financing Options</h4>
            <p>Compare BNPL vs Credit Card vs Personal Loan</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown('<div class="sub-header">Quick Actions</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 Check User Health Score")
        user_id_health = st.text_input("User ID", key="dashboard_health_user_id")
        if st.button("Check Health Score", use_container_width=True):
            if user_id_health:
                health_score = api_get(f"/users/{user_id_health}/health-score")
                if health_score:
                    st.success(f"Score: {health_score['score']} ({health_score['rating']})")
                    
                    # Simplified score gauge
                    score = health_score['score']
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Health Score"},
                        gauge={
                            'axis': {'range': [None, 850]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 580], 'color': "lightgray"},
                                {'range': [580, 670], 'color': "yellow"},
                                {'range': [670, 740], 'color': "lightgreen"},
                                {'range': [740, 850], 'color': "green"}
                            ]
                        }
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("User not found.")
            else:
                st.warning("Enter User ID")
    
    with col2:
        st.markdown("### 💳 Process Checkout")
        checkout_user_id = st.text_input("User ID", key="dashboard_checkout_user_id")
        checkout_amount = st.number_input("Amount (₹)", min_value=0.0, value=100.0, key="dashboard_checkout_amount")
        
        if st.button("Process Checkout", use_container_width=True):
            if checkout_user_id and checkout_amount > 0:
                checkout_data = {
                    "user_id": checkout_user_id,
                    "merchant_id": "merchant_001",
                    "amount": checkout_amount,
                    "apply_convenience_fee": True
                }
                
                result = api_post("/checkout", checkout_data)
                if result:
                    st.success("✅ Checkout successful!")
                else:
                    st.error("❌ Declined by risk engine")
            else:
                st.error("Enter User ID & Amount")
    
    with col3:
        st.markdown("### 📊 Get Financing Comparison")
        comparison_amount = st.number_input("Amount (₹)", min_value=0.0, value=1000.0, key="dashboard_comparison_amount")
        
        if st.button("Generate Comparison", use_container_width=True):
            if comparison_amount > 0:
                comparison = api_post("/compare-scenarios", {
                    "purchase_amount": comparison_amount,
                    "user_id": None
                })
                
                if comparison:
                    scenarios = comparison['scenarios']
                    
                    # Display comparison table
                    st.markdown("#### Comparison Results")
                    comparison_data = []
                    for scenario in scenarios:
                        comparison_data.append({
                            'Type': scenario['type'],
                            'Effective APR (%)': scenario['effective_apr'],
                            'Total Repayment (₹)': float(scenario['total_repayment']),
                            'Monthly Payment (₹)': float(scenario['monthly_payment']),
                            'Term (months)': scenario['term_months']
                        })
                    
                    st.table(comparison_data)
                else:
                    st.error("Error generating comparison")
            else:
                st.error("Enter Amount")

# User Management Page
elif page == "👤 User Management":
    st.markdown('<div class="main-header">User Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 User Profile", "📈 Health Score", "⚙️ Settings"])
    
    with tab1:
        st.markdown('<div class="sub-header">User Profile Management</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            user_id = st.text_input("Enter User ID", value=st.session_state.current_user_id or "")
            if st.button("🔍 Load User"):
                st.session_state.current_user_id = user_id
        
        if st.session_state.current_user_id:
            user_data = api_get(f"/users/{st.session_state.current_user_id}")
            if user_data:
                st.success(f"Loaded user: {user_data['user_id']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Credit Score", user_data['credit_score'])
                    st.metric("Age", user_data['age'])
                    st.metric("Annual Income", f"₹{user_data['annual_income']:,.2f}")
                    st.metric("Completed Loans", user_data['completed_loans'])
                
                with col2:
                    st.metric("Late Payments", user_data['late_payments'])
                    st.metric("Gender", user_data['gender'])
                    st.metric("Device Type", user_data['device_type'])
                    st.metric("Browser", user_data['browser'])
                
                # User obligations
                obligations = api_get(f"/users/{st.session_state.current_user_id}/obligations")
                if obligations:
                    st.markdown("### Active Loans")
                    for loan in obligations:
                        with st.expander(f"Loan {loan['loan_id']} - ₹{float(loan['total_amount']):,.2f}"):
                            st.write(f"**Merchant:** {loan['merchant_id']}")
                            st.write(f"**Status:** {loan['status']}")
                            st.write(f"**Down Payment:** ₹{float(loan['down_payment']):,.2f}")
                            st.write(f"**Installments:** {len(loan['installments'])}")
                            
                            # Installments table
                            st.table(loan['installments'])
    
    with tab2:
        st.markdown('<div class="sub-header">BNPL Health Score</div>', unsafe_allow_html=True)
        
        if st.session_state.current_user_id:
            health_score = api_get(f"/users/{st.session_state.current_user_id}/health-score")
            if health_score:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    score = health_score['score']
                    rating = health_score['rating']
                    
                    # Score gauge
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': f"Health Score: {rating}"},
                        gauge={
                            'axis': {'range': [None, 850]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 580], 'color': "lightgray"},
                                {'range': [580, 670], 'color': "yellow"},
                                {'range': [670, 740], 'color': "lightgreen"},
                                {'range': [740, 850], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 800
                            }
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### Positive Factors")
                    for factor in health_score['positive_factors']:
                        st.success(factor)
                    
                    st.markdown("### Negative Factors")
                    for factor in health_score['negative_factors']:
                        st.warning(factor)
        
        else:
            st.info("Please select a user to view their health score.")
    
    with tab3:
        st.markdown('<div class="sub-header">User Settings</div>', unsafe_allow_html=True)
        
        if st.session_state.current_user_id:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Stress Event Simulation")
                stress_event = st.selectbox(
                    "Select Stress Event",
                    ["NONE", "JOB_LOSS", "MEDICAL_EXPENSE", "DELAYED_SALARY"]
                )
                
                if st.button("🔄 Update Stress Event"):
                    result = api_put(f"/users/{st.session_state.current_user_id}/stress-event", 
                                   {"event_type": stress_event})
                    if result:
                        st.success("Stress event updated successfully!")
            
            with col2:
                st.markdown("### Teen Mode Settings")
                is_teen_mode = st.checkbox("Enable Teen Mode")
                virtual_balance = st.number_input("Virtual Balance", min_value=0.0, value=0.0)
                
                if st.button("💾 Update Teen Mode"):
                    result = api_put(f"/users/{st.session_state.current_user_id}/teen-mode", {
                        "is_teen_mode": is_teen_mode,
                        "virtual_balance": virtual_balance
                    })
                    if result:
                        st.success("Teen mode settings updated successfully!")

# Checkout & Loans Page
elif page == "💳 Checkout & Loans":
    st.markdown('<div class="main-header">Checkout & Loan Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["💳 Process Checkout", "💰 Pay Installment", "📋 Loan Dashboard"])
    
    with tab1:
        st.markdown('<div class="sub-header">Process New Checkout</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", key="checkout_user_id")
            merchant_id = st.text_input("Merchant ID", value="merchant_001")
            amount = st.number_input("Purchase Amount (₹)", min_value=0.0, value=100.0)
            apply_fee = st.checkbox("Apply Convenience Fee", value=True)
        
        with col2:
            if user_id:
                user_data = api_get(f"/users/{user_id}")
                if user_data:
                    st.info(f"User Credit Score: {user_data['credit_score']}")
                    st.info(f"Annual Income: ₹{user_data['annual_income']:,.2f}")
            
            if st.button("💳 Process Checkout", key="process_checkout_btn"):
                if user_id and merchant_id and amount > 0:
                    checkout_data = {
                        "user_id": user_id,
                        "merchant_id": merchant_id,
                        "amount": amount,
                        "apply_convenience_fee": apply_fee
                    }
                    
                    result = api_post("/checkout", checkout_data)
                    if result:
                        st.success("Checkout processed successfully!")
                        st.json(result)
                    else:
                        # Check if this is a risk engine rejection (400 error)
                        st.error("❌ Checkout declined by risk engine. Please try a lower amount or contact support.")
                else:
                    st.error("Please fill in all required fields.")
    
    with tab2:
        st.markdown('<div class="sub-header">Pay Installment</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id_input = st.text_input("User ID", key="pay_user_id_input")
            loan_id = st.text_input("Loan ID", key="pay_loan_id")
            
            # Get user obligations to populate loan options
            obligations = None
            if user_id_input:
                obligations = api_get(f"/users/{user_id_input}/obligations")
                if obligations:
                    st.info(f"Found {len(obligations)} active loans for user {user_id_input}")
                    # Auto-populate loan ID if only one loan exists
                    if len(obligations) == 1:
                        loan_id = obligations[0]['loan_id']
                        st.info(f"Auto-selected loan: {loan_id}")
            
            # Get loan data to show only pending installments
            pending_installments = []
            if loan_id:
                # Get user obligations to find the specific loan
                if not obligations:
                    obligations = api_get(f"/users/{user_id_input}/obligations") if user_id_input else None
                loan_data = None
                if obligations:
                    loan_data = next((loan for loan in obligations if loan['loan_id'] == loan_id), None)
                
                if loan_data:
                    # Filter for pending AND overdue installments (both can be paid)
                    payable_installments = [
                        inst for inst in loan_data['installments'] 
                        if inst['status'] in ['PENDING', 'OVERDUE']
                    ]
                    
                    if payable_installments:
                        installment_options = [
                            f"Installment {inst['installment_number']} - Due: {inst['due_date']} - Amount: ₹{float(inst['amount']):,.2f}"
                            for inst in payable_installments
                        ]
                        selected_installment = st.selectbox(
                            "Select Installment to Pay (Pending or Overdue)",
                            options=installment_options,
                            key="payable_installments_select"
                        )
                        
                        # Extract installment number from selected option
                        if selected_installment:
                            installment_number = int(selected_installment.split(' ')[1].split('-')[0])
                    else:
                        st.warning("No pending or overdue installments found for this loan.")
                        installment_number = None
                else:
                    st.warning("Loan not found or not accessible.")
                    installment_number = None
            else:
                installment_number = None
        
        with col2:
            if loan_id:
                # Get user obligations to find the specific loan
                obligations = api_get(f"/users/{st.session_state.current_user_id}/obligations") if st.session_state.current_user_id else None
                loan_data = None
                if obligations:
                    loan_data = next((loan for loan in obligations if loan['loan_id'] == loan_id), None)
                
                if loan_data:
                    st.info(f"Loan Status: {loan_data['status']}")
                    st.info(f"Total Amount: ₹{float(loan_data['total_amount']):,.2f}")
                    st.info(f"Late Fees Accrued: ₹{float(loan_data['late_fees_accrued']):,.2f}")
                    
                    # Show installments with status
                    st.markdown("### Installment Status")
                    for inst in loan_data['installments']:
                        status_color = "🟢" if inst['status'] == 'PAID' else "🟡" if inst['status'] == 'PENDING' else "🔴"
                        st.write(f"{status_color} Installment {inst['installment_number']}: {inst['status']} - Due: {inst['due_date']} - Amount: ₹{float(inst['amount']):,.2f}")
                else:
                    st.warning("Loan not found or not accessible.")
            
            if st.button("💰 Pay Installment", key="pay_installment_btn"):
                if loan_id and installment_number:
                    result = api_post(f"/loans/{loan_id}/installments/{installment_number}/pay", {})
                    if result:
                        st.success("Installment payment processed successfully!")
                        st.json(result)
                else:
                    st.warning("Please select a loan with pending installments.")
            
            # Add Late Fee Simulation for demonstration
            st.markdown("### 🚨 Late Fee Simulation (For Demo)")
            st.warning("**This is for demonstration purposes only** - Shows how late fees work when payments are missed")
            
            if loan_id and st.button("⏰ Simulate Late Payment", key="simulate_late_fee"):
                # Call the API to simulate late fees
                late_fee_result = api_post(f"/loans/{loan_id}/simulate-late-fee", {})
                if late_fee_result:
                    st.success("Late fees applied successfully!")
                    st.json(late_fee_result)
                else:
                    st.error("Failed to apply late fees. Make sure the loan exists.")
            
            if loan_id and st.button("🔄 Refresh Loan Status", key="refresh_loan_status"):
                # Refresh the loan data to show updated late fees
                st.rerun()
    
    with tab3:
        st.markdown('<div class="sub-header">Loan Dashboard</div>', unsafe_allow_html=True)
        
        user_id = st.text_input("User ID to view loans", key="dashboard_user_id")
        
        if user_id:
            # Add a button to fetch all loans for the user
            if st.button("🔍 Fetch All Loans", key="fetch_loans_btn"):
                obligations = api_get(f"/users/{user_id}/obligations")
                if obligations:
                    st.success(f"Found {len(obligations)} loan(s) for user {user_id}")
                    
                    # Display loan summary table
                    st.markdown("### Loan Summary")
                    loan_data = []
                    for loan in obligations:
                        total_installments = len(loan['installments'])
                        paid_installments = sum(1 for inst in loan['installments'] if inst['status'] == 'PAID')
                        progress = (paid_installments / total_installments) * 100 if total_installments > 0 else 0
                        
                        loan_data.append({
                            'Loan ID': loan['loan_id'],
                            'Status': loan['status'],
                            'Total Amount': f"₹{float(loan['total_amount']):,.2f}",
                            'Late Fees': f"₹{float(loan['late_fees_accrued']):,.2f}",
                            'Progress': f"{paid_installments}/{total_installments} ({progress:.1f}%)"
                        })
                    
                    st.table(loan_data)
                    
                    # Add copy buttons for each loan ID
                    st.markdown("### Copy Loan IDs")
                    for loan in obligations:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.code(f"Loan ID: {loan['loan_id']}")
                        with col2:
                            # Create a simple copy mechanism using JavaScript
                            copy_button = st.button(f"📋 Copy {loan['loan_id'][-8:]}", key=f"copy_{loan['loan_id']}")
                            if copy_button:
                                st.success(f"Copied {loan['loan_id']} to clipboard!")
                    
                    # Detailed loan information
                    st.markdown("### Detailed Loan Information")
                    for loan in obligations:
                        with st.expander(f"Loan {loan['loan_id']} - Status: {loan['status']}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Amount", f"₹{float(loan['total_amount']):,.2f}")
                                st.metric("Down Payment", f"₹{float(loan['down_payment']):,.2f}")
                                st.metric("Convenience Fee", f"₹{float(loan['convenience_fee']):,.2f}")
                            
                            with col2:
                                st.metric("Status", loan['status'])
                                st.metric("Late Fees", f"₹{float(loan['late_fees_accrued']):,.2f}")
                            
                            with col3:
                                # Calculate progress
                                total_installments = len(loan['installments'])
                                paid_installments = sum(1 for inst in loan['installments'] if inst['status'] == 'PAID')
                                progress = (paid_installments / total_installments) * 100 if total_installments > 0 else 0
                                
                                st.metric("Payment Progress", f"{paid_installments}/{total_installments}")
                                st.progress(progress / 100)
                            
                            # Installment details
                            st.markdown("#### Installment Details")
                            for i, inst in enumerate(loan['installments']):
                                status_emoji = "🟢" if inst['status'] == 'PAID' else "🟡" if inst['status'] == 'PENDING' else "🔴"
                                st.write(f"{status_emoji} Installment {i+1}: {inst['status']} - Due: {inst['due_date']} - Amount: ₹{float(inst['amount']):,.2f}")
                else:
                    st.warning("No loans found for this user. The user might not exist or has no active loans.")
            else:
                st.info("Click 'Fetch All Loans' to retrieve loan information for this user.")

# Affordability Analysis Page
elif page == "📊 Affordability Analysis":
    st.markdown('<div class="main-header">Affordability Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔍 Basic Analysis", "🎯 Enhanced Analysis"])
    
    with tab1:
        st.markdown('<div class="sub-header">Basic Affordability Assessment</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", key="afford_user_id")
            purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, value=500.0)
            desired_term = st.number_input("Desired Term (months)", min_value=1, max_value=24, value=3)
        
        with col2:
            if user_id:
                user_data = api_get(f"/users/{user_id}")
                if user_data:
                    st.info(f"User Credit Score: {user_data['credit_score']}")
                    st.info(f"Annual Income: ₹{user_data['annual_income']:,.2f}")
                    st.info(f"Completed Loans: {user_data['completed_loans']}")
                    st.info(f"Late Payments: {user_data['late_payments']}")
        
        if st.button("🔍 Get Affordability Advice"):
            if user_id and purchase_amount > 0:
                advice = api_post("/affordability-advice", {
                    "user_id": user_id,
                    "purchase_amount": purchase_amount,
                    "desired_term_months": desired_term
                })
                
                if advice:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Affordability Score", advice['affordability_score'])
                    
                    with col2:
                        st.metric("Monthly Payment", f"₹{float(advice['estimated_monthly_payment']):,.2f}")
                    
                    with col3:
                        st.metric("Recommended Term", f"{advice['recommended_term_months']} months")
                    
                    st.markdown("### Advice Message")
                    st.info(advice['advice_message'])
                    
                    if advice['warnings']:
                        st.markdown("### Warnings")
                        for warning in advice['warnings']:
                            st.warning(warning)
    
    with tab2:
        st.markdown('<div class="sub-header">Enhanced Affordability Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", key="enhanced_user_id")
            purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, value=1000.0, key="enhanced_amount")
            desired_term = st.number_input("Desired Term (months)", min_value=1, max_value=24, value=6, key="enhanced_term")
        
        with col2:
            if user_id:
                user_data = api_get(f"/users/{user_id}")
                if user_data:
                    # Calculate debt-to-income ratio
                    monthly_income = user_data['annual_income'] / 12
                    st.info(f"Monthly Income: ₹{monthly_income:,.2f}")
                    
                    # Get user obligations
                    obligations = api_get(f"/users/{user_id}/obligations")
                    if obligations:
                        total_outstanding = sum(float(inst['amount']) for loan in obligations for inst in loan['installments'] 
                                              if inst['status'] in ['PENDING', 'OVERDUE'])
                        st.info(f"Outstanding Debt: ₹{total_outstanding:,.2f}")
                        dti_ratio = (total_outstanding / monthly_income) * 100 if monthly_income > 0 else 0
                        st.info(f"Current DTI Ratio: {dti_ratio:.1f}%")
        
        if st.button("🎯 Get Enhanced Analysis"):
            if user_id and purchase_amount > 0:
                analysis = api_post("/enhanced-affordability", {
                    "user_id": user_id,
                    "purchase_amount": purchase_amount,
                    "desired_term_months": desired_term
                })
                
                if analysis:
                    # Display affordability level with color coding
                    level = analysis['affordability_level']
                    if level == 'SAFE':
                        st.success(f"✅ AFFORDABILITY LEVEL: {level}")
                    elif level == 'BORDERLINE':
                        st.warning(f"⚠️ AFFORDABILITY LEVEL: {level}")
                    else:
                        st.error(f"❌ AFFORDABILITY LEVEL: {level}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Affordability Score", analysis['affordability_score'])
                        st.metric("Monthly Payment", f"₹{float(analysis['monthly_payment']):,.2f}")
                    
                    with col2:
                        st.metric("Debt-to-Income Ratio", f"{analysis['debt_to_income_ratio']:.1f}%")
                        st.metric("Risk Factors", len(analysis['risk_factors']))
                    
                    with col3:
                        st.metric("Recommendations", len(analysis['recommendations']))
                    
                    # Risk factors
                    if analysis['risk_factors']:
                        st.markdown("### Risk Factors")
                        for factor in analysis['risk_factors']:
                            st.error(factor)
                    
                    # Recommendations
                    if analysis['recommendations']:
                        st.markdown("### Recommendations")
                        for rec in analysis['recommendations']:
                            st.info(rec)

# Financing Comparison Page
elif page == "💰 Financing Comparison":
    st.markdown('<div class="main-header">Financing Options Comparison</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">Compare BNPL vs Credit Card vs Personal Loan</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, value=1000.0)
        user_id = st.text_input("User ID (optional for personalized rates)")
    
    with col2:
        if user_id:
            user_data = api_get(f"/users/{user_id}")
            if user_data:
                st.info(f"User Credit Score: {user_data['credit_score']}")
    
    if st.button("📊 Generate Comparison"):
        if purchase_amount > 0:
            comparison = api_post("/compare-scenarios", {
                "purchase_amount": purchase_amount,
                "user_id": user_id if user_id else None
            })
            
            if comparison:
                scenarios = comparison['scenarios']
                
                # Create comparison table manually without pandas
                comparison_data = []
                for scenario in scenarios:
                    comparison_data.append({
                        'Type': scenario['type'],
                        'Effective APR (%)': scenario['effective_apr'],
                        'Total Repayment (₹)': float(scenario['total_repayment']),
                        'Monthly Payment (₹)': float(scenario['monthly_payment']),
                        'Term (months)': scenario['term_months']
                    })
                
                # Display comparison table
                st.markdown("### Comparison Table")
                st.table(comparison_data)
                
                # Visualizations using raw data
                col1, col2 = st.columns(2)
                
                with col1:
                    # Total repayment comparison
                    types = [item['Type'] for item in comparison_data]
                    total_repayments = [item['Total Repayment (₹)'] for item in comparison_data]
                    fig = go.Figure(data=[go.Bar(x=types, y=total_repayments, name='Total Repayment')])
                    fig.update_layout(title='Total Repayment Comparison', xaxis_title='Type', yaxis_title='Total Repayment (₹)')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Monthly payment comparison
                    monthly_payments = [item['Monthly Payment (₹)'] for item in comparison_data]
                    fig = go.Figure(data=[go.Bar(x=types, y=monthly_payments, name='Monthly Payment')])
                    fig.update_layout(title='Monthly Payment Comparison', xaxis_title='Type', yaxis_title='Monthly Payment (₹)')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed scenario breakdown
                for scenario in scenarios:
                    with st.expander(f"📋 {scenario['type']} Details"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Effective APR", f"{float(scenario['effective_apr']):.2f}%")
                            st.metric("Total Repayment", f"₹{float(scenario['total_repayment']):,.2f}")
                            st.metric("Monthly Payment", f"₹{float(scenario['monthly_payment']):,.2f}")
                            st.metric("Term", f"{scenario['term_months']} months")
                        
                        with col2:
                            st.markdown("### Pros")
                            for pro in scenario['pros']:
                                st.success(pro)
                            
                            st.markdown("### Cons")
                            for con in scenario['cons']:
                                st.error(con)

# Stress Testing Page
elif page == "⚠️ Stress Testing":
    st.markdown('<div class="main-header">Stress Testing & Risk Simulation</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["⚠️ Stress Event Simulation", "🔄 Refund Scenarios"])
    
    with tab1:
        st.markdown('<div class="sub-header">Stress Event Impact Analysis</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", key="stress_user_id")
            stress_event = st.selectbox(
                "Select Stress Event",
                ["NONE", "JOB_LOSS", "MEDICAL_EXPENSE", "DELAYED_SALARY"]
            )
        
        with col2:
            if user_id:
                user_data = api_get(f"/users/{user_id}")
                if user_data:
                    st.info(f"Current Stress Event: {user_data.get('current_stress_event', 'NONE')}")
                    st.info(f"Credit Score: {user_data['credit_score']}")
                    st.info(f"Completed Loans: {user_data['completed_loans']}")
                    st.info(f"Late Payments: {user_data['late_payments']}")
        
        if st.button("⚠️ Apply Stress Event"):
            if user_id and stress_event:
                result = api_put(f"/users/{user_id}/stress-event", {"event_type": stress_event})
                if result:
                    st.success("Stress event applied successfully!")
                    st.json(result)
    
    with tab2:
        st.markdown('<div class="sub-header">Refund Scenario Simulation</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_id = st.text_input("Loan ID", key="refund_loan_id")
            refund_percentage = st.slider("Refund Percentage", min_value=0.0, max_value=100.0, value=100.0)
        
        with col2:
            if loan_id:
                loan_data = api_get(f"/loans/{loan_id}")
                if loan_data:
                    st.info(f"Loan Amount: ₹{loan_data['total_amount']:,}")
                    st.info(f"Status: {loan_data['status']}")
        
        if st.button("🔄 Simulate Refund"):
            if loan_id and refund_percentage >= 0:
                simulation = api_post("/refund-simulation", {
                    "loan_id": loan_id,
                    "refund_percentage": refund_percentage / 100
                })
                
                if simulation:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Refund Type", simulation['refund_type'])
                        st.metric("Timeline", f"{simulation['timeline_days']} days")
                    
                    with col2:
                        st.metric("Refund Amount", f"₹{float(simulation['refund_amount']):,.2f}")
                        st.metric("Adjustment Method", simulation['adjustment_method'])
                    
                    with col3:
                        st.metric("Complications", len(simulation['complications']))
                    
                    if simulation['complications']:
                        st.markdown("### Complications")
                        for comp in simulation['complications']:
                            st.warning(comp)

# Advanced Features Page
elif page == "🎯 Advanced Features":
    st.markdown('<div class="main-header">Advanced Features</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Debt Spiral Visualization", "👥 Social Comparison", "📊 Advanced Analytics"])
    
    with tab1:
        st.markdown('<div class="sub-header">Debt Spiral Simulation</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("User ID", key="spiral_user_id")
            initial_amount = st.number_input("Initial Loan Amount (₹)", min_value=0.0, value=500.0)
        
        with col2:
            if user_id:
                user_data = api_get(f"/users/{user_id}")
                if user_data:
                    st.info(f"User Credit Score: {user_data['credit_score']}")
                    st.info(f"Late Payments: {user_data['late_payments']}")
        
        if st.button("📈 Generate Debt Spiral"):
            if user_id and initial_amount > 0:
                spiral_data = api_post("/debt-spiral", {
                    "user_id": user_id,
                    "initial_loan_amount": initial_amount
                })
                
                if spiral_data:
                    timeline = spiral_data['timeline']
                    
                    st.markdown("### Debt Spiral Timeline")
                    st.table(timeline)
                    
                    # Visualization using raw data
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        months = [item['month'] for item in timeline]
                        ending_balances = [item['ending_balance'] for item in timeline]
                        fig = go.Figure(data=[go.Scatter(x=months, y=ending_balances, mode='lines+markers')])
                        fig.update_layout(title='Debt Balance Over Time', xaxis_title='Month', yaxis_title='Ending Balance (₹)')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        late_fees = [item['late_fees'] for item in timeline]
                        fig = go.Figure(data=[go.Bar(x=months, y=late_fees)])
                        fig.update_layout(title='Late Fees Accrued', xaxis_title='Month', yaxis_title='Late Fees (₹)')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary metrics
                    st.markdown("### Summary")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Cost with Late Fees", f"₹{float(spiral_data['total_cost_with_late_fees']):,.2f}")
                    
                    with col2:
                        st.metric("Months to Recover", spiral_data['months_to_recover'])
                    
                    with col3:
                        worst_case = spiral_data['worst_case_scenario']
                        st.metric("Max Balance Reached", f"₹{float(worst_case['max_balance']):,.2f}")
    
    with tab2:
        st.markdown('<div class="sub-header">Social Comparison Analysis</div>', unsafe_allow_html=True)
        
        user_id = st.text_input("User ID", key="social_user_id")
        
        if st.button("👥 Get Social Comparison"):
            if user_id:
                comparison = api_post("/social-comparison", {"user_id": user_id})
                
                if comparison:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Percentile Rank", f"{comparison['percentile_rank']}th")
                        st.metric("Average Credit Score", comparison['avg_credit_score'])
                    
                    with col2:
                        st.metric("Average Debt Load", f"₹{float(comparison['avg_debt_load']):,.2f}")
                        st.metric("Payment Timing", comparison['avg_payment_timing'])
                    
                    with col3:
                        benchmark = comparison['benchmark_comparison']
                        st.metric("Credit Score vs Average", f"{benchmark['credit_score_vs_average']}")
                        st.metric("Debt Load vs Average", f"₹{float(benchmark['debt_load_vs_average']):,.2f}")
                    
                    # Visualization
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=comparison['percentile_rank'],
                        title={'text': "Your Percentile Rank"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 25], 'color': "lightgray"},
                                {'range': [25, 50], 'color': "yellow"},
                                {'range': [50, 75], 'color': "lightgreen"},
                                {'range': [75, 100], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 80
                            }
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown('<div class="sub-header">Advanced Analytics Dashboard</div>', unsafe_allow_html=True)
        
        st.markdown("### System Overview")
        
        # This would typically show system-wide analytics
        # For now, we'll show some sample metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", "1,000", delta="+50")
        
        with col2:
            st.metric("Active Loans", "250", delta="+15")
        
        with col3:
            st.metric("Approval Rate", "85%", delta="+2%")
        
        with col4:
            st.metric("Default Rate", "2.5%", delta="-0.5%")
        
        # Sample charts
        st.markdown("### Loan Distribution")
        loan_ranges = ['₹0-₹500', '₹500-₹1000', '₹1000-₹2000', '₹2000+']
        counts = [40, 35, 20, 5]
        
        fig = go.Figure(data=[go.Pie(labels=loan_ranges, values=counts, title='Loan Amount Distribution')])
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💳 BNPL Simulator Application | Built with Streamlit and FastAPI")