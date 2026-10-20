"""Regenerate publication figures from the model-generated CSV outputs.

Dependencies: matplotlib (requirements.txt). The plotted scenarios are not empirical
performance or utility allocation measurements.
"""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'
FIGURES=ROOT/'figures'
FIGURES.mkdir(parents=True,exist_ok=True)

def read(name):
    with (RESULTS/name).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))

# FIG 1 — the combined program-level allocation is assumed as 300+100 MW.
node=read('node_capacity.csv')
capacity=sum(float(r['it_mw']) for r in node)
peak=sum(float(r['facility_peak_mw']) for r in node)
vals=[400.0,capacity,peak]
labels=['2026 combined AI + data\ncentre allocation',
        'Digital Gardens proposed IT capacity',
        'Digital Gardens facility peak at PUE 1.15']
fig,ax=plt.subplots(figsize=(11.8,5.3))
bars=ax.barh(labels,vals)
ax.invert_yaxis();ax.set_xlim(0,max(vals)*1.15)
for bar,val in zip(bars,vals):
    ax.text(val+45,bar.get_y()+bar.get_height()/2,f'{val:,.0f}',va='center',fontsize=11)
ax.set_xlabel('Power capacity (MW): program allocation and screening load')
ax.set_title('New allocation constraint versus proposed network')
fig.tight_layout()
fig.savefig(FIGURES/'Figure_1_capacity_vs_allocation.png',dpi=180)
plt.close(fig)

# FIG 2 — electricity emissions from synthetic carbon-intensity choices only.
rows=read('carbon_heat_sensitivity.csv')
rows=[r for r in rows if float(r['fraction_of_useful_heat_displacing_gas'])==0]
rows.sort(key=lambda r:float(r['grid_kg_co2e_per_mwh']))
x=[float(r['grid_kg_co2e_per_mwh']) for r in rows]
y=[float(r['electricity_co2e_mt_y']) for r in rows]
fig,ax=plt.subplots(figsize=(10.8,5.25))
ax.plot(x,y,marker='o')
ax.grid(alpha=.26)
ax.set_xlabel('Assumed delivered electricity intensity (kg CO$_2$e/MWh)')
ax.set_ylabel('Annual location-based electricity emissions (Mt CO$_2$e/y)')
ax.set_title('Digital Gardens sensitivity: 32.86 TWh/year demand')
fig.tight_layout()
fig.savefig(FIGURES/'Figure_2_emissions_sensitivity.png',dpi=180)
plt.close(fig)

# FIG 3 — 20 s local step, 400 Gb/s link at 50% usable, 20% exposed.
rows=read('proximity_training_scenarios.csv')
by_name={r['scenario']:r for r in rows}
scenarios=[('1 GB','nearby_partitioned_1GB'),('10 GB','nearby_partitioned_10GB'),
           ('100 GB','nearby_partitioned_100GB'),('1 TB','nearby_partitioned_1TB')]
y=[float(by_name[n]['slowdown_pct']) for _,n in scenarios]
fig,ax=plt.subplots(figsize=(10.2,5.1))
bars=ax.bar([name for name,_ in scenarios],y)
for rect,val in zip(bars,y):
    ax.text(rect.get_x()+rect.get_width()/2, val+0.28, f'{val:.3f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_ylim(0,max(y)*1.13)
ax.text(.02,.95,'20 s baseline | 400 Gb/s | 50% usable | 80% overlap',
        transform=ax.transAxes,va='top',fontsize=10)
ax.set_ylabel('Conditional WAN-related slowdown (%)')
ax.set_title('Proximity-aware training: synchronization sensitivity')
ax.grid(axis='y',alpha=.25)
fig.tight_layout()
fig.savefig(FIGURES/'Figure_4_proximity_aware_training.png',dpi=180)
plt.close(fig)
print('Generated three figures in figures/')

# FIG 4 — 2026 hardware reference and prospective 2036/2041 WAN sensitivity.
rows=read('horizon_training_methods.csv')
methods=['Data parallel (all-reduce)','Pipeline parallel (WAN stage)',
         'Local-SGD / DiLoCo H=100 (70B)',
         'Decoupled DiLoCo H=500 (70B)',
         'Decoupled DiLoCo H=500 (1T)',
         'Regional inference (local replica)']
short=['Synchronous data parallel','Cross-site pipeline',
       'Local SGD: 100 steps','Decoupled: 70B / 500 steps',
       'Decoupled: 1T / 500 steps','Site-local inference']
fig,axs=plt.subplots(1,3,figsize=(17,6),sharey=True)
for ax,year in zip(axs,[2026,2036,2041]):
 points=[]
 for m in methods:
  record=next(r for r in rows if int(r['year'])==year and r['method']==m and int(r['representative_site_distance_km'])==250)
  points.append(float(record['network_only_efficiency_pct']))
 ax.barh(short,points);ax.set_xlim(0,105);ax.invert_yaxis()
 ax.set_title(f'{year}: conditional network-only efficiency')
 ax.grid(axis='x',alpha=.25)
 for i,yval in enumerate(points):
  ax.text(min(yval+1,97.5),i,f'{yval:.1f}%',fontsize=8,va='center')
axs[0].set_xlabel('Percent of equivalent site-local steps');axs[1].set_xlabel('Percent');axs[2].set_xlabel('Percent')
fig.suptitle('Network penalty screen: same illustrative 70B workload (1T where stated); 250 km site separation',fontsize=13)
fig.tight_layout(rect=[0,.0,1,.94]);fig.savefig(FIGURES/'Figure_5_2026_2041_training_methods.png',dpi=200);plt.close(fig)

# FIG 5 — annual operational grid emissions normalized to one continuously used facility MW.
rows=read('wonder_per_mw_emissions_comparison.csv')
points=sorted([(int(float(x['bc_grid_emission_intensity_kg_per_MWh'])),float(x['bc_tCO2e_per_continuous_MW_year'])) for x in rows if float(x['wonder_reported_emissions_MtCO2e_per_year'])==25.7])
fig,ax=plt.subplots(figsize=(11,5.6))
ax.plot([x for x,_ in points],[y for _,y in points],marker='o',label='Digital Gardens, assumed grid intensity')
ax.axhspan(25.7e6/7500,30.5e6/7500,alpha=.2,label='Wonder Valley: analyst projection / 7.5 GW')
ax.set_xlabel('Assumed Digital Gardens electricity carbon intensity (kg CO$_2$e/MWh)')
ax.set_ylabel('t CO$_2$e per continuously supplied MW-year')
ax.set_title('Power-normalized emissions, unmatched accounting scopes: scenario comparison')
ax.grid(alpha=.24);ax.legend(loc='upper left',fontsize=9)
fig.tight_layout();fig.savefig(FIGURES/'Figure_3_power_normalized_emissions.png',dpi=200);plt.close(fig)
for f in FIGURES.glob('Figure_*.png'):
 from PIL import Image
 Image.open(f).convert('RGB').save(f.with_suffix('.tif'),compression='tiff_lzw',dpi=(300,300))
print('Rendered 5 PNG/TIFF scenario figures (unmeasured).')
