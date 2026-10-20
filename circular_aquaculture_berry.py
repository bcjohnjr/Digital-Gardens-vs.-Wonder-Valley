"""Digital Gardens circular-food alternative to seasonal baseline; deterministic scenario screen.
No production site, permitted water reuse, nutritional trial, seafood contaminant guarantee,
contracted jobs, heat offtake, or validated factory-scale algae productivity is claimed.
Depends only on Python standard library and on adjacent seasonal_food_heat.py.
"""
from __future__ import annotations
import csv, json, importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'results';OUT.mkdir(exist_ok=True)
SCRIPT=HERE/'software'/'seasonal_food_heat.py'
spec=importlib.util.spec_from_file_location('seasonal', SCRIPT)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

SHARES={'tilapia':0.40,'prawns':0.30,'salmon':0.20,'trout':0.10}
FCR={'tilapia':1.50,'prawns':1.70,'salmon':1.20,'trout':1.30} # kg dry complete feed/kg live-weight fish, unvalidated inputs
RAS_JOB_PER_KT={'tilapia':(12,24),'prawns':(16,35),'salmon':(26,30),'trout':(18,28)} # salmon anchored to DFO benchmark; other species hypothetical
GREENHOUSE_FTE_HA=(4,9) # 2023 national greenhouse vegetable 15,932 employees / 2,236.48 ha ≈7.12 headcount/ha, not FTE
BLUEBERRY_BC_2024=0.94*71497 # AAFC highbush national crop and BC share, approx t
CRANBERRY_BC_2024=45988
RAS_FEED_PROTEIN={'tilapia':0.32,'prawns':0.35,'salmon':0.42,'trout':0.42}
FEED_PHOSPHORUS_FRAC=0.01

def annual(scenario='Expansion', shares=None, residue_capture=0.65, residue_safe=0.40,
           greenhouse_fte_per_ha=GREENHOUSE_FTE_HA, berry_share=0.50,
           nitrogen_capture=0.35, algae_capture=0.40, algae_lipid=0.25,
           algae_oil_recovery=0.70, algal_oil_inclusion=0.01):
    shares=dict(SHARES if shares is None else shares)
    assert abs(sum(shares.values())-1)<1e-9
    saved={sp:old.SPECIES[sp]['share'] for sp in shares}
    try:
        for sp,sh in shares.items():old.SPECIES[sp]['share']=sh
        primary,months=old.compute(scenario)
    finally:
        for sp,sh in saved.items():old.SPECIES[sp]['share']=sh
    tonnes=primary['seafood_liveweight_t']
    species_rows=[]; feed_total=0;fw_feed=0;salmon_feed=0
    aqua_low=0;aqua_high=0;water_heat=0;water_electric=0
    for sp,portion in shares.items():
        output=tonnes*portion;feed=output*FCR[sp]
        feed_total+=feed
        if sp=='salmon':salmon_feed=feed
        else:fw_feed+=feed
        l,h=RAS_JOB_PER_KT[sp]
        aqua_low+=output/1000*l;aqua_high+=output/1000*h
        water_heat+=output*1000*old.SPECIES[sp]['heat_kwh_kg']/1e6
        water_electric+=output*1000*old.SPECIES[sp]['electric_kwh_kg']/1e6
        species_rows.append(dict(species=sp,share_pct=portion*100,annual_liveweight_t=output,
                                 FCR_assumed=FCR[sp],dry_complete_feed_t=feed,
                                 process_heat_GWh=output*1000*old.SPECIES[sp]['heat_kwh_kg']/1e6,
                                 electricity_GWh=output*1000*old.SPECIES[sp]['electric_kwh_kg']/1e6,
                                 FTE_low=output/1000*l,FTE_high=output/1000*h,
                                 water_loop=('saline marine PBR, no direct greenhouse reuse' if sp=='salmon' else 'freshwater, separated recovery treatment')))
    green_veg=primary['greenhouse_vegetables_t']
    wet_residue=green_veg*0.35
    dry_residue=wet_residue*0.12
    suitable=dry_residue*residue_capture*residue_safe
    usable=min(suitable,feed_total*0.10)
    feed_pct=100*usable/feed_total
    N_fw_feed=sum(x['dry_complete_feed_t']*RAS_FEED_PROTEIN[x['species']]*0.16 for x in species_rows if x['species']!='salmon')
    N_sal_feed=salmon_feed*RAS_FEED_PROTEIN['salmon']*0.16
    dissolved_N_fw=N_fw_feed*0.30
    potential_N_hydro=dissolved_N_fw*nitrogen_capture
    greenhouse_N_demand=green_veg*0.003
    dissolved_N_sal=N_sal_feed*0.30
    available_algae_N=dissolved_N_sal*algae_capture
    dissolved_P_sal=salmon_feed*FEED_PHOSPHORUS_FRAC*0.40
    available_algae_P=dissolved_P_sal*algae_capture
    max_algae_biomass=min(available_algae_N/0.08,available_algae_P/0.01)
    possible_lipid_oil=max_algae_biomass*algae_lipid*algae_oil_recovery
    target_algae_oil=salmon_feed*algal_oil_inclusion
    purchased_oil=max(0,target_algae_oil-possible_lipid_oil)
    PBR_area_ha=max_algae_biomass*1000/(20/1000*300)/10000  # 20 g/m2/day x 300 d
    algae_electricity_GWh=max_algae_biomass*1000*3/1e6 # 3 kWh/kg dry biomass mixing/dewatering assumed
    berry_pool=BLUEBERRY_BC_2024+CRANBERRY_BC_2024
    berry_wet=primary['fruit_input_t']*berry_share
    berry_pct=100*berry_wet/berry_pool
    berry_dry=berry_wet*old.DRIED_FRUIT_MASS_FRACTION
    berry_thermal_GWh=berry_wet*1000*old.FRUIT_HEAT_KWH_PER_KG_WET/1e6
    salmon_input=primary['salmon_input_to_dryer_t']
    dried_salmon=primary['dried_salmon_total_t']
    dried_candied=primary['salmon_indian_candy_subtype_t']
    fte_gh=(primary['greenhouse_hectares']*greenhouse_fte_per_ha[0],primary['greenhouse_hectares']*greenhouse_fte_per_ha[1])
    processor_input=primary['fruit_input_t']+salmon_input
    processing_jobs=(processor_input/1000*10,processor_input/1000*30)
    algae_jobs=(20,80) if tonnes>=30000 else (5,20)
    feed_mill_jobs=(15,60) if tonnes>=30000 else (3,15)
    job_low=fte_gh[0]+aqua_low+processing_jobs[0]+algae_jobs[0]+feed_mill_jobs[0]
    job_high=fte_gh[1]+aqua_high+processing_jobs[1]+algae_jobs[1]+feed_mill_jobs[1]
    # PBR additional electricity on top of original heat/electric balance. Separate brewery/feed energy is not included.
    extra_power=primary['total_extra_electricity_GWh']+algae_electricity_GWh
    summary=dict(scenario=scenario,greenhouse_ha=primary['greenhouse_hectares'],greenhouse_produce_t=green_veg,
       seafood_liveweight_t=tonnes,warmwater_share_pct=100*(shares['tilapia']+shares['prawns']),
       annual_heat_demand_GWh=primary['total_heat_demand_GWh'],heat_served_GWh=primary['heat_served_GWh'],
       winter_heat_shortfall_GWh=primary['winter_heat_shortfall_GWh'],
       original_model_extra_electricity_GWh=primary['total_extra_electricity_GWh'],
       marine_PBR_extra_electricity_GWh=algae_electricity_GWh,minimum_total_extra_electricity_GWh=extra_power,
       dry_feed_t=feed_total,greenhouse_residue_wet_t=wet_residue,greenhouse_residue_dry_t=dry_residue,
       feed_grade_plant_ingredient_t=usable,plant_ingredient_share_of_feed_pct=feed_pct,
       freshwater_N_available_t=potential_N_hydro,greenhouse_N_demand_t=greenhouse_N_demand,
       saline_N_available_for_algae_t=available_algae_N,saline_P_available_for_algae_t=available_algae_P,
       theoretical_dry_algae_max_t=max_algae_biomass,algal_oil_possible_max_t=possible_lipid_oil,
       algal_oil_target_t=target_algae_oil,algal_oil_external_gap_t=purchased_oil,
       algae_sunlit_PBR_area_ha=PBR_area_ha,
       berries_2024_benchmark_t=berry_pool,berry_to_dryer_t=berry_wet,berry_fraction_of_2024_berry_harvest_pct=berry_pct,
       dry_berry_output_t=berry_dry,berry_heat_GWh=berry_thermal_GWh,
       salmon_to_dryer_t=salmon_input,dried_salmon_t=dried_salmon,dried_candied_subset_t=dried_candied,
       greenhouse_FTE_low=fte_gh[0],greenhouse_FTE_high=fte_gh[1],
       ras_FTE_low=aqua_low,ras_FTE_high=aqua_high,
       processing_FTE_low=processing_jobs[0],processing_FTE_high=processing_jobs[1],
       algae_FTE_low=algae_jobs[0],algae_FTE_high=algae_jobs[1],
       feed_mill_FTE_low=feed_mill_jobs[0],feed_mill_FTE_high=feed_mill_jobs[1],
       annual_direct_FTE_low=job_low,annual_direct_FTE_high=job_high,
       scope='Conditional design alternatives; no feed safety, bioassay, market, job or energy interconnection validation')
    return summary,species_rows,months

def csvwrite(name,rows):
    if not rows:return
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
    summaries=[];species=[];months=[]
    for scenario in ['Demonstration','Regional','Expansion','Heat-intensive']:
        s,p,m=annual(scenario)
        summaries.append(s)
        species.extend(dict(scenario=scenario,**p2) for p2 in p)
        months.extend(m)
    csvwrite('circular_food_scenarios.csv',summaries)
    csvwrite('circular_aquaculture_species.csv',species)
    csvwrite('circular_monthly_heat.csv',months)
    variants=[]
    for shares_name,sh in [('Original cold-leaning',{'salmon':.44,'trout':.25,'prawns':.10,'tilapia':.21}),('Warmwater-led 70%',SHARES),('Warmwater-led 85%',{'tilapia':.5,'prawns':.35,'salmon':.1,'trout':.05})]:
      for safe in (0.20,0.40,0.65):
       for capture in (0.2,0.35,0.5):
        x,_,_=annual('Expansion',shares=sh,residue_safe=safe,nitrogen_capture=capture)
        variants.append(dict(case=shares_name,suitable_residue_share=safe,freshwater_n_capture=capture,
                             heat_GWh=x['annual_heat_demand_GWh'],electricity_GWh=x['minimum_total_extra_electricity_GWh'],
                             feed_substitution_pct=x['plant_ingredient_share_of_feed_pct'],
                             greenhouse_nutrient_N_t=x['freshwater_N_available_t'],
                             jobs_FTE_min=x['annual_direct_FTE_low'],jobs_FTE_max=x['annual_direct_FTE_high']))
    csvwrite('circular_food_sensitivity.csv',variants)
    with (OUT/'circular_assumptions.json').open('w') as f:
        json.dump({'species_shares':SHARES,'FCR':FCR,'RAS_jobs_per_1000_t':RAS_JOB_PER_KT,
          'greenhouse_fte_per_hectare_assumed':GREENHOUSE_FTE_HA,'2024_berry_benchmark_t':BLUEBERRY_BC_2024+CRANBERRY_BC_2024,
          'waste_plant_ratio_wet_vegetables':.35,'residue_dry_fraction':.12,'recovered_fraction':.65,'feed_grade_fraction':.4,
          'protein_to_N':.16,'freshwater_RAS_dissolved_N_fraction':.30,'freshwater_N_capture':.35,
          'salmon_RAS_dissolved_N_fraction':.30,'marine_N_and_P_capture':.40,'algae_dry_N_fraction':.08,'algae_dry_P_fraction':.01,
          'algae_lipid_fraction':.25,'oil_recovery':.70,'oil_feed_inclusion':.01,'PBR_productivity_g_m2_day':20,'PBR_productive_days':300,
          'PBR_ancillary_kWh_kg_dry_algae':3,
          'limitations':['No salinity mixing between freshwater aquaponics and salmon PBR systems',
          'High predicted nutrient recovery does not establish actual fertilizer displacement',
          'Marine PBR maximum biomass is an N/P stoichiometric ceiling, not an empirical yield',
          'Greenhouse plant residues are not complete feed; feed-grade suitability and formulation unverified',
          'FTE estimates based on scenario staffing ranges and national headcount/ha proxy; not projected vacancies',
          'No guarantee of mercury below detection or downstream wild-salmon recovery',
          'B.C. berry harvest is not measured unsold fruit and is not additionally counted in prior total fruit drying']},f,indent=2)
    for x in summaries:
     print(f"{x['scenario']:15} thermal {x['annual_heat_demand_GWh']/1000:.3f} TWh, electrical {x['minimum_total_extra_electricity_GWh']/1000:.3f} TWh, jobs {x['annual_direct_FTE_low']:.0f}-{x['annual_direct_FTE_high']:.0f}")
    print('EXPANSION:',json.dumps(summaries[2],indent=2))

if __name__=='__main__':main()
