"""
Vehicle recalls vs. crash fatalities, by manufacturer.

Inputs  (place in data/, see data/README.md):
    data/Recalls_Data.csv                NHTSA recalls
    data/vehicle.csv                     NHTSA crash data, vehicle table
    data/cars_on_road_proxy.csv          estimated vehicles on the road (included)

Outputs:
    output/Aggregated Recall and Fatalities Data.csv
    figures/*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DATA = Path("data")
OUT = Path("output")
FIGS = Path("figures")
OUT.mkdir(exist_ok=True)
FIGS.mkdir(exist_ok=True)

FIRST_YEAR, LAST_YEAR = 2010, 2024
LAG_WINDOW = 4  # a recall in year Y is counted for Y and the next 3 years, capped at LAST_YEAR

# Renamed from "Recall Rate per 100k per COR": this is lag-adjusted recalled units
# per vehicle on the road, not a true rate (see README, Limitations).
RECALL_COL = "Lag-Adj Recalled Units per COR (x100k)"
FATALITY_COL = "Fatality Rate per 100k per COR"

# ---------------------------------------------------------------- load
recalls = pd.read_csv(DATA / "Recalls_Data.csv", low_memory=False)
vehicle = pd.read_csv(DATA / "vehicle.csv", low_memory=False)

# ---------------------------------------------------------------- missing data check
recall_cols = ["Manufacturer", "Potentially Affected", "Report Received Date"]
vehicle_cols = ["MAKENAME", "DEATHS", "MOD_YEAR"]
for name, df, cols in [("Recalls", recalls, recall_cols), ("Vehicle", vehicle, vehicle_cols)]:
    pct_missing = df[cols].isnull().mean() * 100
    print(f"Percent missing, {name}:\n{pct_missing}\n")
    assert (pct_missing < 30).all(), f"{name}: a column of interest is over 30% missing"

# ---------------------------------------------------------------- manufacturer mapping
# Maps raw names in both datasets (upper case) to a parent manufacturer.
# Rows whose name is not in this dictionary are dropped.
manufacturer_key = {
    # General Motors
    "GENERAL MOTORS, LLC": "General Motors",
    "CHEVROLET": "General Motors",
    "GMC": "General Motors",
    "CADILLAC": "General Motors",
    "BUICK / OPEL": "General Motors",
    "PONTIAC": "General Motors",
    "OLDSMOBILE": "General Motors",
    "SATURN": "General Motors",
    # Ford
    "FORD MOTOR COMPANY": "Ford",
    "FORD": "Ford",
    "LINCOLN": "Ford",
    "MERCURY": "Ford",
    # Chrysler
    "CHRYSLER (FCA US, LLC)": "Chrysler",
    "CHRYSLER": "Chrysler",
    "DODGE": "Chrysler",
    "PLYMOUTH": "Chrysler",
    "JEEP / KAISER-JEEP / WILLYS- JEEP": "Chrysler",
    "FIAT": "Chrysler",
    "ALFA ROMEO": "Chrysler",
    "RAM": "Chrysler",
    # Volkswagen
    "VOLKSWAGEN GROUP OF AMERICA, INC.": "Volkswagen",
    "VOLKSWAGEN": "Volkswagen",
    "AUDI": "Volkswagen",
    "PORSCHE": "Volkswagen",
    # BMW
    "BMW OF NORTH AMERICA, LLC": "BMW",
    "BMW": "BMW",
    # Daimler
    "DAIMLER TRUCKS NORTH AMERICA, LLC": "Daimler",
    "FREIGHTLINER": "Daimler",
    # Mercedes-Benz
    "MERCEDES-BENZ USA, LLC": "Mercedes",
    "MERCEDES-BENZ": "Mercedes",
    "SMART": "Mercedes",
    # Honda
    "HONDA (AMERICAN HONDA MOTOR CO.)": "Honda",
    "HONDA": "Honda",
    "ACURA": "Honda",
    # Nissan
    "NISSAN NORTH AMERICA, INC.": "Nissan",
    "NISSAN/DATSUN": "Nissan",
    "INFINITI": "Nissan",
}

recalls["Joint Manufacturer"] = recalls["Manufacturer"].str.upper().map(manufacturer_key)
vehicle["Joint Manufacturer"] = vehicle["MAKENAME"].str.upper().map(manufacturer_key)
recalls = recalls[recalls["Joint Manufacturer"].notna()].copy()
vehicle = vehicle[vehicle["Joint Manufacturer"].notna()].copy()

# ---------------------------------------------------------------- year filter and recall lag
# The recalls file has no year column; take it from the last 4 characters of the date.
recalls["RecallYear"] = recalls["Report Received Date"].str[-4:].astype(int)
recalls = recalls[recalls["RecallYear"].between(FIRST_YEAR, LAST_YEAR)].copy()
vehicle = vehicle[vehicle["MOD_YEAR"].between(FIRST_YEAR, LAST_YEAR)].copy()

# Repairs take time, so each recall is counted for several years.
# 2010-2021 -> 4, 2022 -> 3, 2023 -> 2, 2024 -> 1
recalls["LagYears"] = (LAST_YEAR + 1 - recalls["RecallYear"]).clip(upper=LAG_WINDOW)
recalls["Lag Accounted Recalls"] = recalls["Potentially Affected"] * recalls["LagYears"]

# ---------------------------------------------------------------- aggregate and join
df_recalls_aggregated = recalls.groupby("Joint Manufacturer")[["Lag Accounted Recalls"]].sum()
df_fatalities_aggregated = vehicle.groupby("Joint Manufacturer")[["DEATHS"]].sum()
bothdf_combined = pd.concat([df_recalls_aggregated, df_fatalities_aggregated], axis=1)

# Vehicles on the road (COR) proxy, estimated separately (see README).
cor = pd.read_csv(DATA / "cars_on_road_proxy.csv").set_index("Manufacturer")["Cars on Road"]
bothdf_combined["Cars on Road"] = bothdf_combined.index.map(cor)

# x100k so the values are readable
bothdf_combined[RECALL_COL] = bothdf_combined["Lag Accounted Recalls"] / bothdf_combined["Cars on Road"] * 100_000
bothdf_combined[FATALITY_COL] = bothdf_combined["DEATHS"] / bothdf_combined["Cars on Road"] * 100_000
bothdf_combined["Manufacturer"] = bothdf_combined.index

bothdf_combined.to_csv(OUT / "Aggregated Recall and Fatalities Data.csv", index=False)

# ---------------------------------------------------------------- k-means
km_features = bothdf_combined[["Lag Accounted Recalls", "DEATHS", RECALL_COL, FATALITY_COL]]
km_normalized = StandardScaler().fit_transform(km_features)

# k=2 because there are only 9 manufacturers
kmeans = KMeans(n_clusters=2, random_state=0, n_init="auto").fit(km_normalized)
bothdf_combined["Cluster"] = kmeans.labels_
print(bothdf_combined.sort_values("Cluster"))

# ---------------------------------------------------------------- figures
plt.figure()
plt.scatter(bothdf_combined[RECALL_COL], bothdf_combined[FATALITY_COL])
for name, row in bothdf_combined.iterrows():
    plt.annotate(name, (row[RECALL_COL], row[FATALITY_COL]), fontsize=8,
                 xytext=(4, 4), textcoords="offset points")
plt.title("Lag-Adjusted Recalled Units vs. Fatality Rate")
plt.xlabel(RECALL_COL)
plt.ylabel(FATALITY_COL)
plt.tight_layout()
plt.savefig(FIGS / "fig5_recalls_vs_fatalities.png", dpi=200)
plt.close()

for col, color, title, fname in [
    (RECALL_COL, "red", "Lag-Adjusted Recalled Units per Manufacturer", "fig3_recalls_by_manufacturer.png"),
    (FATALITY_COL, "green", "Fatality Rate per Manufacturer", "fig4_fatalities_by_manufacturer.png"),
]:
    plt.figure(figsize=(12, 6))
    plt.bar(bothdf_combined["Manufacturer"], bothdf_combined[col], color=color)
    plt.xlabel("Manufacturer")
    plt.ylabel(col)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(FIGS / fname, dpi=200)
    plt.close()
