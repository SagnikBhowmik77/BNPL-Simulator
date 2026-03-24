# Refund Percentage Explanation

## What is Refund Percentage?

Refund percentage is a parameter in the BNPL simulator that represents **what portion of the original purchase amount should be refunded** when a return or cancellation occurs.

## Key Details:

### **Range**: 0.0 to 1.0 (or 0% to 100%)
- `0.0` = 0% refund (no refund)
- `0.5` = 50% refund (partial refund)
- `1.0` = 100% refund (full refund)

### **Default Value**: 1.0 (100% refund)

## How It Works in the Simulator:

### **1. Refund Simulation Request**
```python
class RefundSimulationRequest(BaseModel):
    loan_id: str
    refund_percentage: float = 1.0  # Default is 100% refund
```

### **2. Refund Type Determination**
The simulator categorizes refunds based on the percentage:

- **FULL Refund** (`refund_percentage = 1.0`)
  - Complete return of purchase amount
  - Adjustment method: "Credit to original payment method"
  - Timeline: 7 days
  - Complications: None (standard process)

- **PARTIAL Refund** (`0.0 < refund_percentage < 1.0`)
  - Partial return (e.g., damaged item, partial cancellation)
  - Adjustment method: "Pro-rated credit to loan balance"
  - Timeline: 14 days
  - Complications: 
    - "Partial refunds may not reduce monthly payments immediately"
    - "Remaining balance still accrues interest/fees"
    - "Merchant processing delays common"

- **NO Refund** (`refund_percentage = 0.0`)
  - No refund available (e.g., non-returnable items)
  - Adjustment method: "No refund available"
  - Timeline: 0 days
  - Complications: "BNPL terms often restrict refunds after payment processing"

## Real-World Examples:

### **Example 1: Full Return**
```bash
# Customer returns entire item
curl -X POST "http://localhost:8001/refund-simulation" \
  -d '{"loan_id": "loan123", "refund_percentage": 1.0}'
```
**Result**: FULL refund, $100 credited back, 7-day timeline

### **Example 2: Partial Return**
```bash
# Customer returns damaged item, gets 70% refund
curl -X POST "http://localhost:8001/refund-simulation" \
  -d '{"loan_id": "loan123", "refund_percentage": 0.7}'
```
**Result**: PARTIAL refund, $70 credited to loan balance, 14-day timeline

### **Example 3: No Refund**
```bash
# Non-returnable item
curl -X POST "http://localhost:8001/refund-simulation" \
  -d '{"loan_id": "loan123", "refund_percentage": 0.0}'
```
**Result**: NO refund, customer still owes full amount

## Why Refund Percentage Matters:

### **1. BNPL Complexity**
Unlike credit cards, BNPL refunds are more complex because:
- The loan has already been funded to the merchant
- Customer may have already made installment payments
- Refunds need to be processed through the BNPL provider

### **2. Financial Impact**
- **Full refunds**: May stop future installments
- **Partial refunds**: Reduce loan balance but payments may continue
- **No refunds**: Customer still owes full amount despite return

### **3. Timeline Variations**
- Full refunds: Faster processing (7 days)
- Partial refunds: Slower processing (14 days) due to complexity

## Testing Refund Scenarios:

You can test different refund percentages to see how the BNPL system handles various return situations:

```bash
# Test full refund
curl -X POST "http://localhost:8001/refund-simulation" \
  -d '{"loan_id": "loan123", "refund_percentage": 1.0}'

# Test partial refund  
curl -X POST "http://localhost:8001/refund-simulation" \
  -d '{"loan_id": "loan123", "refund_percentage": 0.5}'

# Test no refund
curl -X POST "http://localhost:8001/refund-simulation" \
  -d '{"loan_id": "loan123", "refund_percentage": 0.0}'
```

This feature helps simulate the real-world complexity of BNPL refunds, which is often more complicated than traditional payment methods.