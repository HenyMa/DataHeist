import pickle

with open("risk_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict_risk(low_price, high_price, move_in, move_out):
    """
    Predict home buying risk based on price and migration patterns.
    
    Risk factors:
    - High out-migration rate = Higher risk
    - Low property value relative to median = Lower risk (cheaper to buy)
    - High property value relative to median = Higher risk (more to lose)
    """
    avg_price = (low_price + high_price) / 2

    median_price = 1216000
    relative_price = avg_price / median_price

    total_moves = move_in + move_out
    if total_moves > 0:
        pct_leave = move_out / total_moves
    else:
        pct_leave = 0.0

    migration_risk = pct_leave * 50  # Max 50 points when 100% leave

    price_risk = min(relative_price * 50, 50)  # Max 50 points
    
    risk_score = migration_risk + price_risk
    risk_score = min(100.0, max(0.0, risk_score))  # Clamp to 0-100

    if risk_score < 33:
        risk_label = "Low Risk"
        full_probs = [1.0, 0.0, 0.0]
    elif risk_score < 67:
        risk_label = "Medium Risk"
        full_probs = [0.0, 1.0, 0.0]
    else:
        risk_label = "High Risk"
        full_probs = [0.0, 0.0, 1.0]

    return {
        "risk": risk_label,
        "probabilities": full_probs,
        "risk_pct": round(risk_score, 1)
    }

# Test
if __name__ == "__main__":
    result = predict_risk(500000, 800000, 1000, 1200)
    print(result)
