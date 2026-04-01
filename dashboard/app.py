import streamlit as st
import subprocess
import json
import os
import requests
from datetime import datetime

st.set_page_config(
    page_title="UtopiaHire DevSecOps Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ─── SIDEBAR — Security Status Panel ───────────────────────────
with st.sidebar:
    st.title("Security Status")
    st.markdown("---")

    # Check which Docker containers are running
    def is_container_running(name):
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={name}", "--format", "{{.Names}}"],
            capture_output=True, text=True
        )
        return name in result.stdout

    # Status indicators
    suricata_on = is_container_running("suricata")
    jenkins_on = is_container_running("jenkins")
    sonar_on = is_container_running("sonarqube")
    app_on = is_container_running("utopiahire")

    st.markdown("### Active Modules")
    st.markdown(f"{'🟢' if app_on else '🔴'} **App** (backend + frontend)")
    st.markdown(f"{'🟢' if jenkins_on else '🔴'} **Jenkins** CI/CD pipeline")
    st.markdown(f"{'🟢' if sonar_on else '🔴'} **SonarQube** SAST")
    st.markdown(f"{'🟢' if suricata_on else '🔴'} **Suricata** IDS")

    st.markdown("---")
    st.markdown("### Quick Links")
    st.markdown("🔗 [Jenkins](http://localhost:8080)")
    st.markdown("🔗 [SonarQube](http://localhost:9000)")
    st.markdown("🔗 [Grafana](http://localhost:3001)")
    st.markdown("🔗 [Prometheus](http://localhost:9090)")
    st.markdown("🔗 [App Backend](http://localhost:8000)")

# ─── MAIN AREA — Three tabs ─────────────────────────────────────
st.title("UtopiaHire DevSecOps Control Center")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

dev_tab, sec_tab, ops_tab, ai_tab = st.tabs([
    "⚙️ Dev", "🛡️ Sec", "🔧 Ops", "🤖 AI Assistant"
])

# ─── DEV TAB ────────────────────────────────────────────────────
with dev_tab:
    st.header("Development Security Controls")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Static Analysis (SAST)")
        run_semgrep = st.button("▶ Run Semgrep Scan")
        if run_semgrep:
            with st.spinner("Running Semgrep..."):
                result = subprocess.run(
                    ["docker", "run", "--rm",
                     "-v", f"{os.getcwd()}:/src",
                     "semgrep/semgrep", "semgrep",
                     "--config", "p/security-audit",
                     "--json", "/src"],
                    capture_output=True, text=True
                )
                st.code(result.stdout[:2000] or "Scan complete", language="json")

        st.subheader("Secrets Detection")
        run_gitleaks = st.button("▶ Run Gitleaks Scan")
        if run_gitleaks:
            with st.spinner("Scanning for secrets..."):
                result = subprocess.run(
                    ["docker", "run", "--rm",
                     "-v", f"{os.getcwd()}:/path",
                     "zricethezav/gitleaks:latest",
                     "detect", "--source", "/path", "--exit-code", "0"],
                    capture_output=True, text=True
                )
                output = result.stdout + result.stderr
                if "No leaks found" in output:
                    st.success("No secrets found — Gitleaks clean")
                else:
                    st.error("Potential secrets detected!")
                    st.code(output[:1500])

    with col2:
        st.subheader("Dependency Audit")
        run_audit = st.button("▶ Run Dependency Audit")
        if run_audit:
            with st.spinner("Auditing dependencies..."):
                result = subprocess.run(
                    ["docker", "run", "--rm",
                     "-v", f"{os.getcwd()}/backend:/app",
                     "python:3.11-slim",
                     "sh", "-c", "pip install pip-audit -q && pip-audit -r /app/requirements.txt"],
                    capture_output=True, text=True
                )
                st.code(result.stdout or result.stderr, language="text")

        st.subheader("Latest Scan Results")
        # Read the latest reports from Jenkins
        report_path = "security-reports/gitleaks-report.json"
        if os.path.exists(report_path):
            with open(report_path) as f:
                data = json.load(f)
            st.json(data)
        else:
            st.info("No scan results yet. Run a scan above.")

# ─── SEC TAB ────────────────────────────────────────────────────
with sec_tab:
    st.header("Security Monitoring Controls")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Intrusion Detection — Suricata")
        suricata_running = is_container_running("suricata")

        if suricata_running:
            st.success("Suricata IDS is ACTIVE")
            if st.button("⏹ Stop Suricata"):
                subprocess.run(["docker", "stop", "suricata"])
                st.rerun()
        else:
            st.error("Suricata IDS is INACTIVE")
            if st.button("▶ Start Suricata"):
                subprocess.run([
                    "docker", "run", "-d",
                    "--name", "suricata",
                    "--network", "host",
                    "--cap-add", "NET_ADMIN",
                    "--cap-add", "NET_RAW",
                    "-v", f"{os.getcwd()}/suricata/logs:/var/log/suricata",
                    "-v", f"{os.getcwd()}/suricata/rules:/etc/suricata/rules",
                    "jasonish/suricata:latest",
                    "-i", "lo"
                ])
                st.rerun()

        st.subheader("Recent Suricata Alerts")
        log_path = "suricata/logs/fast.log"
        if os.path.exists(log_path):
            with open(log_path) as f:
                lines = f.readlines()[-20:]
            for line in lines:
                if "Attempt" in line or "Attack" in line:
                    st.warning(line.strip())
        else:
            st.info("No Suricata logs yet")

    with col2:
        st.subheader("DAST Scanning — OWASP ZAP")
        run_zap = st.button("▶ Run ZAP Scan Now")
        if run_zap:
            with st.spinner("Running ZAP scan — this takes 2-3 minutes..."):
                subprocess.run([
                    "docker", "run", "--rm",
                    "--network", "host",
                    "-v", f"{os.getcwd()}/security-reports:/zap/wrk:rw",
                    "ghcr.io/zaproxy/zaproxy:stable",
                    "zap-baseline.py",
                    "-t", "http://172.17.0.1:8000",
                    "-r", "zap-report.html",
                    "-I"
                ])
                st.success("ZAP scan complete — see Artifacts tab")

        st.subheader("Firewall — iptables Status")
        if st.button("🔍 Check iptables Rules"):
            result = subprocess.run(
                ["docker", "exec", "utopiahire-main-backend",
                 "iptables", "-L", "INPUT", "-n", "-v"],
                capture_output=True, text=True
            )
            st.code(result.stdout or result.stderr, language="text")

# ─── OPS TAB ────────────────────────────────────────────────────
with ops_tab:
    st.header("Operations Controls")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pipeline — Jenkins")
        if st.button("▶ Trigger Jenkins Build"):
            try:
                resp = requests.post(
                    "http://localhost:8080/job/utopiahire-pipeline/build",
                    auth=("admin", "your_jenkins_password")
                )
                if resp.status_code in [200, 201]:
                    st.success("Jenkins build triggered successfully")
                else:
                    st.warning(f"Response: {resp.status_code}")
            except Exception:
                st.error("Could not reach Jenkins at localhost:8080")

        st.subheader("Application Containers")
        if st.button("▶ Start App (docker compose up)"):
            subprocess.run(["docker", "compose", "up", "-d"])
            st.success("App containers started")

        if st.button("⏹ Stop App (docker compose down)"):
            subprocess.run(["docker", "compose", "down"])
            st.success("App containers stopped")

    with col2:
        st.subheader("Monitoring")
        st.markdown("📊 **Grafana Dashboard:** [localhost:3001](http://localhost:3001)")
        st.markdown("📈 **Prometheus:** [localhost:9090](http://localhost:9090)")

        st.subheader("Container Status")
        result = subprocess.run(
            ["docker", "ps", "--format",
             "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True, text=True
        )
        st.code(result.stdout, language="text")

# ─── AI TAB — placeholder for Phase 2 ──────────────────────────
with ai_tab:
    st.header("AI Security Assistant")
    st.info("AI Assistant will be added in Phase 2. Come back after completing Phase 1.")
