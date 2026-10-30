# Sample Test Scenario Plan: Promotional Voucher Engine

**Target File**: `src/billing/discount_engine.py`  
**Test Suite Path**: `tests/adversarial/test_discount_engine.py`  
**Framework**: `pytest 8.x`  
**Command**: `pytest tests/adversarial/test_discount_engine.py -v`  

---

## 1. Scenario Specifications

### Scenario `SCEN-001`: Discount Exceeding Subtotal (Boundary Check)
- **Corner Case**: `CC-001`
- **Severity**: P0 (Critical Financial Exposure)

#### Given:
```python
subtotal = Decimal("30.00")
discount = Decimal("50.00")
```

#### When:
```python
engine.calculate_cart(items=[{"price": subtotal, "quantity": 1}], discount_amount=discount)
```

#### Then:
```python
with pytest.raises(ValueError, match="Discount cannot exceed subtotal"):
    ...
```

---

### Scenario `SCEN-002`: Concurrent Voucher Redemption (Race Hazard)
- **Corner Case**: `CC-004`
- **Severity**: P0 (Voucher Abuse / Financial Loss)

#### Given:
- Single-use voucher `"WELCOME50"` in database.
- 10 threads synchronized via `threading.Barrier(10)`.

#### When:
- All 10 threads call `engine.calculate_cart(..., coupon_code="WELCOME50")` simultaneously.

#### Then:
- Exactly 1 thread successfully receives the $50 discount.
- Exactly 9 threads receive an error or cart calculation without the discount.
- Coupon usage record count in database equals exactly 1.
