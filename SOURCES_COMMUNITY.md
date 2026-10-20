# Community screen reference register

- Statistics Canada (2022), British Columbia 2021 Census profile: average private household size 2.4. https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?DGUIDlist=2021A000259&GENDERlist=1&HEADERlist=0&Lang=E&STATISTIClist=1&SearchText=richmond
- BC Hydro (2026), public charging tariffs effective April 1: Level 2 CAD 0.3083/kWh, fast charging CAD 0.3969/kWh before tax. https://www.bchydro.com/powersmart/electric-vehicles/public-charging/charging-rates-roaming.html
- Natural Resources Canada, Readiness of Producing and Deploying Liquid Drop-In Fuels: renewable diesel cost may exceed petroleum-derived diesel, with fuel-specific and temporal variation. https://natural-resources.canada.ca/energy-efficiency/transportation-energy-efficiency/readiness-producing-deploying-liquid-drop-fuels-canada
- Digital Gardens' proposal planning population (787,934) supplied by author; site IT capacities from existing input CSVs. All EV fleet prices, EV consumption, annual distance, market food prices, participation, fuel litres, fuel-premium gaps and credit assumptions are analyst sensitivity inputs requiring future verification.

## Corrected food entitlements (author-defined planning obligation, 20 October 2026)
- Fresh produce: 146 kg per eligible resident-year.
- Marketable seafood: 46 kg per eligible resident-year.
- Two-phase cumulative populations are 393,967 and 787,934 (phase split remains an illustrative 50/100% assumption).
- Values of CAD 3.50/kg produce and CAD 7.00/kg seafood are scenario inputs, not verified retail or delivered-cost quotations.
- Gross harvest and aquaculture liveweight cannot both be treated as equivalent to marketable delivered food. The revised screen uses 90% greenhouse pack-out and 65% whole-animal saleable seafood yield; these are unverified conversion assumptions, not independently validated B.C. producer benchmarks. Species-by-species processing trials and food-safety/packaging/distribution agreements are needed.
- Full-stage obligations are 115,038.364 metric tonnes produce and 36,244.964 metric tonnes marketable seafood, or CAD 656.349022 million in annual retail-equivalent value.

Calculation source-of-record for current community economics: results/community_two_phase_baseline.csv and results/agriculture_2021_eight_regional_districts.csv, with reproducibility scripts under model/. GitHub release state is not inferred from the accompanying ZIP.
