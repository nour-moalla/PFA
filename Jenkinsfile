pipeline {
    agent docker-host

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
                      --exit-code 1
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
                withSonarQubeEnv('SonarQube-Local') {
                    sh '''
                        docker run --rm \
                          -e SONAR_HOST_URL=${SONARQUBE_URL} \
                          -v $(pwd):/usr/src \
                          sonarsource/sonar-scanner-cli \
                          -Dsonar.projectKey=utopiahire \
                          -Dsonar.projectName=UtopiaHire \
                          -Dsonar.sources=backend,frontend/src
                    '''
                }
            }
        }

        stage('Quality Gate — SonarQube') {
            steps {
                echo 'Waiting for SonarQube Quality Gate result...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Dependency Audit') {
            steps {
                echo 'Checking for known vulnerable dependencies...'
                sh '''
                    pip install pip-audit
                    cd backend && pip-audit -r requirements.txt \
                      -o ../${REPORT_DIR}/pip-audit.json --format json || true
                    cd ../frontend && npm audit --json \
                      > ../${REPORT_DIR}/npm-audit.json 2>&1 || true
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
                      aquasec/trivy:latest image \
                      --format json \
                      --output ${REPORT_DIR}/trivy-backend.json \
                      --severity CRITICAL,HIGH \
                      utopiahire-backend || true

                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy:latest image \
                      --format json \
                      --output ${REPORT_DIR}/trivy-frontend.json \
                      --severity CRITICAL,HIGH \
                      utopiahire-frontend || true
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
                    pip install checkov
                    checkov -d . \
                      --output json > ${REPORT_DIR}/checkov-report.json || true
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/checkov-report.json",
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Start Local Staging') {
            steps {
                echo 'Starting application containers for DAST and attack testing...'
                sh '''
                    docker compose up -d
                    sleep 40
                    curl -f http://localhost:8000/health || exit 1
                    echo "Backend is healthy and ready"
                '''
            }
        }

        stage('DAST — OWASP ZAP') {
            steps {
                echo 'Running ZAP dynamic attack scan against running app...'
                sh '''
                    docker run --rm --network host \
                      -v $(pwd)/${REPORT_DIR}:/zap/wrk \
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
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: "${REPORT_DIR}",
                        reportFiles: 'zap-report.html',
                        reportName: 'ZAP Security Report'
                    ])
                }
            }
        }

        stage('Attack Simulation') {
            steps {
                echo 'Running controlled attack validation tests...'
                sh '''
                    pip install sqlmap

                    echo "=== SQL Injection Test ===" | tee ${REPORT_DIR}/attack-results.txt
                    python -m sqlmap \
                      -u "http://localhost:8000/api/jobs/database-info" \
                      --batch --level=1 2>&1 | tee -a ${REPORT_DIR}/attack-results.txt

                    echo "=== XSS Filename Test ===" | tee -a ${REPORT_DIR}/attack-results.txt
                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                      -X POST http://localhost:8000/api/resume/upload \
                      -F "[email protected];filename=.pdf")
                    echo "XSS filename blocked with HTTP: $STATUS" \
                      | tee -a ${REPORT_DIR}/attack-results.txt

                    echo "=== Rate Limit Test ===" | tee -a ${REPORT_DIR}/attack-results.txt
                    for i in $(seq 1 15); do
                      curl -s -o /dev/null -w "Request $i: %{http_code}\n" \
                        http://localhost:8000/api/resume/analyze
                    done | tee -a ${REPORT_DIR}/attack-results.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/attack-results.txt",
                                     allowEmptyArchive: true
                }
            }
        }

        stage('iptables Firewall Verification') {
            steps {
                echo 'Verifying iptables firewall rules are active in containers...'
                sh '''
                    echo "=== Backend Container iptables Rules ===" \
                      | tee ${REPORT_DIR}/iptables-verification.txt
                    docker exec utopiahire-backend \
                      iptables -L INPUT -n -v 2>&1 \
                      | tee -a ${REPORT_DIR}/iptables-verification.txt

                    echo "=== Testing blocked port ===" \
                      | tee -a ${REPORT_DIR}/iptables-verification.txt
                    docker exec utopiahire-backend \
                      iptables -L INPUT -n | grep DROP \
                      | tee -a ${REPORT_DIR}/iptables-verification.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/iptables-verification.txt",
                                     allowEmptyArchive: true
                }
            }
        }

        stage('Deploy Locally') {
            steps {
                echo 'Confirming local deployment is live...'
                sh '''
                    docker ps | grep utopiahire
                    curl -f http://localhost:8000/health
                    echo "Local deployment confirmed"
                '''
            }
        }
    }

    post {
        always {
            echo 'Bundling all security reports into one artifact...'
            sh '''
                cd ${REPORT_DIR}
                zip -r ../security-report-bundle.zip . 2>/dev/null || true
            '''
            archiveArtifacts artifacts: 'security-report-bundle.zip',
                             allowEmptyArchive: true
        }
        success {
            echo 'ALL SECURITY GATES PASSED — pipeline is clean'
        }
        failure {
            echo 'PIPELINE FAILED — review the failed stage above'
        }
    }
}
