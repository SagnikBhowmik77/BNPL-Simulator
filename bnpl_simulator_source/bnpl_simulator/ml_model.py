# ml_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score, recall_score
from xgboost import XGBClassifier
import joblib # For saving/loading the model
import os
from .config import MODEL_FILE, DATASET_FILEPATH

# --- Configuration ---
# Choose the metric to optimize for: 'roc_auc' or 'recall_high_risk'
OPTIMIZATION_METRIC = 'recall_high_risk'

def train_and_save_model():
    """Trains a Logistic Regression model and saves it to disk."""
    try:
        df = pd.read_csv(DATASET_FILEPATH)
    except FileNotFoundError:
        print(f"Error: Dataset file not found at {DATASET_FILEPATH}. Cannot train model.")
        return

    # Feature Engineering and Target Variable
    # We'll use a subset of features for this basic example
    features = ['Customer_Age', 'Annual_Income', 'Credit_Score', 'Purchase_Amount',
                'Gender', 'Purchase_Category', 'Device_Type', 'Connection_Type', 'Checkout_Time_Seconds', 'Browser']
    target = 'Repayment_Status'

    X = df[features].copy()
    # Convert target to binary: 'Paid On Time' = 0, 'Late Payment'/'Defaulted' = 1
    y = df[target].apply(lambda x: 0 if x == 'Paid On Time' else 1)

    # Calculate scale_pos_weight for XGBoost to handle class imbalance
    scale_pos_weight = (y == 0).sum() / (y == 1).sum()

    # Split data into training and testing sets for proper evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Define categorical and numerical features
    categorical_features = ['Gender', 'Purchase_Category', 'Device_Type', 'Connection_Type', 'Browser']
    numerical_features = ['Customer_Age', 'Annual_Income', 'Credit_Score', 'Purchase_Amount', 'Checkout_Time_Seconds']

    # Create preprocessing pipelines for numerical and categorical features
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    # Create a column transformer to apply different transformations to different columns
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # Define the models to compare
    models = {
        "Logistic Regression": LogisticRegression(solver='liblinear', random_state=42, class_weight='balanced'),
        "Random Forest": RandomForestClassifier(random_state=42, n_jobs=-1, class_weight='balanced'),
        "XGBoost": XGBClassifier(eval_metric='logloss', random_state=42, n_jobs=-1, scale_pos_weight=scale_pos_weight)
    }

    best_model = None
    best_score = -1
    best_model_name = ""

    print("\n--- Machine Learning Model Evaluation ---")
    for name, model in models.items():
        # Create a full pipeline with preprocessor and classifier
        pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                                   ('classifier', model)])

        # Train the model
        pipeline.fit(X_train, y_train)

        # Make predictions on the test set
        y_pred = pipeline.predict(X_test)
        y_pred_proba = pipeline.predict_proba(X_test)[:, 1] # Probability of class 1 (risky)

        # Evaluate and print metrics
        print(f"\n--- {name} Performance ---")
        print(classification_report(y_test, y_pred, target_names=['Low Risk (0)', 'High Risk (1)']))
        
        # Calculate all relevant scores
        scores = {
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'recall_high_risk': recall_score(y_test, y_pred, pos_label=1)
        }
        print(f"ROC AUC Score: {scores['roc_auc']:.4f}")
        print(f"High-Risk Recall: {scores['recall_high_risk']:.4f}")

        # Track the best model based on the chosen optimization metric
        current_score = scores[OPTIMIZATION_METRIC]
        if current_score > best_score:
            best_score = current_score
            best_model = pipeline
            best_model_name = name

    # Save the best performing model
    if best_model:
        joblib.dump(best_model, MODEL_FILE)
        print(f"\n--- Best Model Selection ---")
        print(f"Optimizing for: '{OPTIMIZATION_METRIC}'")
        print(f"Best performing model is '{best_model_name}' with a score of: {best_score:.4f}.")
        print(f"This model has been saved to {MODEL_FILE} and will be used by the Risk Engine.")

def load_model():
    """Loads the pre-trained ML model."""
    if os.path.exists(MODEL_FILE):
        return joblib.load(MODEL_FILE)
    return None