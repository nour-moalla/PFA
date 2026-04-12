import pandas as pd
import re

df = pd.read_csv(
    "data/raw_dataset.csv",
    engine="python",
    on_bad_lines="skip"
)
df.columns = df.columns.str.strip().str.rstrip(';')
print("Columns:", df.columns.tolist())
print(f"Starting rows: {len(df)}")

# ─── OPERATION 1: Drop the Affected OS column (67% missing) ──────
# We drop it entirely and replace it with a derived 'platform' column
df = df.drop(columns=['Affected OS'])
print("Dropped Affected OS column")

# ─── OPERATION 2: Create 'platform' from Description keywords ────
# This gives us a useful feature WITHOUT losing any rows
def get_platform(text):
    text = str(text).lower()
    if any(w in text for w in ['windows', 'microsoft']):
        return 'windows'
    if any(w in text for w in ['linux', 'ubuntu', 'debian', 'kernel']):
        return 'linux'
    if any(w in text for w in ['android', 'ios', 'iphone', 'mobile']):
        return 'mobile'
    if any(w in text for w in ['wordpress', 'plugin', 'web', 'http',
                                    'browser', 'javascript', 'php', 'api']):
        return 'web'
    return 'unknown'

df['platform'] = df['Description'].apply(get_platform)
print("Platform distribution:", df['platform'].value_counts().to_dict())

# ─── OPERATION 3: Parse the CVSS vector string ────────────────────
# The Attack Vector column contains: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/...
# We extract each component as a separate feature
def parse_cvss(cvss_string):
    result = {'av': 'unknown', 'ac': 'unknown',
              'pr': 'unknown', 'ui': 'unknown'}
    try:
        parts = str(cvss_string).split('/')
        for part in parts:
            if part.startswith('AV:'):
                av_map = {'N':'network','A':'adjacent','L':'local','P':'physical'}
                result['av'] = av_map.get(part.split(':')[1], 'unknown')
            elif part.startswith('AC:'):
                result['ac'] = 'low' if part.endswith('L') else 'high'
            elif part.startswith('PR:'):
                pr_map = {'N':'none','L':'low','H':'high'}
                result['pr'] = pr_map.get(part.split(':')[1], 'unknown')
            elif part.startswith('UI:'):
                result['ui'] = 'none' if part.endswith('N') else 'required'
    except:
        pass
    return result

cvss_parsed = df['Attack Vector'].apply(parse_cvss)
df['attack_vector']  = cvss_parsed.apply(lambda x: x['av'])
df['attack_complexity'] = cvss_parsed.apply(lambda x: x['ac'])
df['privileges_required'] = cvss_parsed.apply(lambda x: x['pr'])
df['user_interaction'] = cvss_parsed.apply(lambda x: x['ui'])
print("Parsed CVSS vectors")

# ─── OPERATION 4: Create severity from CVSS score ─────────────────
def score_to_severity(score):
    try:
        score = float(score)
    except (ValueError, TypeError):
        return 'unknown'
    if score >= 9.0: return 'critical'
    if score >= 7.0: return 'high'
    if score >= 4.0: return 'medium'
    return 'low'

df['severity'] = df['CVSS Score'].apply(score_to_severity)
print("Severity distribution:", df['severity'].value_counts().to_dict())

# ─── OPERATION 5: Remove duplicate CVEs ───────────────────────────
before = len(df)
df = df.drop_duplicates(subset=['CVE ID'])
print(f"Removed {before - len(df)} duplicate CVEs")

# ─── OPERATION 6: Clean text ──────────────────────────────────────
df['Description'] = df['Description'].str.strip()
df['Description'] = df['Description'].fillna('')

# ─── OPERATION 7: Drop original Attack Vector column ─────────────
# We already extracted the useful parts above
df = df.drop(columns=['Attack Vector'])

# ─── OPERATION 8: Reset index ─────────────────────────────────────
df = df.reset_index(drop=True)

df.to_csv("data/cleaned_dataset.csv", index=False)
print(f"\nCleaned dataset saved: {len(df)} rows")
print("Columns:", df.columns.tolist())