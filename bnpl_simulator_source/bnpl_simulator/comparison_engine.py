# bnpl_simulator/comparison_engine.py
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import ComparisonRequest, Scenario
from .models import User as UserModel

def _get_interest_rate(credit_score: int, loan_type: str) -> float:
    """
    A mock function to estimate interest rates based on credit score.
    In a real system, this would be a complex model or an API call.
    """
    if loan_type == "credit_card":
        if credit_score > 750: return 15.0
        if credit_score > 650: return 19.0
        return 24.0
    elif loan_type == "personal_loan":
        if credit_score > 750: return 7.0
        if credit_score > 650: return 11.0
        return 16.0
    return 0.0

def _calculate_emi(principal: Decimal, annual_rate: float, months: int) -> Decimal:
    """Calculates the Equated Monthly Installment (EMI)."""
    if annual_rate == 0:
        return principal / Decimal(months)
    
    monthly_rate = Decimal(annual_rate) / Decimal(1200) # r = R/12/100
    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** months)
    denominator = ((1 + monthly_rate) ** months) - 1
    if denominator == 0:
        return principal / Decimal(months) # Should not happen if rate > 0
    return numerator / denominator

def generate_comparison(request: ComparisonRequest, db: Session) -> List[Scenario]:
    """
    Generates a side-by-side comparison for different financing options.
    """
    scenarios = []
    amount = request.purchase_amount
    credit_score = 650 # Default credit score if no user is provided

    if request.user_id:
        user = db.query(UserModel).filter(UserModel.user_id == request.user_id).first()
        if user:
            credit_score = user.credit_score

    # --- Scenario 1: BNPL ---
    # Based on the app's current model: 25% down, 3 bi-weekly installments
    down_payment_bnpl = amount * Decimal("0.25")
    remaining_bnpl = amount - down_payment_bnpl
    installment_bnpl = remaining_bnpl / 3
    # Term is 3 * 2 weeks = 6 weeks ~= 1.5 months. Let's call it 2 for simplicity.
    scenarios.append(Scenario(
        type="Buy Now, Pay Later (BNPL)",
        effective_apr=0.0,
        total_repayment=amount,
        monthly_payment=installment_bnpl * 2, # Roughly two installments per month
        term_months=2,
        pros=[
            "0% interest if paid on time.",
            "Simple, fixed payment schedule.",
            "Quick approval process, often integrated at checkout."
        ],
        cons=[
            "High late fees if payments are missed.",
            "Can encourage impulse spending.",
            "Typically for smaller purchase amounts."
        ]
    ))

    # --- Scenario 2: Credit Card EMI ---
    cc_apr = _get_interest_rate(credit_score, "credit_card")
    cc_term = 12 # months
    cc_emi = _calculate_emi(amount, cc_apr, cc_term)
    cc_total_repayment = cc_emi * cc_term
    scenarios.append(Scenario(
        type="Credit Card EMI",
        effective_apr=cc_apr,
        total_repayment=cc_total_repayment.quantize(Decimal("0.01")),
        monthly_payment=cc_emi.quantize(Decimal("0.01")),
        term_months=cc_term,
        pros=[
            "Can be used for larger purchases.",
            "May offer rewards points or cashback.",
            "Builds credit history with the credit bureau."
        ],
        cons=[
            f"Interest rate can be high (est. {cc_apr}% APR).",
            "May involve processing fees.",
            "Requires an existing credit card with sufficient limit."
        ]
    ))

    # --- Scenario 3: Personal Loan ---
    pl_apr = _get_interest_rate(credit_score, "personal_loan")
    pl_term = 24 # months
    pl_emi = _calculate_emi(amount, pl_apr, pl_term)
    pl_total_repayment = pl_emi * pl_term
    scenarios.append(Scenario(
        type="Personal Loan",
        effective_apr=pl_apr,
        total_repayment=pl_total_repayment.quantize(Decimal("0.01")),
        monthly_payment=pl_emi.quantize(Decimal("0.01")),
        term_months=pl_term,
        pros=[
            f"Lower interest rates than credit cards (est. {pl_apr}% APR).",
            "Fixed monthly payments over a longer term.",
            "Good for consolidating debt or very large purchases."
        ],
        cons=[
            "Longer application and approval process.",
            "May have origination fees.",
            "Often requires a good credit score for approval."
        ]
    ))

    return scenarios