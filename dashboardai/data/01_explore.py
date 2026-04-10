import pandas as pd

file_path = "data/raw_dataset.csv"

# Count total lines in file
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    total_lines = sum(1 for _ in f)

# Load dataset safely
df = pd.read_csv(
    file_path,
    engine="python",
    on_bad_lines="skip"
)

print("=== DATA QUALITY CHECK ===")
print(f"Total lines in file: {total_lines}")
print(f"Rows loaded:         {len(df)}")
print(f"Rows skipped:        {total_lines - len(df)}")

print("\n=== DATASET OVERVIEW ===")
print(f"Total rows:    {df.shape[0]}")
print(f"Total columns: {df.shape[1]}")
print(f"Columns: {df.columns.tolist()}")

print("\n=== MISSING VALUES ===")
for col in df.columns:
    missing = df[col].isnull().sum()
    pct = missing / len(df) * 100
    print(f"  {col}: {missing} missing ({pct:.1f}%)")

print("\n=== DUPLICATE ROWS ===")
print(f"  Duplicates: {df.duplicated().sum()}")

# Check if column exists before using it (avoid crashes)
if 'CVSS Score' in df.columns:
    print("\n=== CVSS SCORE DISTRIBUTION ===")
    print(df['CVSS Score'].describe())
else:
    print("\n⚠️ 'CVSS Score' column not found")

print("\n=== SAMPLE ROWS ===")
print(df.head(3).to_string())

if 'Attack Vector' in df.columns:
    print("\n=== ATTACK VECTOR SAMPLE ===")
    print(df['Attack Vector'].iloc[0])
else:
    print("\n⚠️ 'Attack Vector' column not found")