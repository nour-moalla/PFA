import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (accuracy_score, f1_score,
                               precision_score, recall_score)

# ─── Load data ────────────────────────────────────────────────────
df_train = pd.read_csv("data/train_set.csv")
df_test  = pd.read_csv("data/test_set.csv")

# ─── Feature engineering ──────────────────────────────────────────
# Combine text + categorical features into one rich text string
def build_text(row):
    return (
        str(row['Description']) + ' ' +
        str(row['severity']) + ' ' +
        str(row['platform']) + ' ' +
        str(row['attack_vector']) + ' ' +
        str(row['attack_complexity']) + ' ' +
        str(row['privileges_required'])
    )

df_train['text'] = df_train.apply(build_text, axis=1)
df_test['text']  = df_test.apply(build_text, axis=1)

# TF-IDF vectoriser
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=2,          # ← ignore words that appear in only 1 document
    max_df=0.95        # ← ignore words that appear in 95%+ of documents
)
X_train = vectorizer.fit_transform(df_train['text'])
X_test  = vectorizer.transform(df_test['text'])

# Encode labels
le = LabelEncoder()
y_train = le.fit_transform(df_train['label'])
y_test  = le.transform(df_test['label'])

joblib.dump(vectorizer, 'ml/vectorizer.pkl')
joblib.dump(le, 'ml/label_encoder.pkl')
print("Features ready. Shapes:", X_train.shape, X_test.shape)

# ─── Train and evaluate THREE models ──────────────────────────────
models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=100, class_weight='balanced',
        random_state=42, n_jobs=-1
    ),
    'Logistic Regression': LogisticRegression(
        max_iter=1000, class_weight='balanced',
        random_state=42, C=1.0
    ),
    'SVM': LinearSVC(
    max_iter=2000,
    class_weight='balanced',
    random_state=42,
    C=0.5          # ← change from 1.0 to 0.5 (less aggressive, better generalization)
    )
}

results = []
best_f1 = 0
best_model_name = ''

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1  = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    pre = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)

    results.append({
        'Model': name,
        'Accuracy': f'{acc:.2%}',
        'Precision': f'{pre:.2%}',
        'Recall': f'{rec:.2%}',
        'F1 Score': f'{f1:.2%}',
    })

    print(f"Accuracy: {acc:.2%}  F1: {f1:.2%}")

    predictions = le.inverse_transform(y_pred)
    true_labels = le.inverse_transform(y_test)
    print(f"Predictions on UtopiaHire test set:")
    for i in range(len(df_test)):
        ok = '✓' if predictions[i] == true_labels[i] else '✗'
        print(f"  {ok} {df_test.iloc[i]['CVE ID']}: true={true_labels[i]} | predicted={predictions[i]}")

    fname = f"ml/{name.lower().replace(' ','_')}_model.pkl"
    joblib.dump(model, fname)
    print(f"Saved: {fname}")

    if f1 > best_f1:
        best_f1 = f1
        best_model_name = name

# ─── Comparison table ─────────────────────────────────────────────
df_results = pd.DataFrame(results)
print("\n=== MODEL COMPARISON TABLE ===")
print(df_results.to_string(index=False))
df_results.to_csv('ml/model_comparison.csv', index=False)

print(f"\n★ Best model: {best_model_name} (F1={best_f1:.2%})")
print("This model will be used in the AI Security Assistant.")
