"""Two-phase Digital Gardens community-programme and electrical sensitivity.
Standard-library, pure scenario arithmetic. All financial rates are illustrative
unless cited and are NOT audited revenues or actual contractual commitments.
NO household electricity giveaway is included.
"""
import csv, json, math
from agriculture_diesel import calculate as ag_diesel_calculate
from pathlib import Path
OUT=Path(__file__).resolve().parent.parent/'results';OUT.mkdir(exist_ok=True)
POP=787_934; IT=3_624.51; HOURS=8760
CONFIG={
'population_both_phases':POP, 'phase_1_population_share':.50, 'average_residents_per_household':2.4,
'household_eligible_ev_share':.90, 'replacement_cycle_years':12,
'ev_asset_value_cad':38_000, 'ev_financing_rate':.05,
'free_charging_participation':.85, 'distance_km_per_ev_year':12_000,
'ev_energy_at_battery_kwh_per_km':.19, 'charging_losses_fraction':.10,
'blended_charging_market_value_cad_per_kwh':.35,
'charging_delivered_energy_supply_cost_cad_per_kwh':.14,
'charging_operations_cad_per_kwh':.05,
'public_ac_charger_kw':7.2,'peak_charging_simultaneity':.06,
'greenhouse_production_tonnes':250_000, 'fresh_produce_entitlement_kg_per_resident':146, 'fresh_produce_packout_fraction':0.90,
'greenhouse_assumed_market_value_cad_per_kg':3.5,
'aquaculture_production_tonnes':120_000,'seafood_entitlement_kg_per_resident':46, 'seafood_saleable_yield_fraction':0.65,
'aquaculture_assumed_market_value_cad_per_kg':7.0,'food_funding_cost_fraction_of_market_value':.65,
'agriculture_fuel_eligible_litres':ag_diesel_calculate()[2]['diesel_l'],'ag_fossil_parity_gap_cad_per_litre':.25,
'other_commercial_fuel_eligible_litres':180_000_000,'other_fossil_parity_gap_cad_per_litre':.18,
'dryer_eligible_fruit_tonnes':5000, 'producer_dryer_discount_cad_per_tonne':25,
'programme_aspiration_cad_year':4_600_000_000,
'it_utilization':.90,'pue':1.15,'heat_capture_fraction':.85,'heat_end_use_fraction_of_captured':.60,
'scope2_kg_per_mwh':50,
}
def annuity_factor(r,n): return (r*(1+r)**n)/((1+r)**n-1) if r else 1/n

def estimate(c,phase=1):
 a=phase
 pop=c['population_both_phases']*(c['phase_1_population_share'] if phase==1 else 1)
 phase_fraction=pop/c['population_both_phases'];hh=pop/c['average_residents_per_household']
 evs=hh*c['household_eligible_ev_share']
 charging_evs=hh*c['free_charging_participation']
 kwh=charging_evs*c['distance_km_per_ev_year']*c['ev_energy_at_battery_kwh_per_km']/(1-c['charging_losses_fraction'])
 charging_market=kwh*c['blended_charging_market_value_cad_per_kwh']
 charging_cost=kwh*(c['charging_delivered_energy_supply_cost_cad_per_kwh']+c['charging_operations_cad_per_kwh'])
 ev_annual_equivalent=evs*c['ev_asset_value_cad']/c['replacement_cycle_years']
 ev_financed_cost=evs*c['ev_asset_value_cad']*annuity_factor(c['ev_financing_rate'],c['replacement_cycle_years'])
 produce_kg=pop*c['fresh_produce_entitlement_kg_per_resident']
 seafood_kg=pop*c['seafood_entitlement_kg_per_resident']
 produce_market=produce_kg*c['greenhouse_assumed_market_value_cad_per_kg']
 seafood_market=seafood_kg*c['aquaculture_assumed_market_value_cad_per_kg']
 food_market=produce_market+seafood_market
 ag_fuel=c['agriculture_fuel_eligible_litres']*max(0,c['ag_fossil_parity_gap_cad_per_litre'])*phase_fraction
 other_fuel=c['other_commercial_fuel_eligible_litres']*max(0,c['other_fossil_parity_gap_cad_per_litre'])*phase_fraction
 dryer=c['dryer_eligible_fruit_tonnes']*c['producer_dryer_discount_cad_per_tonne']*phase_fraction
 market=ev_annual_equivalent+charging_market+food_market+ag_fuel+other_fuel+dryer
 funding=ev_financed_cost+charging_cost+c['food_funding_cost_fraction_of_market_value']*food_market+ag_fuel+other_fuel+dryer
 return dict(phase=phase,population=round(pop),households=round(hh),vehicle_eligible=round(evs),charging_evs=round(charging_evs),charging_gwh=kwh/1e6,charging_average_mw=kwh/8760/1000,illustrative_charger_peak_mw=charging_evs*c['peak_charging_simultaneity']*c['public_ac_charger_kw']/1000,
 vehicle_annualized_value_mcad=ev_annual_equivalent/1e6,vehicle_financed_cost_mcad=ev_financed_cost/1e6,
 free_charging_market_value_mcad=charging_market/1e6,charging_annual_funding_mcad=charging_cost/1e6,
 fresh_produce_entitlement_kg_per_resident=c['fresh_produce_entitlement_kg_per_resident'], seafood_entitlement_kg_per_resident=c['seafood_entitlement_kg_per_resident'],
 produce_allocated_tonnes=produce_kg/1000, seafood_allocated_tonnes=seafood_kg/1000, combined_food_allocated_tonnes=(produce_kg+seafood_kg)/1000,
 produce_share_of_projected_harvest_pct=100*produce_kg/(1000*c['greenhouse_production_tonnes']), seafood_share_of_projected_harvest_pct=100*seafood_kg/(1000*c['aquaculture_production_tonnes']),
 remaining_produce_tonnes=c['greenhouse_production_tonnes']*c['fresh_produce_packout_fraction']-produce_kg/1000, remaining_seafood_tonnes=c['aquaculture_production_tonnes']*c['seafood_saleable_yield_fraction']-seafood_kg/1000,
 produce_share_of_saleable_supply_pct=100*produce_kg/(1000*c['greenhouse_production_tonnes']*c['fresh_produce_packout_fraction']), seafood_share_of_saleable_supply_pct=100*seafood_kg/(1000*c['aquaculture_production_tonnes']*c['seafood_saleable_yield_fraction']),
 greenhouse_food_market_value_mcad=produce_market/1e6,seafood_market_value_mcad=seafood_market/1e6,
 agricultural_fuel_price_parity_subsidy_mcad=ag_fuel/1e6,other_renewable_fuel_parity_subsidy_mcad=other_fuel/1e6,fruit_drying_discount_mcad=dryer/1e6,
 annual_household_electricity_subsidy_mcad=0,
 total_annual_community_value_mcad=market/1e6,annual_programme_funding_mcad=funding/1e6,
 remaining_4600m_value_mcad=max(0,c['programme_aspiration_cad_year']-market)/1e6,
 remaining_4600m_funding_mcad=max(0,c['programme_aspiration_cad_year']-funding)/1e6)

def puematrix():
 rows=[]
 for u in (.65,.75,.90):
  for p in (1.10,1.15,1.30):
   it_kwh=IT*1000*u*HOURS
   facility_twh=it_kwh*p/1e9
   cap_twh=it_kwh*.85/1e9
   rows.append(dict(it_utilization=u,pue=p,facility_twh=facility_twh,heat_capture_twh=cap_twh,heat_potential_enduse_twh=cap_twh*.60,scope2_million_tco2e_at_50kg_mwh=facility_twh*.05))
 return rows

def writecsv(name,rows):
 with (OUT/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
if __name__=='__main__':
 baseline=[estimate(CONFIG,1),estimate(CONFIG,2)]
 writecsv('community_two_phase_baseline.csv',baseline)
 writecsv('electricity_heat_pue_utilization.csv',puematrix())
 scenarios=[]
 for scen,evup,participation,gapag,gapother,produceprice,seafoodprice,foodcost in [
  ('low',.65,.55,.10,.10,2.50,5.00,.50),('central',.90,.85,.25,.18,3.50,7.00,.65),('high',1,1,.45,.35,4.50,9.00,.85)]:
  c=dict(CONFIG,household_eligible_ev_share=evup,free_charging_participation=participation,ag_fossil_parity_gap_cad_per_litre=gapag,other_fossil_parity_gap_cad_per_litre=gapother,greenhouse_assumed_market_value_cad_per_kg=produceprice,aquaculture_assumed_market_value_cad_per_kg=seafoodprice,food_funding_cost_fraction_of_market_value=foodcost)
  for phase in (1,2):
   scenarios.append(dict(scenario=scen,**estimate(c,phase)))
 writecsv('community_two_phase_sensitivity.csv',scenarios)
 with (OUT/'community_assumptions.json').open('w',encoding='utf-8') as f:json.dump(CONFIG,f,indent=2)
 print(json.dumps(baseline,indent=2))
 print('PUE',puematrix())
