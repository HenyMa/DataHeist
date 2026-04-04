import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

from preprocess import preprocess


# Step 1: Load and prepare data
df = preprocess("../data/data.csv")

# Step 2: Choose features (inputs)
X = df[['PropertyValue', 'PctLeave', 'PctMoveIn', 'NetFlow', 'RelativePrice']]

# Step 3: Choose target (what we are predicting)
y = df['RiskLevel']


# Step 4: Split into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2
)


# Step 5: Create model
model = RandomForestClassifier(n_estimators=100)

# Step 6: Train model
model.fit(X_train, y_train)


# Step 7: Make predictions
train_predictions = model.predict(X_train)
test_predictions = model.predict(X_test)


# Step 8: Check accuracy
train_accuracy = accuracy_score(y_train, train_predictions)
test_accuracy = accuracy_score(y_test, test_predictions)

print("Training Accuracy:", train_accuracy)
print("Testing Accuracy:", test_accuracy)


# Step 9: Confusion matrix
cm = confusion_matrix(y_test, test_predictions)
print("\nConfusion Matrix:")
print(cm)


# Step 10: Feature importance
importances = model.feature_importances_

print("\nFeature Importance:")
for i in range(len(X.columns)):
    print(X.columns[i], ":", importances[i])


# Step 11: Save model
with open("../models/risk_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("\nModel saved!")
