# Vehicle Recalls and Fatalities: Manufacturer-Level Analysis

Exploratory analysis of whether manufacturers with more recalled vehicles also have higher crash fatality rates. Course project for CISC 5380 (Fall 2025).

**Result in one line:** across the nine manufacturers studied, recalled units per vehicle on the road show no clear linear pattern with fatality rate, and the regression notebook finds vehicle exposure (cars on the road) a stronger predictor of deaths than recalls. With only nine data points, this is exploratory, not conclusive.

## Data

- **NHTSA Recalls Data** (data.transportation.gov): recall date, manufacturer, number of vehicles potentially affected.
- **NHTSA Fatality Analysis Reporting System (FARS), vehicle table:** vehicle make, model year, deaths.
- **NHTSA survivability curve** (Lu, 2006, DOT HS 809 952), used to estimate vehicles on the road.

Raw files are not included. See [`data/README.md`](data/README.md) for sources and file names.

## Method

1. Mapped vehicle makes (e.g. Acura) to parent manufacturers (e.g. Honda) so the two datasets could be joined. Nine manufacturers were analyzed (Forest River was dropped as a commercial/RV builder).
2. Estimated vehicles on the road (COR) per manufacturer from unit sales and the survivability curve over a 15-year window.
3. Applied a four-year lag to recall volume: recalls from 2010-2021 count 4x, and 2022, 2023, 2024 count 3x, 2x, 1x, to reflect the time it takes for repairs.
4. Summed lag-adjusted recalled units and deaths per manufacturer, then divided by COR (x100,000).
5. Ran K-means (k=2) on four standardized features.

## Results

- Honda has the highest lag-adjusted recalled units per vehicle on the road; Nissan has the highest fatality rate.
- K-means grouped Chrysler, Ford, General Motors, Honda and Nissan (larger volume) apart from BMW, Daimler, Mercedes and Volkswagen.
- BMW's fatality rate is almost double Mercedes', despite both being German luxury brands.

![Recalls vs fatalities](figures/fig5_recalls_vs_fatalities.png)

## Regression analysis (Paige Mitchell)

[`regression/regression_analysis.ipynb`](regression/regression_analysis.ipynb) was written by Paige Mitchell, my project partner. It runs on the combined CSV that `analysis.py` produces. What it reports (n = 9 manufacturers):

| Analysis | Result |
|---|---|
| Pearson correlation, total lag-adjusted recalled units vs. total deaths | r = 0.915, p = 0.0006 |
| Simple linear regression, deaths ~ recalls | R² = 0.836 |
| Multiple linear regression, deaths ~ recalls + cars on the road | R² = 0.931 |

The notebook's conclusion is that vehicle exposure explains fatality counts better than recall counts do. Notes on reading it:
- Both Pearson and the regressions use **totals**, which scale with how many vehicles a manufacturer sells. A strong correlation here is expected and is not evidence that recalls drive deaths.
- The notebook reports R² and coefficients only. It does **not** report significance tests (p-values or standard errors) for the regression coefficients, and the R² values are in-sample on nine points.

## Run it

```bash
pip install -r requirements.txt
# put Recalls_Data.csv and vehicle.csv in data/
python analysis.py
# then, optionally, open regression/regression_analysis.ipynb in Jupyter
```

Outputs go to `output/` (combined CSV) and `figures/`.

## Limitations

- **Only nine data points**, so statistical results are weak.
- **The recall measure is not a true rate.** It is lag-adjusted recalled units divided by COR (x100k). A vehicle recalled more than once is counted each time, and the lag multiplier inflates values. The column was renamed `Lag-Adj Recalled Units per COR (x100k)` for this reason.
- **COR is an estimate.** It uses one survivability curve for all manufacturers and excludes vehicles older than 15 years. The sales-by-year inputs and the multiplication were done separately and are **not in this repo**; the nine final values are in [`data/cars_on_road_proxy.csv`](data/cars_on_road_proxy.csv).
- No adjustment for vehicle age mix, driver demographics, or recall severity (an A/C recall and a brake recall count the same).
- Recalls are filtered by report year (2010-2024) and crash records by vehicle model year (2010-2024), which are not the same window.
- Correlational only; no causal claim is made.

## Possible extensions

A "lookback" analysis: instead of aggregating over all 15 years, compare recalls and fatalities in 5- or 10-year windows to see how the relationship changes over time and whether recent safety trends differ by manufacturer.

## Contributors

- **Lily Bryan:** data preprocessing, manufacturer mapping, vehicles-on-the-road estimate, recall lag, K-means clustering, visualizations, and the written report.
- **Paige Mitchell:** the regression and correlation notebook in `regression/`.

## License

MIT. See [LICENSE](LICENSE).
