# main.py
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager, contextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, OperationalError, TimeoutError
import logging
import time

from . import models
from .risk_engine import RiskEngine
from .data_loader import load_users_from_csv
from .database import engine, Base, get_db, SessionLocal, create_indexes
from .ml_model import train_and_save_model
from . import comparison_engine
from .affordability_engine import EnhancedAffordabilityEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# It's set to None at import time and will be populated during the startup event.
risk_engine: RiskEngine | None = None
LATE_FEE_PER_INSTALLMENT = Decimal("10.00") # Example fixed late fee per overdue installment
CONVENIENCE_FEE_PERCENTAGE = Decimal("0.02") # Example 2% convenience fee

# Import cache utilities
from .cache_utils import get_cache_key, get_cached_data, set_cached_data

# Create the FastAPI app
app = FastAPI(
    title="Buy Now Pay Later Simulator",
    description="A backend API to simulate BNPL loan approval and management with optimized performance.",
    lifespan=None
)

# Custom exception handlers for better error responses
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database error",
            "message": "The system is experiencing technical difficulties. Please try again later.",
            "details": "Database query failed due to heavy load or connection issues."
        }
    )

@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    logger.error(f"Operational error: {exc}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "Service temporarily unavailable",
            "message": "The database is temporarily overloaded. Please try again in a few moments.",
            "details": "Database connection timeout or resource exhaustion."
        }
    )

@app.exception_handler(TimeoutError)
async def timeout_error_handler(request: Request, exc: TimeoutError):
    logger.error(f"Query timeout: {exc}")
    return JSONResponse(
        status_code=504,
        content={
            "error": "Request timeout",
            "message": "The request took too long to process. Please try with smaller data or try again later.",
            "details": "Query execution exceeded maximum allowed time."
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Log the error for debugging
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request failed",
            "message": str(exc.detail) if isinstance(exc.detail, str) else "An error occurred",
            "status_code": exc.status_code
        }
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code to run on application startup ---
    logger.info("--- Application Startup ---")

    try:
        # 1. Create database tables
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine) # Create tables based on our models
        
        # 2. Create database indexes for optimization
        logger.info("Creating database indexes...")
        create_indexes()

        # 3. Populate DB with user data if it's empty
        db = SessionLocal()
        try:
            user_count = db.query(models.User).count()
            if user_count == 0:
                logger.info("Users table is empty. Populating from CSV...")
                users_to_create = load_users_from_csv()
                if users_to_create:
                    db.add_all(users_to_create)
                    db.commit()
                    logger.info(f"Loaded {len(users_to_create)} user profiles into the database.")
                else:
                    logger.warning("No users loaded from CSV - dataset may be empty or invalid")
            else:
                logger.info(f"Users table already populated with {user_count} users. Skipping data load.")
        except Exception as e:
            logger.error(f"Error populating user data: {e}")
            db.rollback()
        finally:
            db.close()

        # 4. Train the ML model and save it
        logger.info("Training ML model...")
        train_and_save_model()

        # 5. Initialize the Risk Engine. Now it can load the trained model.
        global risk_engine
        risk_engine = RiskEngine()
        logger.info("Risk engine initialized and ready.")

        logger.info("--- Application Startup Complete ---")
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

    yield # The application runs here

    # --- Code to run on application shutdown (optional) ---
    logger.info("--- Application Shutdown ---")

# Set the lifespan after defining it
app.router.lifespan_context = lifespan

# Add middleware to log requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    return response

@app.get("/")
def read_root():
    return {"message": "Welcome to the BNPL Simulator API! Navigate to /docs for the interactive documentation."}

@app.post("/checkout", response_model=models.CheckoutResponse, status_code=201)
def process_checkout(request: models.CheckoutRequest, db: Session = Depends(get_db)) -> models.CheckoutResponse:
    """
    Handles a new BNPL request from a user at checkout.
    Returns the new loan and any risk-based warnings.
    """
    # Ensure overdue statuses and late fees are updated before processing a new loan
    _check_and_update_overdue_installments(db)

    if risk_engine is None:
        raise HTTPException(status_code=503, detail="Risk engine is not yet available. Please wait a moment and try again.")

    # 1. Fetch User Data
    user = db.query(models.User).filter(models.User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # 2. Gather more data for the risk engine (user_profile_pydantic, outstanding_debt)
    # Calculate the user's total outstanding debt from all active loans
    outstanding_debt = _get_outstanding_debt(user.user_id, db)

    # 3. Call the Risk Engine with the updated data
    user_profile_pydantic = models.UserProfile.model_validate(user)
    decision = risk_engine.decide(
        user=user_profile_pydantic, purchase_amount=request.amount, outstanding_debt=outstanding_debt
    )

    
    if decision["decision"] == "DECLINED":
        raise HTTPException(status_code=400, detail={"message": "Loan application declined.", "reasons": decision.get("reasons", []), "warnings": decision.get("warnings", [])})

    # 4. If Approved, Create and Save the Loan to the database
    # For this example, we'll use a fixed 4-installment plan with 25% down payment.
    down_payment = request.amount * Decimal("0.25")
    remaining_balance = request.amount - down_payment
    installment_amount = remaining_balance / 3

    
    # Handle Teen Mode specific logic for virtual balance
    if user.is_teen_mode:
        if user.virtual_balance < down_payment:
            # This check should ideally be caught by the risk engine, but double-check
            raise HTTPException(status_code=400, detail="Insufficient virtual balance for down payment in Teen Mode.")
        user.virtual_balance -= down_payment # Deduct from virtual balance
        convenience_fee = Decimal("0.0")  # No real fees in teen mode
        db.add(user) # Persist virtual balance change.
    else:
        # Transparency Layer: Calculate convenience fee
        convenience_fee = request.amount * CONVENIENCE_FEE_PERCENTAGE if request.apply_convenience_fee else Decimal("0.0")
    

    db_loan = models.LoanDB(
        loan_id=f"loan-{uuid.uuid4()}",
        user_id=request.user_id,
        merchant_id=request.merchant_id,
        total_amount=request.amount, # Pass Decimal directly
        down_payment=down_payment,   # Pass Decimal directly
        convenience_fee=convenience_fee # Apply calculated convenience fee
    )
    db.add(db_loan)

    for i in range(3): # Create 3 installments
        db_installment = models.InstallmentDB(
            installment_number=i + 1,
            due_date=date.today() + timedelta(weeks=2 * (i + 1)),
            amount=installment_amount, # Pass Decimal directly
            loan_id=db_loan.loan_id
        )
        db.add(db_installment)

    db.commit()
    db.refresh(db_loan)
    db.refresh(user) # Refresh user to reflect virtual balance change.

    # 5. Return the newly created loan details with any warnings
    return models.CheckoutResponse(
        loan_details=db_loan,
        warnings=decision.get("warnings", [])
    )

def _get_outstanding_debt(user_id: str, db: Session) -> Decimal:
    """Calculates the total outstanding debt for a given user with optimized query."""
    # Use cached data if available
    cache_key = get_cache_key(user_id, "outstanding_debt")
    cached_data = get_cached_data(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        # Optimized query using joins instead of loading all relationships
        from sqlalchemy import and_
        
        outstanding_debt = db.query(func.sum(models.InstallmentDB.amount)).filter(
            and_(
                models.InstallmentDB.loan_id == models.LoanDB.loan_id,
                models.LoanDB.user_id == user_id,
                models.LoanDB.status.in_([models.LoanStatus.ACTIVE, models.LoanStatus.LATE]),
                models.InstallmentDB.status.in_([models.InstallmentStatus.PENDING, models.InstallmentStatus.OVERDUE])
            )
        ).scalar() or Decimal("0.0")
        
        # Cache the result
        set_cached_data(cache_key, outstanding_debt)
        return outstanding_debt
        
    except Exception as e:
        logger.error(f"Error calculating outstanding debt for user {user_id}: {e}")
        return Decimal("0.0")

def _check_and_update_overdue_installments(db: Session):
    """
    Checks all active loans for overdue installments and updates their status,
    accrues late fees, and updates loan status.
    This function should ideally be run periodically by a background task,
    but for demonstration, it's called on relevant API endpoints to ensure data freshness.
    """
    today = date.today()
    
    # Fetch all loans that are not yet paid off
    loans_to_check = db.query(models.LoanDB).filter(models.LoanDB.status != models.LoanStatus.PAID_OFF).all() # Use models.LoanDB

    for loan in loans_to_check:
        has_overdue_installments = False
        
        for installment in loan.installments:
            if installment.status == models.InstallmentStatus.PENDING and installment.due_date < today: # Use models.InstallmentStatus
                # Installment has become overdue
                installment.status = models.InstallmentStatus.OVERDUE
                if not installment.late_fee_applied:
                    loan.late_fees_accrued += LATE_FEE_PER_INSTALLMENT
                    installment.late_fee_applied = True
                    # This is a new late payment. Increment user's count.
                    db.query(models.User).filter(models.User.user_id == loan.user_id).update(
                        {models.User.late_payments: models.User.late_payments + 1}, synchronize_session=False
                    )
                has_overdue_installments = True
            elif installment.status == models.InstallmentStatus.OVERDUE and not installment.late_fee_applied:
                # Installment was already overdue, but fee wasn't applied (e.g., new logic deployment)
                loan.late_fees_accrued += LATE_FEE_PER_INSTALLMENT
                installment.late_fee_applied = True
                has_overdue_installments = True

        # Update loan status based on whether it has any overdue installments
        # Note: PAID_OFF loans are filtered out at the start, so we don't need to worry about reverting them.
        if has_overdue_installments: # If any installment is overdue, the loan is LATE
            if loan.status != models.LoanStatus.LATE:
                loan.status = models.LoanStatus.LATE # Use models.LoanStatus
        else:
            # No overdue installments. Now determine if it's fully paid or should revert to ACTIVE.
            # Check if there are any remaining unpaid installments (PENDING or OVERDUE)
            unpaid_installments_count = db.query(models.InstallmentDB).filter(
                models.InstallmentDB.loan_id == loan.loan_id,
                models.InstallmentDB.status.in_([models.InstallmentStatus.PENDING, models.InstallmentStatus.OVERDUE])
            ).count()

            if unpaid_installments_count == 0:
                # All installments are paid. Loan should be PAID_OFF if it's not already.
                if loan.status != models.LoanStatus.PAID_OFF: # Only update if not already PAID_OFF
                    loan.status = models.LoanStatus.PAID_OFF
                    # Increment user's completed loans count (using models.User for consistency)
                    db.query(models.User).filter(models.User.user_id == loan.user_id).update(
                        {models.User.completed_loans: models.User.completed_loans + 1}, synchronize_session=False
                    )
            elif loan.status == models.LoanStatus.LATE:
                # No overdue installments, but still pending ones, and it was LATE. Revert to ACTIVE.
                unpaid_installments_count = db.query(models.InstallmentDB).filter(
                    models.InstallmentDB.loan_id == loan.loan_id,
                    models.InstallmentDB.status.in_([models.InstallmentStatus.PENDING, models.InstallmentStatus.OVERDUE])
                ).count()
                if unpaid_installments_count > 0:
                    loan.status = models.LoanStatus.ACTIVE
    db.commit()

@app.post("/loans/{loan_id}/installments/{installment_number}/pay", response_model=models.Loan)
def pay_installment(loan_id: str, installment_number: int, db: Session = Depends(get_db)):
    """Simulates a user paying a specific installment of a loan."""
    # Find the specific installment
    db_installment = db.query(models.InstallmentDB).filter(
        models.InstallmentDB.loan_id == loan_id,
        models.InstallmentDB.installment_number == installment_number
    ).first()

    if not db_installment:
        raise HTTPException(status_code=404, detail="Installment not found.")

    if db_installment.status == models.InstallmentStatus.PAID:
        raise HTTPException(status_code=400, detail="This installment has already been paid.")

    # Ensure overdue statuses and late fees are updated before processing payment.
    # This is important if the installment just became overdue before the user paid it,
    # so the late fee is applied before the status changes to PAID.
    _check_and_update_overdue_installments(db)
    # Update the installment status
    db_installment.status = models.InstallmentStatus.PAID

    db.flush() # Make the installment status change visible for the next query
    # Check if all installments for this loan are now paid
    unpaid_installments_count = db.query(models.InstallmentDB).filter(
        models.InstallmentDB.loan_id == loan_id,
        models.InstallmentDB.status != models.InstallmentStatus.PAID
    ).count()

    if unpaid_installments_count == 0:
        db_loan = db.query(models.LoanDB).filter(models.LoanDB.loan_id == loan_id).first()
        if db_loan and db_loan.status != models.LoanStatus.PAID_OFF: # Use models.LoanStatus
            db_loan.status = models.LoanStatus.PAID_OFF # Use models.LoanStatus
            # Increment user's completed loans count (using models.User for consistency)
            db.query(models.User).filter(models.User.user_id == db_loan.user_id).update(
                {models.User.completed_loans: models.User.completed_loans + 1}, synchronize_session=False # Use models.User
            )

    db.commit()
    # Return the updated loan object
    updated_loan = db.query(models.LoanDB).filter(models.LoanDB.loan_id == loan_id).first()
    return updated_loan

@app.get("/users/{user_id}/obligations", response_model=List[models.Loan])
def get_user_obligations(user_id: str, db: Session = Depends(get_db)):
    """
    Shows a user's cumulative obligations by returning all their active loans.
    This helps visualize how multiple BNPL purchases stack up.
    """
    # Ensure statuses are up-to-date before returning data
    _check_and_update_overdue_installments(db)

    active_user_loans = db.query(models.LoanDB).filter(
        models.LoanDB.user_id == user_id,
        models.LoanDB.status.in_([models.LoanStatus.ACTIVE, models.LoanStatus.LATE])
    ).all()

    if not active_user_loans: # If no active loans, check if user exists
        # Check if user exists at all to provide a better error message
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
    
    return active_user_loans

def _calculate_health_score(user_id: str, db: Session) -> models.UserHealthScore:
    """Calculates a gamified 'BNPL Health Score' for a user."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first() # Use models.User
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Ensure user stats are up-to-date by running the check function
    _check_and_update_overdue_installments(db)
    # The user object in the current session might be stale after the update. Refresh it.
    db.refresh(user)

    # --- Scoring Logic ---
    score = 500  # Base score
    positive_factors = []
    negative_factors = []

    # Factor 1: Completed Loans (Big positive impact)
    score += user.completed_loans * 25
    if user.completed_loans > 0:
        positive_factors.append(f"Successfully paid off {user.completed_loans} loan(s).")

    # Factor 2: Past Late Payments (Big negative impact)
    score -= user.late_payments * 40
    if user.late_payments > 0:
        negative_factors.append(f"History of {user.late_payments} late payment(s).")
    elif user.completed_loans > 0:
        positive_factors.append("Excellent record of on-time payments.")
    

    # Factor 3: Current Loan Status
    user_loans = db.query(models.LoanDB).filter(models.LoanDB.user_id == user.user_id).all()
    total_paid_installments = 0
    current_overdue_count = 0
    current_overdue_count = 0 # Count currently overdue installments
    for loan in user_loans:
        for inst in loan.installments:
            if inst.status == models.InstallmentStatus.PAID:
                total_paid_installments += 1
            if inst.status == models.InstallmentStatus.OVERDUE:
                current_overdue_count += 1

    # Small reward for each paid installment
    score += total_paid_installments * 2 # Reward for each paid installment
    
    # Penalty for currently overdue items
    score -= current_overdue_count * 20
    if current_overdue_count > 0:
        negative_factors.append(f"{current_overdue_count} installment(s) currently overdue.")

    # Normalize score to be within a range (e.g., 300-850)
    score = max(300, min(850, score))

    # --- Rating Logic ---
    if score >= 800: rating = "Excellent"
    elif score >= 740: rating = "Very Good"
    elif score >= 670: rating = "Good"
    elif score >= 580: rating = "Fair"
    else: rating = "Poor"

    if not positive_factors:
        positive_factors.append("Start building a positive history by paying on time.")
    if not negative_factors and user.completed_loans > 0:
        negative_factors.append("No negative factors found. Keep it up!")
    elif not negative_factors:
        negative_factors.append("No history yet.")

    return models.UserHealthScore(
        user_id=user_id,
        score=score,
        rating=rating,
        positive_factors=positive_factors,
        negative_factors=negative_factors,
    )

@app.get("/users/{user_id}", response_model=models.UserProfile)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Returns the complete profile of a user.
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return models.UserProfile.model_validate(user)

@app.get("/users/{user_id}/health-score", response_model=models.UserHealthScore)
def get_health_score(user_id: str, db: Session = Depends(get_db)):
    """
    Calculates and returns a dynamic, gamified 'BNPL Health Score' based on
    the user's repayment behavior and history within the simulator.
    """
    return _calculate_health_score(user_id, db)

@app.post("/compare-scenarios", response_model=models.ComparisonResponse)
def get_scenario_comparison(comparison_request: models.ComparisonRequest, db: Session = Depends(get_db)):
    """
    Compares BNPL vs. Credit Card EMI vs. a Personal Loan for a given purchase.
    Shows effective APR, total repayment, and risk exposure side-by-side.
    """
    scenarios = comparison_engine.generate_comparison(comparison_request, db)
    return models.ComparisonResponse(scenarios=scenarios)

# --- New Endpoints for Stress Testing and Teen/Parental Mode ---

class StressEventUpdateRequest(BaseModel):
    event_type: models.StressEventType

@app.put("/users/{user_id}/stress-event", response_model=models.UserProfile)
def update_user_stress_event(user_id: str, request: StressEventUpdateRequest, db: Session = Depends(get_db)):
    """
    Updates a user's current stress event for simulation purposes.
    Setting event_type to NONE clears any active stress event.
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.current_stress_event = request.event_type
    db.commit()
    db.refresh(user) # Refresh the user object to reflect changes
    return models.UserProfile.model_validate(user)

@app.put("/users/{user_id}/teen-mode", response_model=models.UserProfile)
def update_user_teen_mode(user_id: str, request: models.TeenModeUpdateRequest, db: Session = Depends(get_db)):
    """
    Toggles teen mode for a user and optionally sets their virtual balance.
    If is_teen_mode is set to True, virtual_balance must be provided.
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_teen_mode = request.is_teen_mode
    if request.is_teen_mode:
        if request.virtual_balance is None:
            raise HTTPException(status_code=400, detail="virtual_balance must be provided when enabling teen mode.")
        user.virtual_balance = request.virtual_balance
    else:
        # Optionally reset virtual balance when teen mode is disabled
        user.virtual_balance = Decimal("0.0")

    db.commit()
    db.refresh(user) # Refresh the user object to reflect changes
    return models.UserProfile.model_validate(user)

# --- AI-Powered Affordability Advisor Endpoint ---

@app.post("/affordability-advice", response_model=models.AffordabilityAdviceResponse)
def get_affordability_advice(request: models.AffordabilityAdviceRequest, db: Session = Depends(get_db)):
    """
    Provides AI-powered advice on the affordability of a potential BNPL purchase
    for a given user.
    """
    user = db.query(models.User).filter(models.User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Ensure user stats are up-to-date
    _check_and_update_overdue_installments(db)
    db.refresh(user) # Refresh user to get latest stats

    user_profile_pydantic = models.UserProfile.model_validate(user) # Use models.UserProfile
    outstanding_debt = _get_outstanding_debt(user.user_id, db)

    # Initial assessment using the risk engine
    initial_decision = risk_engine.decide(
        user=user_profile_pydantic,
        purchase_amount=request.purchase_amount,
        outstanding_debt=outstanding_debt
    )

    affordability_score = 100 # Base score
    recommended_term_months = 3 # Default for BNPL
    estimated_monthly_payment = request.purchase_amount / 3 # Default for 3 installments
    advice_message = "Based on your profile, this purchase seems manageable."
    warnings = initial_decision.get("warnings", [])

    if initial_decision["decision"] == "DECLINED":
        affordability_score = 20 # Very low
        advice_message = "This purchase is currently not advisable. " + " ".join(initial_decision["reasons"])
        warnings.extend(initial_decision["reasons"])
    else:
        # If approved, refine affordability score and advice
        # Factors influencing affordability:
        # 1. Credit Score: Higher is better
        affordability_score += (user.credit_score - 500) // 10 # Scale credit score impact

        # 2. Income vs. Purchase Amount
        monthly_income = Decimal(user.annual_income) / 12
        if request.purchase_amount > monthly_income * Decimal("0.5"): # Purchase > 50% of monthly income
            affordability_score -= 20
            warnings.append("Purchase amount is high relative to your monthly income.")
        elif request.purchase_amount < monthly_income * Decimal("0.1"): # Purchase < 10% of monthly income
            affordability_score += 10

        # 3. Existing Debt Load
        if outstanding_debt > Decimal("0.0"):
            debt_to_income_ratio = outstanding_debt / monthly_income if monthly_income > 0 else Decimal("100.0")
            if debt_to_income_ratio > Decimal("0.5"): # High debt-to-income
                affordability_score -= 30
                warnings.append("You have significant outstanding debt. Consider reducing it before new purchases.")
            elif debt_to_income_ratio > Decimal("0.2"):
                affordability_score -= 10
                warnings.append("You have some outstanding debt. Manage it carefully.")

        # 4. Past Payment History
        if user.late_payments > 0:
            affordability_score -= user.late_payments * 5
            warnings.append(f"Your history includes {user.late_payments} late payment(s).")
        if user.completed_loans > 0:
            affordability_score += user.completed_loans * 3

        # 5. Stress Events
        if user.current_stress_event == models.StressEventType.JOB_LOSS: # Use models.StressEventType
            affordability_score -= 50
            warnings.append("Active 'Job Loss' event makes new debt highly risky.")
        elif user.current_stress_event == models.StressEventType.MEDICAL_EXPENSE: # Use models.StressEventType
            affordability_score -= 20
            warnings.append("Active 'Medical Expense' event suggests caution with new debt.")
        elif user.current_stress_event == models.StressEventType.DELAYED_SALARY: # Use models.StressEventType
            affordability_score -= 10
            warnings.append("Active 'Delayed Salary' event suggests caution with new debt.")

        # Normalize affordability score
        affordability_score = max(0, min(100, affordability_score))

        # For BNPL, the standard is 25% down, 3 installments over 6 weeks (approx 1.5 months, round to 2)
        recommended_term_months = 2 # Fixed for standard BNPL
        estimated_monthly_payment = (request.purchase_amount * Decimal("0.75")) / Decimal("1.5") # Remaining balance / 1.5 months

        if affordability_score < 50:
            advice_message = "This purchase might strain your finances. Consider a smaller amount or saving up first."
        elif affordability_score < 75:
            advice_message = "This purchase is manageable, but keep an eye on your budget."
        else:
            advice_message = "This purchase appears well within your affordability."

    return models.AffordabilityAdviceResponse(
        user_id=request.user_id,
        affordability_score=affordability_score,
        recommended_term_months=recommended_term_months,
        estimated_monthly_payment=estimated_monthly_payment.quantize(Decimal("0.01")),
        advice_message=advice_message,
        warnings=warnings
    )

# --- Enhanced Affordability Advisor with Advanced Features ---

@app.post("/enhanced-affordability", response_model=models.EnhancedAffordabilityResponse)
def get_enhanced_affordability(request: models.EnhancedAffordabilityRequest, db: Session = Depends(get_db)):
    """
    Provides enhanced affordability analysis with detailed scoring and recommendations.
    Returns SAFE/BORDERLINE/DANGEROUS classification with specific risk factors.
    """
    user = db.query(models.User).filter(models.User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Ensure user stats are up-to-date
    _check_and_update_overdue_installments(db)
    db.refresh(user)

    # Initialize enhanced affordability engine
    affordability_engine = EnhancedAffordabilityEngine()
    
    # Perform enhanced analysis
    analysis = affordability_engine.analyze_affordability(
        user=user,
        purchase_amount=request.purchase_amount,
        desired_term_months=request.desired_term_months,
        db=db
    )

    return models.EnhancedAffordabilityResponse(
        affordability_level=analysis.level.value,
        affordability_score=analysis.score,
        monthly_payment=analysis.monthly_payment,
        debt_to_income_ratio=float(analysis.debt_to_income_ratio),
        risk_factors=analysis.risk_factors,
        recommendations=analysis.recommendations
    )

# --- Return & Refund Complexity Simulation ---

@app.post("/refund-simulation", response_model=models.RefundSimulationResponse)
def simulate_refund(request: models.RefundSimulationRequest, db: Session = Depends(get_db)):
    """
    Simulates complex refund scenarios with BNPL complications.
    Shows how refunds interact with BNPL terms and potential delays.
    """
    # Check if loan exists
    loan = db.query(models.LoanDB).filter(models.LoanDB.loan_id == request.loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found.")

    # Initialize enhanced affordability engine for refund simulation
    affordability_engine = EnhancedAffordabilityEngine()
    
    # Simulate refund scenario
    # Convert percentage (0-100) to decimal (0.0-1.0)
    refund_percentage_decimal = float(request.refund_percentage) / 100.0
    refund_simulation = affordability_engine.simulate_refund_scenario(
        loan_id=request.loan_id,
        refund_percentage=refund_percentage_decimal
    )

    return models.RefundSimulationResponse(
        refund_type=refund_simulation.refund_type.value,
        refund_amount=refund_simulation.refund_amount,
        adjustment_method=refund_simulation.adjustment_method,
        timeline_days=refund_simulation.timeline_days,
        complications=refund_simulation.complications
    )

# --- Debt Spiral Visualization ---

@app.post("/debt-spiral", response_model=models.DebtSpiralResponse)
def get_debt_spiral_data(request: models.DebtSpiralRequest, db: Session = Depends(get_db)):
    """
    Generates data for debt spiral visualization.
    Shows how small missed payments can snowball into larger debt over time.
    """
    user = db.query(models.User).filter(models.User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Initialize enhanced affordability engine
    affordability_engine = EnhancedAffordabilityEngine()
    
    # Generate debt spiral data
    debt_spiral = affordability_engine.generate_debt_spiral_data(
        user_id=request.user_id,
        initial_loan_amount=request.initial_loan_amount
    )

    return models.DebtSpiralResponse(
        timeline=debt_spiral.timeline,
        total_cost_with_late_fees=debt_spiral.total_cost_with_late_fees,
        months_to_recover=debt_spiral.months_to_recover,
        worst_case_scenario=debt_spiral.worst_case_scenario
    )

# --- Social Comparison Mode ---

@app.post("/social-comparison", response_model=models.SocialComparisonResponse)
def get_social_comparison(request: models.SocialComparisonRequest, db: Session = Depends(get_db)):
    """
    Provides anonymized social comparison data.
    Allows users to benchmark their BNPL usage against average consumer data.
    """
    user = db.query(models.User).filter(models.User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Initialize enhanced affordability engine
    affordability_engine = EnhancedAffordabilityEngine()
    
    # Get social comparison data
    comparison = affordability_engine.get_social_comparison(
        user_id=request.user_id,
        db=db
    )

    return models.SocialComparisonResponse(
        percentile_rank=comparison.percentile_rank,
        avg_credit_score=comparison.avg_credit_score,
        avg_debt_load=comparison.avg_debt_load,
        avg_payment_timing=comparison.avg_payment_timing,
        benchmark_comparison=comparison.benchmark_comparison
    )


# --- Late Fee Simulation for Demo ---

@app.post("/loans/{loan_id}/simulate-late-fee", response_model=models.Loan)
def simulate_late_fee(loan_id: str, db: Session = Depends(get_db)):
    """
    Simulate applying late fees to a loan for demonstration purposes.
    This is for demo/testing only - not a real banking operation.
    """
    # Get the loan from database
    loan = db.query(models.LoanDB).filter(models.LoanDB.loan_id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Apply late fees (₹10 per installment)
    late_fee_per_installment = Decimal("10.00")
    total_late_fees = late_fee_per_installment * len(loan.installments)
    
    # Update loan with late fees
    loan.late_fees_accrued += total_late_fees
    loan.status = models.LoanStatus.LATE
    
    # Mark some installments as overdue for demonstration
    for i, installment in enumerate(loan.installments):
        if i % 2 == 0 and installment.status == models.InstallmentStatus.PENDING:
            installment.status = models.InstallmentStatus.OVERDUE
            installment.late_fee = late_fee_per_installment
    
    db.commit()
    db.refresh(loan)
    
    return loan
