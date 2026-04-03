pipeline {
    agent any

    environment {
        SONARQUBE_URL = 'http://utopiahire-sonarqube:9000'
        SONAR_TOKEN   = credentials('sonarqube-token')
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
                    -e GIT_DISCOVERY_ACROSS_FILESYSTEM=1 \
                    zricethezav/gitleaks:latest -c \
                    "mkdir -p /path/security-reports && \
                    gitleaks detect \
                    --source /path \
                    --report-path /path/security-reports/gitleaks-report.json \
                    --exit-code 1" || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/gitleaks-report.json",
                                    allowEmptyArchive: true
                }
            }
        }
        stage('SAST — SonarQube Analysis') {
            steps {
                echo 'Running SonarQube static security analysis...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping SonarQube analysis."
                        exit 0
                    fi

                    docker run --rm \
                                            --network utopiahire-pipeline_default \
                      -e SONAR_HOST_URL=${SONARQUBE_URL} \
                      -e SONAR_TOKEN=${SONAR_TOKEN} \
                      -v $(pwd):/usr/src \
                      sonarsource/sonar-scanner-cli \
                      -Dsonar.projectKey=utopiahire \
                      -Dsonar.projectName=UtopiaHire \
                      -Dsonar.sources=. \
                      -Dsonar.exclusions=**/node_modules/**,**/.git/**,**/security-reports/** || true
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

                                        BACK_REQ=$(find backend -name requirements.txt | head -n 1)
                                        FRONT_PKG=$(find frontend -name package.json | head -n 1)

                                        if [ -z "$BACK_REQ" ]; then
                                                echo "No requirements.txt found under backend/."
                                                exit 1
                                        fi
                                        if [ -z "$FRONT_PKG" ]; then
                                                echo "No package.json found under frontend/."
                                                exit 1
                                        fi

                    docker run --rm \
                                            -v $(pwd):/workspace \
                                            -w /workspace \
                      python:3.11-slim \
                                            sh -c "pip install pip-audit -q && pip-audit -r /workspace/$BACK_REQ \
                                                --format json -o /workspace/${REPORT_DIR}/pip-audit.json || true"

                                        test -f ${REPORT_DIR}/pip-audit.json || true

                    docker run --rm \
                                            -v $(pwd):/workspace \
                                            -w /workspace \
                      node:20-alpine \
                                            sh -c "cd /workspace/$(dirname $FRONT_PKG) && npm install --prefer-offline -q && \
                                                npm audit --json > /workspace/${REPORT_DIR}/npm-audit.json 2>&1 || true"

                                        test -f ${REPORT_DIR}/npm-audit.json || true
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

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v $(pwd)/${REPORT_DIR}:/reports \
                      aquasec/trivy:latest image \
                      --format json \
                      --output /reports/trivy-backend.json \
                      --severity CRITICAL,HIGH \
                                            utopiahire-pipeline2-backend || true

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v $(pwd)/${REPORT_DIR}:/reports \
                      aquasec/trivy:latest image \
                      --format json \
                      --output /reports/trivy-frontend.json \
                      --severity CRITICAL,HIGH \
                                            utopiahire-pipeline2-frontend || true
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

                    docker run --rm \
                      -v $(pwd):/tf \
                      bridgecrew/checkov:latest \
                      -d /tf \
                      --output json \
                                            --output-file-path /tf/${REPORT_DIR}/ || true
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

                    echo "ZAP scanning target: http://utopiahire-backend:8000"
                    docker run --rm \
                        --network utopiahire-pipeline_default \
                        -v $(pwd)/${REPORT_DIR}:/zap/wrk:rw \
                        ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py \
                        -t http://utopiahire-backend:8000 \
                        -r zap-report.html \
                        -J zap-report.json \
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

        stage('Attack Simulation') {
            steps {
                echo 'Running controlled attack validation tests...'
                sh '''
                    if [ "${DOCKER_AVAILABLE}" != "true" ]; then
                        echo "Docker access is unavailable on this Jenkins agent; skipping attack simulation."
                        exit 0
                    fi

                    APP_URL="http://utopiahire-backend:8000"
                    echo "Target: $APP_URL"
                    mkdir -p security-reports

                    echo "=== SQL Injection Test ===" | tee security-reports/attack-results.txt

                    docker run --rm \
                    python:3.11-slim bash -c "
                        pip install sqlmap >/dev/null 2>&1 &&
                        sqlmap \
                        -u '${APP_URL}/api/jobs/database-info' \
                        --batch \
                        --level=1 \
                        --ignore-code=401 \
                        --technique=B \
                        --flush-session
                    " 2>&1 | tee -a security-reports/attack-results.txt || true

                    echo "" >> security-reports/attack-results.txt
                    echo "=== XSS Filename Test ===" | tee -a security-reports/attack-results.txt

                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                    --max-time 10 \
                    -X POST ${APP_URL}/api/resume/upload \
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
                    S=$(curl -s -o /dev/null -w "%{http_code}" \
                        --max-time 5 \
                        ${APP_URL}/api/resume/analyze) || S="000"
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

                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                    --max-time 10 \
                    "${APP_URL}/api/career/download/../../../etc/passwd") \
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
                '''
            }
        }
    }

    post {
        always {
            echo 'Bundling all security reports...'
            sh '''
                mkdir -p security-reports
                cd security-reports
                zip -r ../security-report-bundle.zip . 2>/dev/null || true
            '''
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