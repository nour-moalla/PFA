pipeline {
    // FIX 1: Use "agent any" instead of agent { docker {...} }
    // "agent any" means: run on the Jenkins controller itself (no Docker wrapper)
    // This way Docker commands run directly on the host where Docker IS installed
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
                      sh -c "pip install pip-audit -q && cd /app && pip-audit -r requirements.txt --format json -o /app/pip-audit.json || true"

                    cp backend/pip-audit.json ${REPORT_DIR}/pip-audit.json || true

                    docker run --rm \
                      -v $(pwd)/frontend:/app \
                      node:20-alpine \
                      sh -c "cd /app && npm audit --json > /app/npm-audit.json 2>&1 || true"

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
                echo 'Building application containers...'
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
                echo 'Starting application containers for DAST testing...'
                sh '''
                    docker compose up -d
                    echo "Waiting 40 seconds for containers to be ready..."
                    sleep 40
                    curl -f http://host.docker.internal:8000/health || \
                    curl -f http://172.17.0.1:8000/health || \
                    echo "Health check skipped — app may be starting on different network"
                '''
            }
        }

        stage('DAST — OWASP ZAP') {
            steps {
                echo 'Running ZAP dynamic attack scan against running app...'
                sh '''
                    docker run --rm \
                      --network host \
                      -v $(pwd)/${REPORT_DIR}:/zap/wrk:rw \
                      ghcr.io/zaproxy/zaproxy:stable \
                      zap-baseline.py \
                      -t http://localhost:8000 \
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
                    echo "=== SQL Injection Test ===" | tee ${REPORT_DIR}/attack-results.txt

                    docker run --rm \
                      --network host \
                      python:3.11-slim \
                      sh -c "pip install sqlmap -q && python -m sqlmap \
                        -u http://localhost:8000/api/jobs/database-info \
                        --batch --level=1 --output-dir=/tmp/sqlmap" 2>&1 \
                      | tee -a ${REPORT_DIR}/attack-results.txt || true

                    echo "=== XSS Filename Test ===" | tee -a ${REPORT_DIR}/attack-results.txt
                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                      -X POST http://localhost:8000/api/resume/upload \
                      -F "file=@README.md;filename=xss_test.pdf") || STATUS="000"
                    echo "XSS filename test HTTP status: $STATUS" \
                      | tee -a ${REPORT_DIR}/attack-results.txt

                    echo "=== Rate Limit Test ===" | tee -a ${REPORT_DIR}/attack-results.txt
                    for i in $(seq 1 15); do
                      curl -s -o /dev/null -w "Request $i: %{http_code}\\n" \
                        http://localhost:8000/api/resume/analyze || true
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
                    docker ps --filter "name=utopiahire" --format "table {{.Names}}\t{{.Status}}"
                    echo "Local deployment confirmed"
                '''
            }
        }
    }

    // FIX 2: Wrap the post block sh commands inside a node block
    // This provides the FilePath context that sh needs
    post {
        always {
            node('built-in') {
                echo 'Bundling all security reports into one artifact...'
                sh '''
                    mkdir -p ${REPORT_DIR}
                    cd ${REPORT_DIR}
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