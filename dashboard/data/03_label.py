import pandas as pd

df = pd.read_csv("data/cleaned_dataset.csv")

def classify_vulnerability(description):
    """
    Classify a CVE description into a vulnerability type.
    Rules are checked in order — first match wins.
    More specific patterns come before general ones.
    """
    text = str(description).lower()

    # SQL Injection
    if any(k in text for k in ['sql injection', 'sqli', 'sql query',
                                       'union select', 'sql command']):
        return 'sqli'

    # Cross-Site Scripting
    if any(k in text for k in ['cross-site scripting', 'xss',
                                       'stored xss', 'reflected xss',
                                       'javascript injection']):
        return 'xss'

    # Remote Code Execution
    if any(k in text for k in ['remote code execution', 'rce',
                                       'arbitrary code', 'execute code',
                                       'code execution']):
        return 'rce'

    # Command Injection
    if any(k in text for k in ['command injection', 'os command',
                                       'shell injection', 'arbitrary commands']):
        return 'cmdi'

    # Path Traversal / Directory Traversal
    if any(k in text for k in ['path traversal', 'directory traversal',
                                       '../.', 'file traversal']):
        return 'path_traversal'

    # CSRF
    if any(k in text for k in ['cross-site request forgery', 'csrf',
                                       'cross site request']):
        return 'csrf'

    # File Upload vulnerabilities
    if any(k in text for k in ['file upload', 'unrestricted upload',
                                       'upload arbitrary']):
        return 'file_upload'

    # SSRF
    if any(k in text for k in ['server-side request forgery', 'ssrf',
                                       'arbitrary url', 'request forgery']):
        return 'ssrf'

    # Broken Access Control / Authorization
    if any(k in text for k in ['access control', 'authorization',
                                       'privilege escalation', 'unauthorized access',
                                       'lacks authorization']):
        return 'broken_access_control'

    # Credential / Secret exposure
    if any(k in text for k in ['hardcoded', 'credential', 'api key',
                                       'password', 'secret', 'token']):
        return 'secret_exposure'

    # Default — unclassified (these go to 'other')
    return 'other'

df['label'] = df['Description'].apply(classify_vulnerability)

print("=== LABEL DISTRIBUTION ===")
print(df['label'].value_counts())
print(f"\nTotal labelled: {len(df)}")
print(f"Unlabelled (other): {(df['label']=='other').sum()}")

# Save all rows including 'other' — we will decide later what to do with them
df.to_csv("data/labelled_dataset.csv", index=False)
print("\nSaved: data/labelled_dataset.csv")