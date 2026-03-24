# models.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, Date, Enum as SQLAlchemyEnum, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from .database import Base

# Enums for status fields to ensure data consistency
class LoanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAID_OFF = "PAID_OFF"
    LATE = "LATE"
    DEFAULT = "DEFAULT"

class InstallmentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    OVERDUE = "OVERDUE"

class StressEventType(str, Enum):
    """Types of unexpected events for stress testing."""
    NONE = "NONE"
    JOB_LOSS = "JOB_LOSS"
    MEDICAL_EXPENSE = "MEDICAL_EXPENSE"
    DELAYED_SALARY = "DELAYED_SALARY"

# --- Pydantic Models for API Data Transfer (Schemas) ---

class Installment(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Enable ORM mode for Pydantic v2
    installment_number: int
    due_date: date
    amount: Decimal
    status: InstallmentStatus = InstallmentStatus.PENDING

class Loan(BaseModel):
    loan_id: str
    model_config = ConfigDict(from_attributes=True) # Enable ORM mode for Pydantic v2
    user_id: str
    merchant_id: str
    total_amount: Decimal
    down_payment: Decimal
    status: LoanStatus = LoanStatus.ACTIVE
    convenience_fee: Decimal = Decimal("0.0") # For Transparency Layer
    installments: List[Installment]
    late_fees_accrued: Decimal = Decimal("0.0")

class UserHealthScore(BaseModel):
    user_id: str
    score: int
    rating: str
    positive_factors: List[str]
    negative_factors: List[str]

class CheckoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    loan_details: Loan
    warnings: List[str] = []

class ComparisonRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    purchase_amount: Decimal
    user_id: Optional[str] = None # To get user-specific rates

class Scenario(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str # "BNPL", "Credit Card EMI", "Personal Loan"
    effective_apr: float
    total_repayment: Decimal
    monthly_payment: Decimal
    term_months: int
    pros: List[str]
    cons: List[str]

class ComparisonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    scenarios: List[Scenario]


class UserProfile(BaseModel):
    user_id: str
    credit_score: int
    completed_loans: int = 0
    late_payments: int = 0
    # New fields from the dataset
    age: int
    gender: str
    annual_income: float
    purchase_category: str
    device_type: str
    connection_type: str
    checkout_time_seconds: int
    browser: str
    # New fields for Stress Testing and Teen/Parental Mode
    current_stress_event: Optional[StressEventType] = StressEventType.NONE
    is_teen_mode: bool = False
    virtual_balance: Decimal = Decimal("0.0")

    class Config:
        from_attributes = True

# --- SQLAlchemy Models for Database Tables ---

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    credit_score = Column(Integer)
    age = Column(Integer)
    gender = Column(String)
    annual_income = Column(Float)
    purchase_category = Column(String)
    device_type = Column(String)
    connection_type = Column(String)
    checkout_time_seconds = Column(Integer)
    browser = Column(String)

    # These fields are for the simulation, not loaded from CSV initially
    completed_loans = Column(Integer, default=0)
    late_payments = Column(Integer, default=0)
    # New fields for Stress Testing and Teen/Parental Mode
    current_stress_event = Column(SQLAlchemyEnum(StressEventType), default=StressEventType.NONE)
    is_teen_mode = Column(Boolean, default=False)
    virtual_balance = Column(Numeric(10, 2), default=0.0)
    parent_user_id = Column(String, ForeignKey("users.user_id"), nullable=True) # Self-referencing foreign key

    # Relationships for parental mode
    parent = relationship("User", remote_side=[user_id], back_populates="children")
    children = relationship("User", back_populates="parent", foreign_keys=[parent_user_id])

    loans = relationship("LoanDB", back_populates="owner")

class LoanDB(Base):
    __tablename__ = "loans"
    loan_id = Column(String, primary_key=True, index=True)
    merchant_id = Column(String)
    total_amount = Column(Numeric(10, 2))
    down_payment = Column(Numeric(10, 2))
    convenience_fee = Column(Numeric(10, 2), default=0.0) # For Transparency Layer
    status = Column(SQLAlchemyEnum(LoanStatus), default=LoanStatus.ACTIVE)
    late_fees_accrued = Column(Numeric(10, 2), default=0.0)

    user_id = Column(String, ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="loans")

    installments = relationship("InstallmentDB", back_populates="loan", lazy="joined")

class InstallmentDB(Base):
    __tablename__ = "installments"
    id = Column(Integer, primary_key=True, index=True)
    installment_number = Column(Integer)
    due_date = Column(Date)
    amount = Column(Numeric(10, 2))
    status = Column(SQLAlchemyEnum(InstallmentStatus), default=InstallmentStatus.PENDING)

    loan_id = Column(String, ForeignKey("loans.loan_id"))
    loan = relationship("LoanDB", back_populates="installments")
    late_fee_applied = Column(Boolean, default=False)

# --- Pydantic Models for AI-Powered Affordability Advisor ---

class AffordabilityAdviceRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    purchase_amount: Decimal
    desired_term_months: Optional[int] = None # User might specify a desired term

class AffordabilityAdviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    affordability_score: int # A score indicating how affordable the loan is
    recommended_term_months: int
    estimated_monthly_payment: Decimal
    advice_message: str
    warnings: List[str] = []

class TeenModeUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    is_teen_mode: bool
    virtual_balance: Optional[Decimal] = None

class CheckoutRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    merchant_id: str
    amount: Decimal
    # Transparency Layer: Optional field to indicate if convenience fee should be applied
    apply_convenience_fee: bool = True

# --- Enhanced Models for Advanced Features ---

class EnhancedAffordabilityRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    purchase_amount: Decimal
    desired_term_months: Optional[int] = 3

class EnhancedAffordabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    affordability_level: str  # SAFE, BORDERLINE, DANGEROUS
    affordability_score: int
    monthly_payment: Decimal
    debt_to_income_ratio: float
    risk_factors: List[str]
    recommendations: List[str]

class RefundSimulationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    loan_id: str
    refund_percentage: float = 1.0  # 0.0 to 1.0

class RefundSimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    refund_type: str  # FULL, PARTIAL, NONE
    refund_amount: Decimal
    adjustment_method: str
    timeline_days: int
    complications: List[str]

class DebtSpiralRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    initial_loan_amount: Decimal

class DebtSpiralResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    timeline: List[Dict[str, Any]]
    total_cost_with_late_fees: Decimal
    months_to_recover: int
    worst_case_scenario: Dict[str, Any]

class SocialComparisonRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str

class SocialComparisonResponse(BaseModel):
    percentile_rank: int
    avg_credit_score: int
    avg_debt_load: Decimal
    avg_payment_timing: str
    benchmark_comparison: Dict
