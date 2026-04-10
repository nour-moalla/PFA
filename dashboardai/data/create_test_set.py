import pandas as pd

# ─── 11 REAL UtopiaHire vulnerabilities ───────────────────────────────────────
# Source: GitHub Copilot analysis of the actual UtopiaHire codebase + JURY_SECURITY_REPORT.md
# These are verified findings — not invented. Used as the test set.
# The model is trained on NVD public CVE data, tested on these real project findings.

utopiahire_vulns = [
    {
        'CVE ID': 'UTH-001',
        'Description': (
            'The .env file contains a live AI API key committed directly into the source-controlled '
            'repository. If this repository is shared, cloned, or leaked, an attacker can reuse '
            'that credential to call the AI provider, consume quota, incur costs, and access model '
            'usage tied to the account. This is a direct secret management failure — the secret is '
            'stored in plaintext in a tracked project file rather than injected securely at runtime.'
        ),
        'CVSS Score': 8.2,
        'label': 'secret_exposure',
        'severity': 'high',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'none',
        'user_interaction': 'none',
        'status': 'still_present'
    },
    {
        'CVE ID': 'UTH-002',
        'Description': (
            'In docker-compose.devops.yml, Grafana is started with GF_SECURITY_ADMIN_PASSWORD '
            'set to a static weak value admin123. If the Grafana port is reachable by other users '
            'on the host network, this creates a straightforward credential-guessing entry point '
            'into monitoring dashboards and potentially sensitive operational data. Hardcoded weak '
            'credentials in deployment manifests propagate across environments and are often '
            'forgotten after initial setup.'
        ),
        'CVSS Score': 7.5,
        'label': 'secret_exposure',
        'severity': 'high',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'none',
        'user_interaction': 'none',
        'status': 'still_present'
    },
    {
        'CVE ID': 'UTH-003',
        'Description': (
            'The Streamlit dashboard in app.py triggers Jenkins builds using a hardcoded password '
            'string in the requests.post auth tuple. Credentials end up in source code, are likely '
            'copied into real values over time, and can be extracted from repository history or '
            'logs. Credential material for CI systems should be injected from secrets storage and '
            'never embedded in application code paths.'
        ),
        'CVSS Score': 6.8,
        'label': 'secret_exposure',
        'severity': 'medium',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'low',
        'user_interaction': 'none',
        'status': 'still_present'
    },
    {
        'CVE ID': 'UTH-004',
        'Description': (
            'The Jenkins service entrypoint in docker-compose.devops.yml runs chmod 666 on '
            '/var/run/docker.sock, making the Docker daemon socket world-writable inside the '
            'container. Any process with access to that socket can effectively control Docker on '
            'the host, which is equivalent to host-level remote code execution by spawning '
            'privileged containers or mounting host filesystems. This is a critical container '
            'breakout enabler if Jenkins or any co-located process is compromised.'
        ),
        'CVSS Score': 9.1,
        'label': 'rce',
        'severity': 'critical',
        'platform': 'web',
        'attack_vector': 'local',
        'attack_complexity': 'low',
        'privileges_required': 'low',
        'user_interaction': 'none',
        'status': 'still_present'
    },
    {
        'CVE ID': 'UTH-005',
        'Description': (
            'The Streamlit dashboard in app.py exposes operational actions such as '
            'stopping and starting Suricata and running docker compose up and down, but there is '
            'no application-level authentication or role check. If this dashboard is accessible '
            'beyond a trusted localhost-only boundary, an attacker could invoke privileged '
            'DevSecOps actions from the UI without any identity verification. This is a direct '
            'broken access control risk on critical operational functions.'
        ),
        'CVSS Score': 8.0,
        'label': 'broken_access_control',
        'severity': 'high',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'none',
        'user_interaction': 'none',
        'status': 'still_present'
    },
    {
        'CVE ID': 'UTH-006',
        'Description': (
            'Backend endpoints in main.py were previously callable directly without enforced token '
            'validation, even when frontend routes appeared protected. An attacker could bypass UI '
            'controls and call resume, interview, career, and jobs endpoints directly without '
            'authentication. This issue was later mitigated by adding dependency-based auth guards '
            'in main.py as documented in JURY_SECURITY_REPORT.md.'
        ),
        'CVSS Score': 8.6,
        'label': 'broken_access_control',
        'severity': 'high',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'none',
        'user_interaction': 'none',
        'status': 'fixed'
    },
    {
        'CVE ID': 'UTH-007',
        'Description': (
            'Interview endpoints previously accepted session_id without verifying ownership, so a '
            'guessed or leaked session ID could expose another user\'s interview history or scores. '
            'This IDOR vulnerability is documented in JURY_SECURITY_REPORT.md and was fixed '
            'through ownership checks in interview.py. Before the fix, any authenticated user '
            'could access any other user\'s interview session by manipulating the session_id.'
        ),
        'CVSS Score': 7.7,
        'label': 'broken_access_control',
        'severity': 'high',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'low',
        'user_interaction': 'none',
        'status': 'fixed'
    },
    {
        'CVE ID': 'UTH-008',
        'Description': (
            'The endpoint /api/career/download/{filename} in career_insights.py previously '
            'accepted unsafe path input, enabling directory traversal attempts to read arbitrary '
            'files outside the intended directory. The current implementation now sanitizes '
            'basename and enforces roadmap_*.pdf constraints. This path traversal vulnerability '
            'is explicitly documented in JURY_SECURITY_REPORT.md and has been remediated.'
        ),
        'CVSS Score': 7.4,
        'label': 'path_traversal',
        'severity': 'high',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'low',
        'user_interaction': 'none',
        'status': 'fixed'
    },
    {
        'CVE ID': 'UTH-009',
        'Description': (
            'The /api/resume/analyze endpoint previously lacked throttling and could be abused '
            'for request flooding, API quota burn, or compute exhaustion. Without rate limiting, '
            'an attacker could repeatedly submit large workloads and degrade service availability. '
            'The fix is now present with SlowAPI limiter at resume.py as documented in '
            'JURY_SECURITY_REPORT.md.'
        ),
        'CVSS Score': 6.5,
        'label': 'other',
        'severity': 'medium',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'none',
        'user_interaction': 'none',
        'status': 'fixed'
    },
    {
        'CVE ID': 'UTH-010',
        'Description': (
            'Upload endpoints in upload_validation.py previously trusted file extensions only, '
            'allowing non-PDF payloads renamed as .pdf to be uploaded. This unrestricted file '
            'upload vulnerability is documented in JURY_SECURITY_REPORT.md. The hardening now '
            'enforces size limits, magic-byte MIME checks, and safe UUID filenames, confirming '
            'a real prior file upload validation flaw that has been addressed.'
        ),
        'CVSS Score': 7.1,
        'label': 'file_upload',
        'severity': 'high',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'low',
        'user_interaction': 'none',
        'status': 'fixed'
    },
    {
        'CVE ID': 'UTH-011',
        'Description': (
            'Untrusted resume content in ai_service.py could previously influence downstream '
            'model behavior through prompt injection if not properly isolated. A malicious user '
            'could craft resume text containing instructions that override system prompts and '
            'manipulate the AI response. The current mitigation explicitly instructs the model '
            'to treat tagged resume content as untrusted data only, as documented in '
            'JURY_SECURITY_REPORT.md.'
        ),
        'CVSS Score': 5.9,
        'label': 'other',
        'severity': 'medium',
        'platform': 'web',
        'attack_vector': 'network',
        'attack_complexity': 'low',
        'privileges_required': 'none',
        'user_interaction': 'required',
        'status': 'fixed'
    },
]

df_test = pd.DataFrame(utopiahire_vulns)
df_test['source'] = 'utopiahire_phase0'

# ─── Load training set ────────────────────────────────────────────────────────
df_train = pd.read_csv("data/balanced_dataset.csv")
df_train['source'] = 'nvd_base'

df_train.to_csv("data/train_set.csv", index=False)
df_test.to_csv("data/test_set.csv", index=False)

print(f"Training set: {len(df_train)} rows (NVD balanced dataset)")
print(f"Test set:     {len(df_test)} rows (UtopiaHire real findings)")

print("\nTest set summary:")
print(df_test[['CVE ID', 'label', 'severity', 'status']].to_string(index=False))

print("\nLabel distribution in test set:")
print(df_test['label'].value_counts().to_string())

# ─── Safety check: all test labels must exist in training ─────────────────────
train_labels = set(df_train['label'].unique())
test_labels  = set(df_test['label'].unique())
missing = test_labels - train_labels
if missing:
    print(f"\n⚠️  WARNING: These labels are in test but NOT in training: {missing}")
    print("   Fix: change those rows to an existing training label.")
else:
    print("\n✅ All test labels exist in the training set. No LabelEncoder errors expected.")
