import json
import os
import joblib
from langchain_core.tools import tool
from rag_engine import search_knowledge_base

# ─── TOOL 1: Read Gitleaks secrets scan results ───────────────────
@tool
def read_gitleaks_results() -> str:
    """
    Read the latest Gitleaks secrets scan results from the Jenkins pipeline.
    Use this tool when the user asks about leaked secrets, exposed API keys,
    hardcoded credentials, or anything related to secret detection.
    Returns a summary of all secrets found.
    """
    # Jenkins saves the report here after every pipeline run
    path = "security-reports/gitleaks-report.json"

    if not os.path.exists(path):
        return ("No Gitleaks report found. "
                "Run the Jenkins pipeline first to generate scan results.")

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        return f"Could not read Gitleaks report: {e}"

    # Empty list means no secrets found — this is good
    if not data:
        return "Gitleaks scan PASSED — No secrets or credentials found in the repository."

    # Format each finding as a clear summary
    findings = [f"Gitleaks found {len(data)} secret(s):"]
    for i, leak in enumerate(data[:10], 1):
        findings.append(
            f"  Finding {i}: {leak.get('Description','unknown type')} | "
            f"File: {leak.get('File','?')} | "
            f"Line: {leak.get('StartLine','?')} | "
            f"Rule: {leak.get('RuleID','?')}"
        )
    return "\n".join(findings)


# ─── TOOL 2: Read SonarQube SAST results ─────────────────────────
@tool
def read_sonarqube_results() -> str:
    """
    Read the latest SonarQube static code analysis results.
    Use this when the user asks about code vulnerabilities, code quality,
    security hotspots, bugs in the source code, or SAST findings.
    Returns a list of vulnerabilities found by SonarQube.
    """
    try:
        import requests
        # Call SonarQube API to get vulnerability issues
        resp = requests.get(
            "http://localhost:9000/api/issues/search",
            params={
                "projectKeys": "utopiahire",
                "types": "VULNERABILITY",
                "ps": 10
            },
            auth=("admin", "admin"),
            timeout=5
        )
        if resp.status_code != 200:
            return f"SonarQube returned status {resp.status_code}. Is it running at localhost:9000?"

        issues = resp.json().get("issues", [])
        if not issues:
            return "SonarQube found no vulnerabilities — code passes security analysis."

        lines = [f"SonarQube found {len(issues)} vulnerabilities:"]
        for i, issue in enumerate(issues, 1):
            component = issue.get('component', '').split(':')[-1]
            lines.append(
                f"  {i}. [{issue.get('severity','?')}] {issue.get('message','?')} | "
                f"File: {component} | Line: {issue.get('line','?')}"
            )
        return "\n".join(lines)

    except Exception as e:
        return f"Could not connect to SonarQube: {e}. Make sure it is running at localhost:9000."


# ─── TOOL 3: Read ZAP DAST results ───────────────────────────────
@tool
def read_zap_results() -> str:
    """
    Read the latest OWASP ZAP dynamic scan results.
    Use this when the user asks about runtime vulnerabilities, HTTP security,
    missing headers, injection points found during live testing, or DAST findings.
    Returns a summary of high and medium severity alerts.
    """
    path = "security-reports/zap-report.json"

    if not os.path.exists(path):
        return "No ZAP report found. Run the Jenkins pipeline to generate ZAP scan results."

    try:
        with open(path) as f:
            data = json.load(f)
    except Exception as e:
        return f"Could not read ZAP report: {e}"

    sites = data.get("site", [])
    if not sites:
        return "ZAP report exists but contains no site data."

    alerts = sites[0].get("alerts", [])
    high   = [a for a in alerts if "High"   in a.get("riskdesc", "")]
    medium = [a for a in alerts if "Medium" in a.get("riskdesc", "")]

    lines = [f"ZAP DAST scan found {len(high)} High and {len(medium)} Medium alerts:"]
    for alert in high[:5]:
        lines.append(f"  [HIGH] {alert.get('name','?')} — {alert.get('solution','No solution provided')[:150]}")
    for alert in medium[:3]:
        lines.append(f"  [MEDIUM] {alert.get('name','?')}")

    return "\n".join(lines)


# ─── TOOL 4: Read Suricata IDS alerts ────────────────────────────
@tool
def read_suricata_alerts() -> str:
    """
    Read the latest Suricata network intrusion detection alerts.
    Use this when the user asks about network attacks, intrusion attempts,
    SQL injection detected at network level, or Suricata IDS findings.
    Returns the last 20 alerts from the fast.log file.
    """
    path = "suricata/logs/fast.log"

    if not os.path.exists(path):
        return "No Suricata log found. Is Suricata running? Check docker ps."

    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except Exception as e:
        return f"Could not read Suricata log: {e}"

    # Filter empty lines
    alerts = [l.strip() for l in lines if l.strip()]

    if not alerts:
        return "Suricata is running but no alerts have been detected yet."

    recent = alerts[-20:]
    return f"Last {len(recent)} Suricata alerts:\n" + "\n".join(recent)


# ─── TOOL 5: ML vulnerability detector ──────────────────────────
@tool
def detect_vulnerability_with_ml(text: str) -> str:
    """
    Use the trained ML model to classify a text input as a vulnerability type.
    Use this when the user pastes code, a log entry, or a payload and asks
    what type of vulnerability it represents.
    Input: any text — code, log line, HTTP request, payload, description.
    Returns: predicted vulnerability type, confidence score, and a recommendation.
    """
    try:
        vectorizer = joblib.load("ml/vectorizer.pkl")
        le         = joblib.load("ml/label_encoder.pkl")
        model      = joblib.load("ml/random_forest_model.pkl")
    except FileNotFoundError:
        return "ML model files not found. Run Part 1 scripts first to train the model."

    try:
        X = vectorizer.transform([text])
        label_id   = model.predict(X)[0]
        label      = le.inverse_transform([label_id])[0]
        probas     = model.predict_proba(X)[0]
        confidence = float(probas[label_id])

        # Get RAG recommendation for this type
        rag_results = search_knowledge_base(
            f"{label} vulnerability fix recommendation", k=1
        )
        rec = rag_results[0].page_content[:300] if rag_results else "No recommendation found."

        severity_map = {
            'sqli': 'CRITICAL', 'rce': 'CRITICAL',
            'broken_access_control': 'HIGH', 'cmdi': 'HIGH',
            'xss': 'HIGH', 'csrf': 'HIGH',
            'file_upload': 'HIGH', 'ssrf': 'HIGH',
            'secret_exposure': 'CRITICAL',
            'path_traversal': 'HIGH', 'other': 'MEDIUM'
        }
        severity = severity_map.get(label, 'MEDIUM')

        return (
            f"ML Detection Result:\n"
            f"  Type:       {label.upper()}\n"
            f"  Severity:   {severity}\n"
            f"  Confidence: {confidence:.1%}\n"
            f"  From knowledge base:\n{rec}"
        )
    except Exception as e:
        return f"ML detection error: {e}"


# List all tools — imported by the agent in Step 10
ALL_TOOLS = [
    read_gitleaks_results,
    read_sonarqube_results,
    read_zap_results,
    read_suricata_alerts,
    detect_vulnerability_with_ml
]