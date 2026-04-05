import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    return df


def normalize_schema(df):
    if 'PropertyValue' not in df.columns:
        if {'LowValue', 'HighValue'}.issubset(df.columns):
            df['PropertyValue'] = (df['LowValue'] + df['HighValue']) / 2
        else:
            raise KeyError("Missing PropertyValue (or LowValue/HighValue)")

    if 'PctMoveIn' not in df.columns:
        if 'MoveIn' in df.columns:
            df['PctMoveIn'] = df['MoveIn']
        else:
            raise KeyError("Missing PctMoveIn (or MoveIn)")

    if 'PctLeave' not in df.columns:
        if 'MoveOut' in df.columns:
            df['PctLeave'] = df['MoveOut']
        else:
            raise KeyError("Missing PctLeave (or MoveOut)")

    if df['PctMoveIn'].max() > 1 or df['PctLeave'].max() > 1:
        total = (df['PctMoveIn'] + df['PctLeave']).replace(0, pd.NA)
        df['PctMoveIn'] = (df['PctMoveIn'] / total).fillna(0)
        df['PctLeave'] = (df['PctLeave'] / total).fillna(0)

    return df


def add_features(df):
    df['NetFlow'] = df['PctMoveIn'] - df['PctLeave']
    
    median_price = df['PropertyValue'].median()
    
    df['RelativePrice'] = df['PropertyValue'] / median_price
    
    return df


def create_risk_labels(df):
    
    risk_list = []
    
    for i in range(len(df)):
        leave = df.loc[i, 'PctLeave']

        if leave < 0.33:
            risk = 0   # Low Risk - stable population
        elif leave < 0.67:
            risk = 1   # Medium Risk - some outflow
        else:
            risk = 2   # High Risk - significant outflow
        
        risk_list.append(risk)
    
    df['RiskLevel'] = risk_list
    return df


def preprocess(path):
    df = load_data(path)
    df = normalize_schema(df)
    df = add_features(df)
    df = create_risk_labels(df)
    return df
