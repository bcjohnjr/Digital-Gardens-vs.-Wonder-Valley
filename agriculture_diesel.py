"""2021 census-anchored regional agricultural machinery diesel SCREEN only.
Eight entire regional districts form an UPPER-CATCHMENT, NOT a municipality-level farm census.
Census counts/areas are official B.C. 2021 Agriculture in Brief. Fuel intensities are
scenario coefficients; no measured regional diesel volumes or vendor prices are asserted.
Agriculture excludes forestry, fisheries, marine vessels and off-farm trucking.
"""
import csv,json
from pathlib import Path
DIR=Path(__file__).resolve().parent.parent
OUT=DIR/'results';OUT.mkdir(exist_ok=True)
# name, code, 2021 farms, total farmland ha, crops ha, seeded pasture, natural pasture,
# other land, hay ha, fruit ha, vegetables ha, nursery ha, sod ha, source URL
URL='https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/agriculture-and-seafood/statistics/census/ag-in-brief/'
RDS=[
 ('Squamish-Lillooet','SL',117,7526,2120,498,3136,578,912,30,40,19,0,URL+'dec2024/cd/ag_in_brief_2021_-_cd_squamish-lillooet_-_december_2024_correction.pdf'),
 ('Thompson-Nicola','TN',895,516079,28365,10427,419904,6103,7541,51,246,5,0,URL+'dec2024/cd/ag_in_brief_2021_-_cd_thompson-nicola_-_december_2024_correction.pdf'),
 ('Columbia-Shuswap','CS',510,27052,10170,1663,8253,1616,3265,122,57,27,8,URL+'dec2024/cd/ag_in_brief_2021_-_cd_columbia-shuswap_-_december_2024_correction.pdf'),
 ('North Okanagan','NO',972,62415,19666,2180,32397,2586,5411,470,133,110,33,URL+'dec2024/cd/ag_in_brief_2021_-_cd_north_okanagan_-_december_2024_correction.pdf'),
 ('Central Okanagan','CO',807,20888,6608,606,11193,1474,705,3879,98,358,19,URL+'dec2024/cd/ag_in_brief_2021_-_cd_central_okanagan_-_december_2024_correction.pdf'),
 ('Okanagan-Similkameen','OS',1231,65516,10558,1252,48822,2370,633,7166,282,10,0,URL+'dec2024/cd/ag_in_brief_2021_-_cd_okanagan-similkameen_-_december_2024_correction.pdf'),
 ('Fraser Valley','FV',2358,60350,36962,2619,14027,4748,10784,6473,1843,868,410,URL+'dec2024/cd/ag_in_brief_2021_-_cd_fraser_valley_-_december_2024_correction.pdf'),
 ('Greater Vancouver','GV',2118,34360,24999,999,2627,4517,5535,8368,2401,580,97,URL+'ag_in_brief_2021_-_cd_greater_vancouver.pdf'),
]
COEFF={'hay_l_ha':30.,'residual_field_l_ha':65.,'fruit_berries_nuts_l_ha':130.,'vegetables_l_ha':150.,'nursery_sod_l_ha':100.,'seeded_pasture_l_ha':25.,'natural_pasture_l_ha':1.5,'other_farmland_l_ha':3.,'farm_service_l_farm':800.,'price_gap_cad_l':.25,'fuel_density_CO2_kg_l':2.681,'uptake_fraction':1.0,'phase1_fraction':.5,'existing_ag_fuel_cap_l':100_000_000}
# Heuristic shares determine assigned RESPONSIBILITY FOR FUEL-SUBSIDY ADMINISTRATION,
# not observed municipal farm volumes. All weights sum to 1 per RD.
NODES=[('Lillooet','SL',1),('Cache Creek','TN',.15),('Kamloops','TN',.55),('Chase','TN',.30),('Salmon Arm','CS',1),('Vernon','NO',1),('Kelowna','CO',.75),('West Kelowna','CO',.25),('Penticton','OS',.45),('Oliver','OS',.30),('Osoyoos','OS',.25),('Hope','FV',.10),('Agassiz / Kent','FV',.15),('Chilliwack','FV',.25),('Abbotsford','FV',.35),('Mission','FV',.15),('Maple Ridge','GV',1)]
def calculate(mult=1.0,price_gap=None,uptake=1):
 c=COEFF;gap=c['price_gap_cad_l'] if price_gap is None else price_gap
 districts=[]
 for name,code,farms,land,crops,seeded,natural,other,hay,fruit,veg,nursery,sod,url in RDS:
  residual=max(0,crops-hay-fruit-veg-nursery-sod)
  terms={'hay':hay*c['hay_l_ha'],'residual_field':residual*c['residual_field_l_ha'],'fruit_berries_nuts':fruit*c['fruit_berries_nuts_l_ha'],'vegetables':veg*c['vegetables_l_ha'],'nursery_sod':(nursery+sod)*c['nursery_sod_l_ha'],'seeded_pasture':seeded*c['seeded_pasture_l_ha'],'natural_pasture':natural*c['natural_pasture_l_ha'],'other_land':other*c['other_farmland_l_ha'],'farm_service':farms*c['farm_service_l_farm']}
  litres=sum(terms.values())*mult
  districts.append(dict(region=name,code=code,farms_2021=farms,total_farmland_ha_2021=land,crops_ha_2021=crops,hay_ha_2021=hay,field_residual_ha_2021=residual,fruit_berries_nuts_ha_2021=fruit,vegetables_ha_2021=veg,nursery_sod_ha_2021=nursery+sod,seeded_pasture_ha_2021=seeded,natural_pasture_ha_2021=natural,other_farmland_ha_2021=other,estimated_diesel_l=litres,annual_price_parity_cad=max(0,gap)*litres*uptake,conditional_petroleum_combustion_kg_co2=litres*c['fuel_density_CO2_kg_l']*uptake,classification='official 2021 area; assumed fuel intensities; catchment wider than municipality',source=url,**{('diesel_'+k+'_l'):v*mult for k,v in terms.items()}))
 codes={d['code']:d for d in districts}
 sites=[]
 for city,region,weight in NODES:
  d=codes[region]
  sites.append(dict(site=city,regional_district=d['region'],regional_code=region,allocation_weight=weight,attributed_farms=d['farms_2021']*weight,attributed_diesel_l=d['estimated_diesel_l']*weight,attributed_parity_cad=d['annual_price_parity_cad']*weight,classification='heuristic attribution, not measured city litres; entire regional catchment allocated to associated host nodes'))
 total=sum(d['estimated_diesel_l'] for d in districts)
 summary=dict(districts=len(districts),sites=len(sites),farms_in_full_districts=sum(d['farms_2021'] for d in districts),diesel_l=total,ag_parity_cad_year=max(0,gap)*total*uptake,phase1_cad_year=max(0,gap)*total*uptake*c['phase1_fraction'],phase2_cad_year=max(0,gap)*total*uptake,earlier_assumed_cap_l=c['existing_ag_fuel_cap_l'],difference_to_earlier_cap_l=c['existing_ag_fuel_cap_l']-total,petroleum_co2_combustion_t=total*c['fuel_density_CO2_kg_l']*uptake/1000,unit_status='screen only; combustion baseline not a lifecycle emission saving')
 return districts,sites,summary

def csvwrite(name,rows):
 with (OUT/name).open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
if __name__=='__main__':
 districts,sites,s=calculate();csvwrite('agriculture_2021_eight_regional_districts.csv',districts);csvwrite('agriculture_17_site_diesel_attribution.csv',sites)
 scenarios=[]
 for intensity in (.5,1,1.6):
  for gap in (.1,.25,.45):
   _,_,x=calculate(mult=intensity,price_gap=gap)
   scenarios.append({'fuel_intensity_factor':intensity,'renewable_minus_fossil_cad_l':gap,'estimated_litres_year':x['diesel_l'],'price_parity_cad_year':x['ag_parity_cad_year'],'phase1_cad_year':x['phase1_cad_year'],'unit':'full 8 regional district scenario'})
 csvwrite('agriculture_diesel_sensitivity.csv',scenarios)
 (OUT/'agriculture_fuel_assumptions.json').write_text(json.dumps({'model':COEFF,'sources':'Official 2021 BC Agriculture in Brief census division profiles. Farm fuel coefficients explicitly hypothetical.','area_is_region_not_municipality':True,'sites':NODES},indent=2))
 (OUT/'agriculture_summary.json').write_text(json.dumps(s,indent=2))
 print(json.dumps(s,indent=2))
