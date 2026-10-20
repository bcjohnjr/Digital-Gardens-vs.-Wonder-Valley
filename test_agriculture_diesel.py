import sys,unittest
sys.path.insert(0,__file__.rsplit('/',1)[0])
from agriculture_diesel import *
from community_benefits import CONFIG,estimate
class FarmModelTests(unittest.TestCase):
 def test_eight_regions(self):self.assertEqual(len(RDS),8)
 def test_seventeen_communities(self):self.assertEqual(len(NODES),17)
 def test_rd_weights(self):
  for r in RDS:self.assertAlmostEqual(sum(w for _,c,w in NODES if c==r[1]),1)
 def test_no_site_double_count(self):
  d,site,s=calculate();self.assertAlmostEqual(sum(x['attributed_diesel_l'] for x in site),s['diesel_l'])
 def test_fuel_intensity_nonnegative(self):
  d,_,s=calculate();self.assertGreater(s['diesel_l'],0);self.assertTrue(all(z['estimated_diesel_l']>=0 for z in d))
 def test_fuel_gap_floor(self):self.assertEqual(calculate(price_gap=-.1)[2]['ag_parity_cad_year'],0)
 def test_fuel_vs_old_volume(self):self.assertLess(calculate()[2]['diesel_l'],100_000_000)
 def test_community_sync(self):self.assertAlmostEqual(estimate(CONFIG,2)['agricultural_fuel_price_parity_subsidy_mcad']*1e6,calculate()[2]['ag_parity_cad_year'])
 def test_phase_addition(self):self.assertAlmostEqual(estimate(CONFIG,1)['agricultural_fuel_price_parity_subsidy_mcad']*2,estimate(CONFIG,2)['agricultural_fuel_price_parity_subsidy_mcad'])
 def test_scale_monotonic(self):self.assertLess(calculate(.5)[2]['diesel_l'],calculate(1.6)[2]['diesel_l'])
if __name__=='__main__':unittest.main()
