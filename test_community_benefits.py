import sys, unittest
sys.path.insert(0,__file__.rsplit('/',1)[0])
from community_benefits import CONFIG, estimate, puematrix
class TestCommunity(unittest.TestCase):
 def test_pop(self): self.assertEqual(estimate(CONFIG,2)['population'],787934)
 def test_half(self): self.assertEqual(estimate(CONFIG,1)['population'],393967)
 def test_none_home(self): self.assertEqual(estimate(CONFIG,2)['annual_household_electricity_subsidy_mcad'],0)
 def test_energy(self): self.assertAlmostEqual(estimate(CONFIG,2)['charging_gwh'],706.951894444,places=5)
 def test_peak(self): self.assertAlmostEqual(estimate(CONFIG,2)['illustrative_charger_peak_mw'],120.553902)
 def test_phase(self): self.assertAlmostEqual(estimate(CONFIG,1)['total_annual_community_value_mcad']*2,estimate(CONFIG,2)['total_annual_community_value_mcad'])
 def test_parity(self):
  d=dict(CONFIG,ag_fossil_parity_gap_cad_per_litre=-.1,other_fossil_parity_gap_cad_per_litre=-.2)
  self.assertEqual(estimate(d,2)['agricultural_fuel_price_parity_subsidy_mcad'],0)
  self.assertEqual(estimate(d,2)['other_renewable_fuel_parity_subsidy_mcad'],0)
 def test_2026(self):
  base=[v for v in puematrix() if v['it_utilization']==.9 and v['pue']==1.15][0]
  self.assertAlmostEqual(base['facility_twh'],32.861982366,places=8)
  self.assertAlmostEqual(base['heat_potential_enduse_twh'],14.5735747884,places=8)
 def test_capture_independent_of_pue(self):
  a=[x for x in puematrix() if x['it_utilization']==.65]
  self.assertEqual(len(set(round(x['heat_capture_twh'],8) for x in a)),1)
 def test_entitlements(self):
  full=estimate(CONFIG,2);half=estimate(CONFIG,1)
  self.assertEqual(full['produce_allocated_tonnes'],115038.364)
  self.assertEqual(full['seafood_allocated_tonnes'],36244.964)
  self.assertAlmostEqual(half['produce_allocated_tonnes']*2,full['produce_allocated_tonnes'])
  self.assertAlmostEqual(half['seafood_allocated_tonnes']*2,full['seafood_allocated_tonnes'])
 def test_revised_food_values(self):
  full=estimate(CONFIG,2)
  self.assertAlmostEqual(full['greenhouse_food_market_value_mcad'],402.634274)
  self.assertAlmostEqual(full['seafood_market_value_mcad'],253.714748)
  self.assertAlmostEqual(full['total_annual_community_value_mcad'],1876.6514349305)
 def test_food_supply_capacity(self):
  full=estimate(CONFIG,2)
  self.assertLess(full['produce_share_of_projected_harvest_pct'],100)
  self.assertLess(full['seafood_share_of_projected_harvest_pct'],100)
  self.assertLess(full['seafood_share_of_saleable_supply_pct'],100)
  self.assertAlmostEqual(full['seafood_share_of_saleable_supply_pct'],46.4679025641,places=5)
 def test_positive_finance_gap(self):self.assertGreater(estimate(CONFIG,2)['remaining_4600m_value_mcad'],2500)
if __name__=='__main__':unittest.main()
