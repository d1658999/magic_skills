# Acceptance Test Suite Template

Use this template during **Phase 3** to scaffold structured broad-spectrum test suites that trace directly back to requirement IDs.

---

```python
"""Acceptance Test Suite for [Feature / Component Name].

Traces to Requirements: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005.
Coverage Strategy: Four-Pillar Broad Spectrum (Golden Paths, Alternate, Errors, E2E).
Target Minimum Scenario Coverage: >= 90%.
"""

import pytest
from typing import Dict, Any

# ==============================================================================
# PILLAR 1: GOLDEN HAPPY PATH SCENARIOS (Nominal Operation - 40% Weight)
# ==============================================================================

class TestPillar1GoldenPaths:
    """Tests primary success journeys under nominal inputs."""

    def test_primary_user_journey_success(self, client, db_session):
        """Traces to REQ-001 / AC-01: Nominal user registration and creation."""
        payload = {
            "email": "primary.user@example.com",
            "name": "Alex Mercer",
            "role": "MEMBER"
        }
        response = client.post("/api/v1/resource", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["email"] == payload["email"]
        assert data["status"] == "ACTIVE"


# ==============================================================================
# PILLAR 2: ALTERNATE VALID BRANCHES & PERMUTATIONS (30% Weight)
# ==============================================================================

class TestPillar2AlternateBranches:
    """Tests valid variations, optional parameters, sorting, and pagination."""

    @pytest.mark.parametrize("query_params, expected_count", [
        ({"page": 1, "limit": 10}, 10),
        ({"page": 2, "limit": 10}, 5),
        ({"role": "ADMIN"}, 2),
        ({"sort": "created_at:desc"}, 15),
    ])
    def test_list_query_permutations(self, client, query_params, expected_count):
        """Traces to REQ-004 / AC-02: Pagination and filtering variations."""
        response = client.get("/api/v1/resource", params=query_params)
        assert response.status_code == 200
        assert len(response.json()["items"]) == expected_count

    def test_optional_parameters_omitted(self, client):
        """Traces to REQ-003 / AC-03: Handling omitted optional fields gracefully."""
        minimal_payload = {"email": "minimal@example.com", "name": "Min User"}
        response = client.post("/api/v1/resource", json=minimal_payload)
        assert response.status_code == 201
        assert response.json()["avatar_url"] is None


# ==============================================================================
# PILLAR 3: EXPECTED / STANDARD ERROR SCENARIOS (20% Weight)
# ==============================================================================

class TestPillar3ExpectedErrors:
    """Tests standard validation rejections, 4xx responses, and conflict errors."""

    @pytest.mark.parametrize("invalid_payload, expected_status, expected_error_code", [
        ({"email": "not-an-email", "name": "Test"}, 400, "INVALID_EMAIL"),
        ({"email": "valid@example.com"}, 400, "MISSING_REQUIRED_FIELD"),
        ({"email": "", "name": ""}, 400, "EMPTY_INPUT"),
    ])
    def test_input_validation_rejections(self, client, invalid_payload, expected_status, expected_error_code):
        """Traces to REQ-001 / AC-04: Standard schema rejection on invalid input."""
        response = client.post("/api/v1/resource", json=invalid_payload)
        assert response.status_code == expected_status
        assert response.json()["error_code"] == expected_error_code

    def test_duplicate_resource_conflict_409(self, client, seeded_entity):
        """Traces to REQ-001 / AC-05: Conflict on duplicate identity."""
        conflict_payload = {"email": seeded_entity.email, "name": "Duplicate"}
        response = client.post("/api/v1/resource", json=conflict_payload)
        assert response.status_code == 409
        assert response.json()["error_code"] == "RESOURCE_ALREADY_EXISTS"


# ==============================================================================
# PILLAR 4: END-TO-END WORKFLOW INTEGRATION (10% Weight)
# ==============================================================================

class TestPillar4EndToEndWorkflows:
    """Tests multi-step operational flows from initiation to completion."""

    def test_full_lifecycle_workflow(self, client):
        """Traces to REQ-005 / AC-06: End-to-end multi-step lifecycle."""
        # Step 1: Create
        create_res = client.post("/api/v1/resource", json={"email": "lifecycle@example.com", "name": "Life User"})
        assert create_res.status_code == 201
        res_id = create_res.json()["id"]

        # Step 2: Read
        get_res = client.get(f"/api/v1/resource/{res_id}")
        assert get_res.status_code == 200

        # Step 3: Update
        update_res = client.put(f"/api/v1/resource/{res_id}", json={"name": "Updated Life User"})
        assert update_res.status_code == 200

        # Step 4: Verify Final State
        final_res = client.get(f"/api/v1/resource/{res_id}")
        assert final_res.json()["name"] == "Updated Life User"
```
