# Stress Event Impact Analysis

## How Stress Events Affect BNPL Decisions

The BNPL simulator includes three types of stress events that significantly impact loan approval decisions and affordability assessments:

### 1. **JOB_LOSS** - Most Severe Impact
**Impact**: **Automatic Decline**
- **When**: Any purchase request during active job loss event
- **Why**: Complete income uncertainty makes any new debt too risky
- **Output Change**: Loan application will be **DECLINED** with reason: "Loan declined due to active 'Job Loss' stress event. Focus on essential expenses."

### 2. **MEDICAL_EXPENSE** - Moderate Impact  
**Impact**: **Warning + Risk Factor Increase**
- **When**: Purchase request during active medical expense event
- **Why**: Medical expenses create financial strain, increasing default risk
- **Output Changes**:
  - Adds warning: "Active 'Medical Expense' stress event detected. Consider if this purchase is essential."
  - In affordability engine: Increases perceived risk by 20% (MEDICAL_EXPENSE_RISK_FACTOR = 1.2)
  - May trigger higher affordability score penalties

### 3. **DELAYED_SALARY** - Conditional Impact
**Impact**: **Warning + Conditional Decline**
- **When**: Purchase request during delayed salary event
- **Why**: Temporary cash flow issues affect payment ability
- **Output Changes**:
  - Always adds warning: "Active 'Delayed Salary' stress event detected. Ensure you can meet upcoming payments."
  - **If purchase > 50% of monthly income**: Adds stronger warning about delaying purchase
  - May trigger affordability warnings or borderline classification

## Specific Scenarios Where You'll See Changes

### Scenario 1: Job Loss Event
```python
# User profile with job loss stress event
user.current_stress_event = StressEventType.JOB_LOSS

# ANY purchase amount will be declined
purchase_amount = Decimal("50.00")  # Even small purchases
# Result: DECLINED - "Loan declined due to active 'Job Loss' stress event"
```

### Scenario 2: Medical Expense + High Purchase
```python
# User with medical expense and high purchase relative to income
user.current_stress_event = StressEventType.MEDICAL_EXPENSE
user.annual_income = 40000  # $3,333/month
purchase_amount = Decimal("1500.00")  # High purchase

# Result: 
# - Warning about medical expense
# - Affordability score reduced by 20% risk factor
# - May trigger DECLINE if other risk factors present
```

### Scenario 3: Delayed Salary + Large Purchase
```python
# User with delayed salary and large purchase
user.current_stress_event = StressEventType.DELAYED_SALARY
user.annual_income = 36000  # $3,000/month
purchase_amount = Decimal("2000.00")  # >50% of monthly income

# Result:
# - Warning about delayed salary
# - Additional warning: "Purchase amount $2,000.00 is significant given your delayed salary event"
# - Affordability level likely BORDERLINE or DANGEROUS
```

## API Endpoints That Show Stress Event Impact

### 1. **/checkout** - Loan Approval
- **Direct Impact**: Job loss = automatic decline
- **Indirect Impact**: Medical expense/delayed salary = warnings and risk assessment changes

### 2. **/affordability-advice** - Affordability Assessment
- **Medical Expense**: Reduces affordability score by 20%
- **Delayed Salary**: Triggers warnings if purchase > 50% of monthly income
- **Job Loss**: May trigger "DANGEROUS" affordability level

### 3. **/enhanced-affordability** - Detailed Analysis
- **All stress events**: Affect affordability score calculation
- **Risk factors**: Include stress event warnings
- **Recommendations**: Tailored based on stress event type

### 4. **/users/{user_id}/stress-event** - Update Stress Event
- **Usage**: `PUT /users/user123/stress-event` with body `{"event_type": "JOB_LOSS"}`
- **Immediate Effect**: Changes all subsequent loan decisions for that user

## Testing Stress Event Impact

To see stress events in action:

1. **Set a stress event**:
```bash
curl -X PUT "http://localhost:8001/users/user123/stress-event" \
  -H "Content-Type: application/json" \
  -d '{"event_type": "JOB_LOSS"}'
```

2. **Try a loan application**:
```bash
curl -X POST "http://localhost:8001/checkout" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "merchant_id": "merchant1", "amount": 100.0}'
```

3. **Expected Result**: DECLINED with job loss reason

## Key Thresholds and Values

```python
# From risk_engine.py
JOB_LOSS_DECLINE_THRESHOLD = Decimal("0.0")  # Any purchase declined
MEDICAL_EXPENSE_RISK_FACTOR = Decimal("1.2")  # 20% risk increase
DELAYED_SALARY_WARNING_THRESHOLD = Decimal("0.5")  # 50% of monthly income

# From affordability_engine.py
safe_dti_threshold = Decimal("0.20")  # 20% debt-to-income ratio
borderline_dti_threshold = Decimal("0.35")  # 35% debt-to-income ratio
```

## Real-World Simulation Benefits

These stress events help simulate real-world scenarios where:
- **Job loss** makes any new debt unaffordable
- **Medical expenses** create financial strain affecting payment ability  
- **Delayed salary** creates temporary cash flow issues

This makes the BNPL simulator more realistic and helps users understand how life events impact credit decisions.