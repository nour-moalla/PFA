# Access Control Fixes

Date: 2026-03-29

## Summary
This document records the broken access control issues that were fixed across the backend and frontend.

## Fixed Issues

### 1) Missing server-side authentication on sensitive APIs
- Problem: Protected UI routes existed, but backend APIs could still be called directly without authentication.
- Fix: Added token-based authentication dependency to all sensitive API routers.
- Result: Calls to resume/interview/career/jobs APIs now require a valid Firebase Bearer token.

### 2) CORS origin misconfiguration
- Problem: CORS origins were configured as a literal string instead of using configured origin values.
- Fix: Switched to actual configured list (`settings.CORS_ORIGINS`).
- Result: Origin checks now use real allowed origins.

### 3) Interview session object-level authorization (IDOR risk)
- Problem: Session endpoints accepted `session_id` without verifying ownership, allowing cross-user access if a session ID was known.
- Fix: Bound sessions to authenticated user (`owner_uid`) and enforced ownership checks on session operations.
- Result: Users can only access/modify their own interview sessions.

### 4) Path traversal/arbitrary file access in PDF download endpoint
- Problem: Download endpoint accepted unvalidated filename path segments.
- Fix: Restricted filenames to safe basename values matching generated roadmap pattern (`roadmap_*.pdf`).
- Result: Prevents directory traversal and unauthorized file reads.

### 5) Frontend token propagation to backend requests
- Problem: Frontend API client did not attach auth token to requests.
- Fix: Added Axios request interceptor to attach Firebase ID token (`Authorization: Bearer <token>`).
- Result: Authenticated users seamlessly call protected backend APIs.

## Files Changed

- `backend/app/core/auth.py`
  - Added Firebase token verification dependency (`get_current_user`).
- `backend/app/core/config.py`
  - Added auth config settings:
  - `FIREBASE_CREDENTIALS_JSON`
  - `FIREBASE_CREDENTIALS_FILE`
- `backend/main.py`
  - Applied auth dependencies to sensitive routers.
  - Fixed CORS origins assignment.
- `backend/app/routers/interview.py`
  - Added ownership checks for interview sessions.
  - Stored and enforced `owner_uid` per session.
- `backend/app/routers/career_insights.py`
  - Hardened `/download/{filename}` filename validation.
- `frontend/src/api/client.js`
  - Added request interceptor to include Firebase ID token.
- `backend/requirements.in`
  - Added `firebase-admin>=6.5.0`.
- `backend/requirements.txt`
  - Added `firebase-admin>=6.5.0`.

## Verification
- Static diagnostics check was run after edits.
- Result: No errors reported.

## Deployment Notes
Set one of the following backend auth configs in runtime environment:

- `FIREBASE_CREDENTIALS_JSON` (service account JSON content), or
- `FIREBASE_CREDENTIALS_FILE` (path to service account JSON), or
- Application Default Credentials (ADC) in your execution environment.

If Firebase Admin is not configured, protected endpoints will fail closed with a service-unavailable auth error..
