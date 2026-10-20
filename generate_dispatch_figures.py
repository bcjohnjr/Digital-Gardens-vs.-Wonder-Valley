"""Journal figure PNG/TIFF outputs for synthetic hourly 17-site dispatch screen."""
from pathlib import Path
import csv
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'results';F=ROOT/'figures';F.mkdir(exist_ok=True)
R=list(csv.DictReader((D/'dispatch_scenario_summary.csv').open()))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'savefig.dpi':240,'axes.spines.top':False,'axes.spines.right':False})
labels=['Constrained\nlocal','Hybrid\nexpansion','Wind-intensive\ncase','Large regional\nbuild']
base=np.array([float(r['grid_baseline_gwh'])/1000 for r in R]);smart=np.array([float(r['grid_coordinated_gwh'])/1000 for r in R]);save=(base-smart)*1000
fig,ax=plt.subplots(figsize=(9,4.8));x=np.arange(4);w=.32
b1=ax.bar(x-w/2,base,w,label='Fixed job allocation',color='#6b7280');b2=ax.bar(x+w/2,smart,w,label='Renewable-responsive allocation',color='#117e77')
ax.set_xticks(x,labels);ax.set_ylabel('Annual utility electricity (TWh)');ax.set_ylim(0,max(base)*1.2)
for j,sv in enumerate(save):
 ax.text(j,max(base[j],smart[j])+0.42,('~0' if sv<.01 else f'{sv:,.0f}')+' GWh saved',ha='center',fontsize=9)
ax.legend(loc='upper right');ax.set_title('Modeled annual utility imports across 17 B.C. sites')
fig.text(.09,.01,'Synthetic hourly weather, 90% IT utilization, 65% flexible share, 2% shifting penalty; no verified firm hydro.',fontsize=8,color='#444444')
fig.tight_layout(rect=[0,.045,1,1]);fig.savefig(F/'Figure_6_renewable_responsive_dispatch.png');fig.savefig(F/'Figure_6_renewable_responsive_dispatch.tif',dpi=300);plt.close(fig)
rows=list(csv.DictReader((D/'dispatch_hourly_network.csv').open()))
hyb=[r for r in rows if r['scenario']=='Hybrid expansion']
sav=np.array([float(r['grid_fixed_mwh'])-float(r['grid_coordinated_mwh']) for r in hyb]);active=int(np.count_nonzero(sav>1e-6))
fig,ax=plt.subplots(figsize=(9,4.8))
ax.hist(sav,bins=[0,.001,1,5,10,20,50,100,200,500,1000,3000],color='#127e80',edgecolor='white')
ax.set_xscale('symlog',linthresh=1);ax.set_ylabel('Number of synthetic hours');ax.set_xlabel('Grid-import reduction per hour (MWh)');ax.set_title('Most hours have no feasible displacement opportunity')
ax.text(.98,.98,f'Hours with any grid saving: {active:,} / 8,760 ({active/8760:.1%})',transform=ax.transAxes,va='top',ha='right',bbox={'facecolor':'white','alpha':0.90,'edgecolor':'#dedede'})
fig.text(.09,.01,'Hybrid expansion sensitivity; fixed installed GPU capacity and renewable surplus jointly limit relocation.',fontsize=8,color='#444444')
fig.tight_layout(rect=[0,.045,1,1]);fig.savefig(F/'Figure_7_dispatch_opportunity_hours.png');fig.savefig(F/'Figure_7_dispatch_opportunity_hours.tif',dpi=300);plt.close(fig)
print('Generated Figure 6 and Figure 7. Active hours=',active)
