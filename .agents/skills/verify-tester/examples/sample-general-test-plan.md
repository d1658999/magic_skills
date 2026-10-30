# Sample General Test Scenario Plan: User Authentication

**Module**: `src/auth/service.py`  
**Test Suite**: `tests/functional/test_auth_service.py`  
**Target Scenario Coverage**: **$\ge 90\%$**  
**Achieved Coverage**: **$94.4\%$**  

---

## Pillar Allocation Summary

- **Pillar 1 (Golden Happy Paths)**: 8 Scenarios (44.4%)
- **Pillar 2 (Alternate Valid Branches)**: 4 Scenarios (22.2%)
- **Pillar 3 (Expected Error Handling)**: 5 Scenarios (27.8%)
- **Pillar 4 (End-to-End Lifecycles)**: 1 Scenario (5.6%)

---

## Key Scenario Specifications

### Scenario `TC-AUTH-01`: Nominal User Registration (Pillar 1)
- **Target**: `auth_service.register(email, password)`
- **Given**: Valid unallocated email `"user@example.com"`, password `"StrongP@ss1"`.
- **When**: `auth_service.register()` is executed.
- **Then**: Returns `UserDTO` with `status == "PENDING_VERIFICATION"`, database contains record with hashed password (bcrypt).

### Scenario `TC-AUTH-15`: User Directory Filter by Status (Pillar 2)
- **Target**: `auth_service.list_users(caller, status="DEACTIVATED")`
- **Given**: Database seeded with 10 ACTIVE users and 2 DEACTIVATED users.
- **When**: Admin caller lists users with `status="DEACTIVATED"`.
- **Then**: Returned list length is exactly 2; all items have `status == "DEACTIVATED"`.

### Scenario `TC-AUTH-04`: Duplicate Email Registration Rejection (Pillar 3)
- **Target**: `auth_service.register(email, password)`
- **Given**: User `"existing@example.com"` already in database.
- **When**: Registration attempted with `"existing@example.com"`.
- **Then**: Raises `DuplicateUserError(status_code=409, code="EMAIL_ALREADY_EXISTS")`.
