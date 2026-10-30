# Sample Requirements Traceability Matrix: User Authentication

**Component**: `src/auth/`  
**Specification**: `PRD-AUTH-V2`  
**Date**: `2026-10-30`  
**Target Coverage**: `90.0%` | **Achieved**: `94.4%`  
**Verification Verdict**: ✅ **PASSED**  

---

## Bidirectional Register

| Req ID | Requirement Description | Acceptance Criteria | Pillar | Scenario ID | Function Name | Status |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| `REQ-AUTH-001` | Nominal User Registration | Valid email & password creates user | 1 (Happy) | `TC-AUTH-01` | `test_register_nominal_success` | `VERIFIED` |
| `REQ-AUTH-001` | Password Length Validation | Password < 8 characters rejected | 3 (Error) | `TC-AUTH-02` | `test_register_short_password_rejected` | `VERIFIED` |
| `REQ-AUTH-001` | Email Format Validation | Invalid email string rejected | 3 (Error) | `TC-AUTH-03` | `test_register_invalid_email_format` | `VERIFIED` |
| `REQ-AUTH-001` | Unique Email Enforcement | Duplicate email returns 409 | 3 (Error) | `TC-AUTH-04` | `test_register_duplicate_email_409` | `VERIFIED` |
| `REQ-AUTH-002` | Credential Authentication | Valid credentials return JWT | 1 (Happy) | `TC-AUTH-05` | `test_login_nominal_success_jwt` | `VERIFIED` |
| `REQ-AUTH-002` | Password Verification | Wrong password returns 401 | 3 (Error) | `TC-AUTH-06` | `test_login_invalid_password_returns_401` | `VERIFIED` |
| `REQ-AUTH-002` | User Identity Verification | Unknown email returns 401 | 3 (Error) | `TC-AUTH-07` | `test_login_unknown_user_returns_401` | `VERIFIED` |
| `REQ-AUTH-002` | Token Expiration Claim | Token lifetime is 3600 seconds | 1 (Happy) | `TC-AUTH-08` | `test_jwt_expiration_duration_claim` | `VERIFIED` |
| `REQ-AUTH-003` | Profile Retrieval | Returns profile matching UserDTO | 1 (Happy) | `TC-AUTH-09` | `test_get_profile_authenticated_user` | `VERIFIED` |
| `REQ-AUTH-003` | Display Name Mutation | Updates name in DB & returns DTO | 1 (Happy) | `TC-AUTH-10` | `test_update_display_name_success` | `VERIFIED` |
| `REQ-AUTH-003` | Optional Avatar Parameter | Optional avatar omitted safely | 2 (Alternate) | `TC-AUTH-11` | `test_profile_optional_avatar_omitted` | `VERIFIED` |
| `REQ-AUTH-003` | Authentication Guard | Missing token returns 401 | 3 (Error) | `TC-AUTH-12` | `test_profile_unauthenticated_guard` | `VERIFIED` |
| `REQ-AUTH-004` | Admin User Directory | Admin user lists registered users | 1 (Happy) | `TC-AUTH-13` | `test_admin_list_users_nominal` | `VERIFIED` |
| `REQ-AUTH-004` | Directory Pagination | Navigation via page & limit params | 2 (Alternate) | `TC-AUTH-14` | `test_admin_directory_pagination_page_2` | `VERIFIED` |
| `REQ-AUTH-004` | Directory Status Filter | Filter by ACTIVE / DEACTIVATED | 2 (Alternate) | `TC-AUTH-15` | `test_admin_directory_status_filtering` | `VERIFIED` |
| `REQ-AUTH-004` | Role Authorization Guard | Regular user receives 403 Forbidden | 3 (Error) | `TC-AUTH-16` | `test_non_admin_directory_access_403` | `VERIFIED` |
| `REQ-AUTH-005` | Account Self-Deactivation | User deactivates; status updated | 1 (Happy) | `TC-AUTH-17` | `test_deactivate_account_success` | `VERIFIED` |
| `REQ-AUTH-005` | Deactivated Login Block | Login attempt returns 403 Forbidden | 4 (E2E) | `TC-AUTH-18` | `test_full_onboarding_to_deactivation_lifecycle` | `VERIFIED` |
