# risk_engine.py

from typing import Dict, List
from decimal import Decimal
import pandas as pd
from . import models # Import the models module directly
from .ml_model import load_model
from bnpl_simulator.models import StressEventType

class RiskEngine:
    # Constants for our risk rules
    MIN_CREDIT_SCORE = 580
    MAX_LATE_PAYMENT_PERCENTAGE = Decimal("0.10")
    MAX_PURCHASE_AMOUNT_NEW_USER = Decimal("500.00")
    MAX_PURCHASE_AMOUNT_ESTABLISHED_USER = Decimal("2500.00")
    MAX_TOTAL_OUTSTANDING_DEBT = Decimal("5000.00")
    WARNING_DEBT_THRESHOLD_PERCENTAGE = Decimal("0.80") # Warn if debt exceeds 80% of max
    MIN_ANNUAL_INCOME = Decimal("30000.00")
    MAX_PURCHASE_AMOUNT_HIGH_INCOME = Decimal("3000.00")
    HIGH_INCOME_THRESHOLD = Decimal("80000.00")
    ML_RISK_THRESHOLD = 0.5  # Probability threshold for ML model to consider as risky

    # Stress event specific thresholds/impacts
    JOB_LOSS_DECLINE_THRESHOLD = Decimal("0.0") # Any purchase during job loss is declined
    MEDICAL_EXPENSE_RISK_FACTOR = Decimal("1.2") # Increase perceived risk by 20%
    DELAYED_SALARY_WARNING_THRESHOLD = Decimal("0.5") # Warn if purchase > 50% of monthly income

    def __init__(self):
        self.ml_model = load_model()

    def decide(self, user: models.UserProfile, purchase_amount: Decimal, outstanding_debt: Decimal = Decimal("0.0")) -> Dict:
        """Analyzes a purchase request against a user's profile and current debt."""
        reasons: List[str] = []
        warnings: List[str] = []

        # --- Teen Mode Override ---
        if user.is_teen_mode:
            if purchase_amount > user.virtual_balance:
                reasons.append(f"Virtual purchase amount ${purchase_amount:.2f} exceeds virtual balance ${user.virtual_balance:.2f}.")
            # For teen mode, we might want to always approve if virtual balance is sufficient,
            # or apply very lenient rules. For now, let's just check virtual balance.
            if not reasons:
                return {"decision": "APPROVED", "reason": "Teen mode: Virtual balance sufficient.", "warnings": []}
            else:
                return {"decision": "DECLINED", "reasons": reasons, "warnings": []}


        # --- Stress Event Impact ---
        if user.current_stress_event == models.StressEventType.JOB_LOSS:
            reasons.append("Loan declined due to active 'Job Loss' stress event. Focus on essential expenses.")
            return {"decision": "DECLINED", "reasons": reasons, "warnings": warnings}
        elif user.current_stress_event == models.StressEventType.MEDICAL_EXPENSE:
            warnings.append("Active 'Medical Expense' stress event detected. Consider if this purchase is essential.")
            # Potentially adjust other rules, e.g., lower max purchase amount
        elif user.current_stress_event == models.StressEventType.DELAYED_SALARY:
            warnings.append("Active 'Delayed Salary' stress event detected. Ensure you can meet upcoming payments.")
            # If purchase amount is high relative to monthly income, add a stronger warning or decline
            monthly_income = Decimal(user.annual_income) / 12
            if purchase_amount > monthly_income * self.DELAYED_SALARY_WARNING_THRESHOLD:
                warnings.append(f"Purchase amount ${purchase_amount:.2f} is significant given your delayed salary event. Consider delaying this purchase.")

        # Rule 1: Check credit score
        if user.credit_score < self.MIN_CREDIT_SCORE:
            reasons.append(f"Credit score {user.credit_score} is below minimum of {self.MIN_CREDIT_SCORE}.")

        # Rule 2: Check past payment history
        if user.completed_loans > 0:
            # Assuming 4 installments per loan for simplicity
            total_past_installments = user.completed_loans * 4
            if total_past_installments > 0:
                late_percentage = user.late_payments / total_past_installments
                if late_percentage > self.MAX_LATE_PAYMENT_PERCENTAGE:
                    reasons.append("User has a high percentage of historical late payments.")

        # Rule 3: Check minimum annual income
        if Decimal(user.annual_income) < self.MIN_ANNUAL_INCOME:
            reasons.append(f"Annual income ${user.annual_income:,.2f} is below minimum of ${self.MIN_ANNUAL_INCOME:,.2f}.")

        # Rule 4: Check purchase amount based on user profile
        is_new_user = user.completed_loans == 0
        if is_new_user:
            if purchase_amount > self.MAX_PURCHASE_AMOUNT_NEW_USER:
                reasons.append(f"Purchase amount ${purchase_amount:.2f} exceeds the limit of ${self.MAX_PURCHASE_AMOUNT_NEW_USER:.2f} for new users.")
        else:  # Established user_
            if Decimal(user.annual_income) >= self.HIGH_INCOME_THRESHOLD:
                if purchase_amount > self.MAX_PURCHASE_AMOUNT_HIGH_INCOME:
                    reasons.append(f"Purchase amount ${purchase_amount:.2f} exceeds the limit of ${self.MAX_PURCHASE_AMOUNT_HIGH_INCOME:.2f} for high-income users.")
            else:  # Established, not high-income
                if purchase_amount > self.MAX_PURCHASE_AMOUNT_ESTABLISHED_USER:
                    reasons.append(f"Purchase amount ${purchase_amount:.2f} exceeds the limit of ${self.MAX_PURCHASE_AMOUNT_ESTABLISHED_USER:.2f} for established users.")

        # Rule 5: Check total exposure
        new_total_debt = outstanding_debt + purchase_amount
        if new_total_debt > self.MAX_TOTAL_OUTSTANDING_DEBT:
            reasons.append(f"This purchase would bring total debt to ${new_total_debt:.2f}, exceeding the limit of ${self.MAX_TOTAL_OUTSTANDING_DEBT:.2f}.")
        elif new_total_debt > (self.MAX_TOTAL_OUTSTANDING_DEBT * self.WARNING_DEBT_THRESHOLD_PERCENTAGE):
            warnings.append(f"High cumulative debt: This purchase brings total debt to ${new_total_debt:.2f}, which is close to your limit of ${self.MAX_TOTAL_OUTSTANDING_DEBT:.2f}.")

        # Rule 6: Integrate ML Model prediction (if available)
        if self.ml_model:
            # Prepare user data for ML model prediction
            user_data = {
                'Customer_Age': user.age,
                'Annual_Income': user.annual_income,
                'Credit_Score': user.credit_score,
                'Purchase_Amount': float(purchase_amount),  # ML model was trained on floats
                'Gender': user.gender,
                'Purchase_Category': user.purchase_category,
                'Device_Type': user.device_type,
                'Connection_Type': user.connection_type,
                'Checkout_Time_Seconds': user.checkout_time_seconds,
                'Browser': user.browser
            }
            user_df = pd.DataFrame([user_data])
            risk_probability = self.ml_model.predict_proba(user_df)[:, 1][0] # Probability of being risky (class 1)

            if risk_probability > self.ML_RISK_THRESHOLD:
                reasons.append(f"ML model predicts high risk (probability: {risk_probability:.2f}).")

        # Final Decision
        if not reasons:
            response = {"decision": "APPROVED", "reason": "All risk checks passed."}
            if warnings:
                response["warnings"] = warnings
            return response
        else:
            return {"decision": "DECLINED", "reasons": reasons, "warnings": warnings}