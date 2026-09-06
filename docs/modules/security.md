# Security Module

## Overview

- **Purpose**: Manage roles and permissions for access control.
- **Scope**: Role assignment/revocation, authorization checks (role-based and ownership-based).

## Manual Admin Assignment

To assign the ADMIN role to a new identity (e.g., in a development environment), execute the following snippet in a Python shell with the application context loaded:

```python
import asyncio
from camp_match.modules.security.adapters.persistence.repository import SqlAlchemyRoleRepository
from camp_match.modules.security.domain.value_objects import Role
from camp_match.shared_kernel.domain.identifiers import EntityId
from camp_match.platform.db.session import get_db_session

async def assign_admin(identity_id_str: str):
    async with get_db_session() as session:
        repo = SqlAlchemyRoleRepository(session)
        identity_id = EntityId.from_string(identity_id_str)
        await repo.assign_role(identity_id, Role.ADMIN)
        await session.commit()

# Replace with the actual identity ID
asyncio.run(assign_admin("YOUR_IDENTITY_ID_HERE"))
```

## Security Contract for Other Modules

This module provides two primary ways to enforce access control:

### Pattern 1: Role-Scoped (Route-level gating)
For permissions that are not dependent on a specific resource (e.g., admin-only actions), use route-level dependency injection:

```python
@router.post("/some-admin-action", dependencies=[Depends(require_permission(Permission.YOUR_NEW_PERMISSION))])
async def admin_action():
    # Route logic
```

### Pattern 2: Ownership-Scoped (Use-case level gating)
For permissions that depend on resource ownership, load the resource first and perform authorization in the use case:

```python
# In your use case:
# 1. Load resource
resource = await self._repo.get_by_id(resource_id)
# 2. Authorize
decision = await self._auth_service.authorize(
    AuthorizationRequest(identity_id=caller_id, permission=Permission.EDIT_LISTING, resource_owner_id=resource.owner_id)
)
if decision.outcome != AuthorizationOutcome.ALLOWED:
    raise ForbiddenError("You do not own this resource")
```

## Extending Security
To add a new permission:
1.  Add the value to `Permission` in `src/camp_match/modules/security/domain/value_objects.py`.
2.  Add a line to the role-permission mapping in `src/camp_match/modules/security/domain/policy.py`.
3.  Mark it as ownership-scoped or role-scoped in `src/camp_match/modules/security/domain/policy.py`.

**Prohibited Imports:**
- Do not import from `modules.security.adapters.persistence` or `modules.security.adapters.profile`.
- Import only from `modules.security.application.ports` or `modules.security.adapters.api.dependencies`.
