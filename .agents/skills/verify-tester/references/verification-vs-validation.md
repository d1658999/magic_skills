# Verification vs Validation & Acceptance Criteria

This reference outlines the distinction between Verification and Validation, and establishes the formal criteria used to evaluate requirement compliance during verification testing.

---

## 1. Verification vs. Validation (V&V)

In software engineering, Verification and Validation are complementary but distinct activities:

| Dimension | Verification | Validation |
| :--- | :--- | :--- |
| **Core Question** | *"Are we building the system right?"* | *"Are we building the right system?"* |
| **Primary Focus** | Conformance to specifications, contracts, and acceptance criteria. | User intent, business value, usability, and operational fitness. |
| **Measurement** | Objective, deterministic pass/fail assertions against written requirements. | Subjective feedback, user testing, A/B experiments, telemetry. |
| **Role of Verify-Tester** | **Primary Scope**: Prove 100% adherence to documented requirements. | Secondary: Flag ambiguities where specs conflict with user needs. |

---

## 2. Formulating Acceptance Criteria (Given-When-Then)

Every functional requirement must be decomposed into one or more verifiable **Acceptance Criteria (AC)** using the Given-When-Then pattern:

```gherkin
Scenario: Successful Password Reset Request
  Given a registered user with email "user@example.com" exists in the database
  When the user submits a POST request to "/api/v1/auth/forgot-password" with email "user@example.com"
  Then the system responds with HTTP 200 OK
  And a password reset token is generated with a 15-minute expiration timestamp
  And a notification event is published to the email queue with the reset link
```

### Anti-Patterns in Acceptance Criteria:
- ❌ **Vague**: "The system should handle bad passwords gracefully."
- ✅ **Precise**: "When password length < 8 chars, return HTTP 422 with `PASSWORD_TOO_SHORT`."
- ❌ **Implementation-Coupled**: "The system executes a SQL SELECT on table auth_tokens."
- ✅ **Behavioral**: "The system verifies that the token exists and is not expired."

---

## 3. Compliance Verdicts & Sign-Off States

Each acceptance criterion evaluated during testing receives one of four formal verdicts:

1. **`VERIFIED (PASS)`**:
   - The automated test executed, all assertions passed, and data contracts matched the specification.
2. **`NON-COMPLIANT (DEFECT)`**:
   - The test executed but failed. The implementation contradicts the requirement or crashed.
3. **`BLOCKED`**:
   - The test could not execute due to an upstream dependency failure or missing environment fixture.
4. **`DEFERRED / WAIVED`**:
   - Explicitly signed off by product ownership as deferred to a future milestone.
