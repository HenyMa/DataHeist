import pandas as pd

avm = pd.read_csv("data/AVM.csv")
mig = pd.read_csv("data/OC2025_ZIPMigration.csv")


avm_zip = (
    avm.groupby("ZipCode")
    .agg(
        median_value=("FinalValue", "median"),
        median_high=("HighValue", "median"),
        median_low=("LowValue", "median"),
        property_count=("RecordId", "count"),
    )
    .reset_index()
)

# Price uncertainty
avm_zip["price_spread_pct"] = (
    (avm_zip["median_high"] - avm_zip["median_low"])
    / avm_zip["median_value"]
)

df = mig.merge(avm_zip, on="ZipCode", how="left")


# Migration features
df["pct_leave"] = df["MovesOutOfZip"] / df["TotalMoves"]
df["pct_move_in"] = df["MovesIntoZip"] / df["TotalMoves"]
df["replacement_effect"] = df["pct_move_in"] - df["pct_leave"]

# Property feature
median_home_value = df["median_value"].median()
df["value_index"] = df["median_value"] / median_home_value

# Market activity
df["turnover_rate"] = df["TotalMoves"] / df["property_count"]

def minmax(series):
    return (series - series.min()) / (series.max() - series.min())

features = [
    "pct_leave",
    "pct_move_in",
    "replacement_effect",
    "value_index",
    "price_spread_pct",
    "turnover_rate"
]

for f in features:
    df[f + "_norm"] = minmax(df[f])

df["DPS"] = (
    0.30 * df["pct_leave_norm"] +
    0.15 * df["pct_move_in_norm"] +
    0.15 * df["replacement_effect_norm"] +
    0.25 * df["value_index_norm"] +
    0.10 * df["price_spread_pct_norm"] +
    0.05 * df["turnover_rate_norm"]
)

def classify(dps):
    if dps > 0.7:
        return "High Pressure"
    elif dps > 0.4:
        return "Moderate"
    else:
        return "Low"

df["pressure_level"] = df["DPS"].apply(classify)

def buyer(dps):
    if dps < 0.4:
        return "BUY"
    elif dps < 0.7:
        return "BUY SOON"
    else:
        return "RENT"

df["buyer_recommendation"] = df["DPS"].apply(buyer)

df.to_csv("pressuremap_final.csv", index=False)

print("Done! File saved as pressuremap_final.csv")
