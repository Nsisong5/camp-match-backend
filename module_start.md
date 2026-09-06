DESIGN SPECIFICATION

This section fixes the target design. Section 4 tells you how to build it, chunk by chunk. Read this fully before Chunk 1.
Domain model
Role (enum) — STUDENT, SCOUT, ADMIN, OPERATIONS. STUDENT/SCOUT are never assigned or stored by this module — they only ever appear as the result of asking Profile what type a given identity's profile is. ADMIN/OPERATIONS are the only roles this module actually assigns and stores.
Permission (enum, deliberately small right now) — ADMIN_USERS_MANAGE, mapped to the string admin.users.manage. Every permission is declared here, never as a raw string scattered through route code — this is the centralized registry the handoff asks for (Part I). Adding a permission for a future module means adding one line here plus one line to the role→permission mapping below, nothing else.
Role → permission mapping (static, code-defined, not a database table — ADR-036): ADMIN → {ADMIN_USERS_MANAGE}. OPERATIONS, STUDENT, SCOUT currently map to an empty permission set — they exist as roles because the handoff and the domain call for them, but nothing in this MVP grants them a permission yet. That's expected, not a bug to "fix" by inventing one.
Principal (value object) — identity_id (EntityId), roles (a frozen set of Role). Constructed only by the application layer's own role-resolution logic (Chunk 8) — nothing else in the codebase should be able to construct one with roles it didn't actually resolve (ADR-040).
AuthorizationOutcome (enum) — ALLOWED, DENIED, UNAUTHENTICATED, INVALID_CONTEXT. Four genuinely different things, per the handoff's own insistence (Part O) that these not collapse into one generic result.
AuthorizationDecision (value object) — outcome (AuthorizationOutcome), reason (a short human-readable string, safe to put in a log line, not necessarily safe to put verbatim in an API response — see Chunk 4's error mapping for what the API boundary actually returns).
The ownership rule, stated precisely, since it's the one piece of real logic in this whole domain layer: a permission is either role-scoped (granted purely by having the right role — admin.users.manage is this kind) or ownership-scoped (granted only when the requesting identity matches a supplied resource owner, unless the requester is ADMIN, which bypasses this check per ADR-041). Which kind a given permission is, is a property of the permission itself, declared alongside it in the same static registry — not something the caller decides per-call.
Ports
Inbound — one port, one method: AuthorizationService — authorize(identity_id: EntityId, permission: Permission, resource_owner_id: EntityId | None = None) -> AuthorizationDecision. That's the entire public surface other modules' application layers need to know about.
Outbound:
RoleRepository — get_assigned_roles(identity_id) -> frozenset[Role] (returns only ADMIN/OPERATIONS-type assignments — never resolves STUDENT/SCOUT, which never appear here at all), assign_role(identity_id, role) -> None, revoke_role(identity_id, role) -> None. The latter two exist because the domain needs them to be meaningful, even though nothing calls them via HTTP yet (Section 4, Chunk 8 covers exactly how assignment happens for now).
ProfileProvider — one method, get_profile_type(identity_id) -> "StudentOrScout" | None (returns None, not an error, when no profile exists yet — a perfectly normal state for a freshly registered account, per Module 2's own design).
Reused directly, not redefined: shared-kernel Clock, EntityId.
Database
One new table, security_user_roles — deliberately the only one (ADR-036):
Column
Type
Notes
id
UUID
primary key
identity_id
UUID
not null, no foreign key into Identity's table, same reasoning as Profile's identity_id column (Module 2, ADR-027) — a unique-together constraint with role below is what actually matters here
role
text
not null, CHECK restricted to ADMIN/OPERATIONS only — STUDENT/SCOUT are structurally never written here
assigned_at
timestamptz
server-generated default
Unique constraint on (identity_id, role) — an identity can't be assigned the same role twice.
Errors
Error
Extends
code
Current status
Unauthenticated
UnauthorizedError
unauthenticated
Reserved — in the normal HTTP flow, Identity's existing token dependency already rejects an unauthenticated request before Security's own code runs. Kept for a future direct (non-HTTP) caller of authorize().
Forbidden
ForbiddenError
forbidden
The live, real 403 path — raised by require_permission on a DENIED outcome.
UnknownPermission
ValidationError
unknown_permission
Raised if something references a permission not in the static registry — a programming-error guard, not something a well-formed request should ever trigger.
InvalidAuthorizationContext
ValidationError
invalid_authorization_context
Raised when an ownership-scoped permission is checked with no resource_owner_id supplied at all.
RoleNotFound
NotFoundError
role_not_found
Reserved for role-assignment operations (Chunk 8) referencing a role value that isn't valid — limited use in this pass, same honesty note as Identity's InvalidAuthenticationRequest.
PolicyViolation
ForbiddenError
policy_violation
Reserved as a future, more specific subtype of Forbidden (e.g. "quota exceeded," "delegation expired") — not independently triggered yet; Forbidden covers the one real denial path for now.
No new platform-level error mapping needed — Identity's Chunk 8 (project-wide ApplicationError → HTTP translation) already covers every category above.



IMPLEMENTATION INSTRUCTIONS FOR THE



Most operating rules already live in AI_instructions/ and apply here unchanged — inspect before you build, don't duplicate authentication, don't leak ORM models, don't refactor unrelated code, run tests before declaring anything done. Three things specific to this module, worth stating plainly rather than assuming they follow automatically:
Never derive a role from anything the caller sends. Not a header, not a query parameter, not a JWT claim you add yourself later "for convenience." Every role, every time, comes from RoleRepository or ProfileProvider — both server-side, both re-checked on every request. If you find yourself trusting a role value that arrived in a request, stop — that's the exact bypass Section 1's quality bar (Part AN) exists to prevent.
authorize() takes an identity_id, never a pre-built Principal. If a use case elsewhere in the codebase already has a Principal in hand (from get_current_principal, Chunk 9) and wants to check a permission, it still calls authorize() with the identity id from that principal — it does not pass the principal object itself into anything that makes a security decision. This is ADR-040, and it's the kind of rule that's easy to quietly erode "for convenience" later — don't.
Do not touch Identity's or Profile's existing use cases, domain, or persistence. Chunk 10 adds two new routes to Identity's existing router, calling Identity's existing DisableAccount/ReactivateAccount use cases exactly as they already are. If those use cases don't do quite what you'd want, that's a signal to stop and report it, not to modify Identity's application layer as a side effect of this module.



CHUNKED CODING INSTRUCTIONS


CHUNK 1 — Inspect Foundation & Confirm Contract Assumptions

Objective: Confirm this document's assumptions against the real codebase before writing anything.
Implementation instructions:
Read AI_instructions/00_START_HERE.md onward, and AI_state/CURRENT_STATE.md, ARCHITECTURE_STATE.md, DATABASE_STATE.md, API_STATE.md.
Read docs/modules/identity.md and docs/modules/profile.md.
Inspect Identity's DisableAccount/ReactivateAccount use cases and their exact request/response shapes (Chunk 10 will call these directly).
Inspect platform/security/authentication.py (Module 2's relocated get_current_identity_id) and confirm exactly what it returns and raises.
Inspect Profile's GetCurrentUserProfile use case — confirm it accepts an arbitrary identity_id, not only "the caller's own" (Chunk 6 will call it for identities other than whoever happens to be logged in when the check runs).
Report back: confirm all four match this document's assumptions, or flag exactly what doesn't before proceeding.
Acceptance criteria: a written report; no files created or modified.




