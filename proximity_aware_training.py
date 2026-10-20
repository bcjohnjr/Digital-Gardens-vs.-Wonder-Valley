"""Proximity-aware frontier-training communication SCREENING model.

Not a measured training benchmark. Evaluates *critical-path* WAN transfer time
for a supplied inter-site sync payload and exposed (unhidden) fraction of that
transfer compared with a workload-matched same-hardware local baseline.
Inter-site payload is assumed to traverse a single bottleneck link; bandwidth
is gigabits/s, converted to bytes/s by division by eight. Topology and load
balancing are not validated. Zero cross-site traffic means separate jobs or a
fully localized model, NOT distributed synchronous frontier training.
"""
import csv
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'results'
OUT.mkdir(parents=True,exist_ok=True)
BASE_STEP_S=20.0  # illustrative measured-local-baseline placeholder

# Scenario labels are conditional; none are empirical predictions.
SCENARIOS=[
 ('local_only_independent_jobs',0.0,400,0.5,2.0,1.0),
 ('nearby_partitioned_1GB',1.0,400,0.5,2.0,0.2),
 ('nearby_partitioned_10GB',10.0,400,0.5,2.0,0.2),
 ('nearby_partitioned_100GB',100.0,400,0.5,2.0,0.2),
 ('nearby_partitioned_1TB',1000.0,400,0.5,2.0,0.2),
 ('nearby_no_overlap_10GB',10.0,400,0.5,2.0,1.0),
 ('regional_10GB_100Gbps',10.0,100,0.5,1.0,0.2),
 ('regional_10GB_800Gbps',10.0,800,0.5,1.0,0.2),
 ('regional_10GB_1600Gbps',10.0,1600,0.5,1.0,0.2),
 ('nearby_10GB_high_overlap',10.0,400,0.5,2.0,0.05),
]

def evaluate(payload_gb, link_gbps, usable_fraction, rtt_ms, exposed_fraction, local_step_s=BASE_STEP_S):
    assert local_step_s>0 and link_gbps>0 and 0<usable_fraction<=1
    assert payload_gb>=0 and 0<=exposed_fraction<=1
    # decimal gigabytes -> decimal gigabits and network RTT
    wire_s=payload_gb*8.0/(link_gbps*usable_fraction)+(rtt_ms/1000 if payload_gb>0 else 0.0)
    exposed_s=wire_s*exposed_fraction
    return dict(wan_transfer_s=wire_s,exposed_comm_s=exposed_s,
                distributed_step_s=local_step_s+exposed_s,
                slowdown_pct=exposed_s/local_step_s*100)

rows=[]
for name,g,bw,eff,rtt,unhidden in SCENARIOS:
    vals=evaluate(g,bw,eff,rtt,unhidden)
    rows.append(dict(scenario=name,payload_GB=g,link_Gbps=bw,usable_bandwidth_fraction=eff,
                     rtt_ms=rtt,exposed_fraction=unhidden,local_step_s=BASE_STEP_S,
                     **{k:round(v,6) for k,v in vals.items()}))
with (OUT/'proximity_training_scenarios.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

sensitivity=[]
for step in [5,20,60]:
 for gigabytes in [1,10,100,1000]:
  for bw in [100,400,800,1600]:
   for exposed in [0.05,0.2,1.0]:
    r=evaluate(gigabytes,bw,0.5,2.0,exposed,step)
    sensitivity.append(dict(local_step_s=step,payload_GB=gigabytes,link_Gbps=bw,
        usable_fraction=0.5,rtt_ms=2,exposed_fraction=exposed,
        slowdown_pct=round(r['slowdown_pct'],5)))
with (OUT/'proximity_training_sensitivity.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(sensitivity[0]));w.writeheader();w.writerows(sensitivity)
assert abs(evaluate(10,400,0.5,2,0.2)['slowdown_pct']-0.402)<.001
assert evaluate(0,400,0.5,2,1)['slowdown_pct']==0
assert evaluate(1000,400,0.5,2,.2)['slowdown_pct']>30
print('Reproduced scenario rows:')
for row in rows:print(row['scenario'],f"{row['slowdown_pct']:.3f}%")
