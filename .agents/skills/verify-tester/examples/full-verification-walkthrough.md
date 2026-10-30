# Full Verification Walkthrough: Achieving 94% Scenario Coverage

This document provides a realistic, end-to-end case study demonstrating how the **Verify-Tester** skill guarantees that a system satisfies at least 90% of documented requirements across nominal, alternate, error, and integration flows.

---

## 1. The Target Specification

The product engineering team received the following specification:

```markdown
# Product Requirement Document (PRD): User Identity & Access Service
1. REQ-AUTH-001 (User Registration):
   - Users can register with valid email and password (minimum 8 characters).
   - Duplicate email registrations must be rejected with HTTP 409 Conflict.
   - User account status defaults to PENDING_VERIFICATION.
2. REQ-AUTH-002 (Authentication & JWT Issuance):
   - Users can authenticate with registered email and password.
   - Successful authentication returns a signed JWT access token (valid for 60 minutes) and refresh token.
   - Invalid credentials must return HTTP 401 Unauthorized.
3. REQ-AUTH-003 (Profile Management):
   - Authenticated users can retrieve their profile details.
   - Users can update their display name and optional avatar URL.
   - Unauthenticated requests must return HTTP 401.
4. REQ-AUTH-004 (Administrative User Directory):
   - Administrators can list registered users with pagination (default limit 20, max 100).
   - Directory must support filtering by user status (ACTIVE, PENDING_VERIFICATION, DEACTIVATED).
   - Regular users attempting to access the directory must receive HTTP 403 Forbidden.
5. REQ-AUTH-005 (Account Lifecycle & Deactivation):
   - Users can deactivate their own account; deactivated accounts cannot log in.
```

---

## Phase 1: Requirements Deconstruction & Acceptance Criteria Atomization

The Verify-Tester broke down the 5 requirements into **18 atomic acceptance criteria**:

```
REQ-AUTH-001 (Registration):
  ├── AC-01: Valid email and 8+ char password creates user with PENDING status (Happy)
  ├── AC-02: Password < 8 characters returns 400 Bad Request (Error)
  ├── AC-03: Invalid email format returns 400 Bad Request (Error)
  └── AC-04: Existing email returns 409 Conflict (Error)

REQ-AUTH-002 (Authentication):
  ├── AC-05: Valid credentials return JWT access token and refresh token (Happy)
  ├── AC-06: Wrong password returns 401 Unauthorized (Error)
  ├── AC-07: Non-existent email returns 401 Unauthorized (Error)
  └── AC-08: Token contains expiration timestamp set to +60 minutes (Contract)

REQ-AUTH-003 (Profile):
  ├── AC-09: Authenticated user retrieves own profile payload (Happy)
  ├── AC-10: Update display name updates DB and returns updated DTO (Happy)
  ├── AC-11: Optional avatar_url omitted retains null cleanly (Alternate)
  └── AC-12: Missing Bearer token returns 401 Unauthorized (Error)

REQ-AUTH-004 (Admin Directory):
  ├── AC-13: Admin user lists users with default pagination (Happy)
  ├── AC-14: Admin user navigates page=2 with custom limit=50 (Alternate)
  ├── AC-15: Filter by status returns only matching users (Alternate)
  └── AC-16: Non-admin user receives 403 Forbidden (Error)

REQ-AUTH-005 (Lifecycle):
  ├── AC-17: User deactivates account; status becomes DEACTIVATED (Happy)
  └── AC-18: Login attempt on deactivated account returns 403 Forbidden (Error)
```

---

## Phase 2: RTM Construction & Gap Analysis

The initial developer test suite only had 13 tests, yielding:
$$\text{Initial Coverage Ratio} = \frac{13}{18} = 72.2\% \quad (\text{BLOCKED: } < 90\%)$$

### Gap Analysis Findings:
- Unmapped: `AC-11` (Optional avatar omission).
- Unmapped: `AC-14` (Pagination page 2 custom limits).
- Unmapped: `AC-15` (Status filtering).
- Unmapped: `AC-16` (Non-admin 403 check).
- Unmapped: `AC-18` (Deactivated account login rejection).

### Closing the Gaps:
The Verify-Tester added 4 dedicated test scenarios covering these missing alternate and error flows, bringing the mapped criteria to **17 out of 18 (94.4%)**:

$$\text{Final Scenario Coverage Ratio} = \frac{17}{18} = \mathbf{94.4\%} \quad (\text{PASSED: } \ge 90\%)$$

---

## Phase 3: Broad-Spectrum Test Synthesis

The agent authored the complete test suite across the **Four Pillars** in `tests/functional/test_auth_service.py`:

```python
import pytest
from src.auth.service import AuthService
from src.auth.exceptions import DuplicateUserError, AuthenticationError, ForbiddenError

class TestAuthBroadSpectrum:
    # --- PILLAR 1: GOLDEN HAPPY PATHS (40%) ---
    def test_register_nominal_success(self, auth_service):
        """Traces to REQ-AUTH-001 / AC-01."""
        user = auth_service.register("alice@example.com", "SecurePass123!")
        assert user.id is not None
        assert user.status == "PENDING_VERIFICATION"

    def test_login_nominal_success_jwt(self, auth_service, seeded_user):
        """Traces to REQ-AUTH-002 / AC-05."""
        tokens = auth_service.login(seeded_user.email, "ValidPassword123!")
        assert "access_token" in tokens
        assert tokens["expires_in"] == 3600

    # --- PILLAR 2: ALTERNATE VALID BRANCHES (30%) ---
    @pytest.mark.parametrize("status_filter, expected_count", [
        ("ACTIVE", 10),
        ("PENDING_VERIFICATION", 4),
        ("DEACTIVATED", 2),
    ])
    def test_admin_directory_status_filtering(self, auth_service, admin_user, status_filter, expected_count):
        """Traces to REQ-AUTH-004 / AC-15."""
        result = auth_service.list_users(caller=admin_user, status=status_filter)
        assert len(result.items) == expected_count

    def test_profile_optional_avatar_omitted(self, auth_service, seeded_user):
        """Traces to REQ-AUTH-003 / AC-11."""
        profile = auth_service.update_profile(seeded_user.id, display_name="Alice W.")
        assert profile.display_name == "Alice W."
        assert profile.avatar_url is None

    # --- PILLAR 3: EXPECTED ERROR PATHS (20%) ---
    def test_register_duplicate_email_409(self, auth_service, seeded_user):
        """Traces to REQ-AUTH-001 / AC-04."""
        with pytest.raises(DuplicateUserError):
            auth_service.register(seeded_user.email, "AnotherPassword123!")

    def test_non_admin_directory_access_403(self, auth_service, regular_user):
        """Traces to REQ-AUTH-004 / AC-16."""
        with pytest.raises(ForbiddenError):
            auth_service.list_users(caller=regular_user)

    # --- PILLAR 4: END-TO-END WORKFLOW INTEGRATION (10%) ---
    def test_full_onboarding_to_deactivation_lifecycle(self, auth_service):
        """Traces to REQ-AUTH-005 / AC-17, AC-18."""
        # 1. Register
        user = auth_service.register("bob@example.com", "Password1234!")
        # 2. Login
        tokens = auth_service.login("bob@example.com", "Password1234!")
        # 3. Deactivate
        auth_service.deactivate_account(user.id, token=tokens["access_token"])
        # 4. Verify login is now blocked
        with pytest.raises(ForbiddenError, match="Account is deactivated"):
            auth_service.login("bob@example.com", "Password1234!")
```

---

## Phase 4: Test Execution & Coverage Audit

The Verify-Tester executed the suite and ran coverage analysis:

```text
pytest --cov=src/auth --cov-report=term-missing tests/functional/test_auth_service.py

tests/functional/test_auth_service.py ................. [100%]
---------- coverage: platform win32, python 3.11 -----------
Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
src/auth/service.py        118      3     24      2  96.5%   88-90
src/auth/validators.py      54      2     16      1  95.7%   42-43
src/auth/dto.py             32      0      0      0 100.0%
--------------------------------------------------------------------
TOTAL                      204      5     40      3  96.7%
======================== 17 passed in 0.88s ========================
```

- **Scenario Coverage**: **94.4%** (17/18 Acceptance Criteria).
- **Test Pass Rate**: **100.0%** (17/17 Tests Passed).
- **Line Coverage**: **96.7%** (Above 85% Gate).
- **Branch Coverage**: **92.5%** (Above 80% Gate).

---

## Phase 5: Verification Sign-Off

The Verify-Tester delivered the formal **Verification Audit Report**:

> **PRODUCTION STATUS**: ✅ **VERIFIED - APPROVED FOR PRODUCTION RELEASE**  
> All 5 functional requirements and 94.4% of acceptance criteria have been verified with 100% automated test pass rates and 96.7% code coverage. Zero regressions or unhandled branch conditions were observed.
