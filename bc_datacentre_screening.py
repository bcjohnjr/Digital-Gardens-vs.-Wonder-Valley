"""Transparent algebraic SCREENING model, not engineering validation.

Reconstructs reported Digital Gardens capacity and scenarios using only stdlib.
Does not validate workload demand, grid interconnection, unit commitments,
heat offtake, carbon additionality, training speed, economics, or permissions.
Usage: python bc_datacentre_screening.py
"""
from __future__ import annotations
import csv
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'results'
OUT.mkdir(parents=True,exist_ok=True)
NODES=[
 ('Lillooet',10.59),('Cache Creek',4.46),('Kamloops',450.35),('Chase',11.04),
 ('Salmon Arm',89.39),('Vernon',204.79),('Kelowna',665.05),('West Kelowna',165.96),
 ('Penticton',169.67),('Oliver',23.43),('Osoyoos',25.56),('Hope',30.76),
 ('Agassiz / Kent',28.98),('Chilliwack',428.73),('Abbotsford',706.21),
 ('Mission',190.99),('Maple Ridge',418.55)]
PARAMS=dict(load_factor=0.90,pue=1.15,heat_capture=0.85,heat_use=0.60,
            annual_hours=8760,community_budget_cad_per_mw_y=1_200_000)

def calculate(**overrides):
    p={**PARAMS,**overrides}; mw=sum(m for _,m in NODES)
    it_gwh=mw*p['load_factor']*p['annual_hours']/1000
    facility_gwh=it_gwh*p['pue']
    recovered_potential_gwh=it_gwh*p['heat_capture']
    useful_heat_gwh=recovered_potential_gwh*p['heat_use']
    return dict(nodes=len(NODES),it_capacity_mw=mw,facility_peak_mw=mw*p['pue'],
                it_gwh_y=it_gwh,facility_gwh_y=facility_gwh,
                recovered_potential_gwh_y=recovered_potential_gwh,
                useful_heat_gwh_y=useful_heat_gwh,
                proposed_budget_cad_y=mw*p['community_budget_cad_per_mw_y'])

def write(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

if __name__=='__main__':
    m=calculate()
    node_rows=[]
    for name,mw in NODES:
        node_rows.append(dict(node=name,it_mw=mw,load_mw=mw*PARAMS['load_factor'],
                              facility_peak_mw=mw*PARAMS['pue'],
                              facility_gwh_y=mw*PARAMS['load_factor']*PARAMS['pue']*8760/1000))
    write(OUT/'node_capacity.csv',node_rows)
    carbon_rows=[]
    for carbon_intensity_kg_mwh in [10,25,50,100,150,250]:
      for usable_share in [0,0.25,0.5,1.0]:
        carbon_mt=m['facility_gwh_y']*carbon_intensity_kg_mwh/1e6
        heat_avoided_mt=m['useful_heat_gwh_y']*usable_share*0.2/1000
        carbon_rows.append(dict(grid_kg_co2e_per_mwh=carbon_intensity_kg_mwh,
          fraction_of_useful_heat_displacing_gas=usable_share,
          electricity_co2e_mt_y=round(carbon_mt,4),
          gross_gas_heat_avoidance_mt_y=round(heat_avoided_mt,4),
          net_scope2_less_gas_displacement_mt_y=round(carbon_mt-heat_avoided_mt,4)))
    write(OUT/'carbon_heat_sensitivity.csv',carbon_rows)
    thermal_rows=[]
    for c in [0.50,0.70,0.85,0.95]:
        for u in [0.20,0.4,0.6,0.8]:
            d=calculate(heat_capture=c,heat_use=u)
            thermal_rows.append(dict(capture_fraction=c,use_fraction_of_captured=u,usable_heat_gwh_y=round(d['useful_heat_gwh_y'],2)))
    write(OUT/'heat_sensitivity.csv',thermal_rows)
    # Communication-bandwidth *conditional* serialisation check for source model.
    n_params=1e12; dp_size=132
    bytes_exchange=2*(dp_size-1)/dp_size*n_params
    comm_rows=[]
    for link_gbps in [100,400,800,1600]:
      for efficiency in [0.25,0.5,1.0]:
        seconds=bytes_exchange/(link_gbps*1e9/8*efficiency)
        comm_rows.append(dict(link_gbps=link_gbps,usable_fraction=efficiency,
                              assumed_bytes_crossing_link=int(bytes_exchange),
                              serialisation_time_seconds=round(seconds,3)))
    write(OUT/'conditional_network_serialisation.csv',comm_rows)
    assert abs(m['it_capacity_mw']-3624.51)<.001
    assert 32000<m['facility_gwh_y']<34000
    assert m['useful_heat_gwh_y']<m['it_gwh_y']
    assert m['facility_peak_mw']>4000
    print('Validation: screening algebra tests passed')
    for k,v in m.items():print(f'{k}: {v:,.4f}' if isinstance(v,float) else f'{k}: {v}')
    print('Critical caveat: no site approvals, network throughput or financial revenues proven')
