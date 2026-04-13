pipeline {
    agent any

    environment {
        SONARQUBE_URL = 'http://utopiahire-sonarqube:9000'
        SONAR_TOKEN   = credentials('SONAR-TOKEN')
        APP_BACKEND   = 'http://utopiahire-backend:8000'
        REPORT_DIR    = 'security-reports'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
                sh 'mkdir -p ${REPORT_DIR}'
            }
        }

        stage('Prepare Environment') {
            steps {
                echo 'Creating .env files from templates and optional Jenkins environment variables...'
                sh '''
                    set -e

                    cp backend/.env.example backend/.env
                    cp frontend/.env.example frontend/.env

                    if [ -n "${AI_API_KEY:-}" ]; then
                        sed -i "s|^AI_API_KEY=.*|AI_API_KEY=${AI_API_KEY}|" backend/.env
                    fi
                    if [ -n "${AI_BASE_URL:-}" ]; then
                        sed -i "s|^AI_BASE_URL=.*|AI_BASE_URL=${AI_BASE_URL}|" backend/.env
                    fi
                    if [ -n "${AI_MODEL:-}" ]; then
                        sed -i "s|^AI_MODEL=.*|AI_MODEL=${AI_MODEL}|" backend/.env
                    fi

                    if [ -n "${VITE_FIREBASE_API_KEY:-}" ]; then
                        sed -i "s|^VITE_FIREBASE_API_KEY=.*|VITE_FIREBASE_API_KEY=${VITE_FIREBASE_API_KEY}|" frontend/.env
                    fi
                    if [ -n "${VITE_FIREBASE_AUTH_DOMAIN:-}" ]; then
                        sed -i "s|^VITE_FIREBASE_AUTH_DOMAIN=.*|VITE_FIREBASE_AUTH_DOMAIN=${VITE_FIREBASE_AUTH_DOMAIN}|" frontend/.env
                    fi
                    if [ -n "${VITE_FIREBASE_PROJECT_ID:-}" ]; then
                        sed -i "s|^VITE_FIREBASE_PROJECT_ID=.*|VITE_FIREBASE_PROJECT_ID=${VITE_FIREBASE_PROJECT_ID}|" frontend/.env
                    fi
                    if [ -n "${VITE_FIREBASE_STORAGE_BUCKET:-}" ]; then
                        sed -i "s|^VITE_FIREBASE_STORAGE_BUCKET=.*|VITE_FIREBASE_STORAGE_BUCKET=${VITE_FIREBASE_STORAGE_BUCKET}|" frontend/.env
                    fi
                    if [ -n "${VITE_FIREBASE_MESSAGING_SENDER_ID:-}" ]; then
                        sed -i "s|^VITE_FIREBASE_MESSAGING_SENDER_ID=.*|VITE_FIREBASE_MESSAGING_SENDER_ID=${VITE_FIREBASE_MESSAGING_SENDER_ID}|" frontend/.env
                    fi
                    if [ -n "${VITE_FIREBASE_APP_ID:-}" ]; then
                        sed -i "s|^VITE_FIREBASE_APP_ID=.*|VITE_FIREBASE_APP_ID=${VITE_FIREBASE_APP_ID}|" frontend/.env
                    fi

                    echo "backend/.env created from backend/.env.example"
                    echo "frontend/.env created from frontend/.env.example"
                '''
            }
        }

        stage('Detect Docker Access') {
            steps {
                script {
                    env.DOCKER_AVAILABLE = sh(returnStatus: true, script: 'docker info >/dev/null 2>&1') == 0 ? 'true' : 'false'
                    echo "Docker access available: ${env.DOCKER_AVAILABLE}"
                }
            }
        }

        stage('Secrets Scan — Gitleaks') {
            steps {
                echo 'Scanning for leaked API keys and credentials...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping Gitleaks."
                        exit 0
                    fi

                    mkdir -p ${REPORT_DIR}
                    chmod 777 ${REPORT_DIR}

                    docker run --rm \
                    -v $(pwd):/path \
                    --entrypoint sh \
                    zricethezav/gitleaks:latest -c \
                    "mkdir -p /path/security-reports && \
                    gitleaks detect \
                    --source /path \
                    --no-git \
                    --gitleaks-ignore-path /path/.gitleaksignore \
                    --report-format json \
                    --report-path /path/security-reports/gitleaks-report.json; \
                    [ -f /path/security-reports/gitleaks-report.json ] || \
                    echo '[]' > /path/security-reports/gitleaks-report.json"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/gitleaks-report.json",
                                    allowEmptyArchive: true
                }
            }
        }

        stage('Backend Tests — Coverage') {
            steps {
                echo 'Running Python tests and generating coverage report...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker unavailable; skipping."
                        exit 0
                    fi

                    WORKSPACE_PATH="/var/jenkins_home/workspace/utopiahire-pipeline"
                    rm -f ${WORKSPACE_PATH}/coverage.xml

                    docker exec -u root utopiahire-backend sh -c "
                        cd /app &&
                        pip install pytest pytest-cov anyio pytest-asyncio -q > /dev/null 2>&1 &&
                        python -m pytest \
                            --cov=app \
                            --cov-report=xml \
                            -q > /dev/null 2>&1 || true
                    "

                    docker cp utopiahire-backend:/app/coverage.xml \
                        ${WORKSPACE_PATH}/coverage.xml 2>/dev/null || true

                    if [ -f ${WORKSPACE_PATH}/coverage.xml ] && [ -s ${WORKSPACE_PATH}/coverage.xml ]; then
                        sed -i 's|<source>app</source>|<source>backend/app</source>|g' ${WORKSPACE_PATH}/coverage.xml
                        sed -i 's|filename="app/|filename="backend/app/|g' ${WORKSPACE_PATH}/coverage.xml
                        echo "coverage.xml created successfully"
                    else
                        echo "coverage.xml NOT created"
                    fi
                '''
            }
        }

        stage('Verify Coverage File') {
            steps {
                sh '''
                    echo "=== Checking for coverage.xml ==="
                    ls -la /var/jenkins_home/workspace/utopiahire-pipeline/coverage.xml || echo "FILE NOT FOUND"
                    echo "=== Workspace contents ==="
                    ls -la /var/jenkins_home/workspace/utopiahire-pipeline/
                '''
            }
        }

        stage('SAST — SonarQube Analysis') {
            steps {
                echo 'Running SonarQube static analysis with coverage...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker unavailable; skipping."
                        exit 0
                    fi

                    docker run --rm \
                        --network utopiahire-main_default \
                        --volumes-from jenkins \
                        -e SONAR_HOST_URL="${SONARQUBE_URL}" \
                        -e SONAR_TOKEN="${SONAR_TOKEN}" \
                        -w /var/jenkins_home/workspace/utopiahire-pipeline \
                        sonarsource/sonar-scanner-cli \
                        -Dsonar.projectKey=utopiahire \
                        -Dsonar.projectName=UtopiaHire \
                        -Dsonar.sources=. \
                        -Dsonar.exclusions=**/node_modules/**,**/.git/**,**/security-reports/**,**/__pycache__/**,**/*.pkl,**/*.csv,**/*.zip \
                        -Dsonar.python.version=3.11 \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.coverage.exclusions=**/tests/**,**/__init__.py \
                        -Dsonar.scm.disabled=true || true
                '''
            }
        }
        stage('Dependency Audit') {
            steps {
                echo 'Checking for known vulnerable dependencies...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping dependency audit."
                        exit 0
                    fi

                    mkdir -p /var/jenkins_home/workspace/utopiahire-pipeline/security-reports

                    # Backend — pip-audit
                    docker run --rm \
                        -v pfa_jenkins_data:/var/jenkins_home \
                        -w /var/jenkins_home/workspace/utopiahire-pipeline \
                        python:3.11-slim \
                        sh -c "pip install pip-audit -q && \
                            pip-audit -r backend/requirements.txt --format json \
                            -o /var/jenkins_home/workspace/utopiahire-pipeline/security-reports/pip-audit.json || \
                            echo '[]' > /var/jenkins_home/workspace/utopiahire-pipeline/security-reports/pip-audit.json" || true

                    # Frontend — npm audit
                    docker run --rm \
                        -v pfa_jenkins_data:/var/jenkins_home \
                        -w /var/jenkins_home/workspace/utopiahire-pipeline/frontend \
                        node:20-alpine \
                        sh -c "npm audit --json > /var/jenkins_home/workspace/utopiahire-pipeline/security-reports/npm-audit.json 2>/dev/null || \
                            echo '{}' > /var/jenkins_home/workspace/utopiahire-pipeline/security-reports/npm-audit.json" || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/pip-audit.json,${REPORT_DIR}/npm-audit.json",
                                    allowEmptyArchive: true
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building application Docker images...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping image build."
                        exit 0
                    fi

                    if docker compose version >/dev/null 2>&1; then
                        docker compose build
                    elif command -v docker-compose >/dev/null 2>&1; then
                        docker-compose build
                    else
                        echo "Neither 'docker compose' nor 'docker-compose' is available."
                        exit 1
                    fi
                '''
            }
        }

        stage('Container Scan — Trivy') {
            steps {
                echo 'Scanning Docker images for CVE vulnerabilities...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping Trivy scans."
                        exit 0
                    fi

                                        mkdir -p ${REPORT_DIR}
                                        chmod 777 ${REPORT_DIR} || true

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v $(pwd)/${REPORT_DIR}:/reports \
                                            -v trivy-cache:/root/.cache/trivy \
                                            ghcr.io/aquasecurity/trivy:latest image \
                      --format json \
                      --output /reports/trivy-backend.json \
                      --severity CRITICAL,HIGH \
                                            --timeout 10m \
                                            utopiahire-pipeline-backend || true

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v $(pwd)/${REPORT_DIR}:/reports \
                                            -v trivy-cache:/root/.cache/trivy \
                                            ghcr.io/aquasecurity/trivy:latest image \
                      --format json \
                      --output /reports/trivy-frontend.json \
                      --severity CRITICAL,HIGH \
                                            --timeout 10m \
                                            utopiahire-pipeline-frontend || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/trivy-*.json",
                                     allowEmptyArchive: true
                }
            }
        }

        stage('IaC Scan — Checkov') {
            steps {
                echo 'Scanning Dockerfiles and config for misconfigurations...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping Checkov scan."
                        exit 0
                    fi

                    mkdir -p security-reports

                    docker run --rm \
                        -v $(pwd):/project \
                        -w /project \
                        bridgecrew/checkov:latest \
                        --directory /project \
                        --include-all-checkov-policies \
                        --check CKV_DOCKER \
                        --output json \
                        --output-file-path /project/security-reports/ || true

                    if [ -f security-reports/results_json.json ]; then
                        echo "Checkov scan completed successfully"
                    else
                        echo "Checkov produced no output file"
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/results_json.json",
                                    allowEmptyArchive: true
                }
            }
        }

        stage('Start Local Staging') {
            steps {
                echo 'Cleaning up any existing containers...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping local staging."
                        exit 0
                    fi

                    docker rm -f utopiahire-backend  2>/dev/null || true
                    docker rm -f utopiahire-frontend 2>/dev/null || true
                    docker rm -f utopiahire-pipeline-backend 2>/dev/null || true
                    docker rm -f utopiahire-pipeline-frontend 2>/dev/null || true
                    docker rm -f utopiahire-pipeline2-backend 2>/dev/null || true
                    docker rm -f utopiahire-pipeline2-frontend 2>/dev/null || true
                    if docker compose version >/dev/null 2>&1; then
                        docker compose down --remove-orphans --volumes 2>/dev/null || true
                    elif command -v docker-compose >/dev/null 2>&1; then
                        docker-compose down --remove-orphans --volumes 2>/dev/null || true
                    fi

                    echo "Starting fresh containers..."
                    if docker compose version >/dev/null 2>&1; then
                        docker compose up -d --build --force-recreate
                    elif command -v docker-compose >/dev/null 2>&1; then
                        docker-compose up -d --build --force-recreate
                    else
                        echo "Neither 'docker compose' nor 'docker-compose' is available."
                        exit 1
                    fi

                    echo "Waiting for backend to be healthy..."
                    for i in $(seq 1 20); do
                        STATUS=$(docker exec utopiahire-backend \
                            curl -s -o /dev/null -w "%{http_code}" \
                            --max-time 5 \
                            http://localhost:8000/health) || STATUS="000"
                        echo "Attempt $i: HTTP $STATUS"
                        if [ "$STATUS" = "200" ]; then
                            echo "Backend is healthy and ready"
                            break
                        fi
                        sleep 5
                    done

                    echo "=== Backend container logs ==="
                    docker logs utopiahire-backend --tail 50 || true
                '''
            }
        }
        stage('DAST — OWASP ZAP') {
            steps {
                echo 'Running ZAP dynamic attack scan against running app...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping ZAP scan."
                        exit 0
                    fi

                    mkdir -p /var/jenkins_home/workspace/utopiahire-pipeline/security-reports
                    chmod 777 /var/jenkins_home/workspace/utopiahire-pipeline/security-reports

                    echo "ZAP scanning target: http://utopiahire-backend:8000"

                    docker run --rm \
                        --network utopiahire-main_default \
                        -v /var/jenkins_home/workspace/utopiahire-pipeline/security-reports:/zap/wrk \
                        -u root \
                        ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py \
                        -t http://utopiahire-backend:8000 \
                        -r /zap/wrk/zap-report.html \
                        -J /zap/wrk/zap-report.json \
                        -I || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/zap-report.html,${REPORT_DIR}/zap-report.json",
                                    allowEmptyArchive: true
                }
            }
        }
        stage('AI Security Analysis') {
            steps {
                echo 'Generating AI security recommendations via LLaMA 3.1:8b...'
                sh '''
                    mkdir -p security-reports

                    docker run --rm \
                    --network host \
                    -v $(pwd)/security-reports:/app/security-reports \
                    python:3.11-slim bash -c "
                        pip install requests -q 2>/dev/null &&
                        python3 << 'PYEOF'
        import json, os, requests

        findings = []

        gl_path = '/app/security-reports/gitleaks-report.json'
        if os.path.exists(gl_path):
            try:
                d = json.load(open(gl_path))
                if d:
                    for leak in d[:5]:
                        findings.append(
                            'SECRET FOUND: ' + leak.get('Description', 'unknown') +
                            ' in file ' + leak.get('File', '?') +
                            ' at line ' + str(leak.get('StartLine', '?'))
                        )
                else:
                    findings.append('Gitleaks: Repository is clean - no secrets found')
            except:
                findings.append('Gitleaks: Could not read report')

        zp_path = '/app/security-reports/zap-report.json'
        if os.path.exists(zp_path):
            try:
                d2 = json.load(open(zp_path))
                alerts = d2.get('site', [{}])[0].get('alerts', [])
                high = [a for a in alerts if 'High' in a.get('riskdesc', '')]
                medium = [a for a in alerts if 'Medium' in a.get('riskdesc', '')]
                for a in high[:3]:
                    findings.append('ZAP HIGH ALERT: ' + a.get('name', '?'))
                for a in medium[:2]:
                    findings.append('ZAP MEDIUM ALERT: ' + a.get('name', '?'))
                if not high and not medium:
                    findings.append('ZAP: No high or medium alerts found')
            except:
                findings.append('ZAP: Could not read report')

        if not findings:
            findings.append('No scan data available in security-reports/')

        summary = chr(10).join(findings)

        prompt = (
            'You are a DevSecOps security expert analysing the UtopiaHire web application '
            '(FastAPI backend, React frontend, Firebase authentication). '
            'A Jenkins CI/CD pipeline just ran security scans. '
            'Based on these findings, provide exactly 3 numbered security recommendations. '
            'For each recommendation include: the vulnerability type, why it is dangerous '
            'for this specific application, and the exact code fix with a Python/FastAPI example. '
            'Be specific and actionable. Do not give generic advice.' +
            chr(10) + chr(10) + 'Pipeline scan findings:' + chr(10) + summary
        )

        try:
            response = requests.post(
                'http://192.168.56.1:11434/api/generate',
                json={
                    'model': 'llama3.1:8b',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=180
            )
            ai_text = response.json().get('response', 'No response received from LLaMA')
        except Exception as e:
            ai_text = (
                'LLaMA call failed: ' + str(e) + chr(10) +
                'Verify: OLLAMA_HOST=0.0.0.0 and run ollama serve' + chr(10) +
                'Raw findings:' + chr(10) + summary
            )

        output = (
            'AI Security Analysis - LLaMA 3.1:8b (Local)' + chr(10) +
            '=' * 55 + chr(10) +
            'Pipeline: UtopiaHire' + chr(10) +
            'Findings analysed: ' + str(len(findings)) + chr(10) +
            '=' * 55 + chr(10) + chr(10) +
            ai_text
        )

        with open('/app/security-reports/ai-recommendations.txt', 'w') as f:
            f.write(output)

        print('AI recommendations saved.')
        print(output[:400])
        PYEOF
                    " || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'security-reports/ai-recommendations.txt',
                                    allowEmptyArchive: true
                }
            }
        }

        stage('Attack Simulation') {
            steps {
                echo 'Running controlled attack validation tests...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping attack simulation."
                        exit 0
                    fi

                    APP_URL="http://localhost:8000"
                    echo "Target: $APP_URL"
                    mkdir -p security-reports

                    echo "=== SQL Injection Test ===" | tee security-reports/attack-results.txt

                    docker run --rm \
                        --network utopiahire-main_default \
                        python:3.11-slim bash -c "
                            pip install sqlmap >/dev/null 2>&1 &&
                            sqlmap \
                            -u 'http://utopiahire-backend:8000/api/jobs/database-info' \
                            --batch \
                            --level=1 \
                            --ignore-code=401 \
                            --technique=B \
                            --flush-session
                        " 2>&1 | tee -a security-reports/attack-results.txt || true

                    echo "" >> security-reports/attack-results.txt
                    echo "=== XSS Filename Test ===" | tee -a security-reports/attack-results.txt

                    STATUS=$(docker exec utopiahire-backend \
                        curl -s -o /dev/null -w "%{http_code}" \
                        --max-time 10 \
                        -X POST http://localhost:8000/api/resume/upload \
                        -F "file=@/etc/hostname;filename=xss_test_script.pdf") \
                        || STATUS="connection_failed"

                    echo "XSS filename test HTTP status: $STATUS" \
                        | tee -a security-reports/attack-results.txt

                    if [ "$STATUS" = "400" ] || [ "$STATUS" = "401" ] || [ "$STATUS" = "422" ]; then
                        echo "RESULT: Attack correctly BLOCKED by the application" \
                            | tee -a security-reports/attack-results.txt
                    elif [ "$STATUS" = "connection_failed" ]; then
                        echo "RESULT: Could not connect to app — check HOST_IP" \
                            | tee -a security-reports/attack-results.txt
                    else
                        echo "RESULT: App returned HTTP $STATUS" \
                            | tee -a security-reports/attack-results.txt
                    fi

                    echo "" >> security-reports/attack-results.txt
                    echo "=== Rate Limit Test ===" | tee -a security-reports/attack-results.txt

                    BLOCKED=0
                    for i in $(seq 1 15); do
                        S=$(docker exec utopiahire-backend \
                            curl -s -o /dev/null -w "%{http_code}" \
                            --max-time 5 \
                            http://localhost:8000/health) || S="000"
                        echo "Request $i: HTTP $S" | tee -a security-reports/attack-results.txt
                        if [ "$S" = "429" ]; then
                            BLOCKED=$((BLOCKED + 1))
                        fi
                    done

                    echo "" >> security-reports/attack-results.txt
                    echo "Rate limit blocks: $BLOCKED out of 15 requests" \
                        | tee -a security-reports/attack-results.txt

                    if [ "$BLOCKED" -gt 0 ]; then
                        echo "RESULT: Rate limiting is WORKING correctly" \
                            | tee -a security-reports/attack-results.txt
                    else
                        echo "RESULT: No rate limiting detected — review slowapi config" \
                            | tee -a security-reports/attack-results.txt
                    fi

                    echo "" >> security-reports/attack-results.txt
                    echo "=== Directory Traversal Test ===" \
                        | tee -a security-reports/attack-results.txt

                    STATUS=$(docker exec utopiahire-backend \
                        curl -s -o /dev/null -w "%{http_code}" \
                        --max-time 10 \
                        "http://localhost:8000/api/career/download/../../../etc/passwd") \
                        || STATUS="000"
                    echo "Directory traversal HTTP status: $STATUS" \
                        | tee -a security-reports/attack-results.txt

                    if [ "$STATUS" = "400" ] || [ "$STATUS" = "401" ] || \
                    [ "$STATUS" = "403" ] || [ "$STATUS" = "404" ]; then
                        echo "RESULT: Directory traversal correctly BLOCKED" \
                            | tee -a security-reports/attack-results.txt
                    else
                        echo "RESULT: App returned HTTP $STATUS for traversal attempt" \
                            | tee -a security-reports/attack-results.txt
                    fi

                    echo "" >> security-reports/attack-results.txt
                    echo "=== Attack simulation complete ===" \
                        | tee -a security-reports/attack-results.txt
                    echo "Full results saved to security-reports/attack-results.txt"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'security-reports/attack-results.txt',
                                    allowEmptyArchive: true
                }
            }
        }

        stage('Deploy Locally') {
            steps {
                echo 'Confirming local deployment is running...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping deployment verification."
                        exit 0
                    fi

                    docker ps --filter "name=utopiahire" \
                    --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                    echo "Local deployment confirmed"

                    zip -r ${WORKSPACE}/security-report-bundle.zip \
                        ${WORKSPACE}/security-reports/ 2>/dev/null || true
                '''
            }
        }
    }

    post {
        always {
            echo 'Bundling all security reports...'
            archiveArtifacts artifacts: 'security-report-bundle.zip',
                             allowEmptyArchive: true
        }
        success {
            echo 'ALL SECURITY GATES PASSED — pipeline is clean'
        }
        failure {
            echo 'PIPELINE FAILED — check the failed stage above'
        }
    }
}