from pathlib import Path
import csv
import matplotlib.pyplot as plt
from seasonal_food_heat import BASE,OUT,SCENARIOS
D=BASE/'figures';D.mkdir(exist_ok=True)
def load(n):
 with (OUT/n).open() as f:return list(csv.DictReader(f))
raw=load('seasonal_food_monthly_heat.csv')
mo=[r for r in raw if r['scenario']=='Expansion']
months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
fig,ax=plt.subplots(figsize=(9,4.3),dpi=230)
ax.plot(months,[float(x['recoverable_heat_potential_GWh']) for x in mo],lw=2.4,label='Potential recovered heat')
ax.bar(months,[float(x['greenhouse_demand_GWh']) for x in mo],label='Greenhouse',alpha=.75)
ax.bar(months,[float(x['aquaculture_demand_GWh']) for x in mo],bottom=[float(x['greenhouse_demand_GWh']) for x in mo],label='RAS',alpha=.85)
ax.bar(months,[float(x['fruit_dryer_demand_GWh'])+float(x['salmon_dryer_demand_GWh']) for x in mo], bottom=[float(x['greenhouse_demand_GWh'])+float(x['aquaculture_demand_GWh']) for x in mo],label='Fruit + salmon drying',alpha=.85)
ax.set_ylabel('Monthly thermal energy (GWh)');ax.set_title('Expansion scenario: seasonal heat budget, not measured offtake');ax.grid(axis='y',alpha=.2);ax.legend(ncol=2,loc='upper right',fontsize=8);fig.tight_layout();fig.savefig(D/'Figure_9_Seasonal_Thermal_Dispatch.png');plt.close(fig)
S=load('seasonal_food_scenario_summary.csv');names=[x['scenario'] for x in S]
fig,ax=plt.subplots(figsize=(8.5,4.4),dpi=230)
ix=range(4)
ax.bar([i-.2 for i in ix],[float(x['heat_served_GWh'])/1000 for x in S],width=.4,label='Modeled heat served (TWh/y)')
ax.bar([i+.2 for i in ix],[float(x['total_extra_electricity_GWh'])/1000 for x in S],width=.4,label='Additional electricity (TWh/y)')
ax.set_xticks(list(ix));ax.set_xticklabels(names);ax.set_ylabel('TWh per year');ax.set_title('Food-system deployment: thermal service versus incremental power');ax.legend(fontsize=9);ax.grid(axis='y',alpha=.2);fig.tight_layout();fig.savefig(D/'Figure_10_Heat_vs_Power.png');plt.close(fig)
fig,ax=plt.subplots(figsize=(8.5,4.3),dpi=230)
ix=range(4)
ax.bar([i-.25 for i in ix],[float(x['greenhouse_vegetables_t'])/1000 for x in S],width=.25,label='Greenhouse produce (kt/year)')
ax.bar(ix,[float(x['seafood_liveweight_t'])/1000 for x in S],width=.25,label='Aquaculture live weight (kt/year)')
ax.bar([i+.25 for i in ix],[float(x['dried_fruit_output_t'])/1000+float(x['dried_salmon_total_t'])/1000 for x in S],width=.25,label='Dried product (kt/year)')
ax.set_xticks(list(ix));ax.set_xticklabels(names);ax.set_ylabel('Modelled output (thousand tonnes/year)');ax.set_title('Conditional outputs — no demand, food-safety or price validation');ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(D/'Figure_11_Food_Outputs.png');plt.close(fig)
print('created',len(list(D.glob('Figure_*.png'))),'new figures')
