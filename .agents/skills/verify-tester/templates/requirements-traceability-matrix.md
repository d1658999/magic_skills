# Requirements Traceability Matrix Template

Use this template during **Phase 2** to construct the bidirectional mapping between requirements, acceptance criteria, test scenarios, and verification status.

---

# Requirements Traceability Matrix (RTM): [Feature / System Name]

**Component / Module**: `[e.g., src/auth/service.py]`  
**Specification Source**: `[e.g., docs/specs/auth_prd.md, RFC-104]`  
**Date**: `[YYYY-MM-DD]`  
**Lead Verification Architect**: `[Verify-Tester Agent]`  
**Target Minimum Coverage**: **90.0%**  

---

## 1. Traceability Summary & Metric Dashboard

```
┌────────────────────────────────────────────────────────────────────────┐
│                      RTM TRACEABILITY DASHBOARD                        │
├────────────────────────────────────────────────────────────────────────┤
│ Total Documented Requirements:       [ Total Count ]                   │
│ Total Atomic Acceptance Criteria:    [ AC Count ]                      │
│ Acceptance Criteria with Test Cases: [ Mapped Count ]                  │
│ SCENARIO COVERAGE RATIO:             [ XX.X % ] (Target >= 90.0%)      │
│ VERIFICATION GATE STATUS:            [ PASSED | BLOCKED ]              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Bidirectional Traceability Register

| Req ID | Requirement Statement | Acceptance Criteria (Given/When/Then) | Pillar | Test Scenario ID | Test Function Name | Verification Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `REQ-001` | User registration with valid email | Given valid email and password When user registers Then 201 Created and user record is persisted | 1 (Happy) | `TC-REG-01` | `test_register_valid_user_success` | `VERIFIED` |
| `REQ-001` | User registration password length check | Given password < 8 chars When user registers Then 400 Bad Request with PASSWORD_TOO_SHORT | 3 (Error) | `TC-REG-02` | `test_register_short_password_rejected` | `VERIFIED` |
| `REQ-002` | User login authentication | Given registered user When valid credentials submitted Then 200 OK and JWT access token returned | 1 (Happy) | `TC-AUTH-01` | `test_login_valid_credentials_jwt` | `VERIFIED` |
| `REQ-002` | User login invalid password | Given registered user When wrong password submitted Then 401 Unauthorized returned | 3 (Error) | `TC-AUTH-02` | `test_login_invalid_password_returns_401` | `VERIFIED` |
| `REQ-003` | User profile retrieval | Given authenticated user When GET /profile called Then return profile payload matching UserDTO | 1 (Happy) | `TC-PROF-01` | `test_get_profile_authenticated_user` | `VERIFIED` |
| `REQ-003` | User profile with optional avatar | Given user without avatar When GET /profile called Then avatar_url is null without errors | 2 (Alternate) | `TC-PROF-02` | `test_get_profile_omitted_optional_avatar` | `VERIFIED` |
| `REQ-004` | User list pagination | Given 50 users in DB When GET /users?page=2&limit=10 Then return items 11-20 with total=50 | 2 (Alternate) | `TC-LIST-01` | `test_list_users_pagination_page_2` | `VERIFIED` |
| `REQ-004` | User list role filtering | Given mixed users When GET /users?role=ADMIN Then return only ADMIN accounts | 2 (Alternate) | `TC-LIST-02` | `test_list_users_filter_by_admin_role` | `VERIFIED` |
| `REQ-005` | End-to-end user onboarding flow | Given new visitor When register -> login -> view profile Then all states chain correctly | 4 (E2E) | `TC-E2E-01` | `test_e2e_registration_to_profile_flow` | `VERIFIED` |

---

## 3. Four-Pillar Scenario Balance Audit

| Pillar | Category | Target Weight | Actual Count | Actual Share % | Balance Assessment |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **Pillar 1** | Golden Happy Paths | ~40% | `[Count]` | `[XX%]` | `[Balanced / Under-represented]` |
| **Pillar 2** | Alternate Valid Branches | ~30% | `[Count]` | `[XX%]` | `[Balanced / Under-represented]` |
| **Pillar 3** | Standard Expected Errors | ~20% | `[Count]` | `[XX%]` | `[Balanced / Under-represented]` |
| **Pillar 4** | E2E Integration Workflows| ~10% | `[Count]` | `[XX%]` | `[Balanced / Under-represented]` |
| **TOTAL** | | **100%** | **`[Total]`** | **100%** | **Compliant** |

---

## 4. Unmapped Requirements & Gap Remediation Log

*(If Scenario Coverage is $< 90\%$, document unmapped requirements and action plan below)*

| Unmapped Req ID | Description | Reason Unmapped | Remediation Scenario to Add | Target Pillar |
| :--- | :--- | :--- | :--- | :---: |
| `[None - 100% Mapped]` | — | — | — | — |
