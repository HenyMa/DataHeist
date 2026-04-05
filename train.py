import pandas as pd
import pickle

from sklearn.model_selection import train_test_split, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
import matplotlib.pyplot as plt

from preprocess import preprocess

df = preprocess("oc_user_inputs_clean.csv")

X = df[['PropertyValue', 'PctLeave', 'PctMoveIn', 'NetFlow', 'RelativePrice']]

y = df['RiskLevel']

try:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
except ValueError as split_error:
    print(f"Stratified split unavailable: {split_error}")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

candidate_models = {
    "Logistic Regression": Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        max_depth=15,
    ),
}

results = {}
best_model_name = None
best_model = None
best_f1_score = -1.0
best_test_predictions = None

print("=" * 60)
print("Model Comparison with Cross-Validation")
print("=" * 60)

for model_name, candidate in candidate_models.items():
    print(f"\n{model_name}:")
    
    cv_results = cross_validate(
        candidate,
        X_train,
        y_train,
        cv=5,
        scoring=["accuracy", "precision_weighted", "recall_weighted", "f1_weighted"],
    )
    
    candidate.fit(X_train, y_train)

    test_predictions = candidate.predict(X_test)
    test_accuracy = accuracy_score(y_test, test_predictions)
    test_precision = precision_score(y_test, test_predictions, average="weighted", zero_division=0)
    test_recall = recall_score(y_test, test_predictions, average="weighted", zero_division=0)
    test_f1 = f1_score(y_test, test_predictions, average="weighted", zero_division=0)
    
    results[model_name] = {
        "cv_accuracy": cv_results["test_accuracy"].mean(),
        "cv_f1": cv_results["test_f1_weighted"].mean(),
        "test_accuracy": test_accuracy,
        "test_precision": test_precision,
        "test_recall": test_recall,
        "test_f1": test_f1,
    }
    
    print(f"  Cross-Val Accuracy: {cv_results['test_accuracy'].mean():.4f} (+/- {cv_results['test_accuracy'].std():.4f})")
    print(f"  Cross-Val F1:       {cv_results['test_f1_weighted'].mean():.4f}")
    print(f"  Test Accuracy:      {test_accuracy:.4f}")
    print(f"  Test Precision:     {test_precision:.4f}")
    print(f"  Test Recall:        {test_recall:.4f}")
    print(f"  Test F1:            {test_f1:.4f}")

    if test_f1 > best_f1_score:
        best_f1_score = test_f1
        best_model_name = model_name
        best_model = candidate
        best_test_predictions = test_predictions

print("\n" + "=" * 60)
print(f"Best Model: {best_model_name} (F1: {best_f1_score:.4f})")
print("=" * 60)

with open("risk_model.pkl", "wb") as file:
    pickle.dump(best_model, file)
