# Security Policy

## Vulnerabilities Found (Phase 0)
The following issues were identified during the initial security analysis:

1. Broken access control on backend APIs: sensitive endpoints were callable without backend-side auth checks.
2. Insecure direct object reference (IDOR) risk in interview sessions: session ownership was not enforced.
3. CORS misconfiguration: origin configuration used an incorrect literal value, weakening origin control.
4. Unsafe file download handling: path traversal risk in career PDF download endpoint.
5. Missing rate limiting on expensive endpoints: high-cost AI routes were vulnerable to abuse/DoS-like traffic spikes.
6. Prompt injection risk in LLM flows: untrusted resume/CV text was inserted directly into prompts.
7. Weak upload validation: extension-only checks allowed spoofed file uploads (e.g., renamed non-PDF files).
8. Unsafe upload naming: user-provided filenames influenced storage paths.
9. Dependency vulnerability in frontend toolchain: vulnerable `esbuild` version (GHSA-67mh-4wv8-2f99) detected during audit.
10. Unstructured runtime logging: ad-hoc `print()` logs reduced incident visibility and increased risk of accidental sensitive output.

## Fixes Applied
Security remediation work completed in Days 2-4 includes:

1. Added backend authentication dependency and enforced it on sensitive routers:
- `/api/resume/*`
- `/api/interview/*`
- `/api/career/*`
- `/api/jobs/*`

2. Enforced object-level authorization for interview sessions:
- bound each session to `owner_uid`
- returned `403` for cross-user session access

3. Corrected CORS configuration to use configured origin list (`settings.CORS_ORIGINS`).

4. Hardened file download endpoint:
- strict filename validation (`roadmap_*.pdf`)
- basename enforcement to block path traversal

5. Added rate limiting with SlowAPI:
- centralized limiter setup
- endpoint-level limits (including expensive resume analysis route)

6. Added prompt-injection protections in AI service:
- wrapped untrusted input in escaped XML data blocks
- added explicit model instructions to treat tagged content as data only

7. Hardened file uploads across resume/career/jobs routers:
- MIME validation with magic bytes (`application/pdf` only)
- max upload size set to 5MB
- UUID-generated safe storage names

8. Added structured JSON logging:
- centralized logging config in backend startup
- replaced `print()` with `logger.info/warning/error`
- removed API key logging

9. Updated dependency manifests to include security-related packages (`firebase-admin`, `slowapi`, `python-magic`/`python-magic-bin` as appropriate for environment).

10. Produced security evidence documentation:
- `JURY_SECURITY_REPORT.md`
- `ACCESS_CONTROL_FIXES.md`

## Pipeline Controls
The project uses and/or plans these DevSecOps controls in CI/CD:

1. Gitleaks: secret scanning to prevent committed credentials.
2. Semgrep: static application security testing (SAST) for code-level vulnerabilities.
3. Trivy: container and dependency vulnerability scanning.
4. npm audit / pip dependency checks: package vulnerability detection and remediation tracking.
5. FastAPI auth guards + route-level authorization: runtime access control enforcement.
6. Rate limiting (SlowAPI): abuse/throttling protection for expensive endpoints.
7. Structured logging: JSON logs for incident response and observability tooling.

## How to Report a Vulnerability
If you discover a security issue, please report it responsibly:

- Contact: ahmedmasmoudi16@gmail.com or nourmoalla70@gmail.com
- Include: clear reproduction steps, affected endpoint/module, impact, and suggested fix (if available).
- Response target: initial acknowledgment within 72 hours.

Please do not disclose vulnerabilities publicly before maintainers have had time to investigate and patch.
