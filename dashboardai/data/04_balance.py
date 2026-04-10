import pandas as pd
from sklearn.utils import resample

df = pd.read_csv("data/labelled_dataset.csv")
print("Before balancing:")
print(df['label'].value_counts())

# Target: 100 samples per class minimum
# This keeps the dataset manageable and balanced
TARGET = 100

balanced = []
for label in df['label'].unique():
    group = df[df['label'] == label]
    if len(group) >= TARGET:
        # Undersample — reduce to TARGET rows
        group = resample(group, n_samples=TARGET,
                        random_state=42, replace=False)
    else:
        # Oversample — duplicate rows up to TARGET
        group = resample(group, n_samples=TARGET,
                        random_state=42, replace=True)
    balanced.append(group)

df_bal = pd.concat(balanced).sample(frac=1, random_state=42)
df_bal = df_bal.reset_index(drop=True)

print("\nAfter balancing:")
print(df_bal['label'].value_counts())
print(f"Total rows: {len(df_bal)}")

df_bal.to_csv("data/balanced_dataset.csv", index=False)
print("\nSaved: data/balanced_dataset.csv")