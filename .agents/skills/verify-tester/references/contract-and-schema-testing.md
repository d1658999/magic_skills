# Data Contract & Schema Testing

This reference details how the **Verify-Tester** validates that APIs, services, and modules adhere strictly to defined data contracts, payload schemas, and serialization invariants.

---

## 1. The Contract Testing Principle

Functional behavior is incomplete if the structure of data exchanged between systems is wrong. Contract testing verifies that:
1. Payloads match expected schema types (strings, numbers, booleans, enums).
2. Required fields are always present.
3. Extra / unexpected fields are rejected or handled according to API policy.
4. Data types maintain backward compatibility across API versions.

---

## 2. Schema Validation Approaches

### Pattern 1: JSON Schema Validation (Python `jsonschema`)
```python
import jsonschema

USER_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "email", "name", "created_at"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "email": {"type": "string", "format": "email"},
        "name": {"type": "string", "minLength": 1},
        "role": {"type": "string", "enum": ["ADMIN", "MEMBER", "GUEST"]},
        "created_at": {"type": "string", "format": "date-time"}
    },
    "additionalProperties": False
}

def test_user_api_schema_conformance(api_client):
    response = api_client.get("/api/v1/users/me")
    assert response.status_code == 200
    # Strict schema assertion
    jsonschema.validate(instance=response.json(), schema=USER_RESPONSE_SCHEMA)
```

### Pattern 2: Pydantic Model Contract Parsing
```python
from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime

class UserProfileDTO(BaseModel):
    id: str
    email: EmailStr
    name: str
    avatar_url: Optional[HttpUrl] = None
    created_at: datetime

def test_profile_endpoint_matches_dto(api_client):
    response = api_client.get("/api/v1/profile")
    # Parsing will raise ValidationError if contract is broken
    dto = UserProfileDTO.model_validate(response.json())
    assert dto.email is not None
```

---

## 3. Backward Compatibility Invariants

When testing modifications to existing APIs or data models, verify:
- **No Field Removal**: Existing fields must not be deleted or renamed without version increments.
- **No Optional $\rightarrow$ Required Promotion**: Existing optional fields cannot suddenly become mandatory.
- **Enum Additive Only**: Existing enum values must not be removed or altered.
