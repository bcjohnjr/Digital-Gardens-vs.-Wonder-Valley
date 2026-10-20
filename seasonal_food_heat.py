"""Prospective scenario-screening mass/energy model for Digital Gardens food and heat.
Not site feasibility, measured heat offtake, electricity procurement, market forecast, food safety certification or ecological impact study.
Stdlib only. Heat supplied is potential at the network aggregate; 17-site physical realization requires local offtake and upgrades.
"""
from __future__ import annotations
import csv, json, calendar, math
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'results'
OUT.mkdir(exist_ok=True)
DAYS=[calendar.monthrange(2025,m)[1] for m in range(1,13)]
MONTHS=list(range(1,13))
# Normalize these shape weights (unvalidated B.C. winter seasonality screening, not observed met data).
HEAT_SHAPE=[.155,.135,.115,.085,.050,.025,.015,.015,.045,.080,.120,.160]
assert abs(sum(HEAT_SHAPE)-1.0)<1e-8
# Crop-lighting seasonality; all values are electrical energy, not light converted from recovered heat.
LED_SHAPE=[.17,.15,.13,.09,.05,.02,.01,.02,.06,.09,.10,.11]
LED_SHAPE=[a/sum(LED_SHAPE) for a in LED_SHAPE]
FRUIT_SHAPE=[0,0,0,0,0,.08,.22,.31,.24,.15,0,0]
SALMON_DRY_SHAPE=[.13,.08,.02,0,0,0,0,.03,.15,.20,.22,.17]
AQUA_SHAPE=[1.35,1.30,1.20,1.10,1.00,.80,.65,.65,.80,1.0,1.10,1.25]
AQUA_SHAPE=[DAYS[i]*AQUA_SHAPE[i]/sum(DAYS[j]*AQUA_SHAPE[j] for j in range(12)) for i in range(12)]
SPECIES={
    'salmon': {'share':.44,'heat_kwh_kg':2.0,'electric_kwh_kg':6.0,'category':'cold-water saline/controlled RAS'},
    'trout':  {'share':.25,'heat_kwh_kg':1.5,'electric_kwh_kg':5.0,'category':'freshwater RAS'},
    'prawns': {'share':.10,'heat_kwh_kg':5.0,'electric_kwh_kg':12.0,'category':'warmwater RAS (freshwater prawn sensitivity)'},
    'tilapia':{'share':.21,'heat_kwh_kg':3.0,'electric_kwh_kg':8.0,'category':'warmwater RAS'},
}
# The seafood volumes are prospective incremental live-weight equivalence, not additive to 2024 actual B.C. production.
SCENARIOS={
 'Demonstration':{'greenhouse_ha':100,'ras_tonnes':10000,'fruit_diversion':.02,'shellfish_nursery_modules':1,'salmon_dry_fraction':.08,'led_kwh_m2':40,'veg_yield_kg_m2':14},
 'Regional':{'greenhouse_ha':300,'ras_tonnes':30000,'fruit_diversion':.05,'shellfish_nursery_modules':3,'salmon_dry_fraction':.10,'led_kwh_m2':80,'veg_yield_kg_m2':20},
 'Expansion':{'greenhouse_ha':1000,'ras_tonnes':120000,'fruit_diversion':.05,'shellfish_nursery_modules':12,'salmon_dry_fraction':.10,'led_kwh_m2':160,'veg_yield_kg_m2':25},
 'Heat-intensive':{'greenhouse_ha':3000,'ras_tonnes':250000,'fruit_diversion':.10,'shellfish_nursery_modules':25,'salmon_dry_fraction':.10,'led_kwh_m2':450,'veg_yield_kg_m2':35},
}
# Source/project assumptions. Heat is 14.57TWh upper bound end-use potential from prior model, not measured delivery.
HEAT_MWH=14570000 # MWh per year
HEAT_KWH=HEAT_MWH*1000
IT_MW=3624.51
PUE=1.15
IT_UTIL=.90
HEAT_KWH_PER_M2=450
MARKETED_FRUIT_TONNES_2024=199227 # AAFC, 2024 B.C. marketed fruit, NOT measured waste
FRUIT_HEAT_KWH_PER_KG_WET=1.6
FRUIT_FAN_KWH_PER_KG_WET=.15
DRIED_FRUIT_MASS_FRACTION=.22
FISH_DRY_HEAT_KWH_PER_KG_WET=2.0
FISH_DRY_FAN_KWH_PER_KG_WET=.25
DRIED_FISH_MASS_FRACTION=.35
INDIAN_CANDY_SHARE_OF_DRIED_FISH=.30 # subtype, not added to total dried fish
DIRECT_LOW_TEMP_SHARE=.70
LOW_TEMP_COP=4.0
DRYING_COP=3.0
ELECTRICAL_OVERHEAD_ANCILLARY_FRACTION=.05

def write_csv(path, rows):
    if not rows: return
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def compute(scenario, p=None):
    p=dict(SCENARIOS[scenario] if p is None else p)
    sqm=p['greenhouse_ha']*10000
    seafood_kg=p['ras_tonnes']*1000
    fruit_wet_kg=MARKETED_FRUIT_TONNES_2024*p['fruit_diversion']*1000
    salmon_wet_kg=seafood_kg*SPECIES['salmon']['share']
    salmon_dry_input_kg=salmon_wet_kg*p['salmon_dry_fraction']
    gh_heat_kwh=sqm*HEAT_KWH_PER_M2
    led_kwh=sqm*p['led_kwh_m2']
    nursery_heat_kwh=p['shellfish_nursery_modules']*250000
    nursery_elec_kwh=p['shellfish_nursery_modules']*1000000
    aqua_heat_kwh=seafood_kg*sum(a['share']*a['heat_kwh_kg'] for a in SPECIES.values())+nursery_heat_kwh
    aqua_elec_kwh=seafood_kg*sum(a['share']*a['electric_kwh_kg'] for a in SPECIES.values())+nursery_elec_kwh
    fruit_heat_kwh=fruit_wet_kg*FRUIT_HEAT_KWH_PER_KG_WET
    salmon_heat_kwh=salmon_dry_input_kg*FISH_DRY_HEAT_KWH_PER_KG_WET
    fans_kwh=fruit_wet_kg*FRUIT_FAN_KWH_PER_KG_WET+salmon_dry_input_kg*FISH_DRY_FAN_KWH_PER_KG_WET
    hp_kwh=(gh_heat_kwh+aqua_heat_kwh)*(1-DIRECT_LOW_TEMP_SHARE)/LOW_TEMP_COP+(fruit_heat_kwh+salmon_heat_kwh)/DRYING_COP
    anc_kwh=ELECTRICAL_OVERHEAD_ANCILLARY_FRACTION*(led_kwh+aqua_elec_kwh+fans_kwh+hp_kwh)
    electrical_kwh=led_kwh+aqua_elec_kwh+fans_kwh+hp_kwh+anc_kwh
    monthly=[]
    for i,m in enumerate(MONTHS):
        heat_available=HEAT_KWH*DAYS[i]/365
        demands={'greenhouse':gh_heat_kwh*HEAT_SHAPE[i],'aquaculture':aqua_heat_kwh*AQUA_SHAPE[i],
                 'fruit_drying':fruit_heat_kwh*FRUIT_SHAPE[i], 'salmon_drying':salmon_heat_kwh*SALMON_DRY_SHAPE[i]}
        # Priority allocation is only network aggregate, does not allow heat transfer between cities.
        alloc={}; remaining=heat_available
        for typ in ['aquaculture','greenhouse','fruit_drying','salmon_drying']:
            alloc[typ]=min(max(0,remaining),demands[typ]);remaining-=alloc[typ]
        unmet=sum(demands.values())-sum(alloc.values())
        monthly.append(dict(scenario=scenario,month=m,days=DAYS[i],recoverable_heat_potential_GWh=heat_available/1e6,
            greenhouse_demand_GWh=demands['greenhouse']/1e6,aquaculture_demand_GWh=demands['aquaculture']/1e6,
            fruit_dryer_demand_GWh=demands['fruit_drying']/1e6,salmon_dryer_demand_GWh=demands['salmon_drying']/1e6,
            served_heat_GWh=sum(alloc.values())/1e6,unserved_demand_GWh=unmet/1e6,
            unused_heat_potential_GWh=remaining/1e6,led_electricity_GWh=led_kwh*LED_SHAPE[i]/1e6,
            ras_electricity_GWh=aqua_elec_kwh*DAYS[i]/365/1e6))
    served=sum(x['served_heat_GWh'] for x in monthly)
    unmet=sum(x['unserved_demand_GWh'] for x in monthly)
    res=dict(scenario=scenario,greenhouse_hectares=p['greenhouse_ha'],seafood_liveweight_t=p['ras_tonnes'],
      greenhouse_vegetables_t=sqm*p['veg_yield_kg_m2']/1000,shellfish_nursery_modules=p['shellfish_nursery_modules'],
      fruit_marketed_2024_t=MARKETED_FRUIT_TONNES_2024,fruit_diversion_assumed_pct=100*p['fruit_diversion'],
      fruit_input_t=fruit_wet_kg/1000,dried_fruit_output_t=fruit_wet_kg*DRIED_FRUIT_MASS_FRACTION/1000,
      salmon_input_to_dryer_t=salmon_dry_input_kg/1000,dried_salmon_total_t=salmon_dry_input_kg*DRIED_FISH_MASS_FRACTION/1000,
      salmon_indian_candy_subtype_t=salmon_dry_input_kg*DRIED_FISH_MASS_FRACTION*INDIAN_CANDY_SHARE_OF_DRIED_FISH/1000,
      greenhouse_heat_demand_GWh=gh_heat_kwh/1e6,ras_heat_demand_GWh=aqua_heat_kwh/1e6,
      drying_heat_demand_GWh=(fruit_heat_kwh+salmon_heat_kwh)/1e6,
      total_heat_demand_GWh=(gh_heat_kwh+aqua_heat_kwh+fruit_heat_kwh+salmon_heat_kwh)/1e6,
      heat_served_GWh=served,heat_unserved_GWh=unmet,unused_heat_potential_GWh=HEAT_KWH/1e6-served,
      heat_potential_utilized_pct=100*served/(HEAT_KWH/1e6),
      led_electricity_GWh=led_kwh/1e6,ras_electricity_GWh=aqua_elec_kwh/1e6,
      dryer_fans_electricity_GWh=fans_kwh/1e6,heat_pump_electricity_GWh=hp_kwh/1e6,
      ancillary_electricity_GWh=anc_kwh/1e6,total_extra_electricity_GWh=electrical_kwh/1e6,
      extra_mean_MW=electrical_kwh/8760/1000,
      extra_electricity_pct_of_base_facility=100*electrical_kwh/(IT_MW*IT_UTIL*PUE*8760*1000),
      winter_heat_shortfall_GWh=sum(x['unserved_demand_GWh'] for x in monthly if x['month'] in [11,12,1,2,3]),
      greenhouse_jobs_illustrative_low=int(p['greenhouse_ha']*4),greenhouse_jobs_illustrative_high=int(p['greenhouse_ha']*12),
      ras_jobs_illustrative_low=int(p['ras_tonnes']/300),ras_jobs_illustrative_high=int(p['ras_tonnes']/100))
    return res,monthly

def sensitivity():
    rows=[]
    for h in (350,450,600):
      for led in (40,160,450):
       for aqua in (30000,120000,250000):
        global HEAT_KWH_PER_M2
        HEAT_KWH_PER_M2=h
        p=dict(SCENARIOS['Expansion']);p.update(led_kwh_m2=led,ras_tonnes=aqua)
        r,months=compute('Expansion',p)
        rows.append(dict(heat_kwh_m2=h,led_kwh_m2=led,ras_tonnes=aqua,
           heat_served_GWh=r['heat_served_GWh'],winter_heat_shortfall_GWh=r['winter_heat_shortfall_GWh'],
           electricity_extra_GWh=r['total_extra_electricity_GWh']))
    HEAT_KWH_PER_M2=450
    return rows

def main():
    a=[];b=[]
    for n in SCENARIOS:
      r,mo=compute(n);a.append(r);b.extend(mo)
    write_csv(OUT/'seasonal_food_scenario_summary.csv',a)
    write_csv(OUT/'seasonal_food_monthly_heat.csv',b)
    write_csv(OUT/'food_heat_sensitivity.csv',sensitivity())
    write_csv(OUT/'seafood_species_assumptions.csv',[dict(species=k,**v) for k,v in SPECIES.items()])
    with open(OUT/'seasonal_model_assumptions.json','w') as f:
      json.dump(dict(heat_potential_twh=HEAT_KWH/1e9,bc_marketed_fruit_t=MARKETED_FRUIT_TONNES_2024,
       base_gh_heat_kwh_m2_year=HEAT_KWH_PER_M2, led_kwh_m2_by_scenario={k:v['led_kwh_m2'] for k,v in SCENARIOS.items()},
       low_temp_cop=LOW_TEMP_COP,drying_cop=DRYING_COP,direct_heat_fraction=DIRECT_LOW_TEMP_SHARE,
       assumptions=SCENARIOS,species=SPECIES,annual_heat_allocation='site co-location required; no cross-city heat network',
       source_caveats=['2024 marketed fruit is NOT wasted fruit','seafood volumes require feed/water/oxygen/permits/market','thermal potential NOT observed delivered heat','mercury-free cannot be claimed']
       ),f,indent=2)
    for r in a:
      print(r['scenario'], 'heat served',round(r['heat_served_GWh']), 'unused',round(r['unused_heat_potential_GWh']), 'peak winter deficit',round(r['winter_heat_shortfall_GWh']), 'extra elec', round(r['total_extra_electricity_GWh']), 'vegetables',round(r['greenhouse_vegetables_t']))

def site_feasibility_proxy(scenario):
    """Do not move heat between sites. Assign plant sizes proportional to IT ratings;
    allocate fruit drying only to Okanagan nodes for a spatial sensitivity.
    These allocations are screening proxies, not approved physical projects.
    """
    inputs=BASE/'inputs'/'site_it_capacity_assumptions.csv'
    with open(inputs) as f:nodes=list(csv.DictReader(f))
    total=sum(float(n['it_mw']) for n in nodes)
    oak={'Salmon Arm','Vernon','Kelowna','West Kelowna','Penticton','Oliver','Osoyoos'}
    oak_tot=sum(float(n['it_mw']) for n in nodes if n['node'] in oak)
    nrows=[];monthly=[]
    for n in nodes:
        site=n['node']; share=float(n['it_mw'])/total
        fruit_weight=float(n['it_mw'])/oak_tot if site in oak else 0
        p=dict(SCENARIOS[scenario]); area=p['greenhouse_ha']*10000*share
        farm_kg=p['ras_tonnes']*1000*share
        fruit_kg=MARKETED_FRUIT_TONNES_2024*p['fruit_diversion']*1000*fruit_weight
        salmon_kg=farm_kg*SPECIES['salmon']['share']*p['salmon_dry_fraction']
        gh_heat=area*HEAT_KWH_PER_M2
        ras_heat=farm_kg*sum(v['share']*v['heat_kwh_kg'] for v in SPECIES.values())+p['shellfish_nursery_modules']*250000*share
        fd_heat=fruit_kg*FRUIT_HEAT_KWH_PER_KG_WET
        sd_heat=salmon_kg*FISH_DRY_HEAT_KWH_PER_KG_WET
        available=HEAT_KWH*share
        served=0;deficit=0
        for i,m in enumerate(MONTHS):
            cap=available*DAYS[i]/365
            req={'aquaculture':ras_heat*AQUA_SHAPE[i],'greenhouse':gh_heat*HEAT_SHAPE[i],
                 'fruit_dryer':fd_heat*FRUIT_SHAPE[i],'salmon_dryer':sd_heat*SALMON_DRY_SHAPE[i]}
            remain=cap
            for name in ['aquaculture','greenhouse','fruit_dryer','salmon_dryer']:
                take=min(req[name],max(remain,0)); remain-=take
                monthly.append(dict(scenario=scenario,node=site,month=m,use=name,heat_demand_GWh=req[name]/1e6,served_heat_GWh=take/1e6,unserved_heat_GWh=(req[name]-take)/1e6))
                served+=take;deficit+=req[name]-take
        nrows.append(dict(scenario=scenario,node=site,it_mw=n['it_mw'],recoverable_heat_potential_GWh=available/1e6,
            indicative_greenhouse_ha=p['greenhouse_ha']*share,indicative_ras_liveweight_t=p['ras_tonnes']*share,
            indicative_fruit_to_dry_t=fruit_kg/1000,heat_served_GWh=served/1e6,heat_unserved_GWh=deficit/1e6,
            heat_unused_GWh=(available-served)/1e6,saline_species_site_approved='not established'))
    return nrows,monthly

if __name__=='__main__':
    main()
    site=[];monthly=[]
    for n in SCENARIOS:
        a,b=site_feasibility_proxy(n);site.extend(a);monthly.extend(b)
    write_csv(OUT/'seasonal_food_site_proxy.csv',site)
    write_csv(OUT/'seasonal_food_site_monthly_allocation.csv',monthly)
    print('site-monthly proxy rows:',len(monthly))
