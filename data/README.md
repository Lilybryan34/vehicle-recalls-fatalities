# Data

The two raw files are not committed (they are large and publicly available). Download them and place them in this folder with these names.

| File | Source |
|---|---|
| `Recalls_Data.csv` | NHTSA "Recalls Data" on data.transportation.gov: https://data.transportation.gov/d/6axg-epim (export as CSV). Needs the columns `Manufacturer`, `Potentially Affected`, `Report Received Date`. |
| `vehicle.csv` | NHTSA Fatality Analysis Reporting System (FARS), vehicle table. Raw files: ftp://ftp.nhtsa.dot.gov/fars/ ; query tools: https://cdan.nhtsa.gov/. Needs the columns `MAKENAME`, `DEATHS`, `MOD_YEAR`. |
| `cars_on_road_proxy.csv` | Included. Estimated vehicles on the road per manufacturer. See the main README for how it was built and what is missing. |

**Filters applied:** recalls with a report date in 2010-2024; crash records with a vehicle model year in 2010-2024. NHTSA updates both datasets over time, so a fresh download may differ slightly from the numbers reported here.

Both datasets are U.S. government data.
