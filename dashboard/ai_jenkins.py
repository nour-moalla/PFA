import json, os, requests

findings = []

gl_path = '/reports/gitleaks-report.json'
if os.path.exists(gl_path):
    try:
        d = json.load(open(gl_path))
        if d:
            for leak in d[:5]:
                findings.append('SECRET FOUND: ' + leak.get('Description', 'unknown') + ' in file ' + leak.get('File', '?') + ' at line ' + str(leak.get('StartLine', '?')))
        else:
            findings.append('Gitleaks: Repository is clean - no secrets found')
    except:
        findings.append('Gitleaks: Could not read report')

zp_path = '/reports/zap-report.json'
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

prompt = ('You are a DevSecOps security expert analysing the UtopiaHire web application (FastAPI backend, React frontend, Firebase authentication). A Jenkins CI/CD pipeline just ran security scans. Based on these findings, provide exactly 3 numbered security recommendations. For each recommendation include: the vulnerability type, why it is dangerous for this specific application, and the exact code fix with a Python/FastAPI example. Be specific and actionable. Do not give generic advice.' + chr(10) + chr(10) + 'Pipeline scan findings:' + chr(10) + summary)

try:
    response = requests.post('http://192.168.56.1:11434/api/generate', json={'model': 'llama3.1:8b', 'prompt': prompt, 'stream': False}, timeout=180)
    ai_text = response.json().get('response', 'No response received from LLaMA')
except Exception as e:
    ai_text = ('LLaMA call failed: ' + str(e) + chr(10) + 'Raw findings:' + chr(10) + summary)

output = ('AI Security Analysis - LLaMA 3.1:8b (Local)' + chr(10) + '=' * 55 + chr(10) + 'Pipeline: UtopiaHire' + chr(10) + 'Findings analysed: ' + str(len(findings)) + chr(10) + '=' * 55 + chr(10) + chr(10) + ai_text)

with open('/reports/ai-recommendations.txt', 'w') as f:
    f.write(output)

print('AI recommendations saved.')
print(output[:400])