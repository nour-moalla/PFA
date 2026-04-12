import streamlit as st
import subprocess
import json
import os
import joblib
import requests
import shutil
from datetime import datetime
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'))

st.set_page_config(
    page_title="UtopiaHire SecOps",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --navy:        #0d1b2e;
    --navy-light:  #132236;
    --navy-mid:    #1a2e47;
    --navy-card:   #162032;
    --border:      rgba(255,255,255,0.08);
    --border-soft: rgba(255,255,255,0.04);
    --cyan:        #00d4ff;
    --cyan-glow:   rgba(0,212,255,0.12);
    --pink:        #ff4d8d;
    --pink-glow:   rgba(255,77,141,0.12);
    --orange:      #ff8c42;
    --orange-glow: rgba(255,140,66,0.12);
    --green:       #00e5a0;
    --green-glow:  rgba(0,229,160,0.12);
    --purple:      #7c5cfc;
    --white:       #ffffff;
    --white-80:    rgba(255,255,255,0.8);
    --white-60:    rgba(255,255,255,0.6);
    --white-40:    rgba(255,255,255,0.4);
    --white-20:    rgba(255,255,255,0.2);
    --white-08:    rgba(255,255,255,0.08);
    --font:        'Inter', sans-serif;
    --mono:        'DM Mono', monospace;
}

html, body, [class*="css"] {
    font-family: var(--font) !important;
    background-color: var(--navy) !important;
    color: var(--white-80) !important;
}
.main .block-container {
    background: var(--navy) !important;
    padding: 0 2rem 2rem 2rem !important;
    max-width: 100% !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: var(--navy-mid); border-radius: 99px; }

section[data-testid="stSidebar"] {
    background: var(--navy-light) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.sb-brand {
    padding: 28px 20px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}
.sb-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.sb-logo-icon {
    width: 34px; height: 34px; border-radius: 8px;
    background: linear-gradient(135deg, var(--cyan), var(--purple));
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}
.sb-logo-name { font-size: 15px; font-weight: 700; color: var(--white); }
.sb-logo-sub { font-size: 10px; font-weight: 600; color: var(--cyan); letter-spacing: 2px; text-transform: uppercase; }
.sb-ts { font-family: var(--mono); font-size: 10px; color: var(--white-40); margin-top: 8px; }

.sb-nav { font-size: 10px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: var(--white-40); padding: 16px 20px 6px; }

.sp { display: flex; align-items: center; gap: 10px; padding: 9px 20px; transition: background 0.15s; }
.sp:hover { background: var(--white-08); }
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot.on  { background: var(--green); box-shadow: 0 0 8px var(--green); }
.dot.off { background: var(--pink);  box-shadow: 0 0 6px rgba(255,77,141,0.5); }
.sp-info { flex: 1; }
.sp-name { font-size: 12px; font-weight: 600; color: var(--white-80); }
.sp-url  { font-family: var(--mono); font-size: 10px; color: var(--white-40); }

.ql { display: block; padding: 7px 20px; font-size: 12px; font-weight: 500; color: var(--cyan) !important; text-decoration: none !important; transition: background 0.15s; }
.ql:hover { background: var(--cyan-glow); }

.hero { padding: 32px 0 24px; border-bottom: 1px solid var(--border); margin-bottom: 28px; }
.hero-eye { font-size: 11px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: var(--cyan); margin-bottom: 8px; }
.hero-h { font-size: 30px; font-weight: 800; color: var(--white); line-height: 1.15; margin-bottom: 8px; }
.hero-h span { color: var(--cyan); }
.hero-d { font-size: 14px; color: var(--white-60); max-width: 560px; line-height: 1.6; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--white-40) !important; font-family: var(--font) !important; font-size: 13px !important; font-weight: 500 !important; border-radius: 0 !important; padding: 12px 24px !important; border-bottom: 2px solid transparent !important; transition: all 0.2s !important; }
.stTabs [aria-selected="true"] { color: var(--white) !important; border-bottom-color: var(--cyan) !important; }

.mcard { background: var(--navy-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; position: relative; overflow: hidden; transition: transform 0.2s, border-color 0.2s; }
.mcard:hover { transform: translateY(-2px); border-color: var(--white-20); }
.mcard-glow { position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; border-radius: 50%; filter: blur(25px); opacity: 0.35; }
.mcard-icon { font-size: 20px; margin-bottom: 10px; }
.mcard-lbl { font-size: 10px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: var(--white-40); margin-bottom: 6px; }
.mcard-val { font-size: 28px; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.mcard-sub { font-size: 11px; color: var(--white-40); }

.sh { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; margin-top: 8px; }
.sb { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; padding: 3px 10px; border-radius: 99px; background: var(--cyan-glow); color: var(--cyan); border: 1px solid rgba(0,212,255,0.2); }
.st { font-size: 15px; font-weight: 700; color: var(--white); }

.fc { background: var(--navy-card); border: 1px solid var(--border); border-left: 3px solid var(--pink); border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; transition: border-color 0.2s; }
.fc:hover { border-color: var(--white-20); border-left-color: var(--pink); }
.fc-rule { font-family: var(--mono); font-size: 11px; font-weight: 500; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; color: var(--pink); }
.fc-file { font-family: var(--mono); font-size: 12px; color: var(--orange); margin-bottom: 6px; }
.fc-desc { font-size: 13px; color: var(--white-60); line-height: 1.5; }

.pill { display: inline-block; font-size: 9px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding: 2px 7px; border-radius: 4px; margin-left: 8px; vertical-align: middle; }
.p-c { background: var(--pink-glow); color: var(--pink); border: 1px solid rgba(255,77,141,0.3); }
.p-h { background: var(--orange-glow); color: var(--orange); border: 1px solid rgba(255,140,66,0.3); }
.p-m { background: var(--cyan-glow); color: var(--cyan); border: 1px solid rgba(0,212,255,0.3); }
.p-s { background: var(--green-glow); color: var(--green); border: 1px solid rgba(0,229,160,0.3); }

.ib { background: var(--navy-card); border: 1px solid var(--border); border-radius: 10px; padding: 13px 18px; font-size: 13px; color: var(--white-60); line-height: 1.6; margin-bottom: 12px; }
.ib.c { border-left: 3px solid var(--cyan); }
.ib.g { border-left: 3px solid var(--green); }
.ib.p { border-left: 3px solid var(--pink); }
.ib.o { border-left: 3px solid var(--orange); }

.sc { display: flex; gap: 12px; padding: 11px 0; border-bottom: 1px solid var(--border-soft); align-items: flex-start; }
.sc:last-child { border-bottom: none; }
.sc-msg { font-size: 13px; color: var(--white-80); line-height: 1.4; }
.sc-file { font-family: var(--mono); font-size: 10px; color: var(--white-40); margin-top: 3px; }

.ll { font-family: var(--mono); font-size: 11px; color: var(--orange); padding: 6px 12px; background: rgba(255,140,66,0.04); border-left: 2px solid rgba(255,140,66,0.25); border-radius: 0 4px 4px 0; margin-bottom: 4px; word-break: break-all; line-height: 1.5; }

.dbox { background: var(--navy-card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; margin-top: 14px; }
.dbox-hd { padding: 12px 18px; background: var(--cyan-glow); border-bottom: 1px solid rgba(0,212,255,0.12); }
.dbox-ti { font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: var(--cyan); }
.dr { display: flex; justify-content: space-between; align-items: center; padding: 11px 18px; border-bottom: 1px solid var(--border-soft); }
.dr:last-child { border-bottom: none; }
.dr-k { font-size: 12px; color: var(--white-40); }
.dr-v { font-size: 13px; font-weight: 600; color: var(--white); }
.dr-v.cr { color: var(--pink); }
.dr-v.hi { color: var(--orange); }
.dr-v.me { color: var(--cyan); }

.stButton > button { background: var(--navy-mid) !important; border: 1px solid var(--border) !important; color: var(--white-80) !important; font-family: var(--font) !important; font-size: 13px !important; font-weight: 500 !important; padding: 9px 20px !important; border-radius: 8px !important; transition: all 0.2s !important; width: 100% !important; }
.stButton > button:hover { background: var(--cyan-glow) !important; border-color: var(--cyan) !important; color: var(--cyan) !important; }

.stTextArea textarea, .stTextInput input { background: var(--navy-card) !important; border: 1px solid var(--border) !important; color: var(--white-80) !important; font-family: var(--font) !important; font-size: 13px !important; border-radius: 8px !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color: var(--cyan) !important; box-shadow: 0 0 0 2px var(--cyan-glow) !important; }

.stCode, pre, code { background: #0a1120 !important; border: 1px solid var(--border) !important; color: var(--green) !important; font-family: var(--mono) !important; font-size: 11px !important; border-radius: 8px !important; }

.stChatMessage { background: var(--navy-card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
.stSpinner > div { border-color: var(--cyan) transparent transparent transparent !important; }
hr { border-color: var(--border) !important; }
label, .stTextArea label { color: var(--white-60) !important; font-size: 12px !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────
def container_running(name):
    try:
        dp = shutil.which("docker")
        if not dp: return False
        r = subprocess.run([dp, "ps", "--filter", f"name={name}", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=5)
        return name in r.stdout
    except: return False

def run_docker(cmd):
    dp = shutil.which("docker") or "docker"
    return subprocess.run([dp] + cmd, capture_output=True, text=True)

def pill(sev):
    s = str(sev).upper()
    c = "p-c" if s in ("CRITICAL","BLOCKER") else "p-h" if s in ("HIGH","MAJOR") else "p-m" if s in ("MEDIUM","MINOR") else "p-s"
    return f'<span class="pill {c}">{sev}</span>'

def dr_class(sev):
    s = str(sev).upper()
    return "cr" if s in ("CRITICAL","BLOCKER") else "hi" if s in ("HIGH","MAJOR") else "me"

C = {"critical":"var(--pink)","high":"var(--orange)","safe":"var(--green)","info":"var(--cyan)"}
B = {"critical":"rgba(255,77,141,0.3)","high":"rgba(255,140,66,0.3)","safe":"rgba(0,229,160,0.3)","info":"rgba(0,212,255,0.3)"}


# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    now = datetime.now()
    st.markdown(f"""
    <div class="sb-brand">
        <div class="sb-logo">
            <div class="sb-logo-icon">🛡</div>
            <div><div class="sb-logo-name">UtopiaHire</div><div class="sb-logo-sub">SecOps Platform</div></div>
        </div>
        <div class="sb-ts">Last sync: {now.strftime('%H:%M:%S — %b %d, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-nav">Infrastructure Status</div>', unsafe_allow_html=True)
    for cname, label, url in [
        ("utopiahire-backend",    "API Backend",     ":8000"),
        ("jenkins",               "Jenkins CI/CD",   ":8080"),
        ("utopiahire-sonarqube",  "SonarQube SAST",  ":9000"),
        ("utopiahire-suricata",   "Suricata IDS",    "IDS"),
        ("utopiahire-grafana",    "Grafana",         ":3001"),
        ("utopiahire-prometheus", "Prometheus",      ":9090"),
    ]:
        online = container_running(cname)
        st.markdown(f"""
        <div class="sp">
            <div class="dot {'on' if online else 'off'}"></div>
            <div class="sp-info">
                <div class="sp-name">{label}</div>
                <div class="sp-url">localhost{url}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sb-nav">Quick Access</div>', unsafe_allow_html=True)
    for label, url in [
        ("Jenkins Dashboard", "http://localhost:8080"),
        ("SonarQube Console", "http://localhost:9000"),
        ("Grafana Metrics",   "http://localhost:3001"),
        ("Prometheus",        "http://localhost:9090"),
        ("API Documentation", "http://localhost:8000/docs"),
    ]:
        st.markdown(f'<a class="ql" href="{url}" target="_blank">{label} →</a>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Refresh Status"):
        st.rerun()


# ── HERO ──────────────────────────────────────────────────────────
now = datetime.now()
st.markdown(f"""
<div class="hero">
    <div class="hero-eye">DevSecOps Intelligence Platform</div>
    <div class="hero-h">UtopiaHire <span>Security</span> Operations</div>
    <div class="hero-d">
        Unified security intelligence integrating static code analysis, dynamic scanning,
        network intrusion detection, and AI-powered vulnerability classification —
        fully automated through your Jenkins CI/CD pipeline.
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "  Code Security  ",
    "  Threat Monitoring  ",
    "  Operations  ",
    "  AI Analyst  ",
])


# ═══════════════════ TAB 1 ═══════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="sh"><span class="sb">Phase 01</span><span class="st">Code Security Analysis</span></div>
    <div class="ib c">
        Every Jenkins build runs two automated scans:
        <strong>Gitleaks</strong> checks all files and Git history for exposed secrets like API keys and passwords,
        and <strong>SonarQube</strong> performs static analysis to catch vulnerabilities and bugs in source code
        before they reach production.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">Secret Detection — Gitleaks</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">Gitleaks scans every file and commit for accidentally committed credentials, tokens, and API keys. Results below are from the latest Jenkins pipeline run.</div>', unsafe_allow_html=True)

        gl_path = "../security-reports/gitleaks-report.json"
        if os.path.exists(gl_path):
            with open(gl_path) as f:
                gl_data = json.load(f)
            if gl_data:
                st.markdown(f'<div class="ib p"><strong style="color:var(--pink)">{len(gl_data)} secret(s) detected</strong> — these credentials are exposed in the codebase and must be rotated immediately.</div>', unsafe_allow_html=True)
                for i, leak in enumerate(gl_data[:5], 1):
                    rule  = leak.get("RuleID", leak.get("Description", "UNKNOWN"))
                    fpath = leak.get("File", "Unknown file")
                    line  = leak.get("StartLine", "?")
                    sec   = (leak.get("Secret","")[:40]+"...") if leak.get("Secret","") else ""
                    st.markdown(f"""
                    <div class="fc">
                        <div class="fc-rule">{rule} {pill('CRITICAL')}</div>
                        <div class="fc-file">{fpath} · Line {line}</div>
                        {f'<div class="fc-desc">{sec}</div>' if sec else ''}
                    </div>
                    """, unsafe_allow_html=True)
                if len(gl_data) > 5:
                    st.markdown(f'<div style="font-size:11px;color:var(--white-40);margin-top:4px">+ {len(gl_data)-5} additional findings in full report</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ib g"><strong style="color:var(--green)">No secrets found.</strong> The repository is clean — no credentials or API keys detected.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ib">No report available. Trigger the Jenkins pipeline to generate a scan.</div>', unsafe_allow_html=True)

        if st.button("Run Gitleaks Scan"):
            with st.spinner("Scanning repository..."):
                r = run_docker(["run","--rm","-v",f"{os.path.abspath('..')}:/path",
                    "zricethezav/gitleaks:latest","detect","--source","/path","--exit-code","0"])
                st.code(r.stdout+r.stderr, language="text")

    with c2:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">Static Analysis — SonarQube</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">SonarQube reads your source code and detects security vulnerabilities, bugs, and bad practices without running the application. Updated on every Jenkins build.</div>', unsafe_allow_html=True)

        try:
            gr = requests.get("http://localhost:9000/api/qualitygates/project_status",
                params={"projectKey":"utopiahire"}, auth=("admin","admin"), timeout=3)
            gate = gr.json().get("projectStatus",{}).get("status","UNKNOWN")
            ok = gate == "OK"
            st.markdown(f"""
            <div class="mcard" style="margin-bottom:16px;border-color:{'rgba(0,229,160,0.3)' if ok else 'rgba(255,77,141,0.3)'}">
                <div class="mcard-glow" style="background:{'var(--green)' if ok else 'var(--pink)'}"></div>
                <div class="mcard-lbl">Quality Gate</div>
                <div class="mcard-val" style="color:{'var(--green)' if ok else 'var(--pink)'};font-size:22px">{'Passed' if ok else 'Failed'}</div>
                <div class="mcard-sub">{'All quality checks passed successfully' if ok else 'One or more quality conditions not met'}</div>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown('<div class="ib">SonarQube not reachable at localhost:9000</div>', unsafe_allow_html=True)

        try:
            ir = requests.get("http://localhost:9000/api/issues/search",
                params={"projectKeys":"utopiahire","types":"VULNERABILITY,BUG","ps":7},
                auth=("admin","admin"), timeout=3)
            issues = ir.json().get("issues",[])
            if issues:
                st.markdown(f'<div style="font-size:12px;font-weight:600;color:var(--white-60);margin-bottom:10px">{len(issues)} Issues Found</div>', unsafe_allow_html=True)
                st.markdown('<div class="mcard" style="padding:0;overflow:hidden">', unsafe_allow_html=True)
                for iss in issues:
                    sev  = iss.get("severity","INFO")
                    msg  = iss.get("message","")[:100]
                    comp = iss.get("component","").split(":")[-1]
                    line = iss.get("line","")
                    st.markdown(f"""
                    <div class="sc">
                        {pill(sev[:3])}
                        <div>
                            <div class="sc-msg">{msg}</div>
                            <div class="sc-file">{comp}{f' · line {line}' if line else ''}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        except: pass

        if st.button("Run Dependency Audit"):
            with st.spinner("Auditing dependencies..."):
                r = run_docker(["run","--rm","-v",f"{os.path.abspath('../backend')}:/app",
                    "python:3.11-slim","sh","-c","pip install pip-audit -q && pip-audit -r /app/requirements.txt"])
                st.code(r.stdout or r.stderr, language="text")


# ═══════════════════ TAB 2 ═══════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="sh"><span class="sb">Phase 02</span><span class="st">Threat Monitoring</span></div>
    <div class="ib c">
        Real-time and historical threat detection across two layers:
        <strong>Suricata IDS</strong> monitors every network packet entering the application and raises alerts
        when attack patterns are detected, and <strong>OWASP ZAP</strong> actively probes the live application
        to discover vulnerabilities that only appear at runtime.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">Network IDS — Suricata</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">Suricata inspects every network packet against thousands of attack signatures. It detects SQL injection attempts, port scans, brute force attacks, and malicious payloads in real time.</div>', unsafe_allow_html=True)

        up = container_running("utopiahire-suricata")
        if up:
            st.markdown('<div class="ib g"><strong style="color:var(--green)">Suricata is active</strong> and monitoring all network traffic.</div>', unsafe_allow_html=True)
            if st.button("Stop Suricata IDS"):
                run_docker(["stop","utopiahire-suricata"]); st.rerun()
        else:
            st.markdown('<div class="ib p"><strong style="color:var(--pink)">Suricata is offline.</strong> Network traffic is not being monitored.</div>', unsafe_allow_html=True)
            if st.button("Start Suricata IDS"):
                run_docker(["compose","-f","../docker-compose.devops.yml","up","-d","suricata"]); st.rerun()

        lp = "../suricata/logs/fast.log"
        if os.path.exists(lp):
            with open(lp, encoding="utf-8", errors="replace") as f:
                als = [l.strip() for l in f.readlines() if l.strip()]
            if als:
                st.markdown(f'<div style="font-size:12px;font-weight:600;color:var(--white-60);margin:12px 0 8px">{len(als)} Total Alerts — Last 8</div>', unsafe_allow_html=True)
                for line in als[-8:]:
                    st.markdown(f'<div class="ll">{line}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ib g">No alerts recorded. No malicious traffic detected.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ib">Suricata log not found at expected path.</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">Dynamic Scan — OWASP ZAP</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">ZAP actively attacks the running application to find vulnerabilities that static analysis cannot detect — XSS, injection, missing headers, authentication bypasses, and more.</div>', unsafe_allow_html=True)

        zp = "../security-reports/zap-report.json"
        if os.path.exists(zp):
            try:
                with open(zp) as f: zd = json.load(f)
                alts = zd.get("site",[{}])[0].get("alerts",[])
                hi = [a for a in alts if "High"   in a.get("riskdesc","")]
                me = [a for a in alts if "Medium" in a.get("riskdesc","")]
                pa = len(alts)-len(hi)-len(me)

                z1,z2,z3 = st.columns(3)
                for col, lbl, val, cls in [(z1,"High Risk",len(hi),"critical"),(z2,"Medium Risk",len(me),"high"),(z3,"Passed",pa,"safe")]:
                    with col:
                        st.markdown(f"""
                        <div class="mcard" style="padding:14px 16px;border-color:{B.get(cls,'var(--border)')}">
                            <div class="mcard-glow" style="background:{C.get(cls,'var(--cyan)')}"></div>
                            <div class="mcard-lbl">{lbl}</div>
                            <div class="mcard-val" style="font-size:22px;color:{C.get(cls,'var(--white)')}">{val}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                for a in (hi+me)[:5]:
                    is_hi = "High" in a.get("riskdesc","")
                    st.markdown(f"""
                    <div class="fc" style="border-left-color:{'var(--pink)' if is_hi else 'var(--orange)'}">
                        <div class="fc-rule" style="color:{'var(--pink)' if is_hi else 'var(--orange)'}">{a.get('name','?')} {pill('HIGH' if is_hi else 'MEDIUM')}</div>
                        <div class="fc-desc">{a.get('solution','No solution provided.')[:180]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="ib">Error reading ZAP report: {e}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ib">No ZAP report found. Run a scan to generate results.</div>', unsafe_allow_html=True)

        if st.button("Run ZAP Scan"):
            with st.spinner("Running dynamic scan (2-3 minutes)..."):
                run_docker(["run","--rm","--network","host",
                    "-v",f"{os.path.abspath('../security-reports')}:/zap/wrk:rw",
                    "ghcr.io/zaproxy/zaproxy:stable","zap-baseline.py",
                    "-t","http://172.17.0.1:8000","-r","zap-report.html","-J","zap-report.json","-I"])
                st.rerun()

        if st.button("Inspect Firewall Rules"):
            r = run_docker(["exec","utopiahire-backend","iptables","-L","INPUT","-n","-v"])
            st.code(r.stdout or r.stderr, language="text")


# ═══════════════════ TAB 3 ═══════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="sh"><span class="sb">Phase 03</span><span class="st">Operations Control</span></div>
    <div class="ib c">
        Direct control over your <strong>CI/CD pipeline and infrastructure</strong>.
        Trigger Jenkins builds, start or stop the application, and view the live status
        of all running containers. Every action here has immediate effect on the environment.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">CI/CD Pipeline — Jenkins</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">Trigger a new pipeline run. Jenkins will pull the latest code from GitHub and execute the full security pipeline: secret scanning, SAST, Docker builds, container scanning, DAST, and attack simulation.</div>', unsafe_allow_html=True)

        if st.button("Trigger Jenkins Pipeline"):
            try:
                resp = requests.post("http://localhost:8080/job/utopiahire-pipeline/build",
                    auth=("admin", os.getenv("JENKINS_PASSWORD","admin")))
                if resp.status_code in [200,201]:
                    st.markdown('<div class="ib g">Pipeline build triggered. Open Jenkins to monitor progress.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ib o">Response: HTTP {resp.status_code}</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="ib p">Cannot reach Jenkins. Verify the container is running.</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">Application Lifecycle</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">Start or stop the UtopiaHire backend and frontend containers.</div>', unsafe_allow_html=True)
        a1,a2 = st.columns(2)
        with a1:
            if st.button("Start Application"):
                run_docker(["compose","-f","../docker-compose.yml","up","-d"]); st.rerun()
        with a2:
            if st.button("Stop Application"):
                run_docker(["compose","-f","../docker-compose.yml","down"]); st.rerun()

    with c2:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">Running Containers</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">Live view of all Docker containers currently running in the UtopiaHire environment.</div>', unsafe_allow_html=True)
        r = run_docker(["ps","--format","table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
        st.code(r.stdout or "No containers running.", language="text")


# ═══════════════════ TAB 4 ═══════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="sh"><span class="sb">Phase 04</span><span class="st">AI Security Analyst</span></div>
    <div class="ib c">
        Three AI components work together: a <strong>Machine Learning classifier</strong> (SVM model,
        78.18% F1 score, trained on 1,100 NVD vulnerability records across 11 classes),
        a <strong>RAG knowledge base</strong> of 839 indexed CVE documents for contextual recommendations,
        and a <strong>LLaMA 3.1 agent running locally</strong> that reads your live scan results
        and delivers expert-level security analysis — no data leaves your machine.
    </div>
    """, unsafe_allow_html=True)

    # ── Threat Overview ───────────────────────────────────────────
    gl_c=sq_s=zh_c=su_c="?"
    gl_cl=sq_cl=zh_cl=su_cl="info"
    try:
        gp = "../security-reports/gitleaks-report.json"
        if os.path.exists(gp):
            d=json.load(open(gp)); gl_c=str(len(d)); gl_cl="critical" if len(d)>0 else "safe"
    except: pass
    try:
        r2=requests.get("http://localhost:9000/api/qualitygates/project_status",
            params={"projectKey":"utopiahire"},auth=("admin","admin"),timeout=2)
        sq_s=r2.json().get("projectStatus",{}).get("status","?"); sq_cl="safe" if sq_s=="OK" else "critical"
    except: pass
    try:
        zpp="../security-reports/zap-report.json"
        if os.path.exists(zpp):
            d2=json.load(open(zpp)); aa=d2.get("site",[{}])[0].get("alerts",[])
            zh=len([a for a in aa if "High" in a.get("riskdesc","")]); zh_c=str(zh); zh_cl="critical" if zh>0 else "safe"
    except: pass
    try:
        lpp="../suricata/logs/fast.log"
        if os.path.exists(lpp):
            with open(lpp,encoding="utf-8",errors="replace") as f: sc=len([l for l in f if l.strip()])
            su_c=str(sc); su_cl="high" if sc>0 else "safe"
    except: pass

    m1,m2,m3,m4 = st.columns(4, gap="medium")
    for col,lbl,val,cls,sub,icon in [
        (m1,"Gitleaks Secrets",  gl_c, gl_cl, "Credentials exposed",     "🔑"),
        (m2,"SonarQube Gate",    sq_s, sq_cl, "Code quality status",     "🔍"),
        (m3,"ZAP High Alerts",   zh_c, zh_cl, "Runtime vulnerabilities", "⚡"),
        (m4,"Suricata Alerts",   su_c, su_cl, "Network intrusions",      "🌐"),
    ]:
        with col:
            fs = "20px" if len(str(val))>3 else "28px"
            st.markdown(f"""
            <div class="mcard" style="border-color:{B.get(cls,'var(--border)')}">
                <div class="mcard-glow" style="background:{C.get(cls,'var(--cyan)')}"></div>
                <div class="mcard-icon">{icon}</div>
                <div class="mcard-lbl">{lbl}</div>
                <div class="mcard-val" style="color:{C.get(cls,'var(--white)')};font-size:{fs}">{val}</div>
                <div class="mcard-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    la, ra = st.columns([1,1], gap="large")

    with la:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">ML Vulnerability Classifier</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">Paste any code fragment, HTTP request, log entry, or payload. The SVM model classifies the vulnerability type and severity in under one second.</div>', unsafe_allow_html=True)

        ut = st.text_area("Input to classify", height=130,
            placeholder="e.g. SELECT * FROM users WHERE id='1' OR '1'='1'--")

        if st.button("Classify Vulnerability"):
            if ut.strip():
                with st.spinner("Running classification..."):
                    try:
                        vec=joblib.load("ml/vectorizer.pkl")
                        le=joblib.load("ml/label_encoder.pkl")
                        mdl=joblib.load("ml/svm_model.pkl")
                        X=vec.transform([ut])
                        lid=mdl.predict(X)[0]
                        label=le.inverse_transform([lid])[0]
                        sm={"sqli":"CRITICAL","rce":"CRITICAL","secret_exposure":"CRITICAL",
                            "xss":"HIGH","cmdi":"HIGH","csrf":"HIGH","file_upload":"HIGH",
                            "broken_access_control":"HIGH","path_traversal":"HIGH","ssrf":"HIGH","other":"MEDIUM"}
                        sev=sm.get(label,"MEDIUM")
                        sc=dr_class(sev)
                        readable=label.upper().replace("_"," ")
                        st.markdown(f"""
                        <div class="dbox">
                            <div class="dbox-hd"><div class="dbox-ti">Classification Result</div></div>
                            <div class="dr"><span class="dr-k">Vulnerability Type</span><span class="dr-v {sc}">{readable}</span></div>
                            <div class="dr"><span class="dr-k">Severity Level</span><span class="dr-v {sc}">{sev}</span></div>
                            <div class="dr"><span class="dr-k">Model</span><span class="dr-v">SVM + TF-IDF Vectorizer</span></div>
                            <div class="dr"><span class="dr-k">Training Set</span><span class="dr-v">1,100 NVD CVEs · 11 classes</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        try:
                            from rag_engine import search_knowledge_base
                            recs=search_knowledge_base(f"{label} vulnerability remediation",k=1)
                            if recs:
                                st.markdown('<div style="font-size:12px;font-weight:600;color:var(--white-60);margin:14px 0 8px">Knowledge Base Reference</div>', unsafe_allow_html=True)
                                st.markdown(f'<div class="ib c" style="font-size:12px">{recs[0].page_content[:500]}</div>', unsafe_allow_html=True)
                        except: pass
                    except FileNotFoundError:
                        st.markdown('<div class="ib p">Model files not found. Run the Part 1 training scripts first.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ib">Please enter text to classify.</div>', unsafe_allow_html=True)

    with ra:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--white);margin-bottom:10px">Security Analysis Agent</div>', unsafe_allow_html=True)
        st.markdown('<div class="ib" style="font-size:12px">The agent reads live data from Gitleaks, SonarQube, ZAP, and Suricata before responding. Powered by <strong>LLaMA 3.1:8b running locally</strong> — fully private, no internet required.</div>', unsafe_allow_html=True)

        if "messages" not in st.session_state: st.session_state.messages=[]
        if "history"  not in st.session_state: st.session_state.history=[]

        for msg in st.session_state.messages[-8:]:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if st.button("Run Full Security Analysis"):
            with st.spinner("Agent is reading all scan results..."):
                try:
                    from security_agent import ask_agent
                    resp=ask_agent(
                        "Read ALL available scan results from Gitleaks, SonarQube, ZAP, and Suricata. "
                        "Provide: 1) executive summary, 2) prioritised findings from critical to low, "
                        "3) specific remediation step for each finding.",
                        st.session_state.history)
                    st.session_state.messages.append({"role":"assistant","content":resp})
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="ib p">Agent error: {e}</div>', unsafe_allow_html=True)

        if q:=st.chat_input("Ask about any vulnerability, scan result, or fix strategy..."):
            st.session_state.messages.append({"role":"user","content":q})
            with st.chat_message("user"): st.markdown(q)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        from security_agent import ask_agent
                        resp=ask_agent(q,st.session_state.history)
                        st.markdown(resp)
                        st.session_state.messages.append({"role":"assistant","content":resp})
                        st.session_state.history.extend([("human",q),("ai",resp)])
                    except Exception as e:
                        st.markdown(f"Agent unavailable: {e}")
