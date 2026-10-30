# Broad-Spectrum Coverage Playbook

This reference provides technical guidance on structuring test suites across the **Four Functional Pillars** to achieve $\ge 90\%$ scenario coverage across mainstream application flows.

---

## 1. The Four-Pillar Allocation Strategy

Coverage must not be concentrated solely on happy paths or solely on negative error paths. Balance your test suite across four distinct categories:

```
┌────────────────────────────────────────────────────────┐
│               FOUR-PILLAR SCENARIO WEIGHTING           │
├────────────────────────────────────────────────────────┤
│  40%  Pillar 1: Golden Path (Primary Happy Journeys)   │
│  30%  Pillar 2: Alternate Valid Branches & Variations  │
│  20%  Pillar 3: Expected / Standard Error Handling     │
│  10%  Pillar 4: End-to-End Multi-Step Integration      │
└────────────────────────────────────────────────────────┘
```

---

## 2. Pillar 1: Golden Happy Paths (40%)

The Golden Path represents nominal operation—the path 80% of users take on a normal day.

### Characteristics:
- Clean, realistic input payloads (valid emails, typical order sizes, standard user names).
- Complete data contracts satisfied.
- Database records cleanly created and verified.
- Standard HTTP 200/201 responses returned with full payloads.

### Exemplar Structure:
```python
def test_create_user_golden_path(db_session, api_client):
    payload = {
        "email": "jane.doe@example.com",
        "name": "Jane Doe",
        "role": "MEMBER"
    }
    response = api_client.post("/api/v1/users", json=payload)
    
    # 1. HTTP contract
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["email"] == "jane.doe@example.com"
    assert data["created_at"] is not None

    # 2. Database state persistence
    user_record = db_session.get_user_by_id(data["id"])
    assert user_record.is_active is True
```

---

## 3. Pillar 2: Alternate Valid Branches (30%)

Real applications have numerous valid variations, optional parameters, and business permutations.

### Key Dimensions to Cover:
1. **Optional Field Combinations**:
   - Omitting optional parameters (e.g., `phone_number=None`).
   - Supplying all optional parameters.
2. **Filtering, Sorting & Pagination**:
   - `page=1&limit=20` (default) vs `page=3&limit=50`.
   - `sort=created_at:desc` vs `sort=name:asc`.
   - Filtering with multiple active criteria simultaneously.
3. **Role & Tier Variations**:
   - Free Tier user vs Premium / Enterprise user capabilities.
   - Admin vs Regular Member permissions on view endpoints.
4. **Secondary Channels / Payment Methods**:
   - Credit card vs PayPal vs Wire transfer checkout branches.

### Exemplar Structure (Parameterized):
```python
@pytest.mark.parametrize("query_params, expected_count", [
    ({"status": "ACTIVE"}, 5),
    ({"status": "INACTIVE"}, 2),
    ({"role": "ADMIN", "status": "ACTIVE"}, 1),
    ({"page": 2, "limit": 2}, 2),
    ({"search": "doe"}, 1),
])
def test_list_users_alternate_branches(api_client, query_params, expected_count):
    response = api_client.get("/api/v1/users", params=query_params)
    assert response.status_code == 200
    assert len(response.json()["items"]) == expected_count
```

---

## 4. Pillar 3: Expected / Standard Error Handling (20%)

Systems must fail predictably and informatively when users provide incorrect inputs or encounter expected conflicts.

### Standard Error Scenarios to Cover:
1. **Input Validation Rejections (HTTP 400)**:
   - Malformed email address (`"invalid-email"`).
   - Password below minimum length requirements.
   - Missing required payload parameters (`{"name": "Alice"}` without email).
2. **Authentication & Authorization Rejections (HTTP 401 / 403)**:
   - Missing or expired Bearer token $\rightarrow$ 401 Unauthorized.
   - Valid token but insufficient permissions $\rightarrow$ 403 Forbidden.
3. **Resource Non-Existence (HTTP 404)**:
   - Querying or mutating a non-existent UUID $\rightarrow$ 404 Not Found.
4. **Resource Conflict (HTTP 409)**:
   - Registering an email that already exists in the system $\rightarrow$ 409 Conflict.

### Exemplar Structure:
```python
def test_register_duplicate_email_returns_409(api_client, seeded_user):
    payload = {
        "email": seeded_user.email, # Duplicate!
        "password": "SecurePassword123!"
    }
    response = api_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    body = response.json()
    assert body["error_code"] == "USER_ALREADY_EXISTS"
    assert "already registered" in body["message"]
```

---

## 5. Pillar 4: End-to-End Workflow Integration (10%)

Verify that components work together seamlessly in multi-step business transactions.

### Key Workflow Scenarios:
- **Full User Lifecycle**: Register $\rightarrow$ Confirm Email $\rightarrow$ Login $\rightarrow$ Update Password $\rightarrow$ Deactivate.
- **Order Lifecycle**: Cart Checkout $\rightarrow$ Payment Authorized $\rightarrow$ Order Created $\rightarrow$ Inventory Reserved.
- **Asynchronous Processing**: File Upload $\rightarrow$ Background Job Enqueued $\rightarrow$ Polling Status $\rightarrow$ Complete.
