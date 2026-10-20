"""Reproducible lower-bound WAN communication screens for geographically distributed AI.

This is a deterministic engineering sensitivity study, not a measured training
benchmark or a forecast of hardware delivery, model quality, physical routes,
congestion, or achieved cost to train. NVIDIA NVLink specs refer to rack-scale
fabrics and cannot be assigned to province-wide fiber interconnections.
"""
from __future__ import annotations
import csv
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'results'; OUT.mkdir(parents=True,exist_ok=True)
# Future hardware/network configurations are *assumed* research scenarios.
HORIZONS=[
 ('2026 hardware reference',2026,20.0,400,1.0),
 ('2036 illustrative upgrade',2036,4.0,1600,5.0),
 ('2041 illustrative upgrade',2041,1.0,6400,20.0),
]
SITE_COUNT=17; C_FIBER_KM_S=200000.; FIBER_ROUTE_FACTOR=1.40
ROUTING_MS=.4; DELIVERED_FRACTION=.5

def rtt_ms(distance_km, route_factor=FIBER_ROUTE_FACTOR):
    """Speed-of-light RTT minimum in glass plus separately assumed device delay."""
    physical_min_ms=2*distance_km/C_FIBER_KM_S*1000
    engineered_ms=2*distance_km*route_factor/C_FIBER_KM_S*1000+ROUTING_MS
    return physical_min_ms,engineered_ms

def training_overhead(payload_gb,link_gbps,step_s,rtts=1,exposed=1.,distance_km=250):
    physics,actual=rtt_ms(distance_km)
    serialization=8*payload_gb/(link_gbps*DELIVERED_FRACTION)
    transit=rtts*actual/1000
    overhead=(serialization+transit)*exposed/step_s
    return dict(physical_rtt_floor_ms=physics,illustrative_rtt_ms=actual,
                serialization_s=serialization,latency_s=transit,exposed_fraction=exposed,
                network_overhead_pct=100*overhead,
                network_only_efficiency_pct=100/(1+overhead))

def ring_collective_gb(n_params_billion,byte_per_param=2,n=SITE_COUNT):
    return n_params_billion*byte_per_param*2*(n-1)/n

# Payloads are *testable illustrative critical-bottleneck traffic budgets*, not
# universal or predicted communication for any parallel method. rtts is the
# serial dependency depth, also scenario-dependent.
METHODS=[
 ('Data parallel (all-reduce)', 'global each step',ring_collective_gb(70),2,1.0,1),
 ('Tensor parallel (WAN-sharded)', 'each transformer layer',50,96,1.0,1),
 ('Pipeline parallel (WAN stage)', 'microbatch boundaries',10,32,1.0,1),
 ('Context parallel (WAN)', 'attention exchanges',50,32,1.0,1),
 ('Expert parallel (WAN all-to-all)', 'MoE dispatch and return',100,64,1.0,1),
 ('FSDP/ZeRO-3 over WAN', 'parameter gather and reduce',500,80,1.0,1),
 ('Sequence parallel (WAN)', 'activation shards',20,80,1.0,1),
 ('Local DP+TP+PP+CP+EP (independent jobs)', 'site-local collectives',0,0,1.0,1),
 ('Regional inference (local replica)', 'site-local inference',0,0,1.0,1),
 ('Local-SGD / DiLoCo H=100 (70B)', 'intermittent weight sync',ring_collective_gb(70),2,1.0,100),
 ('Local-SGD / DiLoCo H=500 (70B)', 'intermittent weight sync',ring_collective_gb(70),2,1.0,500),
 ('Decoupled DiLoCo H=500 (70B)', 'asynchronous weight sync',ring_collective_gb(70),2,.2,500),
 ('Decoupled DiLoCo H=500 (1T)', 'asynchronous weight sync',ring_collective_gb(1000),2,.2,500),
]
rows=[]
for label,year,step,bw,speed_gain in HORIZONS:
 for strategy,granularity,payload,rtts,exposure,interval in METHODS:
  for distance in (50,250,800):
   vals=training_overhead(payload,bw,step,0 if payload==0 else rtts,
                          exposure,distance)
   # Only ONE WAN link's load in one synchronization interval; averaged
   # time per local step for H-step local learning. WAN link may be shared.
   if interval>1:
    effective=vals['network_overhead_pct']/interval
    efficiency=100/(1+effective/100)
   else:
    effective=vals['network_overhead_pct']; efficiency=vals['network_only_efficiency_pct']
   rows.append(dict(year=year,hardware_scenario=label,method=strategy,exchange_type=granularity,
       representative_site_distance_km=distance,illustrative_step_s=step,
       site_count=SITE_COUNT,wan_link_rated_gbps=bw,delivered_fraction=DELIVERED_FRACTION,
       payload_GB_per_exchange=round(payload,5),serial_rtt_dependencies=rtts,
       local_steps_per_exchange=interval,exposed_fraction=exposure,
       physical_rtt_lower_bound_ms=round(vals['physical_rtt_floor_ms'],4),
       routed_RTT_assumption_ms=round(vals['illustrative_rtt_ms'],4),
       wire_serialization_s_per_exchange=round(vals['serialization_s'],5),
       communication_overhead_pct_per_local_step=round(effective,3),
       network_only_efficiency_pct=round(efficiency,3),
       same_workload_compute_speedup_assumption=speed_gain))

def write(name,records):
 with (OUT/name).open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
write('horizon_training_methods.csv',rows)

# Explicitly distinguish a *network-only* training overhead from a
# target-quality time-to-train comparator. Qualitative convergence impacts are
# UNKNOWN: these are sensitivity multipliers, not observed quality losses.
quality=[]
for rec in rows:
 if rec['representative_site_distance_km']!=250:continue
 if rec['method'] not in ['Data parallel (all-reduce)', 'Decoupled DiLoCo H=500 (70B)',
                          'Decoupled DiLoCo H=500 (1T)', 'Pipeline parallel (WAN stage)']:
  continue
 for q in (1.0,1.05,1.2):
  overhead=rec['communication_overhead_pct_per_local_step']/100
  goodput=(1/(1+overhead))/q
  quality.append(dict(year=rec['year'],method=rec['method'],
      distance_km=250,unknown_extra_work_to_quality_multiplier=q,
      illustrative_quality_adjusted_goodput_pct=round(100*goodput,3),
      qualification='Quality multiplier unmeasured; not a frontier benchmark'))
write('horizon_quality_sensitivity.csv',quality)

# Normalization uses 7.5 GW of proposed gas-fired output for Wonder Valley and
# Wang's 25.7-30.5 MtCO2e annual ESTIMATE; scope comparability is not established.
from bc_datacentre_screening import calculate
bc=calculate(); peak=bc['facility_peak_mw']; annual_average=bc['facility_gwh_y']*1000/8760
comparison=[]
for bc_intensity in (10,25,50,100,150,250):
 bc_annual_mt=bc['facility_gwh_y']*bc_intensity/1e6
 bc_kg_per_avg_mw_year=bc_annual_mt*1e9/annual_average
 for wonder_mt in (25.7,30.5):
  w_t_per_mw_yr=wonder_mt*1e6/7500
  b_t_per_mw_yr=bc_kg_per_avg_mw_year/1000
  comparison.append(dict(bc_grid_emission_intensity_kg_per_MWh=bc_intensity,
   bc_annual_emissions_MtCO2e=round(bc_annual_mt,4),
   bc_average_facility_load_MW=round(annual_average,3),
   bc_tCO2e_per_continuous_MW_year=round(b_t_per_mw_yr,2),
   wonder_project_gas_generation_GW=7.5,
   wonder_reported_emissions_MtCO2e_per_year=wonder_mt,
   wonder_tCO2e_per_continuous_MW_year=round(w_t_per_mw_yr,2),
   screening_reduction_pct=round(100*(1-b_t_per_mw_yr/w_t_per_mw_yr),2),
   comparable_scope_verified=False))
write('wonder_per_mw_emissions_comparison.csv',comparison)
# Derived heat is generation-potential and captured/delivered *assumption*.
heat=[dict(project='Digital Gardens 17-site (conditional scenario)',
    IT_load_TWh_yr=round(bc['it_gwh_y']/1000,4),
    captured_heat_TWh_yr=round(bc['recovered_potential_gwh_y']/1000,4),
    nominal_useful_heat_TWh_yr=round(bc['useful_heat_gwh_y']/1000,4),
    verified_useful_heat_TWh_yr='',
    useful_heat_MWh_per_avg_facility_MW_yr=round(bc['useful_heat_gwh_y']*1000/annual_average,2),
    comment='Modeled 85% heat capture, 60% utilization; no signed loads'),
  dict(project='Wonder Valley (proposed 7.5 GW gas capacity)',
    IT_load_TWh_yr='',captured_heat_TWh_yr='',nominal_useful_heat_TWh_yr='',
    verified_useful_heat_TWh_yr='',useful_heat_MWh_per_avg_facility_MW_yr='',
    comment='No quantified external useful-heat offtake verified; zero is NOT demonstrated waste rate')]
write('heat_benchmark_scope.csv',heat)
assert 8<rtt_ms(800)[1]<15
assert ring_collective_gb(70)>260
assert len(rows)==len(HORIZONS)*len(METHODS)*3
assert bc['facility_peak_mw']>4000
print('Horizon training strategies:',len(METHODS),'records:',len(rows))
for year in (2026,2036,2041):
 for method in ('Data parallel (all-reduce)','Decoupled DiLoCo H=500 (70B)','Decoupled DiLoCo H=500 (1T)','Regional inference (local replica)'):
  r=next(x for x in rows if x['year']==year and x['representative_site_distance_km']==250 and x['method']==method)
  print(year, method,'overhead=',r['communication_overhead_pct_per_local_step'],'eff=',r['network_only_efficiency_pct'])
print('50 kg screening:',[r['screening_reduction_pct'] for r in comparison if r['bc_grid_emission_intensity_kg_per_MWh']==50])
