import pandas as pd

# Load the dataset
def load_data(path):
    df = pd.read_csv(path)
    return df


# Add new columns (features)
def add_features(df):
    # NetFlow = people moving in - people moving out
    df['NetFlow'] = df['PctMoveIn'] - df['PctLeave']
    
    # Find median property value
    median_price = df['PropertyValue'].median()
    
    # Relative price compared to median
    df['RelativePrice'] = df['PropertyValue'] / median_price
    
    return df


# Create risk labels (this is what we predict)
def create_risk_labels(df):
    median_price = df['PropertyValue'].median()
    
    risk_list = []  # we will store risk values here
    
    for i in range(len(df)):
        price = df.loc[i, 'PropertyValue']
        leave = df.loc[i, 'PctLeave']
        
        # Simple rules for risk
        if leave > 0.6 and price > median_price:
            risk = 2   # High Risk
        elif leave > 0.4:
            risk = 1   # Medium Risk
        else:
            risk = 0   # Low Risk
        
        risk_list.append(risk)
    
    df['RiskLevel'] = risk_list
    return df


# Main function to run everything
def preprocess(path):
    df = load_data(path)
    df = add_features(df)
    df = create_risk_labels(df)
    return df
