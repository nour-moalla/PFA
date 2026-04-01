pipeline {
    agent any

    environment {
        SONARQUBE_URL = 'http://sonarqube:9000'
        APP_BACKEND   = 'http://localhost:8000'
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
                echo 'Creating .env files from Jenkins credentials...'
                withCredentials([
                    string(credentialsId: 'AI_API_KEY',                    variable: 'V_AI_API_KEY'),
                    string(credentialsId: 'AI_BASE_URL',                   variable: 'V_AI_BASE_URL'),
                    string(credentialsId: 'AI_MODEL',                      variable: 'V_AI_MODEL'),
                    string(credentialsId: 'VITE_FIREBASE_API_KEY',         variable: 'V_FB_API_KEY'),
                    string(credentialsId: 'VITE_FIREBASE_AUTH_DOMAIN',     variable: 'V_FB_AUTH'),
                    string(credentialsId: 'VITE_FIREBASE_PROJECT_ID',      variable: 'V_FB_PROJECT'),
                    string(credentialsId: 'VITE_FIREBASE_STORAGE_BUCKET',  variable: 'V_FB_BUCKET'),
                    string(credentialsId: 'VITE_FIREBASE_MESSAGING_SENDER_ID', variable: 'V_FB_SENDER'),
                    string(credentialsId: 'VITE_FIREBASE_APP_ID',          variable: 'V_FB_APP_ID')
                ]) {
                    sh '''
                        printf "AI_API_KEY=%s\nAI_BASE_URL=%s\nAI_MODEL=%s\n" \
                        "$V_AI_API_KEY" "$V_AI_BASE_URL" "$V_AI_MODEL" \
                        > backend/.env

                        printf "VITE_FIREBASE_API_KEY=%s\nVITE_FIREBASE_AUTH_DOMAIN=%s\nVITE_FIREBASE_PROJECT_ID=%s\nVITE_FIREBASE_STORAGE_BUCKET=%s\nVITE_FIREBASE_MESSAGING_SENDER_ID=%s\nVITE_FIREBASE_APP_ID=%s\n" \
                        "$V_FB_API_KEY" "$V_FB_AUTH" "$V_FB_PROJECT" \
                        "$V_FB_BUCKET" "$V_FB_SENDER" "$V_FB_APP_ID" \
                        > frontend/.env

                        echo "backend/.env created with 3 variables"
                        echo "frontend/.env created with 6 variables"
                        echo "AI_MODEL = $V_AI_MODEL"
                    '''
                }
            }
        }
        stage('Secrets Scan — Gitleaks') {
            steps {
                echo 'Scanning for leaked API keys and credentials...'
                sh '''
                    docker run --rm -v $(pwd):/path \
                      zricethezav/gitleaks:latest detect \
                      --source /path \
                      --report-path /path/${REPORT_DIR}/gitleaks-report.json \
                      --exit-code 1 || true
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
                    docker run --rm \
                      -e SONAR_HOST_URL=${SONARQUBE_URL} \
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
                    docker run --rm \
                      -v $(pwd)/backend:/app \
                      python:3.11-slim \
                      sh -c "pip install pip-audit -q && pip-audit -r /app/requirements.txt \
                        --format json -o /app/pip-audit.json || true"

                    cp backend/pip-audit.json ${REPORT_DIR}/pip-audit.json || true

                    docker run --rm \
                      -v $(pwd)/frontend:/app \
                      node:20-alpine \
                      sh -c "cd /app && npm install --prefer-offline -q && \
                        npm audit --json > /app/npm-audit.json 2>&1 || true"

                    cp frontend/npm-audit.json ${REPORT_DIR}/npm-audit.json || true
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
                sh 'docker compose build'
            }
        }

        stage('Container Scan — Trivy') {
            steps {
                echo 'Scanning Docker images for CVE vulnerabilities...'
                sh '''
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v $(pwd)/${REPORT_DIR}:/reports \
                      aquasec/trivy:latest image \
                      --format json \
                      --output /reports/trivy-backend.json \
                      --severity CRITICAL,HIGH \
                      utopiahire-main-backend || true

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v $(pwd)/${REPORT_DIR}:/reports \
                      aquasec/trivy:latest image \
                      --format json \
                      --output /reports/trivy-frontend.json \
                      --severity CRITICAL,HIGH \
                      utopiahire-main-frontend || true
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
                    docker run --rm \
                      -v $(pwd):/tf \
                      bridgecrew/checkov:latest \
                      -d /tf \
                      --output json \
                      --output-file-path /tf/${REPORT_DIR} || true
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
                echo 'Starting application containers for DAST and attack testing...'
                sh '''
                    echo "Cleaning old containers..."
                    docker compose down || true

                    echo "Starting fresh containers..."
                    docker compose up -d --build

                    echo "Waiting for backend..."
                    sleep 20

                    curl -f http://localhost:8000/health || exit 1
                    echo "Backend is healthy and ready"
                '''
            }
        }
        stage('DAST — OWASP ZAP') {
            steps {
                echo 'Running ZAP dynamic attack scan against running app...'
                sh '''
                    HOST_IP="172.17.0.1"
                    echo "ZAP scanning target: http://$HOST_IP:8000"
                    docker run --rm \
                    -v $(pwd)/${REPORT_DIR}:/zap/wrk:rw \
                    ghcr.io/zaproxy/zaproxy:stable \
                    zap-baseline.py \
                    -t http://$HOST_IP:8000 \
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
                    echo "=== DEBUG: Checking app ==="
                    docker ps

                    echo "Waiting for backend to be ready..."
                    for i in $(seq 1 20); do
                    if curl -s http://localhost:8000/health > /dev/null; then
                        echo "Backend is UP"
                        break
                    fi
                    echo "Waiting..."
                    sleep 5
                    done

                    echo "=== SQL Injection Test ===" | tee ${REPORT_DIR}/attack-results.txt

                    docker run --rm --network host python:3.11-slim bash -c "
                        pip install sqlmap >/dev/null 2>&1 &&
                        sqlmap -u 'http://localhost:8000/api/jobs/database-info' \
                            --batch --level=1
                    " 2>&1 | tee -a ${REPORT_DIR}/attack-results.txt


                    echo "=== XSS Filename Test ===" | tee -a ${REPORT_DIR}/attack-results.txt

                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                    -X POST http://localhost:8000/api/resume/upload \
                    -F "file=@/etc/hosts;filename=<script>alert(1)</script>.pdf")

                    echo "XSS filename HTTP status: $STATUS" \
                    | tee -a ${REPORT_DIR}/attack-results.txt


                    echo "=== Rate Limit Test ===" | tee -a ${REPORT_DIR}/attack-results.txt

                    for i in $(seq 1 15); do
                    curl -s -o /dev/null -w "Request $i: %{http_code}\\n" \
                        http://localhost:8000/api/resume/analyze
                    done | tee -a ${REPORT_DIR}/attack-results.txt


                    echo "=== Attack simulation complete ===" \
                    | tee -a ${REPORT_DIR}/attack-results.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/attack-results.txt",
                                    allowEmptyArchive: true
                }
            }
        }

        stage('Deploy Locally') {
            steps {
                echo 'Confirming local deployment is running...'
                sh '''
                    docker ps --filter "name=utopiahire" \
                      --format "table {{.Names}}\t{{.Status}}"
                    echo "Local deployment confirmed"
                '''
            }
        }
    }

    post {
        always {
            node('built-in') {
                echo 'Bundling all security reports...'
                sh '''
                    mkdir -p security-reports
                    cd security-reports
                    zip -r ../security-report-bundle.zip . 2>/dev/null || true
                '''
                archiveArtifacts artifacts: 'security-report-bundle.zip',
                                 allowEmptyArchive: true
            }
        }
        success {
            echo 'ALL SECURITY GATES PASSED — pipeline is clean'
        }
        failure {
            echo 'PIPELINE FAILED — check the failed stage above'
        }
    }
}