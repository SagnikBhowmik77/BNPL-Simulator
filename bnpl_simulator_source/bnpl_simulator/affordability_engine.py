#!/usr/bin/env python3
"""
Enhanced Affordability Engine with advanced features:
- Detailed affordability scoring with safe/borderline/dangerous classifications
- Return & Refund complexity simulation
- Debt spiral visualization data
- Social comparison mode
"""
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
from dataclasses import dataclass
from enum import Enum
from .models import User, LoanDB, InstallmentDB, LoanStatus, InstallmentStatus
from sqlalchemy.orm import Session
from sqlalchemy import func
import statistics
import logging

# Import cache functions from cache_utils module
from .cache_utils import get_cache_key, get_cached_data, set_cached_data

logger = logging.getLogger(__name__)

class AffordabilityLevel(str, Enum):
    SAFE = "SAFE"
    BORDERLINE = "BORDERLINE"
    DANGEROUS = "DANGEROUS"

class RefundType(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    NONE = "NONE"

@dataclass
class AffordabilityAnalysis:
    level: AffordabilityLevel
    score: int
    monthly_payment: Decimal
    debt_to_income_ratio: Decimal
    risk_factors: List[str]
    recommendations: List[str]

@dataclass
class RefundSimulation:
    refund_type: RefundType
    refund_amount: Decimal
    adjustment_method: str
    timeline_days: int
    complications: List[str]

@dataclass
class DebtSpiralData:
    timeline: List[Dict[str, Any]]
    total_cost_with_late_fees: Decimal
    months_to_recover: int
    worst_case_scenario: Dict[str, Any]

@dataclass
class SocialComparison:
    percentile_rank: int
    avg_credit_score: int
    avg_debt_load: Decimal
    avg_payment_timing: str
    benchmark_comparison: Dict[str, Any]

class EnhancedAffordabilityEngine:
    """Advanced affordability analysis engine."""
    
    def __init__(self):
        self.safe_dti_threshold = Decimal("0.20")  # 20% debt-to-income ratio
        self.borderline_dti_threshold = Decimal("0.35")  # 35% debt-to-income ratio
        self.late_fee_per_installment = Decimal("10.00")
        
    def analyze_affordability(self, user: User, purchase_amount: Decimal, 
                            desired_term_months: int = 3, db: Session = None) -> AffordabilityAnalysis:
        """Enhanced affordability analysis with detailed scoring."""
        
        # Calculate monthly income
        monthly_income = Decimal(user.annual_income) / 12
        
        # Calculate existing debt obligations
        existing_debt = self._calculate_existing_debt(user.user_id, db) if db else Decimal("0.0")
        
        # Calculate proposed monthly payment
        down_payment = purchase_amount * Decimal("0.25")
        remaining_balance = purchase_amount - down_payment
        monthly_payment = remaining_balance / desired_term_months
        
        # Calculate debt-to-income ratio
        total_monthly_obligations = existing_debt + monthly_payment
        dti_ratio = (total_monthly_obligations / monthly_income) * 100 if monthly_income > 0 else Decimal("100.0")
        
        # Calculate affordability score (0-100)
        score = self._calculate_affordability_score(user, dti_ratio, monthly_payment, existing_debt)
        
        # Determine affordability level
        if score >= 80:
            level = AffordabilityLevel.SAFE
        elif score >= 50:
            level = AffordabilityLevel.BORDERLINE
        else:
            level = AffordabilityLevel.DANGEROUS
        
        # Generate risk factors and recommendations
        risk_factors = self._identify_risk_factors(user, dti_ratio, score)
        recommendations = self._generate_recommendations(level, user, dti_ratio, score)
        
        return AffordabilityAnalysis(
            level=level,
            score=score,
            monthly_payment=monthly_payment,
            debt_to_income_ratio=dti_ratio,
            risk_factors=risk_factors,
            recommendations=recommendations
        )
    
    def simulate_refund_scenario(self, loan_id: str, refund_percentage: float = 1.0) -> RefundSimulation:
        """Simulate complex refund scenarios with BNPL complications."""
        
        # This would normally query the database, but for now we'll simulate
        # Convert float to Decimal safely
        refund_percentage_decimal = Decimal(str(refund_percentage))
        refund_amount = Decimal("100.00") * refund_percentage_decimal
        
        if refund_percentage == 1.0:
            refund_type = RefundType.FULL
            adjustment_method = "Credit to original payment method"
            timeline_days = 7
            complications = []
        elif refund_percentage > 0:
            refund_type = RefundType.PARTIAL
            adjustment_method = "Pro-rated credit to loan balance"
            timeline_days = 14
            complications = [
                "Partial refunds may not reduce monthly payments immediately",
                "Remaining balance still accrues interest/fees",
                "Merchant processing delays common"
            ]
        else:
            refund_type = RefundType.NONE
            adjustment_method = "No refund available"
            timeline_days = 0
            complications = ["BNPL terms often restrict refunds after payment processing"]
        
        return RefundSimulation(
            refund_type=refund_type,
            refund_amount=refund_amount,
            adjustment_method=adjustment_method,
            timeline_days=timeline_days,
            complications=complications
        )
    
    def generate_debt_spiral_data(self, user_id: str, initial_loan_amount: Decimal) -> DebtSpiralData:
        """Generate data for debt spiral visualization."""
        
        timeline = []
        current_balance = initial_loan_amount
        total_fees_accrued = Decimal("0.00")
        
        # Simulate 12 months of potential debt spiral (reduced for performance)
        for month in range(12):
            month_data = {
                "month": month + 1,
                "starting_balance": current_balance,
                "payment_made": Decimal("0.00"),
                "late_fees": Decimal("0.00"),
                "ending_balance": current_balance
            }
            
            # Simulate missed payment scenario
            if month % 3 == 0 and month > 0:  # Miss payment every 3rd month
                late_fees = self.late_fee_per_installment * 3  # 3 installments missed
                current_balance += late_fees
                total_fees_accrued += late_fees
                month_data["late_fees"] = late_fees
                month_data["ending_balance"] = current_balance
            else:
                # Make partial payment
                payment = min(current_balance * Decimal("0.10"), current_balance)
                current_balance -= payment
                month_data["payment_made"] = payment
                month_data["ending_balance"] = current_balance
            
            timeline.append(month_data)
            
            if current_balance <= 0:
                break
        
        # Calculate recovery timeline
        months_to_recover = len([m for m in timeline if m["ending_balance"] > initial_loan_amount])
        
        # Worst case scenario
        worst_case = {
            "max_balance": max(m["ending_balance"] for m in timeline),
            "total_fees": total_fees_accrued,
            "months_in_debt": len(timeline)
        }
        
        return DebtSpiralData(
            timeline=timeline,
            total_cost_with_late_fees=total_fees_accrued + initial_loan_amount,
            months_to_recover=months_to_recover,
            worst_case_scenario=worst_case
        )
    
    def get_social_comparison(self, user_id: str, db: Session) -> SocialComparison:
        """Get anonymized social comparison data."""
        
        # Get current user's data with optimized query
        try:
            current_user = db.query(User).filter(User.user_id == user_id).first()
            if not current_user:
                return SocialComparison(
                    percentile_rank=50,
                    avg_credit_score=650,
                    avg_debt_load=Decimal("0.00"),
                    avg_payment_timing="on time",
                    benchmark_comparison={}
                )
            
            # Use simulated benchmark data for performance and consistency
            # Based on typical BNPL user profiles
            simulated_avg_credit_score = 620
            simulated_avg_debt_load = Decimal("150.00")
            
            # Calculate percentile rank based on credit score distribution
            # Simulate a normal distribution around 620 with standard deviation of 100
            if current_user.credit_score >= 720:
                percentile_rank = 85  # Top 15%
            elif current_user.credit_score >= 620:
                percentile_rank = 65  # Top 35%
            elif current_user.credit_score >= 520:
                percentile_rank = 45  # Middle 45%
            elif current_user.credit_score >= 420:
                percentile_rank = 25  # Bottom 25%
            else:
                percentile_rank = 10  # Bottom 10%
            
            # Determine payment timing category
            if current_user.late_payments == 0:
                avg_payment_timing = "on time"
            elif current_user.late_payments < 3:
                avg_payment_timing = "occasionally late"
            else:
                avg_payment_timing = "frequently late"
            
            # Calculate user's debt load using optimized calculation
            user_debt = self._calculate_existing_debt(user_id, db)
            
            # Generate benchmark comparison
            benchmark_comparison = {
                "credit_score_vs_average": current_user.credit_score - simulated_avg_credit_score,
                "debt_load_vs_average": float(user_debt - simulated_avg_debt_load),
                "payment_timing": avg_payment_timing
            }
            
            return SocialComparison(
                percentile_rank=percentile_rank,
                avg_credit_score=simulated_avg_credit_score,
                avg_debt_load=simulated_avg_debt_load,
                avg_payment_timing=avg_payment_timing,
                benchmark_comparison=benchmark_comparison
            )
        except Exception as e:
            # Graceful fallback if database query fails
            return SocialComparison(
                percentile_rank=50,
                avg_credit_score=620,
                avg_debt_load=Decimal("150.00"),
                avg_payment_timing="on time",
                benchmark_comparison={
                    "credit_score_vs_average": 0,
                    "debt_load_vs_average": 0.0,
                    "payment_timing": "on time"
                }
            )
    
    def _calculate_existing_debt(self, user_id: str, db: Session = None) -> Decimal:
        """Calculate existing monthly debt obligations with optimized query."""
        # If no database session provided, return a simulated value
        if db is None:
            return Decimal("50.00")  # Simulated existing debt
        
        # Use cached data if available
        cache_key = get_cache_key(user_id, "existing_debt")
        cached_data = get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            # Optimized query to calculate outstanding debt
            # Use a single query with joins instead of loading all relationships
            from sqlalchemy import and_
            
            outstanding_debt = db.query(func.sum(InstallmentDB.amount)).filter(
                and_(
                    InstallmentDB.loan_id == LoanDB.loan_id,
                    LoanDB.user_id == user_id,
                    LoanDB.status.in_([LoanStatus.ACTIVE, LoanStatus.LATE]),
                    InstallmentDB.status.in_([InstallmentStatus.PENDING, InstallmentStatus.OVERDUE])
                )
            ).scalar() or Decimal("0.0")
            
            # Cache the result
            set_cached_data(cache_key, outstanding_debt)
            return outstanding_debt
            
        except Exception as e:
            # Log the error but return a safe default
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating existing debt for user {user_id}: {e}")
            return Decimal("0.0")
    
    def _calculate_affordability_score(self, user: User, dti_ratio: Decimal, 
                                     monthly_payment: Decimal, existing_debt: Decimal) -> int:
        """Calculate overall affordability score."""
        score = 100
        
        # Credit score impact
        if user.credit_score < 600:
            score -= 30
        elif user.credit_score < 700:
            score -= 15
        
        # Debt-to-income ratio impact
        if dti_ratio > 40:
            score -= 40
        elif dti_ratio > 25:
            score -= 20
        elif dti_ratio > 15:
            score -= 10
        
        # Existing debt impact
        if existing_debt > 200:
            score -= 15
        elif existing_debt > 100:
            score -= 5
        
        # Late payment history impact
        if user.late_payments > 5:
            score -= 25
        elif user.late_payments > 2:
            score -= 15
        elif user.late_payments > 0:
            score -= 5
        
        return max(0, min(100, score))
    
    def _identify_risk_factors(self, user: User, dti_ratio: Decimal, score: int) -> List[str]:
        """Identify specific risk factors for this user."""
        factors = []
        
        if user.credit_score < 600:
            factors.append(f"Low credit score ({user.credit_score}) increases risk")
        
        if dti_ratio > 35:
            factors.append(f"High debt-to-income ratio ({dti_ratio:.1f}%)")
        
        if user.late_payments > 0:
            factors.append(f"History of {user.late_payments} late payments")
        
        if score < 50:
            factors.append("Overall affordability score indicates high risk")
        
        return factors
    
    def _generate_recommendations(self, level: AffordabilityLevel, user: User, 
                                dti_ratio: Decimal, score: int) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        if level == AffordabilityLevel.SAFE:
            recommendations.append("✅ This purchase appears affordable based on your financial profile")
            recommendations.append("Consider setting up automatic payments to maintain good standing")
        
        elif level == AffordabilityLevel.BORDERLINE:
            recommendations.append("⚠️ This purchase is borderline affordable")
            recommendations.append("Consider a smaller purchase amount or longer payment term")
            recommendations.append("Build emergency savings before proceeding")
        
        else:  # DANGEROUS
            recommendations.append("❌ This purchase is not recommended at this time")
            recommendations.append("Focus on improving credit score and reducing existing debt")
            recommendations.append("Consider alternative payment methods or saving up")
        
        # Specific recommendations based on issues
        if user.credit_score < 600:
            recommendations.append("Work on improving your credit score before taking on new debt")
        
        if dti_ratio > 30:
            recommendations.append("Reduce existing debt obligations before new purchases")
        
        if user.late_payments > 0:
            recommendations.append("Establish consistent on-time payment history")
        
        return recommendations