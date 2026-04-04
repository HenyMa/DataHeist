import pickle

# Load model
with open("../models/risk_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict_risk(low_price, high_price, move_in, move_out):
    avg_price = (low_price + high_price) / 2
    net_flow = move_in - move_out

    # NOTE: you need median price from training — hardcode or store it
    median_price = 700000  # replace with actual value
    relative_price = avg_price / median_price

    input_data = [[avg_price, move_out, move_in, net_flow, relative_price]]

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0]

    risk_map = {
        0: "Low Risk",
        1: "Medium Risk",
        2: "High Risk"
    }

    return {
        "risk": risk_map[prediction],
        "probabilities": probability.tolist()
    }

# Example test
if __name__ == "__main__":
    result = predict_risk(500000, 800000, 0.3, 0.5)
    print(result)
