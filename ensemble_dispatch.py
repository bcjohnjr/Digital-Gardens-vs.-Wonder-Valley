"""Sensitivity study, NOT independent observed meteorological years."""
import csv
from renewable_dispatch import load_input,hourly_shapes,calc,OUT
sites,metadata,monthly=load_input()
rows=[]
for seed,corr in [(17042026,.50),(42,.50),(2026,.50),(17042026,.20),(17042026,.80)]:
 shapes=hourly_shapes(sites,metadata,monthly,seed=seed,regional_correlation=corr)
 for wind_mult in [.8,1.0,1.2]:
  if wind_mult!=1:
   varied={name:[(s,min(1,w*wind_mult),m) for s,w,m in vals] for name,vals in shapes.items()}
  else: varied=shapes
  summary,*_=calc(sites,varied,'Hybrid expansion')
  rows.append(dict(seed=seed,regional_shock_coefficient=corr,wind_generation_multiplier=wind_mult,grid_baseline_gwh=round(summary['grid_baseline_gwh'],4),grid_after_gwh=round(summary['grid_coordinated_gwh'],4),grid_savings_gwh=round(summary['grid_saved_gwh'],4),savings_percent=round(summary['grid_saving_pct'],4),peak_reduction_mw=round(summary['grid_peak_reduction_mw'],4)))
with (OUT/'hybrid_synthetic_ensemble.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,rows[0].keys());w.writeheader();w.writerows(rows)
print('Ensemble:',len(rows),'runs; min/max saving GWh',min(r['grid_savings_gwh'] for r in rows),max(r['grid_savings_gwh'] for r in rows))
