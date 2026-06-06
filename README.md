# UtopiaHire — AI-Powered DevSecOps Security Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-lightgrey)]()
[![React](https://img.shields.io/badge/React-18.3.1-blue)]()
[![Docker](https://img.shields.io/badge/Docker-enabled-blue)]()
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-orange)]()
[![SonarQube](https://img.shields.io/badge/SonarQube-SAST-yellow)]()
[![AI](https://img.shields.io/badge/AI-LLaMA%203.1%3A8b-purple)]()
[![License](https://img.shields.io/badge/License-Academic-green)]()

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Security Features](#security-features)
- [Jenkins Pipeline](#jenkins-pipeline)
- [AI Security System](#ai-security-system)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Service URLs](#service-urls)
- [Dashboard Usage](#dashboard-usage)
- [Project Structure](#project-structure)
- [Vulnerability Findings](#vulnerability-findings)
- [ML Model Comparison](#ml-model-comparison)
- [Technology Stack](#technology-stack)
- [Important Notes](#important-notes)
- [Authors](#authors)

---

## Project Overview

UtopiaHire is a full-stack AI-powered recruitment platform built for job seekers in the MENA region. It combines a **FastAPI backend**, **React + Vite frontend**, **Firebase authentication**, and an AI resume analysis layer.

This repository implements a **complete DevSecOps security system** around the platform, covering three layers:

- **Application hardening** — 10 vulnerabilities identified in Phase 0 and fully remediated
- **Automated CI/CD security pipeline** — 16 Jenkins stages running on every GitHub push
- **AI security intelligence layer** — SVM classifier + LLaMA 3.1:8b agent + FAISS RAG knowledge base

> All security components run **entirely on-premise**. No security data is sent to external APIs. No cloud inference. No recurring cost.

---

## Architecture

┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                        │
│   React Frontend (3000)  ──►  FastAPI Backend (8000)            │
│           │                         │                           │
│    Firebase Auth              OpenAI / AI API                   │
└─────────────────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────────────┐
│                       DEVSECOPS LAYER                           │
│  Jenkins (8080) ──► SonarQube (9000) ──► Trivy ──► Checkov      │
│  Gitleaks ──► pip-audit / npm-audit ──► OWASP ZAP               │
│  Suricata IDS ──► iptables ──► Prometheus (9090) ──► Grafana    │
└─────────────────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────────────┐
│                      AI SECURITY LAYER                          │
│  SVM Classifier (72.73% accuracy)                               │
│  LLaMA 3.1:8b via Ollama ──► LangGraph ReAct Agent              │
│  FAISS RAG ──► 839 NVD CVE documents ──► all-MiniLM-L6-v2       │
│  Streamlit Dashboard (8501)                                     │
└─────────────────────────────────────────────────────────────────┘

---

## Security Features

### Static Analysis
- **Gitleaks** — full git history scan for committed secrets and API keys
- **SonarQube** — SAST with coverage integration, quality gate enforcement
- **Dependency audit** — `pip-audit` (backend) and `npm audit` (frontend)

### Dynamic Analysis
- **OWASP ZAP** — DAST against live staging environment
- **Attack simulation** — controlled SQL injection, XSS, path traversal, and rate limit tests

### Container Security
- **Trivy** — Docker image CVE scanning (Critical and High only)
- **Checkov** — IaC misconfiguration analysis on Dockerfiles and Compose files
- **Non-root users** — `USER appuser` directive in all production Dockerfiles
- **HEALTHCHECK** directives on all application containers

### Runtime Security
- **Suricata IDS** — 7 custom rules monitoring the Docker bridge network
- **iptables** — container-level network filtering
- **Prometheus** — FastAPI metrics scraping every 15 seconds
- **Grafana** — real-time dashboards for request rate, error rate, response time, and rate limit blocks

### AI Security Intelligence
- **SVM classifier** — 72.73% accuracy, 86.36% precision on real UtopiaHire findings
- **LLaMA 3.1:8b agent** — LangGraph ReAct with 5 live security tools
- **FAISS RAG** — 839 NVD CVE documents, HuggingFace all-MiniLM-L6-v2 embeddings
- **Streamlit dashboard** — interactive AI analyst at localhost:8501

### Application Hardening
- Rate limiting via `slowapi` — `@limiter.limit("10/minute")` on AI endpoints
- CORS restricted to explicit origin allowlist — no wildcard
- Security headers middleware — HSTS, X-Frame-Options, X-Content-Type-Options
- MIME type validation via `python-magic` + 5MB file size limit
- JWT ownership verification on all resource endpoints
- Prompt injection protection — XML delimiter wrapping for user content

---

## Jenkins Pipeline

Defined entirely in `Jenkinsfile` — triggered automatically by GitHub webhook on every push to `main`. All secrets injected at runtime via Jenkins credentials store — never stored in the repository.

| Stage | Description |
|---|---|
| 1 — Checkout | Pull latest code from GitHub |
| 2 — Prepare Environment | Create .env files from templates, inject credentials |
| 3 — Detect Docker Access | Verify Docker daemon is accessible from Jenkins agent |
| 4 — Secrets Scan (Gitleaks) | Scan git history for committed credentials |
| 5 — Backend Tests + Coverage | Run Python test suite, generate coverage.xml |
| 6 — Verify Coverage File | Confirm coverage artifact exists in workspace |
| 7 — SAST (SonarQube) | Static analysis with coverage, quality gate enforcement |
| 8 — Dependency Audit | pip-audit + npm audit against NVD database |
| 9 — Build Docker Images | Build hardened backend and frontend images |
| 10 — Container Scan (Trivy) | CVE scan on built images — fail on Critical/High |
| 11 — IaC Scan (Checkov) | Dockerfile and Compose misconfiguration analysis |
| 12 — Start Local Staging | Launch containers, wait for backend health check |
| 13 — DAST (OWASP ZAP) | Dynamic scan against live staging environment |
| 14 — AI Security Analysis | LLaMA reads all reports, generates recommendations |
| 15 — Attack Simulation | Controlled injection, traversal, and rate limit tests |
| 16 — Deploy Locally | Confirm deployment, bundle and archive all reports |

---

## AI Security System

### ML Classifier
- **Model:** SVM (`LinearSVC`) with TF-IDF vectorization (bigrams, 5,000 terms, sublinear scaling)
- **Training data:** 1,100 balanced NVD CVE entries across 11 vulnerability classes
- **Test set:** Real UtopiaHire vulnerabilities identified during Phase 0 security audit
- **Selected model:** SVM — 72.73% accuracy, 86.36% precision, 78.18% F1

### RAG Knowledge Base
- **Index:** FAISS vector store — 839 NVD CVE documents indexed
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` — 384 dimensions, 22MB, CPU-only
- **Retrieval:** Top-3 semantically similar CVEs returned per query as grounding context
- **Location:** `dashboard/knowledge_base/security_vectordb/`

### LangGraph Security Agent
- **LLM:** LLaMA 3.1:8b via Ollama (local inference, no external API)
- **Framework:** LangGraph `create_react_agent` — ReAct reasoning loop
- **Tools:** 5 live tools reading from Gitleaks, SonarQube, ZAP, Suricata, and SVM model
- **Output format:** WHAT / WHY DANGEROUS / HOW TO FIX / PRIORITY

---

## Prerequisites

- Docker Desktop (Windows) with Compose V2
- Ollama installed with `llama3.1:8b` pulled: `ollama pull llama3.1:8b`
- Python 3.11+
- Node.js 18+ and npm
- Git

---

## Installation and Setup

**Step 1 — Clone the repository**
```bash
git clone https://github.com/nour-moalla/PFA.git
cd PFA
```

**Step 2 — Start the application stack**
```bash
docker compose up -d
```

**Step 3 — Start the DevSecOps stack**
```bash
docker compose -f docker-compose.devops.yml up -d
```

**Step 4 — Reinstall Docker inside Jenkins**  
Required after every PC restart:
```bash
docker exec -u root jenkins bash -c \
  "apt-get update -qq && apt-get install -y docker.io \
  && chmod 666 /var/run/docker.sock"
```

**Step 5 — Connect Jenkins to the application network**
```bash
docker network connect utopiahire-main_default jenkins
```

**Step 6 — Start Ollama** (keep this terminal open)
```bash
ollama serve
```

**Step 7 — Set up and start the AI dashboard**
```bash
cd dashboard
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install streamlit langchain-core langchain-community \
  langchain-ollama langgraph joblib scikit-learn pandas \
  faiss-cpu sentence-transformers requests

streamlit run app.py
```

---

## Service URLs

| Service | URL |
|---|---|
| UtopiaHire Frontend | http://localhost:3000 |
| FastAPI Backend | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Jenkins Pipeline | http://localhost:8080 |
| SonarQube | http://localhost:9000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |
| AI Security Dashboard | http://localhost:8501 |
| Ollama API | http://localhost:11434 |

---

## Dashboard Usage

The Streamlit dashboard provides four tabs:

**Code Security** — Gitleaks secrets findings, SonarQube SAST results, dependency audit output.

**Threat Monitoring** — Suricata IDS live alerts, OWASP ZAP DAST results, network intrusion events.

**Operations** — Running container status, Jenkins pipeline controls, infrastructure health.

**AI Analyst** — Three AI capabilities:
- **ML Classifier:** Paste any text (code, payload, log entry, CVE description) → click *Classify Vulnerability* → SVM returns category and severity in under 1 second
- **Full Security Analysis:** Click *Run Full Security Analysis* → LLaMA agent reads all live scan outputs and returns a prioritized remediation report
- **Security Chat:** Ask any natural language question about your security posture → agent calls the relevant tools and responds with RAG-grounded answers

---

## Project Structure

```
UtopiaHire/
│
├── backend/                         FastAPI backend (port 8000)
│   ├── app/
│   │   ├── routers/                 resume, interview, career endpoints
│   │   ├── core/                    auth, config, ai_service, upload_validation
│   │   └── main.py
│   └── Dockerfile
│
├── frontend/                        React + Vite frontend (port 3000)
│   ├── src/
│   └── Dockerfile
│
├── dashboard/                       Streamlit AI security dashboard (port 8501)
│   ├── app.py                       Main dashboard — 4 tabs
│   ├── tools/
│   │   ├── agent_tools.py           5 LangGraph tools
│   │   ├── security_agent.py        LangGraph ReAct agent + LLaMA
│   │   └── rag_engine.py            FAISS index builder and search
│   ├── ml/
│   │   ├── train_and_compare.py
│   │   ├── svm_model.pkl            Production model
│   │   ├── vectorizer.pkl
│   │   ├── label_encoder.pkl
│   │   └── model_comparison.csv
│   ├── data/
│   │   ├── raw_dataset.csv
│   │   ├── cleaned_dataset.csv
│   │   ├── labelled_dataset.csv
│   │   ├── balanced_dataset.csv
│   │   └── test_set.csv
│   └── knowledge_base/
│       └── security_vectordb/       FAISS index — 839 CVE documents
│
├── suricata/
│   └── rules/
│       └── utopiahire.rules         7 custom IDS rules
│
├── monitoring/                      Prometheus config + Grafana dashboards
├── security-reports/                Pipeline artifacts (Gitleaks, ZAP, Trivy, AI)
├── Jenkinsfile                      16-stage CI/CD pipeline
├── docker-compose.yml               Application stack
└── docker-compose.devops.yml        DevSecOps stack
```

---

## Vulnerability Findings

10 vulnerabilities identified during Phase 0 security audit of the UtopiaHire codebase.

| ID | Vulnerability | Severity | Status |
|---|---|---|---|
| UTH-001 | Exposed API key committed in repository | Critical | Fixed |
| UTH-002 | Wildcard CORS policy (`allow_origins=["*"]`) | Critical | Fixed |
| UTH-003 | Broken access control — missing server-side auth | Critical | Fixed |
| UTH-004 | Docker socket privilege escalation vector | Critical | Partial |
| UTH-005 | Interview session IDOR | High | Fixed |
| UTH-006 | Path traversal in PDF download endpoint | High | Fixed |
| UTH-007 | Missing rate limiting on AI endpoints | High | Fixed |
| UTH-008 | Prompt injection in LLM flows | High | Fixed |
| UTH-009 | Weak file upload validation (extension-only check) | High | Fixed |
| UTH-010 | Sensitive data exposure in application logs | Medium | Fixed |

> UTH-004 is marked **Partial** — the Docker socket must remain accessible to Jenkins for pipeline execution. All application containers run as non-root users as a compensating control.

---

## ML Model Comparison

Three models trained on 1,100 balanced NVD CVE entries and evaluated on a custom test set of real UtopiaHire vulnerabilities.

| Model | Accuracy | Precision | F1 Score | |
|---|---|---|---|---|
| Random Forest | 36.36% | 54.55% | 40.91% | |
| Logistic Regression | 45.45% | 68.18% | 51.82% | |
| **SVM (LinearSVC)** | **72.73%** | **86.36%** | **78.18%** | ✅ Selected |

SVM selected as the production model — highest performance across all metrics, consistent with NLP literature on sparse TF-IDF text classification.

---

## Technology Stack

| Category | Technologies |
|---|---|
| Application | Python 3.11, FastAPI, Uvicorn, React 18, Vite, Firebase |
| CI/CD | Jenkins, Docker, Docker Compose |
| Security Scanning | Gitleaks, SonarQube, OWASP ZAP, Trivy, Checkov, pip-audit, npm-audit |
| Monitoring | Prometheus, Grafana, Suricata IDS, iptables |
| AI / ML | scikit-learn, FAISS, sentence-transformers, Ollama, LLaMA 3.1:8b, LangGraph, LangChain, Streamlit |
| Infrastructure | Docker Compose, Jenkins agent, Bash scripts |

---

## Important Notes

- The `.env` files contain intentional test credentials kept as evidence for Gitleaks detection demonstration. Rotate all credentials before any production use.
- All AI inference runs locally via Ollama. No security data is transmitted to external services.
- After every PC restart, Docker must be reinstalled inside the Jenkins container (Step 4 above). This is a known requirement for the local CI setup.
- The pre-commit hook in `.git/hooks/pre-commit` uses LLaMA to analyse changed Python files for security vulnerabilities before every commit. Requires Ollama to be running.

---

## Authors

**Nour Moalla**  — University end-of-year project (PFA — Projet de Fin d'Année)

> Repository: [github.com/nour-moalla/PFA](https://github.com/nour-moalla/PFA)
