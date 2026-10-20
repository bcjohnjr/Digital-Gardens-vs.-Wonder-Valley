"""Reproducible 17-site *synthetic hourly* flexible-computing dispatch screen.

NOT measured hourly solar/wind. Solar energy reconciles to previously retrieved
2015 BC Hydro monthly proxy series, with hypothetical submonthly shape.
Monthly wind CF is explicitly assumed; spatial/temporal variability synthetic.
Hydro omitted until rights/head/multiyear low-flow hydrographs validated.

Dispatch is an exact greedy reduction of hourly grid purchases for a simplified
linear transferable-load model: every receiving site must have a renewable surplus
and unused rated equipment, every donating site must have grid purchases and
preemptible jobs; transfer creates a small extra recipient electricity burden.

No jobs are migrated in reality, no WAN checkpoint/time-to-quality validated.
"""
from __future__ import annotations
import csv, gzip, calendar, math, random, pathlib, collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'inputs'/'bc17_monthly_pv_wind_proxy.csv'
NODES=ROOT/'inputs'/'site_it_capacity_assumptions.csv'
SITEINFO=ROOT/'inputs'/'bc17_site_resource_proxies.csv'
YEAR=2025  # nonleap synthetic calendar; not claimed 2025 observations
PUE=1.15
SCENARIOS={
 'Constrained local':(1.0,0.3),
 'Hybrid expansion':(2.0,1.0),
 'Wind-intensive sensitivity':(1.0,2.0),
 'Large regional build':(4.0,1.0),
}
FIELDS=['scenario','utilization','movable_fraction','transfer_penalty','hours','it_capacity_mw','solar_nameplate_mw','wind_nameplate_mw','demand_gwh','renewable_gwh','grid_baseline_gwh','grid_coordinated_gwh','grid_saved_gwh','grid_saving_pct','renewable_share_baseline_pct','renewable_share_coordinated_pct','curtail_baseline_gwh','curtail_coordinated_gwh','curtail_avoided_gwh','relocated_work_gwh','additional_transfer_electricity_gwh','peak_grid_baseline_mw','peak_grid_coordinated_mw','max_facility_mw','grid_peak_reduction_mw']

def load_input():
 sites=list(csv.DictReader(NODES.open(encoding='utf-8',newline='')))
 metadata={r['Community']:r for r in csv.DictReader(SITEINFO.open(encoding='utf-8',newline=''))}
 month={}
 for r in csv.DictReader(SOURCE.open(encoding='utf-8',newline='')):
  month[(r['Community'],int(r['month_number']))]=r
 assert len(sites)==17 and len(month)==17*12
 assert all(r['node'] in metadata for r in sites)
 return sites,metadata,month

def hourly_shapes(sites,metadata,month,seed=17042026,regional_correlation=0.50):
 """Produces reproducible 8760 x 17 hourly generation factors, capped at 1.
 Monthly solar kWh per installed kWp and wind monthly CF matched after hourly shaping.
 Correlated stochastic weather: NOT observations / not a physical mesoscale model.
 """
 rng=random.Random(seed)
 regions=['Thompson','Okanagan','Fraser east','Lower mainland']
 daily_reg={}; daily_solar_reg={}
 for day in range(1,366):
  for reg in regions:
   daily_reg[(day,reg)]=rng.gauss(0,1)
   daily_solar_reg[(day,reg)]=max(0.16,min(1.55,0.86+rng.gauss(0,.27)))
 out={s['node']:[None]*8760 for s in sites}
 for s in sites:
  name=s['node']; lat=float(metadata[name]['Latitude APPROX']);reg=metadata[name]['dispatch_wind_region']
  raw_solar=[];raw_wind=[];dates=[]; x=0.;t=0
  for mo in range(1,13):
   for day in range(1,calendar.monthrange(YEAR,mo)[1]+1):
    day_num=(__import__('datetime').date(YEAR,mo,day)-__import__('datetime').date(YEAR,1,1)).days+1
    decl=math.radians(23.44)*math.sin(2*math.pi*(284+day_num)/365)
    phi=math.radians(lat)
    cosh=max(-1,min(1,-math.tan(phi)*math.tan(decl)))
    daylen=(24/math.pi)*math.acos(cosh)
    cloud=daily_solar_reg[(day_num,reg)]*(0.9+0.2*rng.random())
    for hh in range(24):
     sunlight=max(0,math.sin(math.pi*(hh-(12-daylen/2)+0.5)/daylen))**1.55
     raw_solar.append(sunlight*cloud)
     # AR1 site weather plus synoptic regional shocks. Not measured or calibrated.
     x=0.76*x+math.sqrt(1-0.76**2)*rng.gauss(0,1)
     regshock=daily_reg[(day_num,reg)]
     wind=max(0.04,min(1.9,1+regional_correlation*regshock+0.28*x))
     raw_wind.append(wind);dates.append((mo,day,hh));t+=1
  assert len(raw_solar)==8760
  for mo in range(1,13):
   indices=[i for i,(m,_,_) in enumerate(dates) if m==mo]
   r=month[(name,mo)]
   target_s=float(r['pv_kwh_per_kwp'])/1000 # monthly per-MW PV energy in MWh/MW
   # dimensionless solar hourly CF, sum of hours = kWh/kWp / 1000 in MWh per MW
   # 1 MW * kWh/kWp -> MWh = kWh/kWp numerically; fix below:
   target_s=float(r['pv_kwh_per_kwp']) # MWh for each installed MW
   base=sum(raw_solar[i] for i in indices)
   solar_scale=target_s/base if base else 0
   target_w=float(r['wind_assumed_cf'])*len(indices)
   basew=sum(raw_wind[i] for i in indices)
   w_scale=target_w/basew
   # cap and redistribute iteratively, preserving published monthly PV and assumed monthly wind
   def saturating_rescale(vals,target):
    arr=[min(1.,max(0,v)) for v in vals]
    for _ in range(8):
     delta=target-sum(arr)
     if abs(delta)<1e-8:break
     if delta>0:
      cap=sum(1-v for v in arr)
      if cap<1e-10:break
      arr=[v+delta*(1-v)/cap for v in arr]
     else:
      mass=sum(arr)
      if mass<1e-10:break
      arr=[v+delta*v/mass for v in arr]
    return arr
   pv=saturating_rescale([raw_solar[i]*solar_scale for i in indices],target_s)
   wi=saturating_rescale([raw_wind[i]*w_scale for i in indices],target_w)
   assert abs(sum(pv)-target_s)<1e-5,(name,mo,'pv',sum(pv),target_s)
   assert abs(sum(wi)-target_w)<1e-5,(name,mo,'wind',sum(wi),target_w)
   for j,i in enumerate(indices):out[name][i]=(pv[j],wi[j],mo)
 return out

def allocate_one(capacity, pv, wind, util=.90, movable=.65, surcharge=.02):
 """One hour two-stage allocation preserving workloads and receiver GPU caps.
 Electricity MW for jobs proportional to utilization; fixed PUE multiplier.
 """
 n=len(capacity)
 original=[capacity[i]*util*PUE for i in range(n)]
 rated=[c*PUE for c in capacity]
 generation=[pv[i]+wind[i] for i in range(n)]
 jobs=[original[i] for i in range(n)]
 gridbefore=sum(max(0,jobs[i]-generation[i]) for i in range(n))
 curtailbefore=sum(max(0,generation[i]-jobs[i]) for i in range(n))
 buyers=[i for i in range(n) if jobs[i]>generation[i]+1e-10]
 sellers=[i for i in range(n) if generation[i]>jobs[i]+1e-10]
 # receivers need both spare installed compute and stranded renewable power
 buyer_budget={i:min(jobs[i]*movable, jobs[i]-generation[i]) for i in buyers}
 seller_budget={i:min(rated[i]-jobs[i],generation[i]-jobs[i]) for i in sellers}
 buyers.sort(key=lambda i:buyer_budget[i],reverse=True)
 sellers.sort(key=lambda i:seller_budget[i],reverse=True)
 moved=0.
 for i in sellers:
  can_absorb=seller_budget[i]/(1+surcharge)
  if can_absorb<=1e-10:continue
  for j in buyers:
   q=min(can_absorb,buyer_budget[j])
   if q<=1e-10:continue
   jobs[j]-=q;jobs[i]+=q*(1+surcharge)
   buyer_budget[j]-=q;can_absorb-=q;moved+=q
   if can_absorb<=1e-10:break
 gridafter=sum(max(0,jobs[i]-generation[i]) for i in range(n))
 curtailafter=sum(max(0,generation[i]-jobs[i]) for i in range(n))
 assert all(-1e-7<=jobs[i]<=rated[i]+1e-7 for i in range(n))
 assert gridafter<=gridbefore+1e-6
 assert abs(sum(jobs)-sum(original)-moved*surcharge)<1e-5
 assert abs((gridbefore-gridafter)-(curtailbefore-curtailafter)+moved*surcharge)<1e-5
 return dict(before=gridbefore,after=gridafter,curtail_before=curtailbefore,curtail_after=curtailafter,shift=moved,extra=moved*surcharge,original=original,final=jobs,gen=generation,rated=rated)

def calc(sites,shapes,scenario,util=.9,movable=.65,surcharge=.02,save_hourly=False):
 pv_mult,wind_mult=SCENARIOS[scenario]
 names=[s['node'] for s in sites];cap=[float(s['it_mw']) for s in sites];n=len(sites)
 aggregates=collections.defaultdict(lambda:collections.defaultdict(float))
 hourly=[];permonth=collections.defaultdict(lambda:collections.defaultdict(float));siteagg=collections.defaultdict(lambda:collections.defaultdict(float))
 for h in range(8760):
  month=shapes[names[0]][h][2]
  pv=[cap[i]*pv_mult*shapes[names[i]][h][0] for i in range(n)]
  wind=[cap[i]*wind_mult*shapes[names[i]][h][1] for i in range(n)]
  r=allocate_one(cap,pv,wind,util,movable,surcharge)
  k=aggregates['all']
  k['demand']+=sum(r['original']);k['generation']+=sum(r['gen'])
  k['gridbefore']+=r['before'];k['gridafter']+=r['after']
  k['curtailbefore']+=r['curtail_before'];k['curtailafter']+=r['curtail_after'];k['shift']+=r['shift'];k['extra']+=r['extra']
  k['peakbefore']=max(k['peakbefore'],r['before']);k['peakafter']=max(k['peakafter'],r['after'])
  p=permonth[month]
  for key,value in [('demand',sum(r['original'])),('generation',sum(r['gen'])),('gridbefore',r['before']),('gridafter',r['after']),('curtailbefore',r['curtail_before']),('curtailafter',r['curtail_after']),('shift',r['shift']),('extra',r['extra'])]:p[key]+=value
  for i,name in enumerate(names):
   a=siteagg[name]
   base=max(0,r['original'][i]-r['gen'][i]);after=max(0,r['final'][i]-r['gen'][i]);
   a['base']+=base;a['after']+=after;a['demand']+=r['original'][i];a['renewable']+=r['gen'][i]
   a['curtailbefore']+=max(0,r['gen'][i]-r['original'][i]);a['curtailafter']+=max(0,r['gen'][i]-r['final'][i]);a['change']+=(r['final'][i]-r['original'][i]);
  if save_hourly:hourly.append(dict(scenario=scenario,synthetic_hour=h+1,month=month,facility_demand_mwh=round(sum(r['original']),4),renewable_mwh=round(sum(r['gen']),4),grid_fixed_mwh=round(r['before'],4),grid_coordinated_mwh=round(r['after'],4),curtail_fixed_mwh=round(r['curtail_before'],4),curtail_coordinated_mwh=round(r['curtail_after'],4),shifted_compute_mwh=round(r['shift'],4)))
 k=aggregates['all'];base=k['gridbefore'];after=k['gridafter'];demand=k['demand'];
 summary=dict(scenario=scenario,utilization=util,movable_fraction=movable,transfer_penalty=surcharge,hours=8760,it_capacity_mw=sum(cap),solar_nameplate_mw=sum(cap)*pv_mult,wind_nameplate_mw=sum(cap)*wind_mult,demand_gwh=demand/1000,renewable_gwh=k['generation']/1000,grid_baseline_gwh=base/1000,grid_coordinated_gwh=after/1000,grid_saved_gwh=(base-after)/1000,grid_saving_pct=100*(base-after)/base if base else 0,renewable_share_baseline_pct=100*(1-base/demand),renewable_share_coordinated_pct=100*(1-after/(demand+k['extra'])),curtail_baseline_gwh=k['curtailbefore']/1000,curtail_coordinated_gwh=k['curtailafter']/1000,curtail_avoided_gwh=(k['curtailbefore']-k['curtailafter'])/1000,relocated_work_gwh=k['shift']/1000,additional_transfer_electricity_gwh=k['extra']/1000,peak_grid_baseline_mw=k['peakbefore'],peak_grid_coordinated_mw=k['peakafter'],max_facility_mw=sum(cap)*PUE,grid_peak_reduction_mw=k['peakbefore']-k['peakafter'])
 return summary,siteagg,permonth,hourly

def write(path,rows):
 assert rows,(path,'empty')
 with path.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 sites,meta,month=load_input();shapes=hourly_shapes(sites,meta,month)
 with gzip.open(OUT/'synthetic_hourly_site_resource_factors.csv.gz','wt',encoding='utf-8',newline='') as f:
  w=csv.writer(f);w.writerow(['node','hour_1_8760','solar_cf_generated_not_observed','wind_cf_generated_not_observed','month'])
  for site in sites:
   for h,(pv,wind,mo) in enumerate(shapes[site['node']]):w.writerow([site['node'],h+1,round(pv,7),round(wind,7),mo])
 summ=[];allsite=[];allmonthly=[];hourly=[]
 for scenario in SCENARIOS:
  s,site,monthly,hours=calc(sites,shapes,scenario,save_hourly=True);summ.append(s);hourly.extend(hours)
  for name,vals in site.items():allsite.append(dict(scenario=scenario,node=name,it_mw=next(float(a['it_mw']) for a in sites if a['node']==name),demand_gwh=round(vals['demand']/1000,5),renewable_gwh=round(vals['renewable']/1000,5),grid_baseline_gwh=round(vals['base']/1000,5),grid_coordinated_gwh=round(vals['after']/1000,5),grid_saved_gwh=round((vals['base']-vals['after'])/1000,5),net_workload_shift_gwh=round(vals['change']/1000,5),curtail_baseline_gwh=round(vals['curtailbefore']/1000,5),curtail_coordinated_gwh=round(vals['curtailafter']/1000,5)))
  for mo,k in monthly.items():allmonthly.append(dict(scenario=scenario,month=mo,demand_gwh=k['demand']/1000,renewable_gwh=k['generation']/1000,grid_baseline_gwh=k['gridbefore']/1000,grid_coordinated_gwh=k['gridafter']/1000,grid_saved_gwh=(k['gridbefore']-k['gridafter'])/1000,curtail_baseline_gwh=k['curtailbefore']/1000,curtail_coordinated_gwh=k['curtailafter']/1000,relocated_work_gwh=k['shift']/1000))
 write(OUT/'dispatch_scenario_summary.csv',summ)
 write(OUT/'dispatch_site_summary.csv',allsite)
 write(OUT/'dispatch_monthly_summary.csv',allmonthly)
 write(OUT/'dispatch_hourly_network.csv',hourly)
 sensitive=[]
 for scen in ['Constrained local','Hybrid expansion','Wind-intensive sensitivity','Large regional build']:
  for util in [.65,.75,.90]:
   for mov in [.25,.65,.85]:
    s,*_=calc(sites,shapes,scen,util=util,movable=mov);sensitive.append(s)
 write(OUT/'dispatch_utilization_flex_sensitivity.csv',sensitive)
 penalty=[]
 for scen in SCENARIOS:
  for surcharge in [0,.02,.10]:
   s,*_=calc(sites,shapes,scen,surcharge=surcharge);penalty.append(s)
 write(OUT/'dispatch_transfer_penalty_sensitivity.csv',penalty)
 # algebraic screening, not measured improvement
 assert abs(summ[0]['demand_gwh']-32861.98)<2
 assert all(s['grid_saved_gwh']>=-1e-8 for s in summ)
 assert all(s['grid_peak_reduction_mw']>=-1e-8 for s in summ)
 assert len(hourly)==4*8760
 assert all(r['grid_coordinated_gwh']>=0 for r in summ)
 for s in summ:
  print(s['scenario'], 'grid fixed',round(s['grid_baseline_gwh']/1000,3),'TWh','coordinated',round(s['grid_coordinated_gwh']/1000,3),'TWh', 'saving',round(s['grid_saved_gwh'],2),'GWh','peak saving',round(s['grid_peak_reduction_mw'],2),'MW')
 print('PASS: 17-site hourly conservation, saturation, monotone import tests')
if __name__=='__main__':main()
