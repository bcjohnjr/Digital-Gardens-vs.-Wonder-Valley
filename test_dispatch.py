import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'software'))
import renewable_dispatch as rd
class TestRenewableDispatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.sites,cls.info,cls.monthly=rd.load_input()
  cls.shapes=rd.hourly_shapes(cls.sites,cls.info,cls.monthly)
 def test_exact_site_count(self):
  self.assertEqual(len(self.sites),17)
  self.assertAlmostEqual(sum(float(s['it_mw']) for s in self.sites),3624.51,places=2)
 def test_shapes_not_exceed_capacity(self):
  for node,seq in self.shapes.items():
   self.assertEqual(len(seq),8760)
   self.assertTrue(all(0<=pv<=1 and 0<=w<=1 for pv,w,_ in seq),node)
 def test_monthly_energy_reconciliation(self):
  for s in self.sites:
   name=s['node'];seq=self.shapes[name]
   for m in range(1,13):
    r=self.monthly[(name,m)];monthly=[(pv,w) for pv,w,mo in seq if mo==m]
    self.assertAlmostEqual(sum(a for a,b in monthly),float(r['pv_kwh_per_kwp']),places=4)
    self.assertAlmostEqual(sum(b for a,b in monthly),len(monthly)*float(r['wind_assumed_cf']),places=4)
 def test_two_site_transfers_40mw(self):
  # 2 sites, 50MW active per site and 90MW receiver cap -> transfer 40
  x=rd.allocate_one([90,90],[90,0],[0,0],util=50/(90*rd.PUE),movable=.85,surcharge=0)
  self.assertAlmostEqual(x['before'],50)
  self.assertAlmostEqual(x['after'],10)
  self.assertAlmostEqual(x['shift'],40)
 def test_transfer_energy_and_conservation(self):
  x=rd.allocate_one([90,90],[90,0],[0,0],util=50/(90*rd.PUE),movable=.85,surcharge=.02)
  self.assertAlmostEqual(sum(x['final'])-sum(x['original']),.02*x['shift'])
  self.assertLessEqual(x['after'],x['before'])
  self.assertTrue(all(job<rated+1e-8 for job,rated in zip(x['final'],x['rated'])))
 def test_zero_spare_capacity_gives_no_shifting(self):
  x=rd.allocate_one([50,50],[90,0],[0,0],util=1.,movable=1.,surcharge=0)
  self.assertAlmostEqual(x['shift'],0)
 def test_scenario_totals(self):
  s,sites,months,hours=rd.calc(self.sites,self.shapes,'Hybrid expansion',save_hourly=True)
  self.assertAlmostEqual(s['grid_saved_gwh'],129.1794745,places=2)
  self.assertEqual(len(sites),17)
  self.assertEqual(len(hours),8760)
  self.assertLessEqual(s['grid_coordinated_gwh'],s['grid_baseline_gwh'])
 def test_no_peak_capacity_claim(self):
  for scen in rd.SCENARIOS:
   r,*_=rd.calc(self.sites,self.shapes,scen)
   self.assertAlmostEqual(r['grid_peak_reduction_mw'],0,places=5)
if __name__=='__main__':unittest.main()
