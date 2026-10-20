import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'software'))
from circular_aquaculture_berry import annual,SHARES
class TestCircular(unittest.TestCase):
 def setUp(self): self.s,self.p,self.m=annual('Expansion')
 def test_fraction(self):self.assertAlmostEqual(sum(SHARES.values()),1)
 def test_warm(self):self.assertAlmostEqual(self.s['warmwater_share_pct'],70)
 def test_prod(self):self.assertEqual(sum(x['annual_liveweight_t'] for x in self.p),120000)
 def test_feed(self):self.assertAlmostEqual(self.s['dry_feed_t'],sum(x['dry_complete_feed_t'] for x in self.p))
 def test_residue_limit(self):self.assertLess(self.s['feed_grade_plant_ingredient_t'],self.s['dry_feed_t']*.10)
 def test_no_double_fruit(self):self.assertLessEqual(self.s['berry_to_dryer_t'],9961.35)
 def test_freshwater_only(self):self.assertGreater(self.s['freshwater_N_available_t'],0)
 def test_algae_mass_limited(self):self.assertLessEqual(self.s['theoretical_dry_algae_max_t'],self.s['saline_N_available_for_algae_t']/.08+1e-5)
 def test_no_negative_gap(self):self.assertGreaterEqual(self.s['algal_oil_external_gap_t'],0)
 def test_energy(self):self.assertGreater(self.s['minimum_total_extra_electricity_GWh'],3000)
 def test_ras_jobs(self):self.assertGreater(self.s['ras_FTE_low'],1900)
 def test_gh_jobs(self):self.assertEqual(self.s['greenhouse_FTE_low'],4000)
 def test_jobs(self):self.assertGreater(self.s['annual_direct_FTE_high'],self.s['annual_direct_FTE_low'])
 def test_months(self):self.assertEqual(len(self.m),12)
if __name__=='__main__':unittest.main()
